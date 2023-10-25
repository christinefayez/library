from odoo import fields, models, api


class HrAppraisalObjective(models.Model):
    _inherit = 'hr.appraisal.objective'

    @api.depends('manager_rate_id', 'weight')
    def _compute_outcome_percentage(self):
        """ compute percentage from rate """
        for record in self:
            outcome_percentage = 0
            if record.manager_rate_id:
                if record.manager_rate_id.percentage and not record.manager_rate_id.number:
                    outcome_percentage = record.weight * (record.manager_rate_id.percentage / 100)
                elif record.manager_rate_id.number and not record.manager_rate_id.percentage:
                    outcome_percentage = record.manager_rate_id.number
                else:
                    outcome_percentage = record.weight * (record.manager_rate_id.percentage / 100)
            record.outcome_percentage = outcome_percentage
