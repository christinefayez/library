from odoo import fields, models, api
from random import random


class CalibrationReportingWizard(models.TransientModel):
    _name = 'calibration.reporting.wizard'

    year = fields.Char(string='Year')
    contract_subgroups_ids = fields.Many2many(
        comodel_name='hr.contract.subgroup',
        string='Subgroups')
    grouping_by = fields.Selection(
        string='Grouping By',
        selection=[('no_grouping', 'No Grouping'),
                   ('department_rating', 'Department/Rating'),
                   ('rating_department', 'Rating/Department')],
        required=True)

    def redirect_to_calibration_report(self):
        calibration = self.env['hr.calibration'].search([('year', '=', self.year)], limit=1)
        targets = self.env['hr.performance.target'].search([('calibration_id', '=', calibration.id)])
        forms = self.env['hr.appraisal.form'].search([('includes_calibration', '=', True)])
        random_ = random()
        year = self.year
        min_ = 0
        max_ = 0
        if self.grouping_by == 'no_grouping':
            for target in targets:
                rate = target.target
                performance_name = target.name
                min_ = target.min
                max_ = target.max

                target_appraisals = self.env['hr.appraisal'].search(
                    [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                     ('hr_overall_rating', '=', rate), ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                total_appraisals = self.env['hr.appraisal'].search(
                    [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                     ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                if len(total_appraisals) > 0:
                    percentage = len(target_appraisals) / len(total_appraisals) * 100
                else:
                    percentage = 0

                self.env['calibration.report.view'].create({
                    'target': rate,
                    'target_name': performance_name,
                    'min_perc': min_,
                    'max_perc': max_,
                    'target_appraisals': len(target_appraisals),
                    'total_appraisals': len(total_appraisals),
                    'percentage': percentage,
                    'year': year,
                    'random_uid': str(random_)
                })

            target_appraisals = self.env['hr.appraisal'].search(
                [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                 ('hr_overall_rating', '=', 0), ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
            total_appraisals = self.env['hr.appraisal'].search(
                [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                 ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
            if len(total_appraisals) > 0:
                percentage = len(target_appraisals) / len(total_appraisals) * 100
            else:
                percentage = 0

            self.env['calibration.report.view'].create({
                'target': 0,
                'target_name': 'No Rating',
                'min_perc': 0,
                'max_perc': 0,
                'target_appraisals': len(target_appraisals),
                'total_appraisals': len(total_appraisals),
                'percentage': percentage,
                'year': year,
                'random_uid': str(random_)
            })

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'calibration.report.view',
                'view_mode': 'tree,graph',
                'target': 'current',
                'domain': [('random_uid', '=', random_)],
            }

        elif self.grouping_by == 'department_rating':
            departments = self.env['hr.department'].search([('type', '=', 'BD')])
            for department in departments:
                for target in targets:
                    rate = target.target
                    performance_name = target.name
                    min_ = target.min
                    max_ = target.max

                    target_appraisals = self.env['hr.appraisal'].search(
                        [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                         ('hr_overall_rating', '=', rate), ('department', '=', department.id),
                         ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                    total_appraisals = self.env['hr.appraisal'].search(
                        [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                         ('department', '=', department.id),
                         ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                    if len(total_appraisals) > 0:
                        percentage = len(target_appraisals) / len(total_appraisals) * 100
                    else:
                        percentage = 0

                    self.env['calibration.report.view.grouped.d'].create({
                        'department': department.id,
                        'target': rate,
                        'target_name': performance_name,
                        'min_perc': min_,
                        'max_perc': max_,
                        'target_appraisals': len(target_appraisals),
                        'total_appraisals': len(total_appraisals),
                        'percentage': percentage,
                        'year': year,
                        'random_uid': str(random_)
                    })

                target_appraisals = self.env['hr.appraisal'].search(
                    [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                     ('department', '=', department.id),
                     ('hr_overall_rating', '=', 0), ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                total_appraisals = self.env['hr.appraisal'].search(
                    [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                     ('department', '=', department.id),
                     ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                if len(total_appraisals) > 0:
                    percentage = len(target_appraisals) / len(total_appraisals) * 100
                else:
                    percentage = 0

                self.env['calibration.report.view.grouped.d'].create({
                    'department': department.id,
                    'target': 0,
                    'target_name': 'No Rating',
                    'min_perc': 0,
                    'max_perc': 0,
                    'target_appraisals': len(target_appraisals),
                    'total_appraisals': len(total_appraisals),
                    'percentage': percentage,
                    'year': year,
                    'random_uid': str(random_)
                })

            for target in targets:
                rate = target.target
                performance_name = target.name
                min_ = target.min
                max_ = target.max

                target_appraisals = self.env['hr.appraisal'].search(
                    [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                     ('hr_overall_rating', '=', rate), ('department', '=', False),
                     ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                total_appraisals = self.env['hr.appraisal'].search(
                    [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                     ('department', '=', False),
                     ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                if len(total_appraisals) > 0:
                    percentage = len(target_appraisals) / len(total_appraisals) * 100
                else:
                    percentage = 0

                self.env['calibration.report.view.grouped.d'].create({
                    'department': False,
                    'target': rate,
                    'target_name': performance_name,
                    'min_perc': min_,
                    'max_perc': max_,
                    'target_appraisals': len(target_appraisals),
                    'total_appraisals': len(total_appraisals),
                    'percentage': percentage,
                    'year': year,
                    'random_uid': str(random_)
                })

            target_appraisals = self.env['hr.appraisal'].search(
                [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                 ('hr_overall_rating', '=', 0), ('department', '=', False),
                 ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
            total_appraisals = self.env['hr.appraisal'].search(
                [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                 ('department', '=', False),
                 ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
            if len(total_appraisals) > 0:
                percentage = len(target_appraisals) / len(total_appraisals) * 100
            else:
                percentage = 0

            self.env['calibration.report.view.grouped.d'].create({
                'department': False,
                'target': 0,
                'target_name': 'No Rating',
                'min_perc': min_,
                'max_perc': max_,
                'target_appraisals': len(target_appraisals),
                'total_appraisals': len(total_appraisals),
                'percentage': percentage,
                'year': year,
                'random_uid': str(random_)
            })

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'calibration.report.view.grouped.d',
                'view_mode': 'tree,graph',
                'target': 'current',
                'domain': [('random_uid', '=', str(random_))],
                'context': {'group_by': 'department'}
            }

        elif self.grouping_by == 'rating_department':
            departments = self.env['hr.department'].search([('type', '=', 'BD')])

            for target in targets:
                for department in departments:
                    rate = target.target
                    performance_name = target.name
                    min_ = target.min
                    max_ = target.max

                    target_appraisals = self.env['hr.appraisal'].search(
                        [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                         ('hr_overall_rating', '=', rate), ('department', '=', department.id),
                         ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                    total_appraisals = self.env['hr.appraisal'].search(
                        [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                         ('department', '=', department.id),
                         ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                    if len(total_appraisals) > 0:
                        percentage = len(target_appraisals) / len(total_appraisals) * 100
                    else:
                        percentage = 0

                    self.env['calibration.report.view.grouped.r'].create({
                        'department': department.id,
                        'target': rate,
                        'target_name': performance_name,
                        'min_perc': min_,
                        'max_perc': max_,
                        'target_appraisals': len(target_appraisals),
                        'total_appraisals': len(total_appraisals),
                        'percentage': percentage,
                        'year': year,
                        'random_uid': str(random_)
                    })

                target_appraisals = self.env['hr.appraisal'].search(
                    [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                     ('department', '=', False),('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                total_appraisals = self.env['hr.appraisal'].search(
                    [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                     ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                if len(total_appraisals) > 0:
                    percentage = len(target_appraisals) / len(total_appraisals) * 100
                else:
                    percentage = 0

                self.env['calibration.report.view.grouped.r'].create({
                    'department': False,
                    'target': rate,
                    'target_name': performance_name,
                    'min_perc': 0,
                    'max_perc': 0,
                    'target_appraisals': len(target_appraisals),
                    'total_appraisals': len(total_appraisals),
                    'percentage': percentage,
                    'year': year,
                    'random_uid': str(random_)
                })

            for department in departments:
                target_appraisals = self.env['hr.appraisal'].search(
                    [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                     ('hr_overall_rating', '=', 0), ('department', '=', department.id),
                     ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                total_appraisals = self.env['hr.appraisal'].search(
                    [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                     ('department', '=', department.id),
                     ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
                if len(total_appraisals) > 0:
                    percentage = len(target_appraisals) / len(total_appraisals) * 100
                else:
                    percentage = 0

                self.env['calibration.report.view.grouped.r'].create({
                    'department': department.id,
                    'target': 0,
                    'target_name': 'No Rating',
                    'min_perc': min_,
                    'max_perc': max_,
                    'target_appraisals': len(target_appraisals),
                    'total_appraisals': len(total_appraisals),
                    'percentage': percentage,
                    'year': year,
                    'random_uid': str(random_)
                })

            target_appraisals = self.env['hr.appraisal'].search(
                [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                 ('hr_overall_rating', '=', 0), ('department', '=', False),
                 ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
            total_appraisals = self.env['hr.appraisal'].search(
                [('active', '=', True), ('year', '=', year), ('appraisal_form', 'in', forms.ids),
                 ('department', '=', False),
                 ('contract_subgroup_id', 'in', self.contract_subgroups_ids.ids)])
            if len(total_appraisals) > 0:
                percentage = len(target_appraisals) / len(total_appraisals) * 100
            else:
                percentage = 0

            self.env['calibration.report.view.grouped.r'].create({
                'department': False,
                'target': 0,
                'target_name': 'No Rating',
                'min_perc': min_,
                'max_perc': max_,
                'target_appraisals': len(target_appraisals),
                'total_appraisals': len(total_appraisals),
                'percentage': percentage,
                'year': year,
                'random_uid': str(random_)
            })


            return {
                'type': 'ir.actions.act_window',
                'res_model': 'calibration.report.view.grouped.r',
                'view_mode': 'tree,graph',
                'target': 'current',
                'domain': [('random_uid', '=', str(random_))],
                'context': {'group_by': 'target'}
            }
