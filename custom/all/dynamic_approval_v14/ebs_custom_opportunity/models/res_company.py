from odoo import fields, models


class ResCompanyExt(models.Model):
    _inherit = 'res.company'

    default_sale_order_custom_charge_percentage = fields.Float()
    default_sale_order_moh_charge_percentage = fields.Float()
    trade_license_number_ids = fields.One2many(
        comodel_name='company.trade.license.number',
        inverse_name='company_id',
        string='Trading license number')
