# -*- coding: utf-8 -*-

from odoo import models, fields


class AllowanceRequestType(models.Model):
    _name = 'ebs.payroll.allowance.request.type'
    _description = 'Allowance Request Type'

    name = fields.Char(
        string='Name',
        required=True)
