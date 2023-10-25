from odoo import fields, api, models, _


class HrApprovedDelay(models.Model):
    _name = "hr.approved.delay"

    employee_id = fields.Many2one('hr.employee','Employee')
    manager_id = fields.Many2one('hr.employee','Manager')
    total_actual_hours =  fields.Float("Total Delay Hours")
    total_approved_hours = fields.Float("Total Approved Delay Hours")
    approval_user = fields.Many2one('res.users',"Approved by")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    approval_date = fields.Datetime("Approval Datetime")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Waiting Approval'), ('refuse', 'Refused'),
                              ('validate', 'Approved'), ('cancel', 'Cancelled')], default='draft', copy=False)


