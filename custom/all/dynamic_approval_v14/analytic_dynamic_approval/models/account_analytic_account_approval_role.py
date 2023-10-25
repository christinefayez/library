from odoo import fields, models, api


class AccountAnalyticAccountApprovalRole(models.Model):
    """ assign user for each role
        allow end user to configure users
    """
    _name = 'account.analytic.account.approval.role'
    _description = 'Analytic Account Approval Role'
    _rec_name = 'user_id'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        ondelete='cascade',
    )
    role_id = fields.Many2one(
        comodel_name='dynamic.approval.role',
        required=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Default User',
        required=False,
    )

    use_dynamic_user = fields.Boolean(
        string='Use Dynamic User', )

    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Referenced Document',
        required=True,
        ondelete='cascade',
        domain=lambda self: [('model', 'in', self._get_vertical_approval_validation_model_names())],
    )

    model_user_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Default user field for SP',
    )

    _sql_constraints = [
        ('role_analytic_uniq', 'unique(analytic_account_id,role_id)', 'Role must be unique per analytic account !'),
    ]

    @api.model
    def _get_vertical_approval_validation_model_names(self):
        res = []
        return res

    @api.onchange('use_dynamic_user')
    def onchange_reset_user_field_id_model_id(self):
        self.user_id = False
        self.model_id = False
        self.model_user_field_id = False

    def get_approve_user(self, approval, model, res):
        """
        return user need approve.
        you can override to add custom user based on requirement
        :param obj approval: configuration object
        :param string model: technical name of model ex 'sale.order'
        :param  obj res: recordset of object ex 'sale.order(1)'
        """
        self.ensure_one()
        return self.user_id
