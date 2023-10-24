import datetime

from odoo import fields, api, _, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    opportunity_id = fields.Many2one(copy=False)

    risk_amount = fields.Float(sting="Risk Amount", related='opportunity_id.risk_amount', store=True)
    risk_gross_margin = fields.Float(sting="Risk Gross Margin", related='opportunity_id.risk_gross_margin', store=True)
    upside_amount = fields.Float(sting="Upside Amount", related='opportunity_id.upside_amount', store=True)
    upside_gross_margin = fields.Float(sting="Upside Gross Margin", related='opportunity_id.upside_gross_margin', store=True)
    lost = fields.Boolean(sting="Lost", compute='_compute_lost', store=True)

    def _compute_lost(self):
        for record in self:
            record.lost = False
            if record.opportunity_id.active:
                record.lost = False
            else:
                record.lost = True

    user_id = fields.Many2one(related='opportunity_id.user_id', store=True)
    allowed_create_by_ids = fields.Many2many(comodel_name='res.users', compute='_compute_allowed_create_by')
    create_by_id = fields.Many2one('res.users', string="Quote Creator", default=lambda self: self.env.user)
    opportunity_status = fields.Many2one('crm.stage', string="Opportunity Stage", related='opportunity_id.stage_id')
    opportunity_amount = fields.Monetary('Opportunity Amount', related='opportunity_id.expected_revenue')
    opportunity_sequence = fields.Char('Opportunity Number', related='opportunity_id.opportunity_sequence')
    opportunity_value = fields.Monetary('Opportunity Value', related='opportunity_id.opportunity_value')
    margin_percentage = fields.Float('GP%', related='opportunity_id.margin_percentage')
    is_installation_required = fields.Selection(
        [('yes', 'Yes'),
         ('no', 'No'),
         ],
        string="Installation is Required", default='no')
    ond_number = fields.Char('OND Number', related='opportunity_id.ond_number', readonly=False, store=True)
    type = fields.Many2one('quotation.type', string="Quote type")
    quote_expiry_date = fields.Date(string='Quote expiry')
    payment_type = fields.Selection([('credit', 'Credit'),
                                     ('pdc', 'PDC'),
                                     ('lC', 'LC'),
                                     ('cash_cheque', 'Cash/Cheque'),
                                     ('bank_guarantee', 'Bank Guarantee'),
                                     ('payment_in_advance', 'Payment In Advance'),
                                     ('hospital_policy', 'as per hospital policy'),
                                     ], string="Payment Type")
    # TSG Share
    tsg_share = fields.Boolean("TSG Share", default=False)
    tsg_value = fields.Char("TSG Value")
    tsg_user = fields.Many2one('res.users', string="TSG User")

    estimated_gross_margin_profit_amt = fields.Float(
        string='Estimated Gross Margin Profit Amount', compute="_compute_estimated_gross_margin_profit",
        digits='Product Price', store=True, )

    estimated_gross_margin_percentage = fields.Float(
        string='Estimated Gross Margin(%)', compute="_compute_estimated_gross_margin_profit",
        digits='Estimate Gross', store=True,
    )

    visible_customize_fields = fields.Boolean(related="company_id.visible_customize_fields")
    visible_ehs_only_customize_fields = fields.Boolean(
        related="company_id.visible_ehs_only_customize_fields",
        store=True,
    )
    client_order_ref = fields.Char(string='Customer Reference')
    lpo_number = fields.Char(string='LPO Number', related='opportunity_id.lpo_number', readonly=False, store=True)
    lpo_date = fields.Date(string='LPO Date', )
    expected_delivery_date = fields.Date(related='opportunity_id.expected_delivery_date', store=True)
    expected_invoice_date = fields.Date(related='opportunity_id.expected_invoice_date', store=True)
    expected_award_date = fields.Date(related='opportunity_id.expected_award_date', store=True)
    expected_installation_date = fields.Date(related='opportunity_id.expected_installation_date', store=True)
    contact_person_id = fields.Many2one(related='opportunity_id.contact_person_id', store=True)
    function_contact_person = fields.Char(related='opportunity_id.function', store=True, string='Contact Person Title')
    phone_contact_person = fields.Char(related='opportunity_id.phone_contact_person', store=True, string='Contact Person Phone')
    mobile_contact_person = fields.Char(related='opportunity_id.function', store=True, string='Contact Person Mobile')
    email_contact_person = fields.Char(related='opportunity_id.function', store=True, string='Contact Person Email')
    is_product_available = fields.Boolean(
        string='Items Available in Stock',
    )
    landed_cost_id = fields.Many2one(
        comodel_name='stock.landed.cost',
    )
    forecast_category = fields.Many2one(related='opportunity_id.forecast_category_id', store=True)
    tag_ids = fields.Many2many(related='opportunity_id.tag_ids')
    lead_type_id = fields.Many2one(related='opportunity_id.lead_type_id')
    lead_total_cost = fields.Monetary(
        string='Total Opportunity Cost',
        currency_field='currency_id',
        related='opportunity_id.total_cost',
        readonly=True,
    )
    lpo_attachment = fields.Binary(
        string='LPO Attachment',
        compute='_compute_lpo_attachment',
        inverse='_inverse_lpo_attachment',
    )
    lpo_attachment_filename = fields.Char(string='LPO Attachment Filename')
    total_landed_cost_amount = fields.Float(digits='Product Price', compute='_compute_total_landed_cost_amount',
                                            store=True)
    trade_license_number = fields.Many2one(
        'company.trade.license.number',
        domain="[('company_id', '=', company_id)]")
    approval_history_ids = fields.One2many('sale.order.approval.history', 'sale_id')
    line_no_vertical = fields.Boolean(compute='_compute_line_no_vertical')

    @api.depends('amount_total', 'order_line.total_landed_cost')
    def _compute_estimated_gross_margin_profit(self):
        """
        Compute Estimated Gross Margin Profit Amount and Gross Margin Profit Percentage
        :return: {}
        """
        for order in self:
            if order.amount_total:
                est_gross_margin = float(order.amount_total - sum(order.order_line.mapped('total_landed_cost')))
                order.estimated_gross_margin_profit_amt = est_gross_margin
                order.estimated_gross_margin_percentage = (est_gross_margin / order.amount_total)
            else:
                order.estimated_gross_margin_profit_amt = 0.0
                order.estimated_gross_margin_percentage = 0.0

    @api.onchange('quote_expiry_date')
    def _onchange_validity(self):
        """
        Set Expiration Date based on quote_expiry_date
        :return: {}
        """
        for order in self:
            validity_date = False
            if order.quote_expiry_date and order.date_order:
                validity_date = order.quote_expiry_date
            order.validity_date = validity_date

    @api.onchange('opportunity_id')
    def _onchange_opportunity_id(self):
        """
        Set Opportunity type, status, sales rep based on opportunity
        :return: {}
        """
        for record in self:
            if record.opportunity_id:
                lead = record.opportunity_id
                record.update({
                    'tag_ids': [(6, 0, lead.tag_ids.ids)],
                    'opportunity_status': lead.stage_id.id,
                    'user_id': lead.user_id.id,
                    'origin': lead.name,
                })

    def action_confirm(self):
        for rec in self:
            if rec.opportunity_id and rec.opportunity_id.customer_status in ['credit', 'blocked']:
                raise ValidationError(_('You cannot create Quotation for this customer '
                                        'due to exceeding credit limit'))
            elif rec.opportunity_id and rec.opportunity_id.customer_status == 'hold':
                if not self.payment_term_id.is_advanced_payment:
                    raise ValidationError(
                        _('The customer you are trying to create quotation is on hold please change '
                          'the payment term to an immediate to proceed '))
            if not self.env.context.get('disable_required_quotation', False):
                if rec.partner_id and rec.partner_id.customer_type_id.appear_license:
                    restrict_confirm = False
                    # if not rec.partner_id.tax_license:
                    #     restrict_confirm = True
                    # if not rec.partner_id.supplier_contract_attachment_ids:
                    #     restrict_confirm = True
                    if not rec.partner_id.trade_license_number:
                        restrict_confirm = True
                    # if not rec.partner_id.expire_date:
                    #     restrict_confirm = True
                    # if not rec.partner_id.trade_license_attachment_ids:
                    #     restrict_confirm = True
                    if restrict_confirm:
                        raise ValidationError(_('Please fill license information for customer'))
        return super(SaleOrder, self.with_context(
            {k: v for k, v in self._context.items() if k != 'default_tag_ids'})).action_confirm()

    @api.onchange('is_installation_required')
    def _onchange_is_installation_required(self):
        """ set zero for sale.order.lin.installation_charge_provision """
        for record in self:
            if record.is_installation_required == 'no':
                for line in record.order_line:
                    line.installation_charge_provision = 0

    @api.onchange('is_product_available')
    def _onchange_is_product_available(self):
        """ reset landed cost and supplier payment term in lines """
        for record in self:
            record.landed_cost_id = False

    @api.depends('order_line', 'order_line.total_landed_cost')
    def _compute_total_landed_cost_amount(self):
        """ sum total_landed_cost in lines """
        for record in self:
            record.total_landed_cost_amount = sum(record.order_line.mapped('total_landed_cost'))

    @api.depends('order_line.margin', 'amount_total')
    def _compute_margin(self):
        """ override to compute based on amount_total"""
        if not all(self._ids):
            for order in self:
                order.margin = sum(order.order_line.mapped('margin'))
                order.margin_percent = order.amount_total and order.margin / order.amount_total
        else:
            self.env["sale.order.line"].flush(['margin'])
            # On batch records recomputation (e.g. at install), compute the margins
            # with a single read_group query for better performance.
            # This isn't done in an onchange environment because (part of) the data
            # may not be stored in database (new records or unsaved modifications).
            grouped_order_lines_data = self.env['sale.order.line'].read_group(
                [
                    ('order_id', 'in', self.ids),
                ], ['margin', 'order_id'], ['order_id'])
            mapped_data = {m['order_id'][0]: m['margin'] for m in grouped_order_lines_data}
            for order in self:
                order.margin = mapped_data.get(order.id, 0.0)
                order.margin_percent = order.amount_total and order.margin / order.amount_total

    def _compute_lpo_attachment(self):
        """ get binary from attachment """
        for record in self:
            attachment = self.env['ir.attachment'].sudo().search([('lpo_number_sale_order_id', '=', record.id)])
            record.lpo_attachment = attachment.datas

    def _inverse_lpo_attachment(self):
        """ create or update attachment """
        for record in self:
            if record.lpo_attachment:
                attachment = self.env['ir.attachment'].sudo().search([('lpo_number_sale_order_id', '=', record.id)])
                file_name = record.lpo_attachment_filename or 'LPO for %s' % record.name
                if attachment:
                    attachment.write({
                        'datas': record.lpo_attachment,
                        'name': file_name,
                    })
                else:
                    self.env['ir.attachment'].sudo().create({
                        'name': file_name,
                        'type': 'binary',
                        'datas': record.lpo_attachment,
                        'res_model': record._name,
                        'res_id': record.id,
                        'lpo_number_sale_order_id': record.id,
                    })

    def _compute_allowed_create_by(self):
        """ get users from current company only """
        company = self.env.company
        allowed_users = self.env['res.users']
        all_users = self.env['res.users'].search([('share', '=', False)])
        for user in all_users:
            if company in user.company_ids:
                allowed_users |= user
        for record in self:
            record.allowed_create_by_ids = allowed_users

    def action_import_excel_sheet(self):
        return {
            'name': _('Import Sale Order Line'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'import.sale.order.data',
            'view_id': self.env.ref('ebs_custom_opportunity.import_sale_order_wizard_form').id,
            'target': 'new',
            'context': {
                'default_sale_id': self.id
            }
        }

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        this is a modification to an existing method
        method path:
            "odoo/addons/sale/models/sale.py"
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)

        addr = self.partner_id.address_get(['delivery', 'invoice'])
        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
        }
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
            user_id = user_id or self.env.context.get('default_user_id', self.env.uid)

        if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms') and self.env.company.invoice_terms:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
        if not self.env.context.get('not_self_saleperson') or not self.team_id:
            values['team_id'] = self.env['crm.team'].with_context(
                default_team_id=self.partner_id.team_id.id
            )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=user_id)
        self.update(values)

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for order in self:
            opp = order.opportunity_id
            if opp and (opp.partner_id.id != order.partner_id.id):
                opp.write({'partner_id': order.partner_id.id})
        return res

    def _compute_line_no_vertical(self):
        for order in self:
            order.line_no_vertical = False
            for line in order.order_line:
                if not line.cost_revenue_dist_id and line.display_type not in ['line_section', 'line_note']:
                    order.line_no_vertical = True
                else:
                    order.line_no_vertical = False