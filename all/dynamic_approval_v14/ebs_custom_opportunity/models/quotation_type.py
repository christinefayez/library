from odoo import models, fields


class QuotationType(models.Model):
    _name = 'quotation.type'
    _description = 'quotation.type'

    name = fields.Char("Type")
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
