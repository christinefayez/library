from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_order_custom_charge_percentage_default = fields.Float(
        related='company_id.default_sale_order_custom_charge_percentage',
        readonly=False,
    )
    sale_order_moh_charge_percentage_default = fields.Float(
        related='company_id.default_sale_order_moh_charge_percentage',
        readonly=False,
    )
