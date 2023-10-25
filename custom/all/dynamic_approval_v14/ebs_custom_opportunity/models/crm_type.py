from odoo import fields, models


class CrmType(models.Model):
    _name = 'crm.type'
    _description = 'CRM Type'

    name = fields.Char()
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(
        default=True,
    )
