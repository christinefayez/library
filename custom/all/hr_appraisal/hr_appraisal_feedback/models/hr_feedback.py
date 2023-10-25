# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from lxml import etree


class hr_appraisal_feedback(models.Model):
    _name = 'hr.feedback'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users', "Responsible User", required=True)
    requested_user = fields.Many2one('res.users', "Requested From", default=lambda self: self.env.user, readonly=True)
    feedback = fields.Text('Feedback')
    feedback_type = fields.Selection([('form', 'Whole Form'), ('objectives', 'Selected Objectives')],
                                     string='Feedback Type', required=True)
    related_employee = fields.Many2one('hr.employee', string="Related Employee")
    related_objectives = fields.Many2one('hr.appraisal.objective', string='Related Objective')
    related_appraisal = fields.Many2one('hr.appraisal', string='Related Appraisal', readonly=True)
    feedback_before = fields.Date('Needed Before', required=True)
    feedback_submit = fields.Date('Submit Date', readonly=True)
    state = fields.Selection([('pending', 'Pending'), ('submitted', 'Submitted')], 'State', default='pending')
    can_submit = fields.Boolean('Can Submit Feedback', compute="check_can_submit")

    def action_print_appraisal(self):
        self = self.sudo()
        result = self.sudo().env.ref('hr_appraisal_custom.appraisal_report_id').report_action(
            self.sudo().related_appraisal)
        return result

    def check_can_submit(self):
        for rec in self:
            if rec.user_id.id == self.env.user.id:
                rec.can_submit = True
            else:
                rec.can_submit = False

    def submit_feedback(self):
        for rec in self:
            if not rec.feedback:
                raise ValidationError("Feedback can not be empty!")
            rec.write({'feedback_submit': fields.Date.today(),
                       'state': 'submitted'})

    @api.onchange('user_id')
    def _onchange_user(self):
        for rec in self:
            if rec.user_id:
                rec.name = rec.user_id.name + "'s Feedback"
            else:
                rec.name = "Feedback"

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(hr_appraisal_feedback, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                                 submenu=submenu)

        doc = etree.XML(res['arch'])
        if self.env.user.has_group('security_rules.group_hr_employee'):
            if view_type == 'tree':
                nodes = doc.xpath("//tree")
                for node in nodes:
                    node.set('create', '0')
                res['arch'] = etree.tostring(doc)

        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
