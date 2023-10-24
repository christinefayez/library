from odoo import models, fields, api


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    # lot_cost_price = fields.Float(string='Lot Cost')
    lot_serial_cost = fields.Float(string='Lot/Serial Number Cost', compute='_product_qty')
    is_losing_product = fields.Boolean(string='Is Losing Product', readonly=True, default=False, tracking=True)

    @api.onchange('product_id', 'product_id.list_price')
    def _on_change_sales_price(self):
        if self.product_id and self.product_id.list_price < self.product_id.standard_price:
            self.is_losing_product = True
        else:
            self.is_losing_product = False

    @api.depends('quant_ids', 'quant_ids.quantity')
    def _product_qty(self):
        for lot in self:
            # We only care for the quants in internal or transit locations.
            quants = lot.quant_ids.filtered(lambda q: q.location_id.usage == 'internal' or (
                    q.location_id.usage == 'transit' and q.location_id.company_id))
            lot.product_qty = sum(quants.mapped('quantity'))
            lot.lot_serial_cost = sum(quants.mapped('value'))
