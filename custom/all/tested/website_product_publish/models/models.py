# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProdoctPublish(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    is_published = fields.Boolean("Published", copy=False)



    def publish(self):
        if not self.is_published:
            self.is_published = True
