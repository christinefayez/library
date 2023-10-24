from odoo import fields, models


class ResPartnerType(models.Model):
    _name = 'res.partner.type'
    _description = 'Partner Type'

    name = fields.Char(
        required=True,
        translate=True,
    )
    active = fields.Boolean(
        default=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
    type = fields.Selection(
        selection=[('customer', 'Customer'),
                   ('vendor', 'Vendor'),
                   ],
        required=True,
        default='customer',
    )
    appear_license = fields.Boolean()
