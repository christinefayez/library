# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    performance_history = fields.One2many('appraisal.history', 'appraisal_employee', string="Appraisal Employee")

    @api.onchange('parent_id')
    def _onchange_manager_id(self):
        for rec in self:
            rec = rec.sudo()
            appraisals = self.env['hr.appraisal'].search([('employee_id', '=', rec.id)])
            for app in appraisals:
                app._onchange_manager_id()

    def write(self, vals):
        res = super(HrEmployeePrivate, self).write(vals)
        self._onchange_manager_id()
        return res