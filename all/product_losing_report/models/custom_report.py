from odoo import models, fields, api, _


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    avg = fields.Float()
    is_losing_product = fields.Boolean(compute='_onchange_sales_price')
    cost = fields.Float()

    @api.depends('product_id')
    def _onchange_sales_price(self):
        for rec in self:
            sales_order = self.env['sale.order.line'].search([('product_id', '=', rec.product_id.id)], limit=5,
                                                             order='id desc')
            subtotal = sum(sales_order.mapped('price_subtotal'))
            qty = sum(sales_order.mapped('product_uom_qty'))
            avg = 0
            if subtotal > 0 and qty > 0:
                avg = (subtotal / qty)
            rec.avg = avg
            cost = self.env['stock.valuation.layer'].read_group(
                domain=[('product_id', '=', rec.product_id.id)], fields=['product_id', 'value', 'quantity'],
                groupby=['product_id'])
            if cost[0]['value'] > 0 and cost[0]['quantity'] > 0:
                rec.cost = cost[0]['value'] / cost[0]['quantity']
            else:

                rec.cost = 0

            if rec.product_id and rec.product_id.tracking == 'none' and rec.avg < rec.cost and rec.quantity > 0:
                rec.is_losing_product = True
            else:
                rec.is_losing_product = False


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    avg = fields.Float()

    @api.onchange('product_id', 'product_id.list_price')
    def _on_change_sales_price(self):

        sales_order = self.env['sale.order.line'].search([('product_id', '=', self.product_id.id)], limit=5,
                                                         order='id desc')
        subtotal = sum(sales_order.mapped('price_subtotal'))
        qty = sum(sales_order.mapped('product_uom_qty'))
        avg = 0
        if subtotal > 0 and qty > 0:
            avg = (subtotal / qty)
        self.avg = avg

        if self.product_id and avg < self.lot_serial_cost and self.product_qty > 0:
            self.is_losing_product = True
        else:
            self.is_losing_product = False


class StockProductionLot(models.Model):
    _inherit = 'product.losing.report'

    @api.model
    def get_product_losing_report(self):
        lots = self.env['stock.production.lot'].search([('is_losing_product', '=', True)])
        valuations = self.env['stock.valuation.layer'].search([('is_losing_product', '=', True)])
        print(len(valuations), lots)
        loss_product_data = self.env['product.losing.report']
        lose_product = []
        for lot in lots:
            if loss_product_data.search([('lot_id', '=', lot.id), ('company_id', '=', lot.company_id.id)]):
                continue
            else:
                total_selling_price = lot.avg
                total_cost_price = lot.lot_serial_cost

                vals = {
                    'product_id': lot.product_id.id,
                    'lot_id': lot.id,
                    'quantity': lot.product_qty,
                    'total_selling_price': total_selling_price,
                    'total_cost_price': total_cost_price,
                    'losing_amount': total_selling_price - total_cost_price,
                    'company_id': lot.company_id.id,
                }

                losee = loss_product_data.create(vals)
                lose_product.append(losee.id)
        for valuation in valuations:
            if valuation.is_losing_product:
                print(valuation.is_losing_product)
                vals = {
                    'product_id': valuation.product_id.id,
                    'lot_id': False,
                    'quantity': valuation.quantity,
                    'total_selling_price': valuation.avg,
                    'total_cost_price': valuation.cost,
                    'losing_amount': valuation.avg - valuation.cost,
                    'company_id': valuation.company_id.id,
                }
                lose = loss_product_data.create(vals)
                lose_product.append(lose.id)

        action = {
            'name': _('Product Losing Report'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'product.losing.report',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', lose_product)],
            'target': 'current'
        }
        return action
