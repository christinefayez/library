# -*- coding: utf-8 -*-
# from odoo import http


# class Gamestore(http.Controller):
#     @http.route('/gamestore/gamestore/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gamestore/gamestore/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gamestore.listing', {
#             'root': '/gamestore/gamestore',
#             'objects': http.request.env['gamestore.gamestore'].search([]),
#         })

#     @http.route('/gamestore/gamestore/objects/<model("gamestore.gamestore"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gamestore.object', {
#             'object': obj
#         })
