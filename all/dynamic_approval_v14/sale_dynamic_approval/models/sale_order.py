""" inherit sale.order """
from datetime import datetime
import logging
from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _name = 'sale.order.approval.history'

    user_id = fields.Many2one('res.users', string='User')

    status = fields.Selection(
        [('request_approval', 'Request Approval'), ('approved', 'Approved'),
         ('reject', 'Reject'),
         ('recall', 'Recall')
         ],
        string="state", default='no')
    action_date = fields.Date(string='Date')
    sale_id = fields.Many2one('sale.order', string='Sales Order')
    sale_order_status = fields.Selection(selection=lambda self: self.env['sale.order']._fields['state'].selection,
                                         string="Sale Order Status")


_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'dynamic.approval.mixin']
    _not_matched_action_xml_id = 'sale_dynamic_approval.confirm_sale_order_wizard_action'

    # ToDo: remove readonly from field state. it used to allow import historical data only
    state = fields.Selection(
        selection_add=[('under_approval', 'Under Approval'), ('approved', 'Approved'), ('sale',)],
        readonly=False,
    )
    order_line = fields.One2many(
        states={'cancel': [('readonly', True)], 'done': [('readonly', True)], 'under_approval': [('readonly', True)],
                'approved': [('readonly', True)], },
    )
    # appear_recall_button = fields.Boolean(
    #     compute='_compute_appear_recall_button',
    # )
    approval_history_ids = fields.One2many('sale.order.approval.history', 'sale_id')

    partner_id = fields.Many2one(
        string='Customer Name',
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'under_approval': [('readonly', False)],
                'approved': [('readonly', False)]}, )

    def action_draft(self):
        res = super(SaleOrder, self).action_draft()
        self.remove_approval_requests(all=True)
        return res

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        self.mapped('dynamic_approve_request_ids').write({
            'status': 'rejected',
            'approve_date': False,
            'approved_by': False,
        })
        return res

    def action_confirm(self):
        """ override to restrict user to confirm if there is workflow """
        res = super(SaleOrder, self).action_confirm()
        if self.mapped('dynamic_approve_request_ids') and \
                self.mapped('dynamic_approve_request_ids').filtered(lambda request: request.status != 'approved'):
            raise UserError(
                _('You can not confirm order, There are pending approval.'))
        for record in self:
            activity = record._get_user_approval_activities()
            if activity:
                activity.action_feedback()
        return res

    # def action_dynamic_approval_request(self):
    #     """" override to restrict request approval """
    #     res = super(SaleOrder, self).action_dynamic_approval_request()
    #     for record in self:
    #         if not record.order_line:
    #             raise UserError(_('Please add product in order to request approval'))
    #         if not record.amount_total:
    #             raise UserError(_('Please add selling price in order lines'))
    #     return res

    # def _compute_appear_recall_button(self):
    #     """ appear recall button based on user """
    #     current_user = self.env.user
    #     for record in self:
    #         appear_recall_button = False
    #         if record.user_id and record.user_id == current_user:
    #             appear_recall_button = True
    #         if record.create_by_id and record.create_by_id == current_user:
    #             appear_recall_button = True
    #         record.appear_recall_button = appear_recall_button

    # Override the next 3 functions to FIX sale_id & sale_order_status fields that addedd in base mixin module ---> Yassmin 6Jan22
    def _action_reset_original_state(self, reason='', reset_type='reject'):
        """
        set record to original state and notify user or approvers
        :param reason: reason for reset
        :param reset_type: reject / recall
        :param notify_approver: notify users who approved before
        """
        for record in self:
            pending_approve_requests = \
                record.dynamic_approve_request_ids.filtered(lambda approver: approver.status == 'pending')
            approved_requests = \
                record.dynamic_approve_request_ids.filtered(lambda approver: approver.status == 'approved' and
                                                                             approver.dynamic_approval_id == record.dynamic_approval_id)
            activity = record._get_user_approval_activities()
            if reset_type == 'reject':
                if activity:
                    activity.action_feedback(feedback=_('Rejected, Reason ') + reason)
                else:
                    record.message_post(body=_('Rejected, Reason ') + reason)
                #  update approval request status
                pending_approve_requests.write({
                    'status': 'rejected',
                    'approve_date': False,
                    'approved_by': False,
                    'reject_reason': reason,
                    'reject_date': datetime.now(),
                })
                if pending_approve_requests.status == 'rejected':
                    val = {'user_id': self.env.uid,
                           'status': 'reject',
                           'action_date': datetime.now(),
                           'sale_id': self.id,
                           'sale_order_status': self.state,
                           }
                    self.approval_history_ids.create(val)

                # create activity for user based on approval configuration
                if record.dynamic_approval_id and record.dynamic_approval_id.default_notify_user_field_rejection_id:
                    activity_user = \
                        getattr(record, record.dynamic_approval_id.default_notify_user_field_rejection_id.name)
                    if activity_user != self.env.user:
                        record._create_reject_activity(activity_user)
                # send email template to users that need to know if record is rejected
                if record.dynamic_approval_id and record.dynamic_approval_id.notify_user_field_rejection_ids and \
                        record.dynamic_approval_id.rejection_email_template_id:
                    users_to_send = self.env['res.users']
                    for user_field in record.dynamic_approval_id.notify_user_field_rejection_ids:
                        users_to_send |= getattr(record, user_field.name)
                    # not send email for same user twice
                    users_to_send = self.env['res.users'].browse(users_to_send.mapped('id'))
                    for user in users_to_send:
                        if user != self.env.user and user.email:
                            email_values = {'email_to': user.email, 'email_from': self.env.user.email}
                            record.dynamic_approval_id.rejection_email_template_id.with_context(
                                name_to=user.name, user_lang=user.lang, reject_reason=reason).send_mail(
                                record.id, email_values=email_values, force_send=True)
                # send email template to users who approved to record before about rejection
                if record.dynamic_approval_id and record.dynamic_approval_id.need_notify_rejection_approved_user and \
                        record.dynamic_approval_id.rejection_email_template_id:
                    approved_users = approved_requests.mapped('approved_by')
                    for approved_user in approved_users:
                        if approved_user != self.env.user and approved_user.email:
                            email_values = {'email_to': approved_user.email, 'email_from': self.env.user.email}
                            record.dynamic_approval_id.rejection_email_template_id.with_context(
                                name_to=approved_user.name, user_lang=user.lang, reject_reason=reason). \
                                send_mail(record.id, email_values=email_values, force_send=True)
                # run server action
                if record.dynamic_approval_id and record.dynamic_approval_id.rejection_server_action_id:
                    action = self.dynamic_approval_id.rejection_server_action_id.with_context(
                        active_model=self._name,
                        active_ids=[record.id],
                        active_id=record.id,
                    )
                    try:
                        action.run()
                    except Exception as e:
                        _logger.warning('Approval Rejection: record <%s> model <%s> encountered server action issue %s',
                                        record.id, record._name, str(e), exc_info=True)

            if reset_type == 'recall':
                if activity:
                    activity.unlink()
                pending_approve_requests.write({'status': 'recall'})
                approved_requests.write({'status': 'recall'})
                record.message_post(body=_('Recalled, Reason ') + reason)
                if pending_approve_requests.status == 'recall':
                    val = {'user_id': self.env.uid,
                           'status': 'recall',
                           'action_date': datetime.now(),
                           'sale_id': self.id,
                           'sale_order_status': self.state,
                           }
                    self.approval_history_ids.create(val)

                # create activity for user based on approval configuration
                if record.dynamic_approval_id and record.dynamic_approval_id.default_notify_user_field_recall_id:
                    activity_user = getattr(record, record.dynamic_approval_id.default_notify_user_field_recall_id.name)
                    if activity_user != self.env.user:
                        record._create_recall_activity(activity_user)
                # send email template to users that need to know if record is recalled
                if record.dynamic_approval_id and record.dynamic_approval_id.notify_user_field_recall_ids and \
                        record.dynamic_approval_id.recall_email_template_id:
                    users_to_send = self.env['res.users']
                    for user_field in record.dynamic_approval_id.notify_user_field_recall_ids:
                        users_to_send |= getattr(record, user_field.name)
                    # not send email for same user twice
                    users_to_send = self.env['res.users'].browse(users_to_send.mapped('id'))
                    for user in users_to_send:
                        if user != self.env.user and user.email:
                            email_values = {'email_to': user.email, 'email_from': self.env.user.email}
                            record.dynamic_approval_id.recall_email_template_id.with_context(
                                name_to=user.name, user_lang=user.lang, recall_reason=reason).send_mail(
                                record.id, email_values=email_values, force_send=True)
                # send email template to users who approved to record before about recall
                if record.dynamic_approval_id and record.dynamic_approval_id.need_notify_recall_approved_user and \
                        record.dynamic_approval_id.recall_email_template_id:
                    approved_users = approved_requests.mapped('approved_by')
                    for approved_user in approved_users:
                        if approved_user != self.env.user and approved_user.email:
                            email_values = {'email_to': approved_user.email, 'email_from': self.env.user.email}
                            record.dynamic_approval_id.recall_email_template_id.with_context(
                                name_to=approved_user.name, user_lang=user.lang, recall_reason=reason). \
                                send_mail(record.id, email_values=email_values, force_send=True)

                # run server action
                if record.dynamic_approval_id and record.dynamic_approval_id.recall_server_action_id:
                    action = self.dynamic_approval_id.recall_server_action_id.with_context(
                        active_model=self._name,
                        active_ids=[record.id],
                        active_id=record.id,
                    )
                    try:
                        action.run()
                    except Exception as e:
                        _logger.warning(
                            'Approval Recall: record <%s> model <%s> encountered server action issue %s',
                            record.id, record._name, str(e), exc_info=True)

            record.write({
                record._state_field: record.state_from_name or record.dynamic_approval_id.state_from
            })

    # actions workflow
    def action_dynamic_approval_request(self):
        """
        search for advanced approvals that match current record and add approvals
        if record does not match then appear wizard to confirm order without approval
        """
        for record in self:
            if not record.order_line:
                raise UserError(_('Please add product in order to request approval'))
            if not record.amount_total:
                raise UserError(_('Please add selling price in order lines'))
            company = getattr(record, self._company_field)
            # if getattr(record, record._state_field) in self.dynamic_approval_id.state_from:

            if record.dynamic_approve_request_ids:
                if record.state == 'draft':
                    record.remove_approval_requests(all=True)
                else:
                    record.remove_approval_requests(all=False)
                activity = record._get_user_approval_activities()
                if activity:
                    activity.action_feedback()
            matched_approval = self.env['dynamic.approval'].action_set_approver(model=self._name, res=record,
                                                                                company=company)

            if matched_approval:
                record.write({
                    self._state_field: matched_approval.state_under_approval,
                    'approve_requester_id': self.env.user.id,
                    'dynamic_approval_id': matched_approval.id,
                    'state_from_name': getattr(record, record._state_field),
                })
                if record.dynamic_approve_request_ids:
                    next_waiting_approval = \
                    record.dynamic_approve_request_ids.filtered(lambda r: r.status != 'approved').sorted(
                        lambda x: (x.sequence, x.id))[0]
                    next_waiting_approval.status = 'pending'
                    if next_waiting_approval.get_approve_user():
                        user = next_waiting_approval.get_approve_user()[0]
                        record._notify_next_approval_request(matched_approval, user)
                    if next_waiting_approval and self.approve_requester_id:
                        val = {'user_id': self.env.uid,
                               'status': 'request_approval',
                               'action_date': datetime.now(),
                               'sale_id': self.id,
                               'sale_order_status': self.state,
                               }
                        self.approval_history_ids.create(val)
            else:
                if self._not_matched_action_xml_id:
                    action_id = self._not_matched_action_xml_id
                    action = self.env["ir.actions.actions"]._for_xml_id(action_id)
                    return action
            # else:
            #     raise UserError(_('This status is not allowed to request approval'))

    def action_under_approval(self, note=''):
        """
        change status of approval request to approved and trigger next approval level or change status to be approved
        :param note: approval notes that user will add and store it in approval requests and add it as activity feedback
        """
        for record in self:
            user = self.env.user
            if self.env.user.has_group('base_dynamic_approval.dynamic_approval_user_group'):
                pending_approval = record.dynamic_approve_request_ids.filtered(
                    lambda request_approve: request_approve.status == 'pending')
                if pending_approval:
                    allowed_users = pending_approval.get_approve_user()
                    if allowed_users:
                        user = allowed_users[0]
            pending_approve_request_ids = record._get_pending_approvals(user)
            pending_approve_requests = self.env['dynamic.approval.request'].browse(pending_approve_request_ids)
            if pending_approve_requests:
                pending_approve_requests.write({
                    'approve_date': datetime.now(),
                    'approved_by': self.env.user.id,
                    'status': 'approved',
                })
                pending_approve_requests[-1].write({'approve_note': note})

            activity = record._get_user_approval_activities()
            if activity:
                activity.action_feedback(feedback=note)
            else:
                msg = _('Approved')
                if note:
                    msg += ' ' + note
                record.message_post(body=msg)
            if record.dynamic_approval_id.to_approve_server_action_id:
                action = record.dynamic_approval_id.to_approve_server_action_id.with_context(
                    active_model=self._name,
                    active_ids=[record.id],
                    active_id=record.id,
                )
                try:
                    action.run()
                except Exception as e:
                    _logger.warning(
                        'Approval Recall: record <%s> model <%s> encountered server action issue %s',
                        record.id, record._name, str(e), exc_info=True)
            new_approve_requests = \
                record.dynamic_approve_request_ids.filtered(lambda approver: approver.status == 'new')
            if new_approve_requests:
                next_waiting_approval = new_approve_requests.sorted(lambda x: (x.sequence, x.id))[0]
                next_waiting_approval.status = 'pending'
                if next_waiting_approval.get_approve_user():
                    user = next_waiting_approval.get_approve_user()[0]
                    record._notify_next_approval_request(record.dynamic_approval_id, user)
            else:
                record._action_final_approve()
            if pending_approve_requests:
                for rec in pending_approve_requests:
                    if rec.status == 'approved':
                        val = {'user_id': self.env.uid,
                               'status': 'approved',
                               'action_date': datetime.now(),
                               'sale_id': self.id,
                               'sale_order_status': self.state,
                               }
                        self.approval_history_ids.create(val)
