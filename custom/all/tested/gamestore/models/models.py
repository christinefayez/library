# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    customer_code_ids = fields.One2many(comodel_name="partner.product", inverse_name="product_id",
                                        string="Customer Code", required=False, )

    # @api.onchange('qty_available')
    # def _onchange_FIELD_NAME(self):
    #     print('test')
    #     pass

    def _compute_quantities(self):
        products = self.filtered(lambda p: p.type != 'service')
        res = products._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'),
                                                self._context.get('package_id'), self._context.get('from_date'),
                                                self._context.get('to_date'))
        for product in products:
            product.qty_available = res[product.id]['qty_available']
            product.incoming_qty = res[product.id]['incoming_qty']
            product.outgoing_qty = res[product.id]['outgoing_qty']
            product.virtual_available = res[product.id]['virtual_available']
            product.free_qty = res[product.id]['free_qty']
            if res[product.id]['qty_available'] > 0:
                print('test')
        # Services need to be set with 0.0 for all quantities

        services = self - products
        services.qty_available = 0.0
        services.incoming_qty = 0.0
        services.outgoing_qty = 0.0
        services.virtual_available = 0.0
        services.free_qty = 0.0


class CustomerCode(models.Model):
    _name = 'partner.product'

    partner_id = fields.Many2one(comodel_name="res.partner", string="", required=False, )
    product_id = fields.Many2one(comodel_name="product.product", string="", required=False, )
    Customer_code = fields.Char(string="Customer Code", required=True, )
