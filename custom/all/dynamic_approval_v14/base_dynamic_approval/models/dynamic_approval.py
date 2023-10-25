import logging
from odoo import fields, models, api
from odoo.tools import safe_eval
import datetime

_logger = logging.getLogger(__name__)


class DynamicApproval(models.Model):
    _name = 'dynamic.approval'
    _inherit = ['mail.thread', 'mail.activity.mixin', ]
    _description = 'Approval Configuration'
    _order = 'sequence, id'

    @api.model
    def _get_approval_validation_model_names(self):
        res = []
        return res

    state_under_approval = fields.Char(string='State Under Approval',
                                       default='under_approval')  # to convert to it based on function 'action_dynamic_approval_request'
    state_to = fields.Char(string='State To', default='approved')  # to convert to it when no pending approval
    state_from = fields.Char(string='State From',
                             default='draft')  # to check that this stage is source that need to convert from it

    name = fields.Char(
        string='Description',
        required=True,
        translate=True,
    )
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Referenced Document',
        required=True,
        ondelete='cascade',
        domain=lambda self: [('model', 'in', self._get_approval_validation_model_names())],
    )
    model = fields.Char(
        related='model_id.model',
        index=True,
        store=True
    )
    active = fields.Boolean(
        default=True
    )
    sequence = fields.Integer(
        default=10,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
    approval_condition_ids = fields.One2many(
        comodel_name='dynamic.approval.condition',
        inverse_name='approval_id',
        string='Conditions',
        copy=True,
    )
    approval_condition_number = fields.Integer(
        compute='_compute_approval_condition_number'
    )
    approval_level_ids = fields.One2many(
        comodel_name='dynamic.approval.level',
        inverse_name='approval_id',
        string='Levels',
        copy=True,
    )
    # fields used in under approval stage
    email_template_to_approve_id = fields.Many2one(
        comodel_name='mail.template',
    )
    need_create_activity_to_approve = fields.Boolean(
        default=True,
    )
    to_approve_server_action_id = fields.Many2one(
        comodel_name='ir.actions.server',
    )
    reminder_period_to_approve = fields.Integer(
        help='Set trigger duration after request approval pending',
        default=5,
    )
    reminder_pending_approver_email_template_id = fields.Many2one(
        comodel_name='mail.template',
    )
    # fields user after last approve
    default_notify_user_field_after_final_approve_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Default user fields after final approval (Activity)',
    )
    notify_user_field_after_final_approve_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        relation='approval_notify_after_final_approve_field_rel',
        string='Notified users fields after final approve',
    )
    email_template_after_final_approve_id = fields.Many2one(
        comodel_name='mail.template',
    )
    after_final_approve_server_action_id = fields.Many2one(
        comodel_name='ir.actions.server',
    )

    # fields used when user reject
    notify_user_field_rejection_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        relation='approval_notify_reject_field_rel',
        string='Notified users fields for rejection',
    )
    default_notify_user_field_rejection_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Default user field for rejection (Activity)',
    )
    rejection_email_template_id = fields.Many2one(
        comodel_name='mail.template',
    )
    need_notify_rejection_approved_user = fields.Boolean()
    rejection_server_action_id = fields.Many2one(
        comodel_name='ir.actions.server',
    )
    # fields used when user recall
    notify_user_field_recall_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        relation='approval_notify_recall_field_rel',
        string='Notified users fields for recall',
    )
    default_notify_user_field_recall_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Default user field for recall (Activity)',
    )
    recall_email_template_id = fields.Many2one(
        comodel_name='mail.template',
    )
    need_notify_recall_approved_user = fields.Boolean()
    recall_server_action_id = fields.Many2one(
        comodel_name='ir.actions.server',
    )

    def _compute_approval_condition_number(self):
        """compute number of conditions to appear in smart button """
        for record in self:
            record.approval_condition_number = len(record.approval_condition_ids)

    def is_matched_approval(self, res):
        """ return True / False based on approval match record condition """
        self.ensure_one()
        for condition in self.approval_condition_ids:
            if not condition.is_condition_matched(res=res):
                return False
        return True

    def _prepare_approval_request_values(self, model, res):
        """ return values for approval request """
        self.ensure_one()
        levels = []
        evaluation_context = {
            'datetime': safe_eval.datetime,
            'context_today': datetime.datetime.now,
        }
        for level in self.approval_level_ids:
            if level.apply_domain:
                domain = safe_eval.safe_eval(level.domain or '[]', evaluation_context)
                orders = self.env[self.model].search(domain)
                if res in orders:
                    levels.append(level)
            else:
                levels.append(level)

        return [level.prepare_approval_request_values(model=model, res=res) for level in levels]

    @api.model
    def action_set_approver(self, model, res, company):
        """ return approval match record condition """
        print(res)
        state_field = res._state_field
        state_from = getattr(res, state_field)
        print(state_from,'state form')
        approvals = self.sudo().search(
            [('model', '=', model), '|',
             ('company_id', '=', company.id), ('company_id', '=', False),
             ('state_from', '=', state_from)
             ],
            order='sequence ASC')
        matched_approval = self.env['dynamic.approval']
        for approval in approvals:
            if approval.is_matched_approval(res=res):
                matched_approval += approval
                # break
        if matched_approval:
            approval_request_values = matched_approval._prepare_approval_request_values(model, res)
            requests = self.env['dynamic.approval.request'].create(approval_request_values)
            # add try to make sure that user inherit dynamic.approval.mixin
        return matched_approval