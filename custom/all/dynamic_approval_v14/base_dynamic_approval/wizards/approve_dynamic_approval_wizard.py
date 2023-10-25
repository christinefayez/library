from odoo import models, fields, _


class ApproveDynamicApprovalWizard(models.TransientModel):
    _name = 'approve.dynamic.approval.wizard'
    _description = 'Approve Advanced Approval Wizard'

    note = fields.Char()

    def action_approve_order(self):
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        record = self.env[active_model].browse(active_ids)
        record.action_under_approval(note=self.note)
        if active_model == 'sale.order':
            orders = self.env[active_model].browse(active_ids)
            for order in orders:
                order.action_confirm()