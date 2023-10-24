# -*- coding: utf-8 -*-

from odoo import models, fields, api


# from odoo.exceptions import ValidationError


class AdditionalElementTypes(models.Model):
    _name = 'ebspayroll.additional.element.types'
    _description = 'Additional Element types'

    code = fields.Char(
        string='Code',
        required=False)
    name = fields.Char(
        string='Name',
        required=True)

    description = fields.Text(
        string="Description",
        required=False)

    type = fields.Selection(
        string='Type',
        selection=[('A', 'Addition'),
                   ('D', 'Deduction'), ],
        required=True, )


