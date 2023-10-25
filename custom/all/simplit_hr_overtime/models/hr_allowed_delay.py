# -*- coding: utf-8 -*-
#####################

from odoo import fields, api, models, _
from pytz import timezone
import babel
import pytz
import calendar
import datetime
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import datetime
from datetime import datetime as dt
import time

def get_part_of_day(hour):
    return (
        "morning" if 5 <= hour <= 11.59
        else
        "afternoon" if 12 <= hour <= 17
        else
        "evening" if 18 <= hour <= 22
        else
        "night"
    )

def convert_string_into_datetime(sting_date):
    datetime_value = datetime.datetime.strptime(sting_date, '%Y-%m-%d %H:%M') - timedelta(hours=3, minutes=00, seconds=00)
    return datetime_value

class SimplitHrDelay(models.Model):
    _name = "simplit.hr.delay"
    _description = "Simplit Hr Allowed Delay time"
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    manager_id = fields.Many2one('hr.employee', string='Manager')
    start_date = fields.Date('Date')
    late_login = fields.Datetime('Late login')
    delay_time = fields.Float('Delayed Time')
    notes = fields.Text(string='Notes')
    type_penality = fields.Text(string='Penality')
    monthly_delay = fields.Float('Monthly Allowed Delay')
    approved_delay = fields.Float("Approved Delay Hours ")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Waiting Approval'), ('refuse', 'Refused'),
                              ('validate', 'Approved'), ('cancel', 'Cancelled')], default='draft', copy=False)



    def unlink(self):
        if any(self.filtered(lambda delay: delay.state not in ('draft', 'cancel'))):
            raise UserError(_('You cannot delete a delay record which is not draft or cancelled!'))
        return super(SimplitHrDelay, self).unlink()


    def action_submit(self):
        return self.write({'state': 'confirm'})


    def action_cancel(self):
        return self.write({'state': 'cancel'})


    def action_approve(self):
        return self.write({'state': 'validate'})


    def action_refuse(self):
        return self.write({'state': 'refuse'})

    @api.model
    def run_delay_time_scheduler(self):
        """ This Function is called by scheduler. """
        emp_ids = self.env['hr.employee'].search([])
        allowed_delay = self.env.user.company_id.allowed_delay_time
        half_pay_setting = self.env.user.company_id.half_pay
        threeforth_pay_setting = self.env.user.company_id.threeforth_pay
        penalty_type_setting = self.env.user.company_id.penalty_type
        full_pay_setting = self.env.user.company_id.full_pay
        delay_records = []
        # for emp in emp_ids:
        query = """select check_in,employee_id,only_date,check_out from hr_attendance group by check_in,employee_id,only_date,check_out"""
        self.env.cr.execute(query)
        delay_time_records = self.env.cr.fetchall()
        for record in delay_time_records:
            delayed_leave_list = []
            employee = self.env['hr.employee'].search([('id', '=', record[1])])
            # if self.env.user.tz:
            #     tz = pytz.timezone('Asia/Kolkata')
            # else:
            #     tz = pytz.utc
            # users_timezone = pytz.utc.localize(record[0]).astimezone(tz)
            # seconds = (users_timezone.hour * 60 + users_timezone.minute) * 60 + users_timezone.second
            # login_time = seconds/3600
            day = record[0].weekday()
            contract = self.env['hr.contract'].search([('employee_id', '=', record[1])])
            for leave_days in contract.resource_calendar_id.global_leave_ids:
                delta = leave_days.date_to - leave_days.date_from
                for i in range(delta.days + 1):
                    delayed_day = leave_days.date_from + timedelta(days=i)
                    delayed_leave_list.append(delayed_day.date())

            for shift_hour in contract.resource_calendar_id.attendance_ids:
                if str(shift_hour.dayofweek) == str(day):
                    new = 0
                    if contract.employee_allowed_delay:
                        new = shift_hour.hour_from + contract.employee_allowed_delay/60
                    elif allowed_delay:
                        new = shift_hour.hour_from + allowed_delay/60
                    actual_login = str(record[2]) + ' ' + '{0:02.0f}:{1:02.0f}'.format(*divmod(new*60, 60))
                    max_day_checkin = convert_string_into_datetime(actual_login)
                    actual_logout = str(record[2]) + ' ' + '{0:02.0f}:{1:02.0f}'.format(*divmod(shift_hour.hour_to *60, 60))
                    max_day_checkout = convert_string_into_datetime(actual_logout)
                    checkin_attendance_id_utc = self.env['hr.attendance'].search(
                        [('employee_id', '=', record[1]),
                         ('check_in', '>', max_day_checkin),
                         ('check_in', '<=', max_day_checkout),
                         ('delaytime_created', '!=', True)
                         ], order='check_in', limit=1)
                    if checkin_attendance_id_utc not in delay_records:
                        delay_records += checkin_attendance_id_utc
                        if checkin_attendance_id_utc:
                            if record[2] not in delayed_leave_list:
                                rec_seconds = ((checkin_attendance_id_utc.check_in.hour * 60 + checkin_attendance_id_utc.check_in.minute) * 60 + checkin_attendance_id_utc.check_in.second) / 3600
                                login_seconds = ((max_day_checkin.hour * 60 + max_day_checkin.minute) * 60 + max_day_checkin.second) / 3600
                                delay = rec_seconds - login_seconds
                                if penalty_type_setting == 'none':
                                    continue
                                if penalty_type_setting == 'fixed_penalty':
                                    vals = {
                                        'employee_id': checkin_attendance_id_utc.employee_id.id,
                                        'manager_id': employee.parent_id.id or False,
                                        'delay_time': delay,
                                        'type_penality': 'Fixed Penalty',
                                        'start_date': checkin_attendance_id_utc.only_date,
                                        'late_login': checkin_attendance_id_utc.check_in,
                                        'monthly_delay' : contract.monthly_allowed_delay
                                    }
                                    self.env['simplit.hr.delay'].create(vals)
                                    checkin_attendance_id_utc.delaytime_created = True
                                elif penalty_type_setting == 'based_on_wage':
                                    # if delay*60 == half_pay_setting:
                                    #     continue
                                    vals = {
                                        'employee_id': checkin_attendance_id_utc.employee_id.id,
                                        'manager_id': employee.parent_id.id or False,
                                        'delay_time': delay,
                                        'type_penality': 'Based on Wage',
                                        'start_date': checkin_attendance_id_utc.only_date,
                                        'late_login': checkin_attendance_id_utc.check_in,
                                        'monthly_delay' : contract.monthly_allowed_delay
                                    }
                                    self.env['simplit.hr.delay'].create(vals)
                                    checkin_attendance_id_utc.delaytime_created = True

    @api.model
    def get_the_action_of_partial_approval(self):
        if len(set(self.mapped('employee_id'))) > 1:
            raise UserError(_('You cannot select more than one employee!'))
        context = self._context.copy()
        delay_id = self.env['simplit.hr.delay'].browse(self.ids[0])
        context.update({'default_employee_id': delay_id.employee_id.id,
                        'active_ids': self.ids,
                        'default_overtime_or_delay':True})
        action = self.env.ref('simplit_hr_overtime.overtime_delay_approval_wizard_action').read()[0]
        action['context'] = context
        return action

class DelayApproval(models.Model):
    _name = 'simplit.delay.approval'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    manager_id = fields.Many2one('hr.employee', string='Manager')
    total_delay_time = fields.Float('Actual Delay',compute='delays_in_month',store=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Waiting Approval'), ('refuse', 'Refused'),
           ('validate', 'Approved'), ('cancel', 'Cancelled')], default='draft', copy=False)
    monthly_allow_delay = fields.Float('Monthly Allowed Delay',compute='delays_in_month',store=True)
    delay_approve = fields.Float('Approved Delay')
    approval_from = fields.Date(string='Date From', readonly=True, required=True,
        default=lambda self: fields.Date.to_string(date.today().replace(day=21)), states={'draft': [('readonly', False)]})
    approval_to = fields.Date(string='Date To', readonly=True, required=True,
        default=lambda self: fields.Date.to_string((dt.now() + relativedelta(months=+1, day=21, days=-1)).date()),states={'draft': [('readonly', False)]})


    @api.depends('employee_id')
    def delays_in_month(self):
        for approve_d in self:
            delay_obj = self.env['simplit.hr.delay'].search([('employee_id', '=', approve_d.employee_id.id),
                                                             ('start_date', '!=', False)])
            total_delay = 0
            for delay_record in delay_obj:
                if delay_record.start_date >= approve_d.approval_from and delay_record.start_date <= approve_d.approval_to:
                    approve_d.manager_id = delay_record.manager_id.id
                    total_delay += delay_record.delay_time
                    approve_d.monthly_allow_delay = delay_record.monthly_delay
                approve_d.total_delay_time = total_delay

    @api.onchange('employee_id')
    def approve_delay_time(self):
        for approve_time in self:
            self.delay_approve = approve_time.total_delay_time


    def action_submit(self):
        return self.write({'state': 'confirm'})


    def action_cancel(self):
        return self.write({'state': 'cancel'})


    def action_approve(self):
        return self.write({'state': 'validate'})


    def action_refuse(self):
        return self.write({'state': 'refuse'})


    def unlink(self):
        if any(self.filtered(lambda delaytime: delaytime.state not in ('draft', 'cancel'))):
            raise UserError(_('You cannot delete delay time record which is not draft or cancelled!'))
        return super(DelayApproval, self).unlink()

    @api.constrains('employee_id')
    def _check_payslip_duplicate(self):
        records = self.env['simplit.delay.approval'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'validate')])
        for record in records:
            if record.approval_from == self.approval_from and record.approval_to == self.approval_to or record.approval_from == self.approval_from:
                raise ValidationError(_("Sorry...!,Approval for this period is already existed"))


class Contract(models.Model):
    _inherit = 'hr.contract'

    var_delay_pay = fields.Integer(string='Fixed Delay Amount')
    var_overtime_pay = fields.Integer(string='Fixed Overtime Amount')
    kpi_quarterly = fields.Integer(string='KPI(Quarterly)')
    kpi_annually = fields.Integer(string='KPI(Annually)')
    bonus_interval = fields.Selection([('quarterly','Quarterly'),('annual','Annually')],'Bonus Interval')
    quarter_date = fields.Date(string='Quarter Date')
    yearly_date = fields.Date(string='Yearly Date')
    employee_allowed_delay = fields.Integer(string='Allowed Delay Minutes')
    employee_allowed_overtime = fields.Integer(string='Overtime Buffer')
    monthly_allowed_delay = fields.Float('Monthly Allowed Delay')

    @api.constrains('bonus_interval')
    @api.onchange('bonus_interval')
    def get_quarter_date(self):
        payslip_records = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id),('state','=','done')])
        qty_date = self.date_start + relativedelta(months=+3, day=1, days=-1)
        yrly_date = self.date_start + relativedelta(months=+12, day=1, days=-1)
        if self.bonus_interval == 'quarterly':
            self.quarter_date = qty_date
            self.yearly_date=0
        elif self.bonus_interval == 'annual':
            self.yearly_date = yrly_date
            self.quarter_date=0

    def run_bonus_scheduler(self):
        contract_records = self.env['hr.contract'].search([])
        for contract in contract_records:
            payslip_records = self.env['hr.payslip'].search([('employee_id', '=', contract.employee_id.id),
                                                             ('contract_id', '=', contract.id),
                                                             ('state', '=', 'done')])
            for payslip in payslip_records:
                if contract.quarter_date and payslip.date_from.month == contract.quarter_date.month:
                    updated_qty_date = contract.quarter_date + relativedelta(months=+3, day=1)
                    contract.quarter_date = updated_qty_date
                elif contract.yearly_date and payslip.date_from.month == contract.yearly_date.month:
                    updated_yrl_date = contract.yearly_date + relativedelta(months=+12, day=1)
                    contract.yearly_date = updated_yrl_date


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    date_from = fields.Date(string='Date From', readonly=True, required=True,
        default=lambda self: fields.Date.to_string(date.today().replace(day=17)), states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='Date To', readonly=True, required=True,
        default=lambda self: fields.Date.to_string((dt.now() + relativedelta(months=+1, day=17, days=-1)).date()),
        states={'draft': [('readonly', False)]})
    late_logins_of_month = fields.Integer('Total Late Logins', compute='total_delaytimes')
    total_delay_time = fields.Float('Total DelayTime', compute='total_delaytimes')
    penalty = fields.Float('Penalty For Late', compute='total_delaytimes')
    fixed = fields.Boolean('fixed')
    wage = fields.Boolean('Wage')
    kpi_value = fields.Integer('KPI')

    def _get_delay_amount_from_ratio_rules(self,employee_id,delay_records):
        day_of_week = {'Monday': '0', 'Tuesday': '1', 'Wednesday': '2', 'Thursday': '3', 'Friday': '4', 'Saturday': '5',
                       'Sunday': '6'}
        amount = 0
        total_delay_days = delay_records
        total_delays=[]
        rules = self.env['hr.hours.ratio'].search([('hours_type','=','delay')])
        attendance_ids = employee_id.resource_calendar_id.attendance_ids
        for rule in rules:
            if (employee_id.department_id in rule.department_ids and rule.assign_type =='departments')or \
                    (employee_id in rule.employee_ids and rule.assign_type =='employees') or \
                    (employee_id.job_id.job_grade in rule.grade_ids and rule.assign_type =='grades'):
                if rule.day_type == "public holiday":
                    for global_leave in employee_id.resource_calendar_id.global_leave_ids:
                        delay_records=total_delay_days.filtered(lambda x: global_leave.date_from <=
                                                                                     x.start_date <= global_leave.date_to)
                        amount += rule.hour_ratio * sum(delay_records.mapped('approved_delay')) if delay_records else 0
                        total_delay_days -= delay_records
                elif rule.day_type == "weekend":
                    delay_records = total_delay_days.filtered(lambda x: (day_of_week[x.start_date.strftime("%A")]
                                                                      not in attendance_ids.mapped('dayofweek')))
                    total_delay_days -= delay_records
                    if not delay_records:
                        for attendance_id in attendance_ids:
                            delay_records = total_delay_days.filtered(lambda x: day_of_week[x.start_date.strftime("%A")] == attendance_id.dayofweek
                                                                               and not attendance_id.hour_from )
                            amount += rule.hour_ratio * sum(delay_records.mapped('approved_delay')) if delay_records else 0
                            total_delay_days -= delay_records
                elif rule.day_type == "working day":
                    for attendance_id in attendance_ids:
                        delay_records=total_delay_days.filtered(lambda x: day_of_week[x.start_date.strftime("%A")] == attendance_id.dayofweek
                                                                           and attendance_id.hour_from )
                        amount += rule.hour_ratio * sum(delay_records.mapped('approved_delay')) if delay_records else 0
                        total_delay_days -= delay_records
        return amount

    @api.onchange('employee_id', 'contract_id', 'date_from', 'date_to')
    @api.depends('employee_id', 'contract_id', 'date_from', 'date_to')
    def total_delaytimes(self):
        print('totaaaaaaaaaaaaal')
        penalty_settings = self.env.user.company_id.penalty_amount
        penalty_type_settings = self.env.user.company_id.penalty_type
        penalty_amount = 0
        if not penalty_type_settings:
            raise Warning(_("Please configure 'Delay Penalty Type' for Company!"))
        for slip in self:
            print('slip=======',slip)
            delay_records = self.env['simplit.hr.delay'].search(
                [('employee_id', '=', slip.employee_id.id), ('state', '=', 'validate'),
                 ('start_date','>=',slip.date_from),('start_date','<=',slip.date_to)])
            contract_id = slip.contract_id
            monthly_delay_time = sum(delay_records.mapped('approved_delay'))
            monthly_allow_delay_time = sum(delay_records.mapped('monthly_delay'))
            total_delaytime = monthly_delay_time - monthly_allow_delay_time
            if total_delaytime > 0:
                if penalty_type_settings == 'fixed_penalty':
                    if slip.employee_id.contract_id.var_delay_pay:
                        penalty_amount = slip.employee_id.contract_id.var_delay_pay
                    elif penalty_settings:
                        penalty_amount = penalty_settings
                    # penalty_amount = self._get_delay_amount_from_ratio_rules(slip.employee_id,delay_records)
                    if slip and slip.id and isinstance(slip.id, int):
                        slip.total_delay_time = total_delaytime
                    else:
                        slip.total_delay_time = 0.0
                elif penalty_type_settings == 'based_on_wage':
                    penalty_amount = self._get_delay_amount_from_ratio_rules(slip.employee_id,delay_records)
                    if slip and slip.id and isinstance(slip.id, int):
                        slip.total_delay_time = total_delaytime
                    else:
                        slip.total_delay_time = 0.0

            else:
                if slip and slip.id and isinstance(slip.id, int):
                    slip.total_delay_time = 0.0
                else:
                    slip.total_delay_time = 0.0

            slip.late_logins_of_month = len(delay_records)
            slip.penalty += penalty_amount


    def delay_time_view(self):
        delayed_record = self.env['simplit.hr.delay'].search([('state', '=', 'validate'),
                                                                    ('employee_id', '=', self.employee_id.id),
                                                                    ('start_date', '>=', self.date_from),
                                                                    ('start_date', '<=', self.date_to)])
        return {
            'name': _("Delay time"),
            'type': 'ir.actions.act_window',
            'res_model': 'simplit.hr.delay',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', delayed_record.ids)],
        }

    @api.onchange('employee_id')
    def bool_type_payslip(self):
        type_of_penalty = self.env.user.company_id.penalty_type
        if not type_of_penalty:
            raise Warning(_("Please configure 'Delay Penalty Type' in company!"))
        if type_of_penalty == 'fixed_penalty':
            self.fixed = True
            self.wage = False
        elif type_of_penalty == 'based_on_wage':
            self.fixed = False
            self.wage = True


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    date_start = fields.Date(string='Date From', required=True, readonly=True,
        states={'draft': [('readonly', False)]}, default=lambda self: fields.Date.to_string(date.today().replace(day=21)))
    date_end = fields.Date(string='Date To', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: fields.Date.to_string((dt.now() + relativedelta(months=+1, day=21, days=-1)).date()))


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    delaytime_created = fields.Boolean(string='Delaytime Created', default=False)
    early_in = fields.Float("Early In",compute="_compute_early_late_in_out")
    early_out = fields.Float("Early Out",compute="_compute_early_late_in_out")
    late_in = fields.Float("Late In",compute="_compute_early_late_in_out")
    late_out = fields.Float("Late Out",compute="_compute_early_late_in_out")
    attendance_overtime = fields.Float("Overtime",compute="_compute_early_late_in_out")
    attendance_undertime = fields.Float("Undertime",compute="_compute_early_late_in_out")

    @api.depends('check_in','check_out')
    def _compute_early_late_in_out(self):
        day_of_week = {'Monday':'0' ,'Tuesday':'1' ,'Wednesday':'2' ,'Thursday':'3' ,'Friday':'4' ,'Saturday':'5' ,'Sunday':'6' }
        for record in self:
            record.early_in = 0.0
            record.early_out = 0.0
            record.late_in = 0.0
            record.late_out = 0.0
            record.attendance_overtime = 0.0
            record.attendance_undertime = 0.0
            if record.state and record.state not in ['Working Day','Weekend','Public Holidays']:
                continue
            hour_from = [x.hour_from
                         if record.check_in and day_of_week[record.check_in.strftime("%A")] == x.dayofweek
                         else False
                         for x in record.employee_id.resource_calendar_id.attendance_ids]

            hour_to = [x.hour_to
                       if record.check_out and day_of_week[record.check_out.strftime("%A")] == x.dayofweek
                       else False
                       for x in record.employee_id.resource_calendar_id.attendance_ids]
            hour_from = list(filter(None, hour_from))
            hour_to = list(filter(None, hour_to))
            active_tz = ''
            active_tz = pytz.timezone(record.env.user.tz)
            if record and record.employee_id and record.employee_id.resource_calendar_id and record.employee_id.resource_calendar_id.tz:
                active_tz = pytz.timezone(record.employee_id.resource_calendar_id.tz)
            check_in = record.check_in.replace(tzinfo=pytz.utc).astimezone(active_tz) if record.check_in else False
            check_out = record.check_out.replace(tzinfo=pytz.utc).astimezone(active_tz) if record.check_out else False

            check_in_time = check_in.time().hour + \
                            check_in.time().minute/60.0 if check_in else False
            check_out_time = check_out.time().hour + \
                             check_out.time().minute/60.0 if check_out else False
            if record.state in ['Weekend','Public Holidays']:
                times = check_out_time - check_in_time
                record.attendance_overtime = times
            else:
                if check_in_time and hour_from and check_in_time > hour_from[0]:
                    record.late_in = check_in_time - hour_from[0]
                if check_in_time and hour_from and check_in_time < hour_from[0]:
                    record.early_in = hour_from[0] - check_in_time
                if check_out_time and hour_to and check_out_time > hour_to[0]:
                    record.late_out = check_out_time - hour_to[0]
                if check_out_time and hour_to and check_out_time < hour_to[0]:
                    record.early_out = hour_to[0] - check_out_time
                times = (record.early_in-record.early_out) + (record.late_out - record.late_in)
                if (times+record.worked_hours) > record.employee_id.resource_calendar_id.hours_per_day:
                    record.attendance_overtime = times
                else:
                    record.attendance_undertime = abs(times)

class ResCompany(models.Model):
    _inherit = "res.company"

    allowed_delay_time = fields.Integer(string="Allowed Delay Minutes", readonly=0)
    penalty_type = fields.Selection([('none','None'),('fixed_penalty','Fixed Penalty'), ('based_on_wage', 'Based On Wage')], default='none', readonly=0, string="Delay Penalty Type")
    penalty_amount = fields.Integer(string="Late Penalty", readonly=0)
    half_pay = fields.Integer(string="Half Pay", readonly=0)
    threeforth_pay = fields.Integer(string="3/4th Pay", readonly=0,)
    full_pay = fields.Integer(string="Full Pay", readonly=0,)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allowed_delay_time_setting = fields.Integer("Allowed Delay Minutes", related='company_id.allowed_delay_time', readonly=0)
    penalty_type_settings = fields.Selection([('none','None'),('fixed_penalty', 'Fixed Penalty'), ('based_on_wage', 'Based On Wage')],
                                    default='none', readonly=0,  related='company_id.penalty_type', string="Delay Penalty Type")
    penalty_amount_settings = fields.Integer(string="Penalty Amount",  related='company_id.penalty_amount', readonly=0)
    half_pay_settings = fields.Integer(string="Half Pay", related='company_id.half_pay', readonly=0)
    threeforth_pay_settings = fields.Integer(string="3/4th Pay", related='company_id.threeforth_pay', readonly=0)
    full_pay_settings = fields.Integer(string="Full Pay", related='company_id.full_pay', readonly=0)

    @api.onchange('penalty_type_settings')
    def _penalty_type_change(self):
        if self.penalty_type_settings == 'based_on_wage':
            self.penalty_amount_settings = 0


class WorkLocation(models.Model):
    _name = 'hr.worklocation'

    name = fields.Text(string="Location Name")

    _sql_constraints = [
        ('address_uniq', 'unique(name)', "This Location is already exists !"),
    ]


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # work_location = fields.Many2one('hr.worklocation')
    work_location = fields.Char()
    name_in_arabic = fields.Char(string="Name in Arabic")
