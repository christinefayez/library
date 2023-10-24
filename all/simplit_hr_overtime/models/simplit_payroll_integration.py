# -*- coding: utf-8 -*-
#####################

from odoo import fields, api, models, _


class AttendanceIntegration(models.Model):
    _name = "simplit.attendance.integration"

    employee_id = fields.Many2one('hr.employee', string="Employee")
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")
    overtime = fields.Float(string="Overtime")
    overtime_rate = fields.Float(string="OT Rate")
    delaytime = fields.Float(string="Late Logins")
    delay_rate = fields.Float(string="Delay Rate")
    paid_leaves = fields.Float(string="Paid Leaves")
    lwp = fields.Float(string="LWP")
    total_worked_days = fields.Integer(string="Worked Days")
    total_worked_hours = fields.Integer(string="Worked Hours")
    half_day_leaves = fields.Integer(string="Half Day Leaves")

    @api.onchange('employee_id')
    def get_all_values(self):
        if self.employee_id:
            pass

