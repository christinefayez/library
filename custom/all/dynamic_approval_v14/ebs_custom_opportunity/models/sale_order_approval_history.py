from odoo import fields, api, _, models


class SaleOrder(models.Model):
    _name = 'sale.order.approval.history'

    user_id = fields.Many2one('res.users', string='User')

    status = fields.Selection(
        [('request_approval', 'Request Approval'), ('approved', 'Approved'),
         ('reject', 'Reject'),
         ('recall', 'Recall')
         ],
        string="state", default='no')
    action_date = fields.Date(string='Date')
    sale_id = fields.Many2one('sale.order', string='Sales Order')
    sale_order_status = fields.Selection(selection=lambda self:self.env['sale.order']._fields['state'].selection, string="Sale Order Status")
