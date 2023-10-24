from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    lpo_number_sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='LPO Number of Sales Order',
    )
