# -*- coding: utf-8 -*-

from odoo import models, fields, _


class AdditionalElementLines(models.Model):
    _name = 'ebspayroll.additional.element.lines'
    _description = 'Additional Element Lines'

    employee = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True)
    type = fields.Many2one(
        comodel_name='ebspayroll.additional.element.types',
        string='Element Type',
        required=True)
    rule_type = fields.Selection(
        string='Type',
        related="type.type",
        required=False, )
    description = fields.Char(string='Description')
    payment_date = fields.Date(
        string='Payment Date',
        required=True)
    currency = fields.Many2one('res.currency', 'Currency', default=lambda x: x.env.company.currency_id)
    attachment = fields.Binary(string="Attachment")
    amount_in_currency = fields.Float(string='Amount in Currency', required=True)

    _sql_constraints = [
        ('add_element_line_emp_unique', 'unique(employee,type,payment_date)',
         _("There is another element with same type and employee and payment date")),
        ('date_unique', 'check(1=1)', _("Date already exists"))

    ]

    # @api.constrains('payment_date')
    # def _check_payment_date(self):
    #     if len(self.env['ebspayroll.additional.element.lines'].search(
    #                 [('type', '=', self.id),
    #                  ('payment_date', '=', self.payment_date),
    #                  ('id', '!=', self.id)])) > 0:
    #         raise ValidationError(_("Date already exists"))
