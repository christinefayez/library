from odoo import fields, models


class OpportunityRegions(models.Model):
    _name = 'opportunity.region'
    _description = 'Opportunity Region'

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
