from odoo import fields, models, api


class CRMLeadForecastCategory(models.Model):
    _name = 'crm.lead.forecast.category'
    _description = 'CRM Lead Forecast Category'

    name = fields.Char()
    crm_stage_ids = fields.Many2many(
        comodel_name='crm.stage',
        relation='crm_stage_forecast_category_rel',
        column1='stage_id',
        column2='forecast_category_id',
        string='Stages')
    active = fields.Boolean(
        default=True)
    appear_risk = fields.Boolean()
    is_upside = fields.Boolean()
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
