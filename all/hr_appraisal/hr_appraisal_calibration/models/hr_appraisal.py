# -*- coding: utf-8 -*-

from odoo import models, fields

from datetime import datetime

import datetime


class HrAppraisal(models.Model):
    _inherit = "hr.appraisal"

    appraisal_history_o_2_m = fields.One2many('appraisal.history', 'appraisal', string="Appraisal")
    time_hired = fields.Char(string='Seniority', related="employee_id.time_hired")
    hire_date = fields.Date(string='Hire Date', related="employee_id.contract_id.date_start")
    contract_subgroup_id = fields.Many2one(comodel='hr.contract.subgroup', string='Contract Subgroup',
                                           related="employee_id.contract_id.contract_subgroup")
    nationality = fields.Many2one(string='Nationality', related="employee_id.country_id")

    current_year_3_rating = fields.Char(string="Current Year 3 Rating", compute='_get_year')
    current_year_2_rating = fields.Char(string="Current Year 2 Rating", compute='_get_year')
    current_year_1_rating = fields.Char(string="Current Year 1 Rating", compute='_get_year')
    current_year_latest_warning_seq = fields.Char(string="Current Year latest Warning Seq", compute='_get_year')
    current_year_latest_warning_issue = fields.Date(string="Current Year Active Warning Date",
                                                    compute='_get_year')
    current_year_latest_warning_reason = fields.Char(string="Current Year Active Warning Reason", compute='_get_year')
    current_year_1_latest_warning_seq = fields.Char(string="Current Year 1 latest Warning Seq", compute='_get_year')
    current_year_1_latest_warning_issue = fields.Date(string="Last Year Active Warning Date",
                                                      compute='_get_year')
    current_year_1_latest_warning_reason = fields.Char(string="Last Year Active Warning Reason",
                                                       compute='_get_year')


    # @api.depends('current_year_3_rating', 'current_year_2_rating', 'current_year_1_rating',
    #              'current_year_latest_warning_seq', 'current_year_latest_warning_issue',
    #              'current_year_latest_warning_reason', 'current_year_1_latest_warning_seq',
    #              'current_year_1_latest_warning_issue', 'current_year_1_latest_warning_reason')
    def _get_year(self):
        for rec in self:
            current_year = rec.year

            year_3 = self.env['appraisal.history'].search(
                [('appraisal_year_related', '=', str(int(current_year) - 3)),
                 ('appraisal_employee', '=', rec.employee_id.id)], limit=1)
            rec.current_year_3_rating = year_3.hr_overall_rating_final_related
            year_2 = self.env['appraisal.history'].search(
                [('appraisal_year_related', '=', str(int(current_year) - 2)),
                 ('appraisal_employee', '=', rec.employee_id.id)], limit=1)
            rec.current_year_2_rating = year_2.hr_overall_rating_final_related
            year_1 = self.env['appraisal.history'].search(
                [('appraisal_year_related', '=', str(int(current_year) - 1)),
                 ('appraisal_employee', '=', rec.employee_id.id)], limit=1)
            rec.current_year_1_rating = year_1.hr_overall_rating_final_related

            # latest_year_1 = self.env['hr.notice'].search(
            #     [('related_employee', '=', rec.employee_id.id),
            #      ('date_issuing', '>=', '1/1/' + str(int(current_year) - 1)),
            #      ('date_issuing', '<=', '12/31/' + str(int(current_year) - 1))], limit=1, order="date_issuing DESC")

            latest_year_1 = self.env['hr.notice'].search(
                [('related_employee', '=', rec.employee_id.id),
                 ('date_issuing', '>=', datetime.datetime.today() - datetime.timedelta(days=365)),
                 ('date_issuing', '>=', '1/1/' + str(int(current_year) - 1)),
                 ('date_issuing', '<=', '12/31/' + str(int(current_year) - 1))], limit=1, order="date_issuing DESC")

            if latest_year_1:
                rec.current_year_1_latest_warning_issue = latest_year_1.date_issuing
                rec.current_year_1_latest_warning_reason = latest_year_1.reason
                rec.current_year_1_latest_warning_seq = latest_year_1.name
            else:
                rec.current_year_1_latest_warning_issue = ''
                rec.current_year_1_latest_warning_reason = ''
                rec.current_year_1_latest_warning_seq = ''

            latest_year = self.env['hr.notice'].search(
                [('related_employee', '=', rec.employee_id.id), ('date_issuing', '>=', '1/1/' + str(int(current_year))),
                 ('date_issuing', '<=', '12/31/' + str(int(current_year)))], limit=1, order="date_issuing DESC")
            if latest_year:
                rec.current_year_latest_warning_issue = latest_year.date_issuing
                rec.current_year_latest_warning_seq = latest_year.name
                rec.current_year_latest_warning_reason = latest_year.reason
            else:
                rec.current_year_latest_warning_issue = ''
                rec.current_year_latest_warning_seq = ''
                rec.current_year_latest_warning_reason = ''

    def action_complete_appraisal(self):
        super(HrAppraisal, self).action_complete_appraisal()
        performance_history = self.env['appraisal.history']
        val = {
            'appraisal_employee': self.employee_id.id,
            'appraisal': self.id,
            'hr_overall_rating_final_related': self.hr_overall_rating_final,
            'appraisal_year_related': self.year,
            'appraisal_form_related': self.appraisal_form.id

        }
        performance_history.create(val)
        self.is_completed = True

    def process_appraisal_stage(self):
        for appraisal in self:
            if appraisal.hr_overall_rating == 0:
                pass
            elif appraisal.overall_rating_rounded != appraisal.hr_overall_rating:
                appraisal.move_previous_stage()
            elif appraisal.overall_rating_rounded == appraisal.hr_overall_rating:
                appraisal.move_next_stage()


class HrAppraisalStage(models.Model):
    _inherit = "hr.appraisal.stage"

    is_calibration = fields.Boolean(
        string='Is Calibration',
        required=True, default=False)
