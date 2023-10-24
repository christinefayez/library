from odoo import fields, api, _, models
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _parent_name = "parent_opportunity"
    _parent_store = True

    def _default_user_id(self):
        """ allow to override in other module without add field again """
        return self.env.user

    user_id = fields.Many2one(
        default=lambda lead: lead._default_user_id(),
    )
    parent_opportunity = fields.Many2one('crm.lead', copy=False, )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('crm.lead', 'parent_opportunity', 'Child Opportunities')
    child_count = fields.Integer(compute='_compute_child_count')
    expected_revenue = fields.Monetary('Expected Revenue', currency_field='amount_currency', tracking=True,
                                       compute='_compute_total_revenue', store=True)
    opportunity_sequence = fields.Char(string='Opportunity Reference', required=True, copy=False, readonly=False,
                                       index=True, default=lambda self: _('New'))
    customer_status = fields.Selection(related='partner_id.status', string='Customer Status')
    margin_percentage = fields.Float(compute='_compute_gp', string='GP%')
    lead_type_id = fields.Many2one(
        comodel_name='crm.type',
        string='Opportunity Type',
    )
    vertical_id = fields.Many2one('account.analytic.account', string='Vertical', domain=[('is_vertical', '=', True)])

    amount_currency = fields.Many2one('res.currency', string='Amount Currency',
                                      default=lambda self: self.env.company.currency_id)
    total_cost = fields.Monetary('Total Cost', currency_field='company_currency', tracking=True,
                                 compute='_compute_total_cost')
    total_profit_margin = fields.Monetary('Gross Margin', currency_field='company_currency',
                                          compute='_compute_total_profit_margin')
    contact_person_id = fields.Many2one(
        comodel_name='res.partner',
        compute='_compute_contact_person_id',
        store=True,
        readonly=False,
    )
    phone_contact_person = fields.Char(
        compute='_compute_contact_person_info',
        string='Landline Contact Person',
        store=True,
        readonly=False,
    )
    mobile_contact_person = fields.Char(
        compute='_compute_contact_person_info',
        store=True,
        readonly=False,
    )
    email_contact_person = fields.Char(
        compute='_compute_contact_person_info',
        store=True,
        readonly=False,
    )
    
    cost_revenue_ids = fields.One2many('cost.revenue.dist', 'lead_id', string='Cost and Revenue', copy=True)
    opportunity_classification_id = fields.Many2one('opportunity.classification', )
    region = fields.Many2one('res.country.state')

    primary_supplier = fields.Many2one('res.partner', string="Supplier", domain=[('supplier_rank', '>', 0)])
    forecast_category_ids = fields.Many2many(
        comodel_name='crm.lead.forecast.category',
        related='stage_id.forecast_category_ids',
        string='Allowed Forecast Category',
    )
    forecast_category_id = fields.Many2one(
        comodel_name='crm.lead.forecast.category',
        copy=False,
        track_visibility='onchange'
    )
    appear_risk = fields.Boolean(
        related='forecast_category_id.appear_risk',
    )
    levels_of_forecast_category = fields.Selection([('low', 'Low'),
                                                    ('med', 'medium'),
                                                    ('high', 'High')])
    is_won = fields.Boolean(related='stage_id.is_won')
    lost_competitor_id = fields.Many2one(
        'crm.competitor.reason', string='Competitor Name',
        index=True, ondelete='restrict', tracking=True)

    is_competitor_reason = fields.Boolean(related='lost_reason.is_competitor_reason')
    is_bid_bond_required = fields.Boolean()
    tender_submission_deadline = fields.Date()
    tender_description = fields.Text()
    tender_criteria_percentage = fields.Float()
    is_performance_bond_required = fields.Boolean()
    is_bid_bond_bank_letter_required = fields.Boolean()
    bid_bond_number = fields.Char()
    bid_bond_expr_date = fields.Date(string='Bid Bond Expiry Date')
    performance_bond_expiry_date = fields.Date()
    performance_bond_bank_letter = fields.Many2many('ir.attachment', string='Performance Bond Bank Letter',
                                                    relation='performance_bond_bank_letter_attachment_ids')
    bond_bank_letter_attachment_ids = fields.Many2many('ir.attachment', string='Bid Bond Bank Letter',
                                                       relation='bond_bank_letter_attachment_ids')
    performance_bond_number = fields.Integer()
    activity = fields.Char()
    tender_type = fields.Selection([('risk', 'Risk'),
                                    ('upside', 'Upside')],
                                   default='risk',
                                   readonly=True,
                                   compute='_compute_tender_type',
                                   store=True)
    risk_percentage = fields.Float()
    upside_percentage = fields.Float()
    risk_amount = fields.Float(compute='_compute_risk_amount', store=True)
    risk_gross_margin = fields.Float(compute='_compute_risk_gross_margin', store=True)
    upside_amount = fields.Float(compute='_compute_upside_amount', store=True)
    upside_gross_margin = fields.Float(compute='_compute_upside_gross_margin', store=True)
    status = fields.Selection([('open', 'Open'),
                               ('close', 'Closed'),
                               ('won', 'Won'),
                               ('lost', 'Lost'),
                               ('hold', 'On Hold')], default='open', required=True)
    product_classification = fields.Many2many('product.classification', string='Product Classification')
    is_mwb = fields.Boolean(string='Is MWB')
    opportunity_value = fields.Monetary(compute='_compute_opportunity_value_converted',
                                        currency_field='company_currency')
    bid_rationale = fields.Text()
    pricing_strategy = fields.Text()
    competitor_analysis = fields.Char()
    key_assumptions = fields.Char()
    tender_executive_summary = fields.Text(string='Tender Exccutive Summary & Requirement')
    delivery_model = fields.Selection([('ehs', 'EHS'),
                                       ('contractor', 'Sub-Contractor'),
                                       ('vendor', 'Vendor')], default='ehs')
    risk_assessment = fields.Selection([('financial', 'Financial'),
                                        ('non-financial', 'Non-Financial')], default='financial')

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    visible_customize_fields = fields.Boolean(related='company_id.visible_customize_fields')
    visible_ehs_only_customize_fields = fields.Boolean(related='company_id.visible_ehs_only_customize_fields')
    partner_id = fields.Many2one(string='Customer Name')
    on_hold = fields.Boolean('On Hold')
    contract = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    contract_ref = fields.Char(string='Contract Reference')
    sequence = fields.Char(
        readonly=True)  # does not make anything untill fix drag & drop from kanban if there is activity
    opp_classification_is_tender = fields.Boolean(related='opportunity_classification_id.is_tender')
    date_closed = fields.Datetime(readonly=False)
    is_split = fields.Boolean()
    ond_number = fields.Char('OND Number', copy=False, )
    lpo_number = fields.Char(string='LPO Number', copy=False, )
    # delivery details
    expected_delivery_date = fields.Date()
    expected_invoice_date = fields.Date()
    expected_award_date = fields.Date()
    expected_installation_date = fields.Date()
    # contact info
    partner_contact_owner_id = fields.Many2one(
        comodel_name='res.users',
        string='Contact Owner',
        related='partner_id.user_id',
        store=True,
        readonly=False,
    )
    partner_trade_license_number = fields.Char(
        string='Trade License Number',
        related='partner_id.trade_license_number',
        store=True,
        readonly=False,
    )
    partner_license_expire_date = fields.Date(
        string='Expiry date (License)',
        related='partner_id.expire_date',
        store=True,
        readonly=False,
    )
    phone = fields.Char(
        string='Landline',
    )
    is_has_non_draft_order = fields.Boolean(
        compute='_compute_is_has_non_draft_order'
    )
    is_risk_val = fields.Boolean(compute='_compute_is_risk_val')

    @api.onchange('partner_id')
    def auto_region(self):
        if self.partner_id:
            self.region = self.partner_id.state_id.id

    @api.onchange('forecast_category_id', 'appear_risk', 'risk_percentage', 'upside_percentage')
    def _compute_is_risk_val(self):
        for record in self:
            record.is_risk_val = False
            if record.appear_risk:
                record.is_risk_val = True
            elif record.risk_percentage > 0 or record.upside_percentage > 0:
                record.is_risk_val = True

    @api.model
    def fields_get(self, fields=None, attributes=None):
        res = super(CrmLead, self).fields_get(fields, attributes)
        if not self.env.company.visible_customize_fields:
            fields_to_hide = [
                'primary_supplier', 'parent_opportunity', 'risk_assessment', 'delivery_model',
                'tender_executive_summary', 'key_assumptions', 'competitor_analysis', 'pricing_strategy',
                'bid_rationale', 'opportunity_value', 'is_mwb', 'product_classification', 'status',
                'upside_gross_margin', 'upside_amount', 'risk_gross_margin', 'risk_amount', 'upside_percentage',
                'risk_percentage', 'tender_type', 'activity', 'performance_bond_number', 'is_won',
                'performance_bond_bank_letter', 'bond_bank_letter_attachment_ids', 'performance_bond_expiry_date',
                'bid_bond_expr_date', 'bid_bond_number', 'is_bid_bond_bank_letter_required', 'vertical_id',
                'is_performance_bond_required', 'tender_criteria_percentage', 'tender_description', 'customer_status',
                'tender_submission_deadline', 'is_bid_bond_required', 'is_competitor_reason', 'total_cost',
                'lost_competitor_id', 'levels_of_forecast_category', 'forecast_category_ids', 'forecast_category_id',
                'region', 'is_split', 'ond_number', 'opportunity_classification_id', 'cost_revenue_ids',
                'contact_person_id', 'phone_contact_person', 'mobile_contact_person',
                'email_contact_person', 'lead_type_id', 'partner_contact_owner_id',
                'partner_trade_license_number', 'expected_installation_date',
                'partner_license_expire_date', 'total_profit_margin', 'expected_award_date', 'amount_currency',
                'margin_percentage', 'opportunity_sequence', 'parent_opportunity', 'expected_invoice_date',
                'expected_delivery_date',
            ]
            fields_to_edit = ['expected_revenue']
            for rec in fields_to_edit:
                if res.get(rec):
                    res.get(rec)['readonly'] = False
        else:
            fields_to_hide = [
                'visible_ees_crm_customize_fields'
            ]
        for field in fields_to_hide:
            if res.get(field):
                res.get(field)['searchable'] = False
                res.get(field)['sortable'] = False
                res.get(field)['invisible'] = True

        return res

    def _compute_is_has_non_draft_order(self):
        """ update boolean if lead has related sale order in not draft, sent state """
        for record in self:
            record.is_has_non_draft_order = bool(
                record.order_ids.filtered(lambda order: order.state not in ['draft', 'sent', 'cancel']))

    @api.depends('cost_revenue_ids', 'cost_revenue_ids.profit_margin_percentage')
    def _compute_gp(self):
        for rec in self:
            if rec.expected_revenue:
                rec.margin_percentage = rec.total_profit_margin / rec.expected_revenue * 100
            else:
                rec.margin_percentage = 0

    def action_new_quotation(self):
        action = super(CrmLead, self).action_new_quotation()
        # Set Opportunity status in quotations and sales rep
        action['context']['default_user_id'] = self.user_id.id
        action['context']['default_create_by_id'] = self.env.user.id
        action['context']['default_opportunity_status'] = self.stage_id.id
        action['context']['default_contact_name'] = self.contact_name
        action['context']['default_expected_delivery_date'] = self.expected_delivery_date
        action['context']['default_expected_invoice_date'] = self.expected_invoice_date
        action['context']['default_expected_award_date'] = self.expected_award_date
        action['context']['default_expected_installation_date'] = self.expected_installation_date
        return action

    def action_sale_quotations_new(self):
        if self.customer_status == 'credit':
            return self.action_new_quotation()
        elif self.customer_status == 'hold':
            raise ValidationError(_('You cannot create Quotation for this customer due to exceeding credit limit'))
        elif self.customer_status == 'blocked':
            raise ValidationError(_('You cannot create Quotation for Blocked Customer'))
        else:
            if not self.partner_id:
                return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")
            else:
                return self.action_new_quotation()

    @api.depends('expected_revenue', 'amount_currency')
    def _compute_opportunity_value_converted(self):
        for rec in self:
            rec.opportunity_value = rec.amount_currency.compute(rec.expected_revenue, self.company_currency)

    @api.depends('cost_revenue_ids', 'cost_revenue_ids.expected_cost')
    def _compute_total_cost(self):
        collected_cost = 0.0
        for line in self.cost_revenue_ids:
            collected_cost += line.expected_cost
        self.total_cost = collected_cost

    @api.depends('cost_revenue_ids', 'cost_revenue_ids.expected_revenue')
    def _compute_total_revenue(self):
        for record in self:
            collected_revenue = 0.0
            for line in record.cost_revenue_ids:
                collected_revenue += line.expected_revenue
            record.expected_revenue = collected_revenue

    @api.model
    def create(self, vals):
        domain = [('is_default', '=', True), ('company_id', '=', self.env.company.id)]
        team_ids = vals.get('team_id')
        if team_ids:
            domain += ['|', ('team_id', '=', False), ('team_id', '=', team_ids)]
        else:
            domain += [('team_id', '=', False)]

        stage_obj = self.env['crm.stage'].browse(vals.get('stage_id'))
        if not stage_obj.is_default:
            vals['stage_id'] = self.env['crm.stage'].search(domain, limit=1).id or vals.get('stage_id')

        result = super(CrmLead, self).create(vals)
        if vals.get('opportunity_sequence', _('New')) == _('New'):
            seq_date = None
            result['opportunity_sequence'] = self.env['ir.sequence'].next_by_code('crm.lead', sequence_date=seq_date) or _('New')
        return result

    def write(self, vals):
        """ override to set lost based on stage """
        result = super(CrmLead, self).write(vals)
        if vals.get('vertical_id'):
            for order in self.order_ids:
                if order.state not in ['cancel', 'done']:
                    order.vertical_analytic_account_id = vals.get('vertical_id')

        if vals.get('stage_id'):
            stage = self.env['crm.stage'].browse(vals.get('stage_id'))
            for record in self:
                if record.forecast_category_id:
                    old_forecast_category = record.forecast_category_id.display_name
                    new_forecast_category = False
                    if record.forecast_category_id not in stage.forecast_category_ids:
                        if stage.default_forecast_category_id:
                            new_forecast_category = stage.default_forecast_category_id.display_name
                            record.forecast_category_id = stage.default_forecast_category_id
                        elif stage.forecast_category_ids:
                            new_forecast_category = stage.forecast_category_ids[0].display_name
                            record.forecast_category_id = stage.forecast_category_ids[0]

        if vals.get('lost_competitor_id'):
            lost_competitor = self.env['crm.competitor.reason'].browse(vals.get('lost_competitor_id'))
            if lost_competitor and self.mapped('partner_id'):
                lost_competitor.write({
                    'partner_ids': [(4, partner) for partner in self.mapped('partner_id').ids]
                })
        if 'is_split' in vals:
            for record in self:
                if record.company_id.visible_customize_fields and \
                        record.order_ids.filtered(lambda order: order.state not in ['draft', 'sent']):
                    raise ValidationError(_('You are not allowed to change split, please set quotation to draft first'))
        return result

    @api.depends('expected_revenue', 'risk_percentage')
    def _compute_risk_amount(self):
        for rec in self:
            rec.risk_amount = (rec.expected_revenue * rec.risk_percentage) / 100

    @api.depends('margin_percentage', 'risk_amount')
    def _compute_risk_gross_margin(self):
        for rec in self:
            rec.risk_gross_margin = (rec.risk_amount * rec.margin_percentage) / 100

    @api.depends('expected_revenue', 'upside_percentage')
    def _compute_upside_amount(self):
        for rec in self:
            rec.upside_amount = (rec.expected_revenue * rec.upside_percentage) / 100

    @api.depends('margin_percentage', 'upside_amount')
    def _compute_upside_gross_margin(self):
        for rec in self:
            rec.upside_gross_margin = (rec.upside_amount * rec.margin_percentage) / 100

    @api.depends('cost_revenue_ids', 'cost_revenue_ids.profit_margin_amount')
    def _compute_total_profit_margin(self):
        for rec in self:
            collected_profit_margin = 0.0
            for line in rec.cost_revenue_ids:
                collected_profit_margin += line.profit_margin_amount
            rec.total_profit_margin = collected_profit_margin

    @api.constrains('parent_opportunity')
    def _check_opportunity_recursion(self):
        """ check for recursion"""
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive opportunities.'))
        return True

    @api.constrains('forecast_category_id','upside_percentage','risk_percentage')
    def _check_forecast_category_risk_upside(self):
        if self.forecast_category_id and self.forecast_category_id.appear_risk and self.forecast_category_id.is_upside:
            if self.upside_percentage == 0:
                raise ValidationError(_("Please add upside percentage in Risk tab"))
        if self.forecast_category_id and self.forecast_category_id.appear_risk and not self.forecast_category_id.is_upside:
            if self.risk_percentage == 0:
                raise ValidationError(_("Please add risk percentage in Risk tab"))


    # @api.constrains('bid_bond_bank_letter', 'performance_bond_bank_letter')
    # def _check_performance_bond_bank_letter(self):
    #     """ check for performance_bond_bank_letter"""
    #     for record in self:
    #         if record.bid_bond_bank_letter and not record.performance_bond_bank_letter:
    #             raise ValidationError(_('Please upload "Performance Bond Bank Letter" at "Tender" tab'))

    def _compute_child_count(self):
        """ return number of leads children """
        for record in self:
            record.child_count = len(record.child_ids)

    def action_open_child_leads(self):
        """ open child leads that linked to parent """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pipeline',
            'view_mode': 'kanban,tree,graph,pivot,form,calendar,activity',
            'res_model': 'crm.lead',
            'domain': [('id', '=', self.child_ids.ids)],
            'context': {}
        }

    @api.onchange('opportunity_classification_id')
    def onchange_opportunity_classification_id(self):
        """ reset Bid Bond Required info """
        for record in self:
            record.is_bid_bond_required = False
            record.is_performance_bond_required = False
            record.performance_bond_bank_letter = False
            record.bond_bank_letter_attachment_ids = False
            record.is_bid_bond_bank_letter_required = False

    @api.onchange('is_bid_bond_required')
    def onchange_is_bid_bond_required(self):
        """ reset bid info """
        for record in self:
            record.is_performance_bond_required = False
            record.is_bid_bond_bank_letter_required = False
            record.bid_bond_number = False
            record.bid_bond_expr_date = False
            record.bid_bond_number = False
            record.performance_bond_expiry_date = False
            record.performance_bond_number = False

    @api.onchange('is_performance_bond_required')
    def onchange_is_performance_bond_required(self):
        """ reset bid info """
        for record in self:
            record.performance_bond_expiry_date = False
            record.performance_bond_number = False
            record.performance_bond_bank_letter = False

    @api.onchange('is_bid_bond_bank_letter_required')
    def onchange_is_bid_bond_bank_letter(self):
        """ reset Performance Bond Bank Letter """
        for record in self:
            record.bond_bank_letter_attachment_ids = False

    @api.onchange('partner_id', 'lost_reason')
    def onchange_lost_reason_competitor_id(self):
        """ update competitor domain """
        competitors = self.partner_id.competitor_ids
        self.lost_competitor_id = False
        return {'domain': {'lost_competitor_id': [('id', 'in', competitors.ids)]}}

    @api.constrains('expected_delivery_date', 'expected_award_date', 'expected_invoice_date',
                    'expected_installation_date')
    def _constraint_expected_delivery_date(self):
        """ restrict expected_delivery_date before expected_award_date """
        for record in self:
            if not self.env.context.get('disable_delivery_date_constrain', False):
                if record.expected_delivery_date and record.expected_award_date \
                        and record.expected_delivery_date < record.expected_award_date:
                    raise ValidationError(_("Expected Delivery Date must be after Expected Award Date"))
                if record.expected_delivery_date and record.expected_invoice_date and \
                        record.expected_delivery_date > record.expected_invoice_date:
                    raise ValidationError(_("Expected Invoice Date must be after Expected Delivery Date"))

                if record.expected_delivery_date and record.expected_installation_date and \
                        record.expected_delivery_date > record.expected_installation_date:
                    raise ValidationError(_("Expected Installation Date must be after Expected Delivery Date"))

    @api.onchange('vertical_id', 'is_split', 'user_id')
    def _onchange_vertical_id(self):
        """ update cost_revenue_ids with new line """
        for record in self:
            if record.vertical_id and not record.is_has_non_draft_order:
                if not record.cost_revenue_ids.filtered(lambda line: line.is_added_automatically):
                    record.update({
                        'cost_revenue_ids': [(5, 0), (0, 0, {
                            'account_analytic_tag_id': record.vertical_id.id,
                            'salesperson': record.user_id.id if record.user_id else self.env.user.id,
                            'company_id': record.company_id.id if record.company_id else self.env.company.id,
                            'is_added_automatically': True,
                            'expected_revenue': 1,
                            'expected_cost': 1,
                        })]
                    })
                else:
                    added_line_before = record.cost_revenue_ids.filtered(lambda line: line.is_added_automatically)
                    if added_line_before:
                        record.update({
                            'cost_revenue_ids': [(1, added_line_before.id, {
                                'account_analytic_tag_id': record.vertical_id.id,
                                'salesperson': record.user_id.id if record.user_id else self.env.user.id,
                                'company_id': record.company_id.id if record.company_id else self.env.company.id,
                                'is_added_automatically': True,
                            })]
                        })
            if not record.is_split and not record.is_has_non_draft_order:
                record.update({
                    'cost_revenue_ids': [(2, line_id.id, False) for line_id in
                                         record.cost_revenue_ids.filtered(lambda line: not line.is_added_automatically)]
                })

    @api.depends('forecast_category_id')
    def _compute_tender_type(self):
        """ update based on Forecast Category """
        for record in self:
            tender_type = False
            if record.forecast_category_id:
                tender_type = 'risk'
                if record.forecast_category_id.is_upside:
                    tender_type = 'upside'
            record.tender_type = tender_type

    @api.depends('partner_id')
    def _compute_contact_person_id(self):
        """ compute the new values when partner_id has changed """
        for record in self:
            contact_paerson = record.partner_id.child_ids
            record.contact_person_id = contact_paerson[0] if record.partner_id and contact_paerson else False

    @api.depends('contact_person_id')
    def _compute_contact_person_info(self):
        """
        update contact info
        """
        for record in self:
            record.mobile_contact_person = record.contact_person_id.mobile if record.contact_person_id else False
            record.phone_contact_person = record.contact_person_id.phone if record.contact_person_id else False
            record.email_contact_person = record.contact_person_id.email if record.contact_person_id else False

    def _prepare_contact_name_from_partner(self, partner):
        """ override to get name of contact of first child"""
        contact_id = partner.child_ids[0] if partner and partner.child_ids else False
        return {'contact_name': contact_id.name if contact_id else False}

    @api.depends('partner_id', 'company_id', 'contact_person_id')
    def _compute_function(self):
        """ compute the new values when partner_id has changed """
        super()._compute_function()
        for lead in self:
            if lead.company_id.visible_customize_fields and lead.contact_person_id:
                lead.function = lead.contact_person_id.function

    @api.depends('partner_id', 'company_id', 'contact_person_id')
    def _compute_title(self):
        """ compute the new values when partner_id has changed """
        super()._compute_title()
        for lead in self:
            if lead.company_id.visible_customize_fields and lead.contact_person_id:
                lead.title = lead.contact_person_id.title
