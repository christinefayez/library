# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductRestrict(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    restrict_sale = fields.Boolean(string="Restict Sale", )


class ProdcutProductRestrict(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    restrict_sale = fields.Boolean(string="Restict Sale", related="product_tmpl_id.restrict_sale")


class SaleRestrict(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    def check_restrict(self):
        if self.order_line:
            for line in self.order_line:
                if line.product_id.restrict_sale:
                    return True
            return False
        else:
            return False

    def action_confirm(self):
        if self.check_restrict() and not self.env.user.has_group('sale_restict.group_restrict_action_menu'):

            raise ValidationError("This order need Administration Confirm")
        else:
            return super(SaleRestrict, self).action_confirm()
