from odoo import fields, models


class OpportunityClassification(models.Model):
    _name = 'opportunity.classification'
    _description = 'Opportunity Classification'

    name = fields.Char()
    is_tender = fields.Boolean(string='Is Tender', default=False)
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
