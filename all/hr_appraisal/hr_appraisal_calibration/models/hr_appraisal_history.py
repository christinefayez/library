# -*- coding: utf-8 -*-

from odoo import models, fields


class AppraisalHistory(models.Model):
    _name = 'appraisal.history'

    appraisal_employee = fields.Many2one('hr.employee', string="Employee")
    appraisal = fields.Many2one('hr.appraisal')

    hr_overall_rating_final_related = fields.Float(related='appraisal.hr_overall_rating_final', string='Rating',
                                                   readonly=False, store=True)
    appraisal_year_related = fields.Char(related='appraisal.year', readonly=False, store=True)
    appraisal_form_related = fields.Many2one(related='appraisal.appraisal_form', readonly=False, store=True)

    pip_final_decision = fields.Selection(related='appraisal.manager_final_decision', string='PIP Decision')

    group = fields.Many2one(related='appraisal_employee.contract_id.group', store=True, readonly=True)
    department = fields.Many2one(related='appraisal_employee.contract_id.department', store=True, readonly=True)
    section = fields.Many2one(related='appraisal_employee.contract_id.section', store=True, readonly=True)
    subsection = fields.Many2one(related='appraisal_employee.contract_id.subsection', store=True, readonly=True)
    line_manager = fields.Many2one(related='appraisal_employee.parent_id', store=True, readonly=True)
    # strata_id = fields.Char(related='appraisal_employee.strata_id', store=True, readonly=True)
