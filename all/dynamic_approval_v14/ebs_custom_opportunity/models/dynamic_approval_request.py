from datetime import datetime

from odoo import api, models, fields


class DynamicApprovalRequest(models.Model):
    _inherit = 'dynamic.approval.request'

    # @api.onchange('status')
    # def onchange_state_approval_history(self):
    #     if self.status == 'approved':
    #         val = {'user_id': self.env.uid,
    #                'status': 'approved',
    #                'action_date': datetime.now()}
    #         self.approval_history_ids = (0, 0, val)
    #     elif self.status == 'rejected':
    #         val = {'user_id': self.env.uid,
    #                'status': 'reject',
    #                'action_date': datetime.now()}
    #         self.approval_history_ids = (0, 0, val)
    #     elif self.status == 'recall':
    #         val = {'user_id': self.env.uid,
    #                'status': 'recall',
    #                'action_date': datetime.now()}
    #         self.approval_history_ids = (0, 0, val)
    #     return

