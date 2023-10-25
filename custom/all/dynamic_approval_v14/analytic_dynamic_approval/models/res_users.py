from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    analytic_approval_role_ids = fields.One2many(
        comodel_name='account.analytic.account.approval.role',
        inverse_name='user_id',
    )

    def __init__(self, pool, cr):
        init_res = super().__init__(pool, cr)
        type(self).SELF_READABLE_FIELDS = self.SELF_READABLE_FIELDS + ['analytic_approval_role_ids']
        return init_res
