# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SalaryRules(models.Model):
    _inherit = 'hr.salary.rule'

    istaxable = fields.Boolean(
        string='Is Taxable',
        required=False)

    template = fields.Selection(
        string='Template',
        selection=[
            ('AE', 'Additional Element'),
            ('rap', 'Request for Allowance Payment'),
            ('aap', 'Allowance Amortization Payment'),
            ('arap', 'Remaining Amortization Payment'),
        ],
        required=False, )

    related_element_type = fields.Many2one(
        comodel_name='ebspayroll.additional.element.types',
        string='Additional Element Type',
        required=False)
    allowance_type_id = fields.Many2one(
        comodel_name='ebs.payroll.allowance.request.type',
        string='Allowance Type',
        required=False)

    @api.onchange('template')
    def _template_onchange(self):
        payslip = True
        taxable = False
        condition = 'none'
        amount_type = 'code'
        code = ""
        self.related_element_type = None

        # if self.template == 'TRAN':
        #     code = "result=payslip.env['hr.payslip'].calculateTransportation(payslip,employee)"
        #     payslip = True
        if self.template == 'AE':
            code = ""
            payslip = True
        self.appears_on_payslip = payslip
        self.istaxable = taxable
        self.condition_select = condition
        self.amount_select = amount_type
        self.amount_python_compute = code
        return

    @api.onchange('related_element_type')
    def _related_element_type_onchange(self):
        if self.related_element_type and self.template:
            rec_code = '' + self.related_element_type.name
            python_code = "result=payslip.env['hr.payslip'].calculateAdditionalElements(payslip,employee,'" + rec_code + "')"
            self.amount_python_compute = python_code
        return

    @api.onchange('allowance_type_id')
    def _allowance_type_onchange(self):
        if self.allowance_type_id and self.template:
            rec_code = '' + self.allowance_type_id.name
            if self.template == 'arap':
                code = "result=payslip.env['hr.payslip'].calculateRemainingAmortizationPayment(payslip,employee,'" + rec_code + "')"
            if self.template == 'rap':
                code = "result=payslip.env['hr.payslip'].calculateAllowancePayment(payslip,employee,'" + rec_code + "')"
            if self.template == 'aap':
                code = "result=-(payslip.env['hr.payslip'].calculateAmortizationPayment(payslip,employee,'" + rec_code + "'))"
            self.amount_python_compute = code
        return
