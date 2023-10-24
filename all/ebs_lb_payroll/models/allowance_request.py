# -*- coding: utf-8 -*-

from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AllowanceRequest(models.Model):
    _name = 'ebs.payroll.allowance.request'
    _description = 'Allowance Request'
    _order = "request_date desc"

    def _get_default_employee_id(self):
        return self.env.user.employee_id.id or False

    def _get_domain_employee_id(self):
        if self.env.user.has_group('base.group_user') and not self.env.user.has_group('hr.group_hr_user'):
            return [('id', '=', self.env.user.employee_id.id)]
        else:
            return [(1, '=', 1)]

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        default=_get_default_employee_id,
        domain=_get_domain_employee_id,
        required=True)

    request_type = fields.Many2one(
        comodel_name='ebs.payroll.allowance.request.type',
        string='Type',
        required=True)
    amount = fields.Float(
        string='Amount',
        required=True)
    request_date = fields.Date(
        string='Request Date',
        required=True, default=date.today())
    payment_date = fields.Date(
        string='Payment Date',
        required=False)
    amortization_start_date = fields.Date(
        string='Amortization Start Date',
        required=False)
    number_of_month = fields.Integer(
        string='Number of Month',
        required=False)

    description = fields.Text(
        string="Description",
        required=False)
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'),
                   ('submit', 'Submitted'),
                   ('approved', 'Approved'),
                   ('financial', 'Financial Approval'),
                   ('reject', 'Rejected'),
                   ],
        required=False, default='draft')

    lines_ids = fields.One2many(
        comodel_name='ebs.payroll.allowance.request.lines',
        inverse_name='parent_id',
        string='Lines',
        required=False)

    name = fields.Char(compute='_compute_name', string='Name')

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    payslip_id = fields.Many2one('hr.payslip', string='Paid On Payslip', readonly=True)
    display_approve = fields.Boolean(required=False, compute="_display_approve_btn")

    @api.onchange('employee_id')
    def _display_approve_btn(self):
        for rec in self:
            if rec.employee_id.parent_id:
                if rec.env.user.id == rec.employee_id.parent_id.user_id.id:
                    rec.display_approve = True
                else:
                    rec.display_approve = False
            else:
                rec.display_approve = False

    @api.depends('employee_id', 'request_type')
    def _compute_name(self):
        for record in self:
            record.name = record.employee_id.name + ' [' + record.request_type.name + ']'

    def submit_request(self):
        basic = self.employee_id.contract_id.related_compensation.filtered(
            lambda x: x.name.component_type == 'basic_pay' and x.state == 'active').amount * 2
        if self.amount > basic:
            raise ValidationError(_('Amount requested is more than the entitled'))
        other_allowance = self.env['ebs.payroll.allowance.request'].search(
            [('employee_id', '=', self.employee_id.id),
             ('state', 'in', ['submit', 'approved'])])
        if other_allowance:
            raise ValidationError(_('Previous Balance is still outstanding'))
        lines = self.env['ebs.payroll.allowance.request.lines'].search(
            [('parent_id.employee_id', '=', self.employee_id.id), ('payslip_id', '=', False),
             ('parent_state', '=', 'financial')])
        if lines:
            raise ValidationError(_('Previous Balance is still outstanding'))
        self.state = 'submit'

    def accept_request(self):
        lines = self.env['ebs.payroll.allowance.request.lines'].search(
            [('parent_id.employee_id', '=', self.employee_id.id), ('payslip_id', '=', False),
             ('parent_state', '=', 'financial')])
        if lines:
            raise ValidationError(_('Previous Balance is still outstanding'))
        if not self.payment_date:
            raise ValidationError(_("Missing Payment Date"))
        if not self.amortization_start_date:
            raise ValidationError(_("Missing amortization date"))
        if not self.number_of_month:
            raise ValidationError(_("Missing number of month"))

        payment = self.amount / self.number_of_month
        for x in range(self.number_of_month):
            line_date = self.amortization_start_date + relativedelta(months=x)

            self.env['ebs.payroll.allowance.request.lines'].create({
                'parent_id': self.id,
                'date': line_date,
                'amount': payment
            })

            self.state = 'approved'

    def financial_request(self):
        self.state = 'financial'

    def reject_request(self):
        self.state = 'reject'

    def draft_request(self):
        self.state = 'draft'
        self.write({'lines_ids': [(5, 0, 0)]})

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError("Only draft records can be deleted")
        return super(AllowanceRequest, self).unlink()


class AllowanceRequestlines(models.Model):
    _name = 'ebs.payroll.allowance.request.lines'
    _description = 'Allowance Request lines'

    parent_id = fields.Many2one(
        comodel_name='ebs.payroll.allowance.request',
        string='Request',
        required=False)
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=False, related='parent_id.employee_id')

    parent_type = fields.Many2one(
        comodel_name='ebs.payroll.allowance.request.type',
        string='Type',
        required=False, related='parent_id.request_type')

    parent_state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'),
                   ('submit', 'Submitted'),
                   ('approved', 'Approved'),
                   ('financial', 'Financial Approval'),
                   ('reject', 'Rejected'),
                   ],
        required=False, related='parent_id.state')

    date = fields.Date(
        string='Date',
        required=False)

    amount = fields.Float(
        string='Amount',
        required=False)
    payslip_id = fields.Many2one('hr.payslip', string='Paid On Payslip', readonly=True)
