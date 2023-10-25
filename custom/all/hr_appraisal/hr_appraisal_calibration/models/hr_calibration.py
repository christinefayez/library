# -*- coding: utf-8 -*-

from odoo import models, fields


class HrCalibration(models.Model):
    _name = 'hr.calibration'

    year = fields.Char(string="Year")
    target = fields.One2many('hr.performance.target', 'calibration_id', string="Target")
    appraisal_no = fields.Integer(
        string='Appraisal No',
        compute='_get_appraisal_no')

    def name_get(self):
        names = []
        for record in self:
            names.append((record.id, "%s" % record.year))
        return names

    def _get_appraisal_no(self):
        for rec in self:
            calibration_stage = self.env['hr.appraisal.stage'].search([('is_calibration', '=', True)], limit=1)
            appraisals = self.env['hr.appraisal'].search(
                [('year', '=', self.year), ('stage_id', '=', calibration_stage.id)])
            rec.appraisal_no = len(appraisals)

    def redirect_to_calibration(self):
        calibration_stage = self.env['hr.appraisal.stage'].search([('is_calibration', '=', True)], limit=1)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.appraisal',
            'view_mode': 'tree',
            'view_id': self.env.ref('hr_appraisal_calibration.hr_appraisal_calibration_tree_view').id,
            'target': 'current',
            'domain': [('year', '=', self.year), ('stage_id', '=', calibration_stage.id)],
        }

    def redirect_to_calibration_report(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Calibration Reporting Wizard',
            'res_model': 'calibration.reporting.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('hr_appraisal_calibration.calibration_reporting_wizard_view_form').id,
            'target': 'new',
            'context': {
                'default_year': self.year
            }
        }

    def copy_manager_ratings(self):
        calibration_stage = self.env['hr.appraisal.stage'].search([('is_calibration', '=', True)], limit=1)

        appraisals = self.env['hr.appraisal'].search(
            [('year', '=', self.year), ('stage_id', '=', calibration_stage.id)])

        for appraisal in appraisals:
            if appraisal.hr_overall_rating == 0:
                appraisal.hr_overall_rating = appraisal.overall_rating_rounded

        view = self.env.ref('sh_message.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['message'] = 'Thank you, the values have been copied.'
        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': context,
        }

    def move_next(self):
        calibration_stage = self.env['hr.appraisal.stage'].search([('is_calibration', '=', True)], limit=1)

        appraisals = self.env['hr.appraisal'].search(
            [('year', '=', self.year), ('stage_id', '=', calibration_stage.id)])

        for appraisal in appraisals:
            if appraisal.hr_overall_rating == 0:
                pass
            elif appraisal.overall_rating_rounded == appraisal.hr_overall_rating or appraisal.appraisal_form.always_release_ratings:
                appraisal.move_next_stage()

        view = self.env.ref('sh_message.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['message'] = 'Thank you, the ratings have been released.'
        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': context,
        }

    def move_previous(self):
        calibration_stage = self.env['hr.appraisal.stage'].search([('is_calibration', '=', True)], limit=1)

        appraisals = self.env['hr.appraisal'].search(
            [('year', '=', self.year), ('stage_id', '=', calibration_stage.id)])

        for appraisal in appraisals:
            if appraisal.hr_overall_rating == 0:
                pass
            elif appraisal.overall_rating_rounded != appraisal.hr_overall_rating:
                appraisal.move_previous_stage()

        view = self.env.ref('sh_message.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['message'] = 'Thank you, the managers have been notified.'
        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': context,
        }
