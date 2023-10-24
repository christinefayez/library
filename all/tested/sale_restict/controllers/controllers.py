# -*- coding: utf-8 -*-
# from odoo import http


# class SaleRestict(http.Controller):
#     @http.route('/sale_restict/sale_restict/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_restict/sale_restict/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_restict.listing', {
#             'root': '/sale_restict/sale_restict',
#             'objects': http.request.env['sale_restict.sale_restict'].search([]),
#         })

#     @http.route('/sale_restict/sale_restict/objects/<model("sale_restict.sale_restict"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_restict.object', {
#             'object': obj
#         })
