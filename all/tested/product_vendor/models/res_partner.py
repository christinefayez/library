# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    vendor_id = fields.Many2one('product.brand', 'Brand')
    model_number = fields.Char(string="Model Number", required=False, )
    barcode_2 = fields.Char(string="Second barcode", required=False, )
    digital = fields.Boolean(string="Digital Product", )
    d_type = fields.Selection(string="Digital Type", selection=[('epay', 'EPAY'), ('ezai', 'EZ PIN'), ], required=False,
                              )
    card = fields.Char(string="Card", required=False, )
    amount = fields.Char(string="Amount", required=False, )
    currency = fields.Char(string="Currency", required=False, )
    sku = fields.Integer(string="", required=False, )
    amount_ezi = fields.Char(string="Amount", required=False, )


    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = []
        if not (name == '' and operator == 'ilike'):
            args += ['|', '|', '|', '|',
                     ('name', operator, name),
                     ('model_number', operator, name),
                     ('barcode', operator, name),
                     ('barcode_2', operator, name),
                     ('product_variant_ids.default_code', operator, name)]
        return super(ProductTemplate, self)._name_search(name='', args=args, operator='ilike', limit=limit,
                                                         name_get_uid=name_get_uid)


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = []
        if not (name == '' and operator == 'ilike'):
            args += ['|', '|', '|', '|',
                     ('name', operator, name),
                     ('model_number', operator, name),
                     ('barcode', operator, name),
                     ('barcode_2', operator, name),
                     ('product_variant_ids.default_code', operator, name)]
        return super(ProductProduct, self)._name_search(name='', args=args, operator='ilike', limit=limit,
                                                        name_get_uid=name_get_uid)

    vendor_id = fields.Many2one(string="Brand", related="product_tmpl_id.vendor_id")
    model_number = fields.Char(string="Model Number", related="product_tmpl_id.model_number")
    barcode_2 = fields.Char(string="Second barcode", related="product_tmpl_id.barcode_2")
    digital = fields.Boolean(string="Digital Product", related="product_tmpl_id.digital")
    d_type = fields.Selection(string="Digital Type", related="product_tmpl_id.d_type")
    card = fields.Char(string="Card", related="product_tmpl_id.card")
    amount = fields.Char(string="Amount", related="product_tmpl_id.amount")
    currency = fields.Char(string="Currency", related="product_tmpl_id.currency")
    # sku = fields.Integer(string="", required=False, related="product_tmpl_id.sku" )
    # amount_ezi = fields.Char(string="Amount", required=False, related="product_tmpl_id.amount_ezi" )


class Brand(models.Model):
    _name = 'product.brand'
    _rec_name = 'name'

    name = fields.Char()
    code = fields.Char(string="code", required=False, )


class SaleReports(models.Model):
    _inherit = 'sale.report'

    brand_id = fields.Many2one('product.brand', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['brand_id'] = ", t.vendor_id as brand_id"
        groupby += ', t.vendor_id'

        return super(SaleReports, self)._query(with_clause, fields, groupby, from_clause)
