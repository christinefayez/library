# -*- coding: utf-8 -*-
#####################

import datetime
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta

from odoo import fields, api, models, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools.float_utils import float_round


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    day_period = fields.Selection([('morning', 'Morning'), ('afternoon', 'Night')], required=True, default='morning')

class SimplitHrOvertime(models.Model):
    _name = "simplit.hr.overtime"
    _description = "Simplit Hr Overtime"
    _rec_name = 'employee_id'
    _order = 'id desc'

    day_type = fields.Selection([('weekend','Weekend'), ('working day','Working Day'),
                                 ('public holiday','Public Holiday')],string="Day Type")
    # day_period = fields.Selection([('morning','Morning'),('afternoon','Night'),('all_day','Any Time Of Day')],default="all_day")
    time_frame = fields.Selection([('15:19','From 3 PM to 7 PM'),('19:7','From 7 PM to 7 AM')])

    @api.constrains('time_frame')
    def check_day_type_time_frame(self):
        for this in self:
            if this.day_type in ['weekend','public holiday'] and this.time_frame:
                raise ValidationError(_('You can not select a time frame to weekend or puplic holiday types'))

    employee_id = fields.Many2one('hr.employee', string="Employee")
    manager_id = fields.Many2one('hr.employee', string='Manager')
    start_date = fields.Date('Date')
    effective_date = fields.Date('Effective Date')
    overtime_hours = fields.Float('Approved Overtime Hours')
    weekend_working = fields.Float('Week Off worked hours')
    actual_overtime_hours = fields.Float('Actual Overtime Hours')
    notes = fields.Text(string='Notes')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Waiting Approval'), ('refuse', 'Refused'),
           ('validate', 'Approved'), ('cancel', 'Cancelled')], default='draft', copy=False)
    attendance_id = fields.Many2one('hr.attendance', string='Attendance')
    actual_working_hours = fields.Float("Total Working Hours")
    only_day = fields.Char(string="Day", compute='only_startday', store=True)
    emp_week_off = fields.Char(string="Week Off Day")


    def get_the_action_of_partial_approval(self):
        if len(set(self.mapped('employee_id'))) > 1:
            raise UserError(_('You cannot select more than one employee!'))
        context = self._context.copy()
        overtime_id = self.env['simplit.hr.overtime'].browse(self.ids[0])
        context.update({'default_employee_id': overtime_id.employee_id.id,
                        'active_ids': self.ids})
        action = self.env.ref('simplit_hr_overtime.overtime_delay_approval_wizard_action').read()[0]
        action['context'] = context
        return action

    @api.model
    def run_overtime_scheduler(self):
        """ This Function is called by scheduler. """
        emp_ids = self.env['hr.employee'].search([])
        overtime_limit = self.env.user.company_id.simplit_overtime_max
        allowed_overtime = self.env.user.company_id.allowed_over_time_setting
        penalty_type = self.env.user.company_id.overtime_pay_type
        ot_records = []
        wo_records = []
        sc_wo_records =[]
        query = """select sum(worked_hours),only_date,employee_id,overtime_created,only_day_in,off_day from hr_attendance where overtime_created is not true group by only_date,employee_id,overtime_created,only_day_in,off_day"""
        self.env.cr.execute(query)
        attendance_records = self.env.cr.fetchall()
        for record in attendance_records:
            contracts = self.env['hr.contract'].search([('employee_id', '=', record[2])])
            employee = self.env['hr.employee'].search([('id', '=', record[2])])
            weekoff_records =  self.env['week.off'].search([('employee_id', '=', record[2]),('state','=','validate')])
            all_days = []
            all_wkoff = []
            leave_list = []
            for shift_hour in contracts.resource_calendar_id.attendance_ids:
                shift_days = dict(shift_hour._fields['dayofweek'].selection).get(shift_hour.dayofweek)
                if shift_days not in all_days:
                    all_days.append(shift_days)
            for wk in weekoff_records:
                if wk.weekoff_day not in all_wkoff:
                    all_wkoff.append(wk.weekoff_day)

            for leave_days in contracts.resource_calendar_id.global_leave_ids:
                delta = leave_days.date_to - leave_days.date_from
                for i in range(delta.days + 1):
                    day = leave_days.date_from + timedelta(days=i)
                    leave_list.append(day.date())

            if record[4] in all_days:
                if record[4] not in all_wkoff and record[1] not in leave_list:
                    # if record[1] not in leave_list:
                    attend = self.env['hr.attendance'].search([('employee_id', '=', record[2]),('only_day_in', '!=', record[5])])
                    if attend not in ot_records:
                        ot_records += attend
                        if attend:
                            actual_worked_hours = record[0]
                            hours_with_limit = 0
                            if contracts.employee_allowed_overtime:
                                hours_with_limit = contracts.resource_calendar_id.hours_per_day+contracts.employee_allowed_overtime/60
                            elif allowed_overtime:
                                hours_with_limit = contracts.resource_calendar_id.hours_per_day+allowed_overtime/60
                            if actual_worked_hours > hours_with_limit:
                                hours = actual_worked_hours - hours_with_limit
                                if penalty_type == 'none':
                                    continue
                                if penalty_type == 'based_on_wage' or 'fixed_amount':
                                    if hours < overtime_limit:
                                        vals1 = {
                                            'employee_id': record[2],
                                            'manager_id':  employee.parent_id.id or False,
                                            'start_date': record[1],
                                            'effective_date': record[1] + relativedelta(months=+1),
                                            'overtime_hours': round(hours, 2),
                                            'actual_overtime_hours': round(hours, 2),
                                            'emp_week_off': record[5]
                                        }
                                        self.env['simplit.hr.overtime'].create(vals1)
                                    if hours >= overtime_limit:
                                        vals = {
                                            'employee_id': record[2],
                                            'manager_id': employee.parent_id.id or False,
                                            'start_date': record[1],
                                            'effective_date': record[1] + relativedelta(months=+1),
                                            'overtime_hours': round(overtime_limit, 2),
                                            'actual_overtime_hours': round(overtime_limit, 2),
                                            'emp_week_off': record[5]
                                        }
                                        self.env['simplit.hr.overtime'].create(vals)
                                    for attend_record in attend:
                                        attend_record.overtime_created = True
                            elif actual_worked_hours <= hours_with_limit:
                                continue
            elif record[4] not in all_days:
                attend_wo = self.env['hr.attendance'].search([('employee_id', '=', record[2]),('only_day_in', '!=', record[5])])
                if attend_wo not in wo_records:
                    wo_records += attend_wo
                    if attend_wo:
                        if penalty_type == 'none':
                            continue
                        if penalty_type == 'based_on_wage' or 'fixed_amount':
                            vals3 = {
                                'employee_id': record[2],
                                'manager_id': employee.parent_id.id or False,
                                'start_date': record[1],
                                'effective_date': record[1] + relativedelta(months=+1),
                                'weekend_working': record[0],
                                'actual_overtime_hours': record[0],
                                'emp_week_off':record[5]
                            }
                            self.env['simplit.hr.overtime'].create(vals3)
                            for attend_record_wo in attend_wo:
                                attend_record_wo.overtime_created = True

            for wk_rec in weekoff_records:
                wk_attend = self.env['hr.attendance'].search([('employee_id', '=', record[2]),('only_day_in', '=', record[5])])
                for wk_of in wk_attend:
                    if wk_of not in sc_wo_records:
                        sc_wo_records += wk_of
                        if wk_of:
                            if penalty_type == 'none':
                                continue
                            if penalty_type == 'based_on_wage' or 'fixed_amount':
                                vals2 = {
                                    'employee_id': wk_of.employee_id.id,
                                    'manager_id': employee.parent_id.id or False,
                                    'start_date': wk_of.only_date,
                                    'effective_date': wk_of.only_date + relativedelta(months=+1),
                                    'weekend_working': wk_of.worked_hours,
                                    'actual_overtime_hours': wk_of.worked_hours,
                                    'emp_week_off':wk_of.off_day
                                }
                                self.env['simplit.hr.overtime'].create(vals2)
                                for attend_record_wk in wk_attend:
                                    attend_record_wk.overtime_created = True

    @api.depends('start_date')
    def only_startday(self):
        for record in self:
            if record.start_date:
                record.only_day = record.start_date.strftime("%A")

    @api.constrains('overtime_hours')
    @api.onchange('overtime_hours')
    def _check_currect_overtime(self):
        if self.overtime_hours > self.actual_overtime_hours:
            raise UserError(_('You cannot select more than actual overtime!'))


    def unlink(self):
        if any(self.filtered(lambda overtime: overtime.state not in ('draft', 'cancel'))):
            raise UserError(_('You cannot delete a overtime record which is not draft or cancelled!'))
        return super(SimplitHrOvertime, self).unlink()


    def action_submit(self):
        return self.write({'state': 'confirm'})


    def action_cancel(self):
        return self.write({'state': 'cancel'})


    def action_approve(self):
        return self.write({'state': 'validate'})


    def action_refuse(self):
        return self.write({'state': 'refuse'})


    def action_view_attendance(self):
        return {
            'name': _("Attendance Records"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.attendance',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('employee_id', '=', self.employee_id.id)],
        }


# class Contract(models.Model):
#     _inherit = "hr.contract"
#
#     # work_hours = fields.Float(string='Working Hours')
#     weekday_overtime_rate = fields.Float(string="WeekDays Overtime Clock")
#     weekend_overtime_rate = fields.Float(string="WeekOff Overtime Clock")


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    @api.constrains('check_out', 'employee_id')
    def _check_validity(self):
        for attendance in self:
            if not attendance.check_out:
                continue
            # check attendance state
            day_of_week = {'Monday': '0', 'Tuesday': '1', 'Wednesday': '2', 'Thursday': '3', 'Friday': '4',
                           'Saturday': '5',
                           'Sunday': '6'}
            working_day_attendance = attendance.employee_id.resource_calendar_id. \
                attendance_ids.filtered(lambda x: day_of_week[attendance.check_in.strftime("%A")] == x.dayofweek
                                                  and x.hour_from and x.hour_to) if attendance.check_in else False
            public_holidays_attendance = attendance.employee_id.resource_calendar_id.\
                global_leave_ids.filtered(lambda x: x.date_from.date() < attendance.check_in.date() <= x.date_to.date()) if attendance.check_in else False
            print(attendance.check_in.date())
            print(attendance.employee_id.resource_calendar_id.global_leave_ids.filtered(lambda x: x.date_from.date() <= attendance.check_in.date() <= x.date_to.date()))
            print(public_holidays_attendance)

            if attendance.state in ('Public Holidays','Working Day','Weekend') or not attendance.state :
                if public_holidays_attendance:
                    attendance.state = 'Public Holidays'
                elif working_day_attendance:
                    attendance.state = 'Working Day'
                else:
                    attendance.state = 'Weekend'

            # check if there is any delay or overtime
            if attendance.state in ['Working Day', 'Weekend', 'Public Holidays']:
                must_working_hours = attendance.employee_id.resource_calendar_id.hours_per_day
                # create overtime
                if (must_working_hours < attendance.worked_hours and attendance.state == 'Working Day')\
                        or (attendance.state in ['Weekend','Public Holidays'] and attendance.worked_hours):
                    # for weekends it creates overtime with the all worked day hours
                    overtime_hours = attendance.worked_hours - must_working_hours if attendance.state == 'Working Day' else attendance.worked_hours
                    # overtime_hours = overtime_datetime.hour+overtime_datetime.minute/100
                    val = {
                        'employee_id': attendance.employee_id.id,
                        'manager_id': attendance.employee_id.parent_id.id or False,
                        'start_date': attendance.check_in.date(),
                        'effective_date': attendance.check_in.date() + relativedelta(months=+1),
                        'actual_overtime_hours': round(overtime_hours, 2)}
                    if attendance.state == 'Weekend':
                        val['day_type'] = 'weekend'
                        val['time_frame'] = False
                        # val['day_period'] = 'all_day'
                    elif attendance.state == 'Public Holidays':
                        val['day_type'] = 'public holiday'
                        val['time_frame'] = False
                        # val['day_period'] = 'all_day'
                    else:
                        val['day_type'] = 'working day'
                        #('15:19','From 3 PM to 7 PM'),('19:7','From 7 PM to 7 AM')
                        active_tz = pytz.timezone(attendance.employee_id.resource_calendar_id.tz)
                        from_15 = datetime(attendance.check_out.date().year, attendance.check_out.date().month, attendance.check_out.date().day, hour=15, tzinfo=active_tz)
                        to_19 = datetime(attendance.check_out.date().year, attendance.check_out.date().month, attendance.check_out.date().day, hour=19, tzinfo=active_tz)
                        from_19 = datetime(attendance.check_out.date().year, attendance.check_out.date().month, attendance.check_out.date().day, hour=19, tzinfo=active_tz)
                        to_7 = datetime(attendance.check_out.date().year, attendance.check_out.date().month, (attendance.check_out.date() + timedelta(days=1)).day, hour=7, tzinfo=active_tz)
                        print(from_15)
                        # print(from_15.tzinfo)
                        print(to_19)
                        # print(to_19.tzinfo)
                        print(from_19)
                        # print(from_19.tzinfo)
                        print(to_7)
                        # print(to_7.tzinfo)
                        # print(attendance.check_out)
                        # print(attendance.check_out.tzinfo)
                        print(attendance.check_out.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(attendance.employee_id.resource_calendar_id.tz)))
                        # print(from_15 > attendance.check_out  > to_19)
                        # print(from_19 > attendance.check_out  > to_7)
                        if attendance.check_out.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(attendance.employee_id.resource_calendar_id.tz)) > to_19:
                            sub_val = {
                                'employee_id': attendance.employee_id.id,
                                'manager_id': attendance.employee_id.parent_id.id or False,
                                'start_date': attendance.check_in.date(),
                                'effective_date': attendance.check_in.date() + relativedelta(months=+1),
                                'actual_overtime_hours': 4.00,
                                'day_type' : 'working day',
                                'time_frame' : '15:19',
                                }
                            self.env['simplit.hr.overtime'].create(sub_val)
                            val['actual_overtime_hours'] = round(overtime_hours - 4.00, 2)
                            val['time_frame'] = '19:7'
                        elif from_15 < attendance.check_out.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(attendance.employee_id.resource_calendar_id.tz))  < to_19:
                            val['time_frame'] = '15:19'
                        # elif from_19 < attendance.check_out  < to_7:
                        #     val['time_frame'] = '19:7'
                        # val['day_period'] = attendance.employee_id.resource_calendar_id.attendance_ids.filtered(lambda x: day_of_week[attendance.check_in.strftime("%A")] == x.dayofweek and x.hour_from and x.hour_to).day_period

                    self.env['simplit.hr.overtime'].create(val)
                # create delay
                if must_working_hours > attendance.worked_hours and attendance.state == 'Working Day':
                    delay_hours = must_working_hours - attendance.worked_hours
                    # delay_hours = delay_datetime.hour+delay_datetime.minute/100
                    val = {
                        'employee_id': attendance.employee_id.id,
                        'manager_id': attendance.employee_id.parent_id.id or False,
                        'delay_time': delay_hours,
                        'type_penality': 'Python Code',
                        'start_date': attendance.check_in.date(),
                        'late_login': attendance.check_in,
                        'monthly_delay': attendance.employee_id.contract_id.monthly_allowed_delay}
                    self.env['simplit.hr.delay'].create(val)

        super(HrAttendance, self)._check_validity()

    overtime_created = fields.Boolean(string='Overtime Created', default=False)
    only_date = fields.Date(string='Date', compute='only_checkin_date', store=True)
    only_day_in = fields.Char(string="Day", compute='only_checkin_date', store=True)
    off_day = fields.Char(string="Week Off Day")

    # @api.constrains('check_in')
    @api.depends('check_in')
    def only_checkin_date(self):
        for record in self:
            if record.check_in:
                record.only_date = record.check_in.date()
                record.only_day_in = record.check_in.strftime("%A")

    @api.constrains('employee_id')
    @api.onchange('employee_id')
    def get_employee_off(self):
        weekoff_record = self.env['week.off'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'validate')])
        for rec in weekoff_record:
            if self.only_day_in == rec.weekoff_day:
                self.off_day = rec.weekoff_day


class ResCompany(models.Model):
    _inherit = "res.company"

    allowed_over_time_setting = fields.Integer(string="Overtime Buffer", readonly=0)
    simplit_overtime_max = fields.Integer(string="Max Overtime", default=0, readonly=0)
    overtime_pay_type = fields.Selection(
        [('none', 'None'), ('fixed_amount', 'Fixed Amount'), ('based_on_wage', 'Based On Wage')], default='none',
        readonly=0, string="Overtime")
    amount = fields.Integer(string="Amount", readonly=0)
    half_pay = fields.Integer(string="Half Pay", readonly=0)
    threeforth_pay = fields.Integer(string="3/4th Pay", readonly=0)
    full_pay = fields.Integer(string="Full Pay", readonly=0, )
    week_day_pay = fields.Integer(string="Week Day Pay/Hour", readonly=0)
    week_off_pay = fields.Integer(string="Week Off Pay/Hour", readonly=0)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allowed_over_time = fields.Integer(string="Overtime Buffer",related='company_id.allowed_over_time_setting', readonly=0)
    simplit_overtime_max_setting = fields.Integer("Max Overtime Hours", related='company_id.simplit_overtime_max',readonly=0)
    pay_type_settings = fields.Selection(
        [('none', 'None'), ('fixed_amount', 'Fixed Amount'), ('based_on_wage', 'Based On Wage')],
        default='none', readonly=0, related='company_id.overtime_pay_type', string="Overtime")
    amount_settings = fields.Integer(string="Amount", related='company_id.amount',
                                             readonly=0)
    week_day_pay_settings = fields.Integer(string="Week Day Pay/Hour",  related='company_id.week_day_pay',readonly=0)
    week_off_pay_settings = fields.Integer(string="Week Off Pay/Hour",  related='company_id.week_off_pay',readonly=0)

    @api.onchange('pay_type_settings')
    def _pay_type_change(self):
        if self.pay_type_settings == 'based_on_wage':
            self.amount_settings = 0


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_sick_leave_pay_rate(self):
        # date_of_joining = self.employee_id.contract_id.date_start
        # now = fields.Date.today()
        # working_days = (now - date_of_joining).days + 1
        # pay_rate = self.env['leave.pay.rate'].search([('company_id','=',self.company_id.id),('min_days','<',working_days),('max_days','>=',working_days)])
        # if pay_rate.pay_rate == 'full_pay':
        #     return 1
        # elif pay_rate.pay_rate == 'three_quarters_pay':
        #     return 0.75
        # elif pay_rate.pay_rate == 'half_pay':
        #     return 0.5
        # elif pay_rate.pay_rate == 'one_quarter_pay':
        #     return 0.25
        # else:
        #     return 0
        return 0
    name_in_arabic_pay = fields.Char(string="Name in Arabic")
    overtime_of_month = fields.Float("Total Overtime Hours", compute='total_overtime')
    weekday_ot_month = fields.Float("Weekdays Overtime", computte='total_overtime')
    weekends_ot_month = fields.Float("Weekends Overtime", computte='total_overtime')
    unpaid_leaves = fields.Float("Unpaid Leaves", compute='total_unpaid_leaves')
    sick_leaves_duration = fields.Float(string="Sick Leaves Days", compute='total_sick_leaves_duration')
    annual_leaves_allocation_count = fields.Float(string="Annual Leaves Total", compute='total_annual_leaves_duration')
    annual_leaves_allocation_used_count = fields.Float(string="Annual Leaves Used", compute='total_annual_leaves_duration')

    fixed_ot = fields.Boolean('Fixed')
    wage_ot = fields.Boolean('Wage')
    total_overtime_count = fields.Float("Number of OverTimes",compute='total_overtime')
    fixed_ot_amount = fields.Integer('Fixed OT',compute='total_overtime')
    friday_off_count = fields.Integer('Number of Weekoffs',compute='total_overtime')
    # holidays_alw = fields.Integer('Holiday Allowances',compute='total_overtime')


    @api.constrains('employee_id')
    def _check_payslip_duplicate(self):
        records = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'done')])
        for record in records:
            if record.date_from == self.date_from and record.date_to == self.date_to:
                raise ValidationError(_("Sorry...!,Payslip for this Employee has already generated : "+record.employee_id.name))

    def _get_overtime_amount_from_ratio_rules(self,employee_id,overtime_record):
        day_of_week = {'Monday': '0', 'Tuesday': '1', 'Wednesday': '2', 'Thursday': '3', 'Friday': '4', 'Saturday': '5',
                       'Sunday': '6'}
        amount = 0
        rules = self.env['hr.hours.ratio'].search([('hours_type','=','overtime')])
        attendance_ids = employee_id.resource_calendar_id.attendance_ids
        for rule in rules:
            if employee_id.department_id in rule.department_ids and rule.assign_type =='departments'or\
                    employee_id in rule.employee_ids and rule.assign_type =='employees' or\
                    employee_id.job_id.job_grade in rule.grade_ids and rule.assign_type =='grades':
                if rule.day_type == "public holiday":
                    for global_leave in employee_id.resource_calendar_id.global_leave_ids:
                        if global_leave.date_from.date() <= overtime_record.start_date <= global_leave.date_to.date():
                            amount += rule.hour_ratio * overtime_record.overtime_hours
                elif rule.day_type == "weekend":
                    if day_of_week[overtime_record.only_day] not in attendance_ids.mapped('dayofweek'):
                        amount += rule.hour_ratio * overtime_record.overtime_hours
                    else:
                        for attendance_id in attendance_ids:
                            if day_of_week[overtime_record.only_day] == attendance_id.dayofweek and not attendance_id.hour_from:
                                amount += rule.hour_ratio * overtime_record.overtime_hours
                elif rule.day_type == "working day":
                    for attendance_id in attendance_ids:
                        if day_of_week[overtime_record.only_day] == attendance_id.dayofweek:
                            amount += rule.hour_ratio * overtime_record.overtime_hours
        return amount


    @api.onchange('employee_id','date_from','date_to')
    @api.depends('employee_id','date_from','date_to')
    def total_overtime(self):
        overtime_record = self.env['simplit.hr.overtime'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate')])
        contract_records = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
        # attend_records = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id)])
        # weekoff_recordss = self.env['week.off'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'validate')])
        pay_type_setting = self.env.user.company_id.overtime_pay_type
        if not pay_type_setting:
            raise Warning(_("Please Configure 'Overtime' in Company!"))
        amount_setting = self.env.user.company_id.amount
        week_day_pay_setting = self.env.user.company_id.week_day_pay
        week_off_pay_settings = self.env.user.company_id.week_off_pay
        count = 0.0
        friday_count = 0
        total_weekday_ot = 0.0
        total_weekoff_ot = 0.0
        weekday_ot = 0.0
        weekoff_ot = 0.0
        fixed_amount = 0
        number_of_working = 0
        for record in overtime_record:
            # over_date = datetime.datetime.strptime(str(record.start_date), "%Y-%m-%d")
            if record.effective_date and self.date_from and self.date_to:
                if record.effective_date >= self.date_from and record.effective_date <= self.date_to:
                    count += len(record)
                    if pay_type_setting == 'none':
                        continue
                    if pay_type_setting == 'fixed_amount':
                        if record.weekend_working > 0:
                            friday_count += len(record)
                            total_weekoff_ot += record.weekend_working
                            if contract_records.var_overtime_pay:
                                # amount_setting = 0
                                fixed_amount = contract_records.var_overtime_pay
                            elif amount_setting:
                                fixed_amount = amount_setting
                        if record.overtime_hours > 0:
                            total_weekday_ot += record.overtime_hours
                            if contract_records.var_overtime_pay:
                                fixed_amount = contract_records.var_overtime_pay
                            elif amount_setting:
                                fixed_amount = amount_setting
                    if pay_type_setting == 'based_on_wage':
                        if record.weekend_working > 0:
                            friday_count += len(record)
                            # weekoff_ot += contract_record.weekend_overtime_rate * record.overtime_hours
                            weekoff_ot += record.weekend_working
                        if record.overtime_hours > 0:
                            # weekday_ot += contract_record.weekday_overtime_rate * record.overtime_hours
                            hour_ratio = 0
                            # if record.day_type == 'public holiday':
                            #     ratios = self.env['hr.hours.ratio'].search([('day_type','=','public holiday'),('hours_type','=','overtime')])
                            #     for ratio in ratios:
                            #         if len(ratio.grade_ids) > 0:
                            #             if record.employee_id.contract_id.job_grade.id in ratio.grade_ids.ids:
                            #                 hour_ratio = ratio.hour_ratio
                            #                 break
                            #         if len(ratio.department_ids) > 0:
                            #             if record.employee_id.department_id.id in ratio.department_ids.ids:
                            #                 hour_ratio = ratio.hour_ratio
                            #                 break
                            #         if len(ratio.employee_ids) > 0:
                            #             if record.employee_id.id in ratio.employee_ids.ids:
                            #                 hour_ratio = ratio.hour_ratio
                            #                 break
                            # if record.day_type == 'weekend':
                            #     ratios = self.env['hr.hours.ratio'].search([('day_type','=','weekend'),('hours_type','=','overtime')])
                            #     for ratio in ratios:
                            #         if len(ratio.grade_ids) > 0:
                            #             if record.employee_id.contract_id.job_grade.id in ratio.grade_ids.ids:
                            #                 hour_ratio = ratio.hour_ratio
                            #                 break
                            #         if len(ratio.department_ids) > 0:
                            #             if record.employee_id.department_id.id in ratio.department_ids.ids:
                            #                 hour_ratio = ratio.hour_ratio
                            #                 break
                            #         if len(ratio.employee_ids) > 0:
                            #             if record.employee_id.id in ratio.employee_ids.ids:
                            #                 hour_ratio = ratio.hour_ratio
                            #                 break
                            if record.day_type:
                                # ,('day_period','=',record.day_period)
                                ratios = self.env['hr.hours.ratio'].search([('day_type','=',record.day_type),('hours_type','=','overtime'),('time_frame','=',record.time_frame)])
                                for ratio in ratios:
                                    if ratio.assign_type == 'grades':
                                        if record.employee_id.contract_id.job_grade.id in ratio.grade_ids.ids:
                                            hour_ratio = ratio.hour_ratio
                                            break
                                    if ratio.assign_type == 'departments':
                                        if record.employee_id.department_id.id in ratio.department_ids.ids:
                                            hour_ratio = ratio.hour_ratio
                                            break
                                    if ratio.assign_type == 'employees':
                                        if record.employee_id.id in ratio.employee_ids.ids:
                                            hour_ratio = ratio.hour_ratio
                                            break
                            weekday_ot += record.overtime_hours * hour_ratio
                            fixed_amount += self._get_overtime_amount_from_ratio_rules(self.employee_id,record)
                        total_weekday_ot = weekday_ot
                        total_weekoff_ot = weekoff_ot
                    # number_of_working += record.actual_working_hours
        # self.overtime_of_month += count
        self.friday_off_count += friday_count
        self.fixed_ot_amount = fixed_amount
        self.total_overtime_count += count
        self.overtime_of_month = total_weekday_ot
        self.weekday_ot_month = total_weekday_ot
        self.weekends_ot_month = total_weekoff_ot
        # #Global Leaves Count
        # leave_day = 0
        # leave_list = []
        # for leave_days in contract_records.resource_calendar_id.global_leave_ids:
        #     delta = leave_days.date_to - leave_days.date_from
        #     for i in range(delta.days + 1):
        #         day = leave_days.date_from + timedelta(days=i)
        #         leave_list.append(day.date())
        #
        # ps_start_dt = self.date_from
        # ps_end_date = self.date_to
        # dt = self.date_from
        # day_of_weeks = [0, 1, 2, 3, 4, 5, 6]
        # off_day = list(set(day_of_weeks) - set(
        #     int(d) for d in self.employee_id.resource_calendar_id.attendance_ids.mapped('dayofweek')))
        # for day in range(0, (ps_end_date-ps_start_dt).days + 1):
        #     if dt.weekday() in off_day:
        #         leave_list.append(dt)
        #     if dt == ps_end_date:
        #         break
        #     dt = dt + timedelta(days=1)

        # for att_rec in attend_records:
        #     if att_rec.only_date >= self.date_from and att_rec.only_date <= self.date_to:
        #         if att_rec.only_date in leave_list:
        #             leave_day += len(att_rec)
        # self.holidays_alw += leave_day

    @api.depends('employee_id','date_from','date_to')
    def total_unpaid_leaves(self):
        for this in self:
            this.unpaid_leaves = 0
            leave_type = self.env['hr.leave.type'].search([('unpaid', '=', True)])
            unpaid_leave_records = self.env['hr.leave'].search(
                [('employee_id', '=', this.employee_id.id), ('state', '=', 'validate'),
                 ('holiday_status_id', 'in', leave_type.ids)])
            this.unpaid_leaves = sum(unpaid_leave_records.filtered(lambda x: this.date_from <= x.request_date_from <= this.date_to).mapped('number_of_days'))

    @api.depends('employee_id','date_from','date_to')
    def total_sick_leaves_duration(self):
        for record in self:
            record.sick_leaves_duration = 0
            leave_type = self.env['hr.leave.type'].search([('is_sick_leave', '=', True)])
            sick_leave_records = self.env['hr.leave'].search(
                [('employee_id', '=', record.employee_id.id), ('state', '=', 'validate'),
                 ('holiday_status_id', 'in', leave_type.ids)])
            record.sick_leaves_duration = sum(sick_leave_records.filtered(lambda x: record.date_from <= x.request_date_from <= record.date_to).mapped('number_of_days'))

    @api.depends('employee_id','date_from','date_to')
    def total_annual_leaves_duration(self):
        for this in self:
            if not this.employee_id:
                this.annual_leaves_allocation_count = 0.0
                this.annual_leaves_allocation_used_count = 0.0
            else:
                this.annual_leaves_allocation_count = 0
                this.annual_leaves_allocation_used_count = 0
                allocations = self.env['hr.leave.allocation'].search([
                    ('employee_id', '=', this.employee_id.id),
                    ('holiday_status_id.active', '=', True),
                    ('state', '=', 'validate'),
                    ('holiday_status_id.is_annual_leave', '=', True)
                ])
                this.annual_leaves_allocation_count = float_round(sum(allocations.mapped('number_of_days')), precision_digits=2)
                # allocation_display = "%g" % allocation_count
                self._cr.execute("""
                    SELECT
                        sum(h.number_of_days) AS days,
                        h.employee_id
                    FROM
                        (
                            SELECT holiday_status_id, number_of_days,
                                state, employee_id
                            FROM hr_leave_allocation
                            UNION ALL
                            SELECT holiday_status_id, (number_of_days * -1) as number_of_days,
                                state, employee_id
                            FROM hr_leave
                        ) h
                        join hr_leave_type s ON (s.id=h.holiday_status_id)
                    WHERE
                        s.active = true AND s.is_annual_leave = true AND h.state='validate' AND
                        (s.allocation_type='fixed' OR s.allocation_type='fixed_allocation') AND
                        h.employee_id in %s
                    GROUP BY h.employee_id""", (tuple(this.employee_id.ids),))
                remaining = dict((row['employee_id'], row['days']) for row in self._cr.dictfetchall())
                value = float_round(remaining.get(this.employee_id.id, 0.0), precision_digits=2)
                leaves_count = value
                remaining_leaves = value
                this.annual_leaves_allocation_used_count = float_round(this.annual_leaves_allocation_count - remaining_leaves, precision_digits=2)
            # allocation_used_display = "%g" % allocation_used_count
            # leave_type = self.env['hr.leave.type'].search([('is_annual_leave', '=', True)])
            # annual_leave_records = self.env['hr.leave'].search(
            #     [('employee_id', '=', this.employee_id.id), ('state', '=', 'validate'), ('holiday_status_id', 'in', leave_type.ids)])
            # this.annual_leaves_duration = sum(annual_leave_records.filtered(lambda x: this.date_from <= x.request_date_from <= this.date_to).mapped('number_of_days'))

    # @api.model
    # def create(self, vals):
    #     res = super(HrPayslip, self).create(vals)
    #     type_of_pay = self.env.user.company_id.overtime_pay_type
    #     if type_of_pay == 'fixed_amount':
    #         res.fixed_ot = True
    #         res.wage_ot = False
    #     elif type_of_pay == 'based_on_wage':
    #         res.fixed_ot = False
    #         res.wage_ot = True
    #     return res

    @api.onchange('employee_id')
    def bool_type_payslip_ot(self):
        type_of_pay = self.env.user.company_id.overtime_pay_type
        if type_of_pay == 'fixed_amount':
            self.fixed_ot = True
            self.wage_ot = False
        elif type_of_pay == 'based_on_wage':
            self.fixed_ot = False
            self.wage_ot = True
        self.name_in_arabic_pay = self.employee_id.name_in_arabic


    def overtime_employee(self):
        return {
            'name': _("Overtime Calculation"),
            'type': 'ir.actions.act_window',
            'res_model': 'simplit.hr.overtime',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('employee_id', '=', self.employee_id.id),('state', '=', 'validate')],
        }


    def sick_leaves_view(self):
        leave_type = self.env['hr.leave.type'].search([('is_sick_leave', '=', True)])
        sick_leave_records = self.env['hr.leave'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'),
             ('holiday_status_id', 'in', leave_type.ids)])
        return {
            'name': _("Sick Leaves"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'), ('id','in',sick_leave_records.ids)],
        }

    def unpaid_leaves_view(self):
        leave_type = self.env['hr.leave.type'].search([('unpaid', '=', True)])
        unpaid_leave_records = self.env['hr.leave'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'), ('holiday_status_id', 'in', leave_type.ids)])
        return {
            'name': _("Unpaid Leaves"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'), ('id','in',unpaid_leave_records.ids)],
        }
    def annual_leaves_view(self):
        leave_type = self.env['hr.leave.type'].search([('is_annual_leave', '=', True)])
        annual_leave_records = self.env['hr.leave'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'), ('holiday_status_id', 'in', leave_type.ids)])
        return {
            'name': _("Annual Leaves"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'), ('id','in',annual_leave_records.ids)],
        }


class EmployeeWeekOff(models.Model):
    _name = "week.off"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    weekoff_date = fields.Date('WeekOff Date')
    weekoff_day = fields.Char('WeekOff Day',compute='week_off_day',store=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
        help="The status is set to 'To Submit', when a weekoff request is created." +
        "\nThe status is 'To Approve', when weekoff request is confirmed by user." +
        "\nThe status is 'Refused', when weekoff request is refused by manager." +
        "\nThe status is 'Approved', when weekoff request is approved by manager.")

    @api.depends('weekoff_date')
    def week_off_day(self):
        for record in self:
            if record.weekoff_date:
                record.weekoff_day = record.weekoff_date.strftime("%A")


    def action_confirm(self):
        if self.filtered(lambda week: week.state != 'draft'):
            raise UserError(_('WeekOff request must be in Draft state ("To Submit") in order to confirm it.'))
        self.write({'state': 'confirm'})
        return True


    def action_approve(self):
        off_day_setting = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id)])
        for off in off_day_setting:
            off.off_day = self.weekoff_day
        return self.write({'state': 'validate'})


    def action_refuse(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for weekoff in self:
            if weekoff.state not in ['confirm', 'validate']:
                raise UserError(_('WeekOff request must be confirmed or validated in order to refuse it.'))

            if weekoff.state == 'validate':
                weekoff.write({'state': 'refuse'})
        return True


    def action_validate(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if any(weekoff.state not in ['confirm', 'validate1'] for weekoff in self):
            raise UserError(_('WeekOff request must be confirmed in order to approve it.'))

        self.write({'state': 'validate'})


    def action_draft(self):
        for weekoff in self:
            if weekoff.state not in ['confirm', 'refuse']:
                raise UserError(_('WeekOff request state must be "Refused" or "To Approve" in order to be reset to draft.'))
            weekoff.write({'state': 'draft'})
