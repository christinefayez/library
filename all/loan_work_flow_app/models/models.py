from odoo import models, fields, api, _
from odoo.tools.image import image_data_uri


class LoanInherit(models.Model):
    _inherit = 'hr.loan'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('doo', 'DOO'),
        ('dof', 'Dof'),
        ('ceo', 'CEO'),
        ('done', 'Done'),
        ('waiting_approval_1', 'Submitted'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )

    doo_user_id = fields.Many2one('res.users')
    dof_user_id = fields.Many2one('res.users')
    ceo_user_id = fields.Many2one('res.users')
    loan_description = fields.Text()

    def doo_approve(self):
        self.write({
            'state': 'dof',
            'doo_user_id': self.env.uid,

        })
        user = self.env.user.has_group('loan_work_flow_app.loan_doo_user_group')
        print(self.env.user.id)
        if user:
            done_activity = self.env['mail.activity'].search([('user_id', '=', self.env.user.id)])
            if done_activity:
                done_activity.action_done()
        dof_users = self.env.ref('loan_work_flow_app.loan_doo_user_group').users
        for dof in dof_users:
            self.activity_schedule(
                user_id=dof.id,
                activity_type_id=4,
                date_deadline=fields.date.today()
            )

    def dof_approve(self):
        self.write({
            'state': 'ceo',
            'dof_user_id': self.env.uid,

        })

        user = self.env.user.has_group('loan_work_flow_app.loan_dof_user_group')
        print(self.env.user.id)
        if user:
            done_activity = self.env['mail.activity'].search([('user_id', '=', self.env.user.id)])
            if done_activity:
                done_activity.action_done()
        ceo_users = self.env.ref('loan_work_flow_app.loan_dof_user_group').users
        for ceo in ceo_users:
            self.activity_schedule(
                user_id=ceo.id,
                activity_type_id=4,
                date_deadline=fields.date.today()
            )

    def ceo_approve(self):
        self.write({
            'state': 'done',
            'ceo_user_id': self.env.uid,

        })

        user = self.env.user.has_group('loan_work_flow_app.loan_ceo_user_group')
        print(self.env.user.id)
        if user:
            done_activity = self.env['mail.activity'].search([('user_id', '=', self.env.user.id)])
            if done_activity:
                done_activity.action_done()

    def print_pdf(self):
        return {
            'type': 'ir.actions.act_window',
            'target': 'new',
            'name': _('Print Loan Report'),
            'view_mode': 'form',
            'res_model': 'loan.report.wizard',
            'context': {'default_loan_id': self.id},
        }
