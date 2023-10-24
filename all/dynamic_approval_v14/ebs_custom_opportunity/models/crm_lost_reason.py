from odoo import fields, models


class CrmLostReason(models.Model):
    _inherit = 'crm.lost.reason'

    is_competitor_reason = fields.Boolean()
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
