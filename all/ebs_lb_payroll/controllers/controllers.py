# -*- coding: utf-8 -*-
from odoo import http

# class I10nLbPayroll(http.Controller):
#     @http.route('/i10n_lb_payroll/i10n_lb_payroll/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/i10n_lb_payroll/i10n_lb_payroll/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('i10n_lb_payroll.listing', {
#             'root': '/i10n_lb_payroll/i10n_lb_payroll',
#             'objects': http.request.env['i10n_lb_payroll.i10n_lb_payroll'].search([]),
#         })

#     @http.route('/i10n_lb_payroll/i10n_lb_payroll/objects/<model("i10n_lb_payroll.i10n_lb_payroll"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('i10n_lb_payroll.object', {
#             'object': obj
#         })