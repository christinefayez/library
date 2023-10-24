# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime


class CreateMassAppraisal(models.TransientModel):
    _name = 'hr.mass.appraisal'
    _description = 'Create appraisals for contacts wizard'

    @api.model
    def default_get(self, fields):
        """ Use active_ids from the context to fetch the leads/opps to merge.
            In order to get merged, these leads/opps can't be in 'Dead' or 'Closed'
        """
        record_id = self._context.get('active_id')
        result = super(CreateMassAppraisal, self).default_get(fields)

        if record_id:
            if 'employee_ids' in fields:
                form_id = self.env['hr.appraisal.form'].browse(record_id)
                # subgroups = form_id.related_contract_subgroup.ids
                grade_ids = self.env['job.grade'].search([('id', 'in', form_id.grade_ids.ids)]).ids
                job_ids = self.env['hr.job'].search([('id', 'in', form_id.job_ids.ids)]).ids

                # ,
                #  ('contract_id.contract_subgroup', 'in', subgroups), ('contract_id.state', '=', 'open')
                if form_id.filter_by == 'grade_ids':
                    emp_ids = self.env['hr.employee'].search(
                    [('job_grade', 'in', grade_ids)]
                    )
                    del_emp = self.env['hr.appraisal'].search(
                        [('employee_id', 'in', emp_ids.ids),
                         ('appraisal_form', '=', form_id.id)]).mapped(
                        "employee_id")
                    result['employee_ids'] = (emp_ids - del_emp).ids
                elif form_id.filter_by == 'job_ids':
                    emp_ids = self.env['hr.employee'].search(
                    [('job_id', 'in', job_ids)]
                    )
                    del_emp = self.env['hr.appraisal'].search(
                        [('employee_id', 'in', emp_ids.ids),
                         ('appraisal_form', '=', form_id.id)]).mapped(
                        "employee_id")
                    result['employee_ids'] = (emp_ids - del_emp).ids
        return result

    related_appraisal_form = fields.Many2one('hr.appraisal.form', 'Related Apprisal Form')

    employee_ids = fields.Many2many('hr.employee', string="Employees")

    def create_appraisals(self):
        self = self.sudo()
        default_form = self.related_appraisal_form
        rec = self.env['hr.appraisal']
        for emp in self.employee_ids:
            for q in default_form.period_id.quarter_lines:
                vals = {
                    'employee_id': emp.id,
                    'appraisal_form': default_form.id,
                    'date_close': q.to_date,
                    'related_period': default_form.period_id.id,
                    'related_quarter': q.id,
                    # 'current_manager': emp.parent_id.id
                }
                rec |= self.env['hr.appraisal'].create(vals)
        rec._onchange_employee_id()
        rec._onchange_appraisal_form()
        self.env['hr.appraisal'].cron_start_appraisal()

    def remove_all(self):
        # self.employee_ids = [(5,)]
        # return False
        return {
            'view_mode': 'form',
            'res_model': 'hr.mass.appraisal.empty',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_related_appraisal_form': self.related_appraisal_form.id,
            }
        }

    @api.onchange('related_appraisal_form')
    def onchange_form(self):
        self = self.sudo()
        form_id = self.related_appraisal_form
        # subgroups = form_id.related_contract_subgroup.ids
        grade_ids = self.env['job.grade'].search([('id', 'in', form_id.grade_ids.ids)]).ids
        job_ids = self.env['hr.job'].search([('id', 'in', form_id.job_ids.ids)]).ids
        employee_ids = []
        # ,
        #  ('contract_id.contract_subgroup', 'in', subgroups), ('contract_id.state', '=', 'open')
        if form_id.filter_by == 'grade_ids':
            emp_ids = self.env['hr.employee'].search(
            [('job_grade', 'in', grade_ids)]
            )
            del_emp = self.env['hr.appraisal'].search(
                [('employee_id', 'in', emp_ids.ids),
                 ('appraisal_form', '=', form_id.id)]).mapped(
                "employee_id")
            employee_ids = (emp_ids - del_emp).ids
        elif form_id.filter_by == 'job_ids':
            emp_ids = self.env['hr.employee'].search(
            [('job_id', 'in', job_ids)]
            )
            del_emp = self.env['hr.appraisal'].search(
                [('employee_id', 'in', emp_ids.ids),
                 ('appraisal_form', '=', form_id.id)]).mapped(
                "employee_id")
            employee_ids = (emp_ids - del_emp).ids
        return {'domain': {'employee_ids': [('id', 'in', employee_ids)]}}


class CreateMassAppraisalEmpty(models.TransientModel):
    _name = 'hr.mass.appraisal.empty'
    _description = 'Create appraisals for contacts wizard'

    @api.model
    def default_get(self, fields):
        result = super(CreateMassAppraisalEmpty, self).default_get(fields)
        result['employee_ids'] = False
        return result

    related_appraisal_form = fields.Many2one('hr.appraisal.form', 'Related Apprisal Form')

    employee_ids = fields.Many2many('hr.employee', string="Employees")

    def create_appraisals(self):
        self = self.sudo()
        default_form = self.related_appraisal_form
        rec = self.env['hr.appraisal']
        for emp in self.employee_ids:
            for q in default_form.period_id.quarter_lines:
                vals = {
                    'employee_id': emp.id,
                    'appraisal_form': default_form.id,
                    'date_close': q.to_date,
                    'related_period': default_form.period_id.id,
                    'related_quarter': q.id,
                    # 'current_manager': emp.parent_id.id
                }
                rec |= self.env['hr.appraisal'].create(vals)
        rec._onchange_employee_id()
        rec._onchange_appraisal_form()
        self.env['hr.appraisal'].cron_start_appraisal()

    def remove_all(self):
        return {
            'view_mode': 'form',
            'res_model': 'hr.mass.appraisal.empty',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_related_appraisal_form': self.related_appraisal_form.id,
            }
        }

    @api.onchange('related_appraisal_form')
    def onchange_form(self):
        # self = self.sudo()
        form_id = self.related_appraisal_form
        # subgroups = form_id.related_contract_subgroup.ids
        grade_ids = self.env['job.grade'].search([('id', 'in', form_id.grade_ids.ids)]).ids
        job_ids = self.env['hr.job'].search([('id', 'in', form_id.job_ids.ids)]).ids
        employee_ids = []

        # ,
        #  ('contract_id.contract_subgroup', 'in', subgroups), ('contract_id.state', '=', 'open')
        if form_id.filter_by == 'grade_ids':
            emp_ids = self.env['hr.employee'].search(
            [('job_grade', 'in', grade_ids)]
            )
            del_emp = self.env['hr.appraisal'].search(
                [('employee_id', 'in', emp_ids.ids),
                 ('appraisal_form', '=', form_id.id)]).mapped(
                "employee_id")
            employee_ids = (emp_ids - del_emp).ids
        elif form_id.filter_by == 'job_ids':
            emp_ids = self.env['hr.employee'].search(
            [('job_id', 'in', job_ids)]
            )
            del_emp = self.env['hr.appraisal'].search(
                [('employee_id', 'in', emp_ids.ids),
                 ('appraisal_form', '=', form_id.id)]).mapped(
                "employee_id")
            employee_ids = (emp_ids - del_emp).ids
        return {'domain': {'employee_ids': [('id', 'in', employee_ids)]}}
