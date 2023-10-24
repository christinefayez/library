from odoo.addons import decimal_precision as dp

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm, UserError
from datetime import datetime
from odoo.tools import date_utils

class ALLOCATIONSS(models.Model):
    _inherit = 'hr.leave.allocation'

    is_overtime_allocation = fields.Boolean()

class PartialApprovalEmployee(models.TransientModel):
    _name = "overtime.delay.partial.approval.wizard"

    approved_hours = fields.Float("Approved Hours")
    employee_id = fields.Many2one('hr.employee', string='Employee',required=True)
    actual_total_hours = fields.Float("Total Hours", compute="_compute_actual_hours")
    overtime_ids = fields.Many2many(comodel_name='simplit.hr.overtime', string='Overtime Lines')
    delay_ids = fields.Many2many(comodel_name='simplit.hr.delay', string='Delay Lines')
    show_lines = fields.Boolean("Show Hours Lines")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    overtime_or_delay = fields.Boolean("Delay or Overtime",
                                       help="we're using this wizard for both models overtime and delay so we need to differ between them")

    def _get_selected_records(self):
        records = self.env[self._context.get('active_model')] \
            .browse(self._context.get('active_ids'))
        if not self.overtime_or_delay:
            if self.start_date and self.end_date:
                records = records.filtered(lambda overtime: self.start_date <= overtime.start_date <= self.end_date)
            elif self.start_date:
                records = records.filtered(lambda overtime: self.start_date <= overtime.start_date)
            elif self.end_date:
                records = records.filtered(lambda overtime: overtime.start_date <= self.end_date)
        else:
            if self.start_date and self.end_date:
                records = records.filtered(lambda delay: self.start_date <= delay.start_date <= self.end_date)
            elif self.start_date:
                records = records.filtered(lambda delay: self.start_date <= delay.start_date)
            elif self.end_date:
                records = records.filtered(lambda delay: delay.start_date <= self.end_date)
        return records

    @api.onchange('employee_id','start_date','end_date')
    def _compute_actual_hours(self):
        records = self._get_selected_records()
        if not self.overtime_or_delay:
            self.actual_total_hours = sum(records.mapped('actual_overtime_hours'))
            self.overtime_ids = [(6, 0, records.ids)]
        else:
            self.actual_total_hours = sum(records.mapped('delay_time'))
            self.delay_ids = [(6, 0, records.ids)]

    def update_approved_hours(self):
        records = self._get_selected_records()
        minus_record = abs(self.actual_total_hours - self.approved_hours )
        for record in records:
            if self.approved_hours == self.actual_total_hours:
                if not self.overtime_or_delay:
                    record.overtime_hours=record.actual_overtime_hours
                    if record.day_type in ['weekend','public holiday']:
                        leave_type_id = self.env['hr.leave.type'].search(
                            [('category', '=', 'annual'), ('company_id', '=', self.employee_id.company_id.id)],
                            limit=1)
                        allocation_val = {'name': leave_type_id.name,
                                          'holiday_status_id': leave_type_id.id,
                                          'allocation_type': 'regular',
                                          'number_of_days': 1,
                                          'number_per_interval': 1,
                                          'interval_number': 1,
                                          'unit_per_interval': 'days',
                                          'interval_unit': 'weeks',
                                          'holiday_type': 'employee',
                                          'employee_id': self.employee_id.id,
                                          'allocation_from_date': date_utils.start_of(fields.Datetime.now(), "year"),
                                          'allocation_to_date': date_utils.end_of(fields.Datetime.now(), "year"),
                                          'is_overtime_allocation':True}
                        self.env['hr.leave.allocation'].sudo().create(allocation_val)
                else:
                    record.approved_delay=record.delay_time
            elif self.approved_hours > self.actual_total_hours:
                raise UserError(_("The Approved Hours must be less than actual hours!"))
            if minus_record > 0:
                if not self.overtime_or_delay:
                    if record.actual_overtime_hours >= minus_record:
                        record.overtime_hours = record.actual_overtime_hours-minus_record
                        minus_record = 0
                        if record.day_type in ['weekend','public holiday']:
                            leave_type_id = self.env['hr.leave.type'].search(
                                [('category', '=', 'annual'), ('company_id', '=', self.employee_id.company_id.id)],
                                limit=1)
                            allocation_val = {'name': leave_type_id.name,
                                              'holiday_status_id': leave_type_id.id,
                                              'allocation_type': 'regular',
                                              'number_of_days': 1,
                                              'number_per_interval': 1,
                                              'interval_number': 1,
                                              'unit_per_interval': 'days',
                                              'interval_unit': 'weeks',
                                              'holiday_type': 'employee',
                                              'employee_id': self.employee_id.id,
                                              'allocation_from_date': date_utils.start_of(fields.Datetime.now(), "year"),
                                              'allocation_to_date': date_utils.end_of(fields.Datetime.now(), "year"),
                                              'is_overtime_allocation':True}
                            self.env['hr.leave.allocation'].sudo().create(allocation_val)
                    else:
                        record.overtime_hours = 0
                        minus_record -= record.actual_overtime_hours
                elif self.overtime_or_delay:
                    if record.delay_time >= minus_record:
                        record.approved_delay = record.delay_time-minus_record
                        minus_record = 0
                    else:
                        record.approved_delay = 0
                        minus_record -= record.delay_time
            else:
                if not self.overtime_or_delay:
                    record.overtime_hours = record.actual_overtime_hours
                    if record.day_type in ['weekend','public holiday']:
                        leave_type_id = self.env['hr.leave.type'].search(
                            [('category', '=', 'annual'), ('company_id', '=', self.employee_id.company_id.id)],
                            limit=1)
                        allocation_val = {'name': leave_type_id.name,
                                          'holiday_status_id': leave_type_id.id,
                                          'allocation_type': 'regular',
                                          'number_of_days': 1,
                                          'number_per_interval': 1,
                                          'interval_number': 1,
                                          'unit_per_interval': 'days',
                                          'interval_unit': 'weeks',
                                          'holiday_type': 'employee',
                                          'employee_id': self.employee_id.id,
                                          'allocation_from_date': date_utils.start_of(fields.Datetime.now(), "year"),
                                          'allocation_to_date': date_utils.end_of(fields.Datetime.now(), "year"),
                                          'is_overtime_allocation':True}
                        self.env['hr.leave.allocation'].sudo().create(allocation_val)
                else:
                    record.approved_delay = record.delay_time

            record.state='validate'
        if self.overtime_or_delay:
            model = self.env['hr.approved.delay']
        else:
            model = self.env['hr.approved.overtime']
        model.create({
            'employee_id': self.employee_id.id,
            'manager_id': self.employee_id.parent_id.id,
            'approval_user': self.env.user.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'state': 'validate',
            'total_actual_hours': self.actual_total_hours,
            'total_approved_hours': self.approved_hours,
            'approval_date': datetime.now(),
        })


    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}
