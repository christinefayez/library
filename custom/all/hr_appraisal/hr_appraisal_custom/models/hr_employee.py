# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _inherit = 'hr.employee'

    job_grade = fields.Many2one(related="contract_id.job_grade", store=True)
