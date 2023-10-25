# -*- coding: utf-8 -*-
from odoo import http

# class HrAppraisalFeedback(http.Controller):
#     @http.route('/hr_appraisal_feedback/hr_appraisal_feedback/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_appraisal_feedback/hr_appraisal_feedback/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_appraisal_feedback.listing', {
#             'root': '/hr_appraisal_feedback/hr_appraisal_feedback',
#             'objects': http.request.env['hr_appraisal_feedback.hr_appraisal_feedback'].search([]),
#         })

#     @http.route('/hr_appraisal_feedback/hr_appraisal_feedback/objects/<model("hr_appraisal_feedback.hr_appraisal_feedback"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_appraisal_feedback.object', {
#             'object': obj
#         })