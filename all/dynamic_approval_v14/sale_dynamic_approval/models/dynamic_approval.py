from odoo import models, api

import datetime

class DynamicApproval(models.Model):
    _inherit = 'dynamic.approval'

    @api.model
    def _get_approval_validation_model_names(self):
        """ add model sale.order to model options """
        res = super()._get_approval_validation_model_names()
        res.append('sale.order')
        return res


class DynamicApprovalRequest(models.Model):
    _inherit = 'dynamic.approval.request'

    @api.onchange('status')
    def onchange_state_approval_history(self):
        if self.status == 'approved':
            val = {'user_id': self.env.uid,
                   'status': 'approved',
                   'action_date': datetime.now()}
            self.approval_history_ids = (0, 0, val)
        elif self.status == 'rejected':
            val = {'user_id': self.env.uid,
                   'status': 'reject',
                   'action_date': datetime.now()}
            self.approval_history_ids = (0, 0, val)
        elif self.status == 'recall':
            val = {'user_id': self.env.uid,
                   'status': 'recall',
                   'action_date': datetime.now()}
            self.approval_history_ids = (0, 0, val)
        return
