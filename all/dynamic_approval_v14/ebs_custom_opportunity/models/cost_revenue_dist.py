from odoo import fields, api, _, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class CostRevenueDist(models.Model):
    _name = 'cost.revenue.dist'
    _description = 'Cost Revenue Distribution'

    account_analytic_tag_id = fields.Many2one('account.analytic.account', required=True, copy=True)
    expected_revenue = fields.Monetary(required=True, default=1, currency_field='amount_currency')
    expected_cost = fields.Monetary(required=True, default=1, currency_field='amount_currency')
    profit_margin_amount = fields.Monetary(compute='_compute_profit_amount', default=1,
                                           currency_field='amount_currency')
    profit_margin_percentage = fields.Float(compute='_compute_profit_margin', default=1)
    salesperson = fields.Many2one('res.users', domain="[('share','=',False)]", required=False)
    lead_id = fields.Many2one('crm.lead', copy=True)
    amount_currency = fields.Many2one(related='lead_id.amount_currency')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    is_added_automatically = fields.Boolean()

    @api.depends('expected_revenue', 'expected_cost')
    def _compute_profit_amount(self):
        for rec in self:
            profit_margin_amount = 0
            if rec.expected_revenue != 0:
                profit_margin_amount = rec.expected_revenue - rec.expected_cost
            rec.profit_margin_amount = profit_margin_amount

    @api.depends('expected_revenue', 'expected_cost')
    def _compute_profit_margin(self):
        for rec in self:
            profit_margin_percentage = 0
            if rec.expected_revenue != 0:
                profit_margin_percentage = (rec.profit_margin_amount / rec.expected_revenue) * 100
            rec.profit_margin_percentage = profit_margin_percentage

    @api.model
    def create(self, vals):
        rec = super(CostRevenueDist, self).create(vals)
        if 'salesperson' in vals and 'lead_id' in vals:
            partner = self.env['res.users'].browse(vals.get('salesperson')).partner_id
            if partner != self.env.user.partner_id:
                self.message_subscribe_salesperson(partner_ids=[partner.id], lead_id=vals.get('lead_id'))
        return rec

    def write(self, vals):
        old_salespersons = self.mapped('salesperson')
        rec = super(CostRevenueDist, self).write(vals)
        if 'salesperson' in vals:
            self.message_unsubscribe_salesperson(partner_ids=old_salespersons.mapped('partner_id').ids)
            partner = self.env['res.users'].browse(vals.get('salesperson')).partner_id
            if partner != self.env.user.partner_id:
                self.message_subscribe_salesperson(partner_ids=partner.ids)
        return rec

    def unlink(self):
        """ remove follower from lead """
        self.message_unsubscribe_salesperson(self.mapped('salesperson').mapped('partner_id').ids)
        return super(CostRevenueDist, self).unlink()

    def message_subscribe_salesperson(self, partner_ids=False, lead_id=False):
        """ add new user in lead as follower """
        if partner_ids and lead_id:
            follower_wizard = self.env['mail.wizard.invite']. \
                with_context(default_res_model='crm.lead', default_res_id=lead_id).create({
                'partner_ids': [(6, 0, partner_ids)],
                'send_mail': True,
                })
            follower_wizard.add_followers()
        else:
            for record in self:
                if record.lead_id:
                    follower_wizard = self.env['mail.wizard.invite']. \
                        with_context(default_res_model='crm.lead', default_res_id=record.lead_id).create({
                        'partner_ids': [(6, 0, partner_ids)],
                        'send_mail': True,
                        })
                    follower_wizard.add_followers()

    def message_unsubscribe_salesperson(self, partner_ids=False):
        """ remove user from lead """
        for record in self:
            if record.lead_id:
                if partner_ids:
                    record.lead_id.message_unsubscribe(partner_ids=partner_ids)
                    if record.lead_id.user_id.partner_id.id in partner_ids:
                        record.lead_id.message_subscribe(record.lead_id.user_id.ids)

    @api.constrains('lead_id', 'lead_id.is_split')
    def _constrain_split_lead(self):
        """ restrict add new line if lead is_split = False """
        for record in self:
            if record.lead_id and not record.lead_id.is_split and not record.is_added_automatically:
                raise ValidationError(_("You cannot add extra cost and revenue distribution "
                                        "if you do not activate split"))

    def action_open_form_edit(self):
        """
        open form view in edit mode to allow user to edit record
        this used only when record is readonly
        """
        self.ensure_one()
        return {
            'name': 'Update %s' % self.account_analytic_tag_id.name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'target': 'new',
            'context': {'create': False},
        }

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('account_analytic_tag_id.name', '=ilike', name.split(' ')[0] + '%'),
                      ('salesperson.name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    def name_get(self):
        result = []
        for record in self:
            name = '{} / {}'.format(record.account_analytic_tag_id.name, record.salesperson.name)
            result.append((record.id, name))
        return result
