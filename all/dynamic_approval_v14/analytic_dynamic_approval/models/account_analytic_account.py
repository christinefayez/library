from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    apply_approval_role = fields.Boolean(
        default=True,
    )
    approval_role_ids = fields.One2many(
        comodel_name='account.analytic.account.approval.role',
        inverse_name='analytic_account_id',
    )

    @api.onchange('apply_approval_role')
    def _onchange_apply_approval_role(self):
        """ reset approvel roles """
        for record in self:
            record.approval_role_ids.unlink()

