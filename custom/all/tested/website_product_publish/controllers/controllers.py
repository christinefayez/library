# -*- coding: utf-8 -*-
# from odoo import http


# class WebsiteProductPublish(http.Controller):
#     @http.route('/website_product_publish/website_product_publish/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_product_publish/website_product_publish/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_product_publish.listing', {
#             'root': '/website_product_publish/website_product_publish',
#             'objects': http.request.env['website_product_publish.website_product_publish'].search([]),
#         })

#     @http.route('/website_product_publish/website_product_publish/objects/<model("website_product_publish.website_product_publish"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_product_publish.object', {
#             'object': obj
#         })
