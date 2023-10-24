from odoo import api, fields, models


class CrmStage(models.Model):
    _inherit = 'crm.stage'
    forecast_category_ids = fields.Many2many(
        comodel_name='crm.lead.forecast.category',
        relation='crm_stage_forecast_category_rel',
        column1='forecast_category_id',
        column2='stage_id',
        string='Forecast Category')
    default_forecast_category_id = fields.Many2one(
        comodel_name='crm.lead.forecast.category',
    )
    is_default = fields.Boolean(string='Is Default Stage' ,default=False)

    @api.onchange('forecast_category_ids')
    def _onchange_forecast_category_ids(self):
        """ reset default_forecast_category_id """
        for record in self:
            record.default_forecast_category_id = False
