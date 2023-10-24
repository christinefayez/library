from odoo import models, fields, api, _


class StockProductionLot(models.Model):
    _name = 'product.losing.report'
    _description = 'Product Losing Report'

    product_id = fields.Many2one('product.product', string='Product')
    lot_id = fields.Many2one('stock.production.lot', string='Lot/Serial Number')
    total_selling_price = fields.Float(string='Selling Price')
    total_cost_price = fields.Float(string='Cost Price')
    losing_amount = fields.Float(string='Losing Amount')
    quantity = fields.Integer(string='Quantity')
    company_id = fields.Many2one('res.company', string='Company')

    @api.model
    def get_product_losing_report(self):
        lots = self.env['stock.production.lot'].search([('is_losing_product', '=', True)])
        loss_product_data = self.env['product.losing.report']
        data = []
        for lot in lots:
            if loss_product_data.search([('lot_id', '=', lot.id), ('company_id', '=', lot.company_id.id)]):
                continue
            else:
                total_selling_price = lot.product_id.list_price * lot.product_qty
                total_cost_price = lot.lot_serial_cost * lot.product_qty

                data.append({
                    'product_id': lot.product_id.id,
                    'lot_id': lot.id,
                    'quantity': lot.product_qty,
                    'total_selling_price': total_selling_price,
                    'total_cost_price': total_cost_price,
                    'losing_amount': total_selling_price - total_cost_price,
                    'company_id': lot.company_id.id,
                })

        loss_product_data.create(data)

        action = {
            'name': _('Product Losing Report'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'product.losing.report',
            'type': 'ir.actions.act_window',
            'domain': [],
            'target': 'current'
        }
        return action
