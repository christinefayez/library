from odoo import fields, api, _, models
import re
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # contact_owner = fields.Many2one('res.partner')
    office_address = fields.Char(string='Office Address')
    user_id = fields.Many2one('res.users', string='Contact Owner',
                              help='The internal user in charge of this contact.')
    customer_sequence = fields.Char(string='Customer Reference', copy=False,
                                    default='New')
    collection_agent = fields.Many2one('res.users', string='Collection Agent')
    customer_linkedin = fields.Char(string='LinkedIn Account')
    customer_google = fields.Char(string='Google Account')
    status = fields.Selection(
        [('credit', 'Credit Hold'), ('hold', 'On Hold'), ('active', 'Active'), ('blocked', 'Blocked')],
        default='active', string='Partner Status',
    )
    po_box = fields.Char(string='Po Box')
    invoice_count = fields.Integer("Invoice Number", compute='_invoice_count')
    trade_license_number = fields.Char(string='Trade license number')
    expire_date = fields.Date(string='Expiry date (License)')
    oracle_customer_number = fields.Char(string='Oracle Customer Number')
    credit_limit = fields.Monetary(string='Credit Limit')
    credit_limit_balance = fields.Monetary(string='Credit Limit Balance', compute='_compute_credit_limit_balance',
                                           store=True)
    major_key_account_id = fields.Many2one('key.account', string='Major Key Account')
    customer_code_class = fields.Selection([('gov', 'GOVERNMENT'), ('private', 'PRIVATE'),
                                            ('semi_gov', 'SEMI GOVERNMENT'), ('dealer', 'DEALER'),
                                            ('retailer', 'RETAILER'), ('employees', 'EMPLOYEES'),
                                            ('retail', 'RETAIL'), ('military', 'MILITARY'),
                                            ('general', 'GENERAL'), ('supplier', 'SUPPLIER'),
                                            ('contractors', 'CONTRACTORS'), ('university', 'UNIVERSITY'),
                                            ('related_party', 'RELATED PARTY '),
                                            ('supplier_customer', 'SUPPLIER & CUSTOMER'),
                                            ('owners', 'OWNERS'), ('principal', 'Principal')])
    customer_site_status = fields.Selection([('active', 'Active'),
                                             ('inactive', 'Inactive')], default='active', required=True)
    competitor_ids = fields.Many2many(
        comodel_name='crm.competitor.reason',
        relation='res_partner_competitor_reason_rel',
        column1='partner_id',
        column2='competitor_id',
        string='Competitor(s)',
    )
    vendor_code = fields.Char()
    collection_point_address = fields.Char()
    vat_application = fields.Selection([('yes', 'Yes'),
                                        ('no', 'No')])
    trade_license_attachment_ids = fields.Many2many('ir.attachment', relation='trade_license_attachment',
                                                    string='Trade License Attachment')
    tax_license = fields.Char()
    inco_term = fields.Selection([('ex', 'Ex-Works'),
                                  ('fob', 'FOB'),
                                  ('cnf', 'CNF')])
    supplier_contract_attachment_ids = fields.Many2many('ir.attachment', relation='supplier_contract_attachment',
                                                        string='Supplier Contract')
    supplier_expiry_start_effect = fields.Date(string='Expiry Start Effect')
    visible_customize_fields = fields.Boolean(related='company_id.visible_customize_fields')
    phone = fields.Char(
        string='Landline',
    )
    preferred_number = fields.Char()
    customer_type_id = fields.Many2one(
        comodel_name='res.partner.type',
    )
    vendor_type_id = fields.Many2one(
        comodel_name='res.partner.type',
    )
    appear_license = fields.Boolean(
        compute='_compute_appear_license',
    )
    parent_company_id = fields.Many2one(
        comodel_name='res.partner',
        help='Technical field used to update contact with parent',
    )

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('customer_sequence', operator, name)]
        return self._search(domain + args, limit = limit, access_rights_uid = name_get_uid)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('customer_rank', False) > 0:
                is_company = vals.get('is_company', False)
                if vals.get('customer_sequence', 'New') == 'New' and (is_company == True):
                    vals['customer_sequence'] = self.env['ir.sequence'].next_by_code('res.partner') or 'New'
            if vals.get('parent_company_id'):
                vals['parent_id'] = vals.get('parent_company_id')
            if not vals.get('oracle_customer_number', False) and (vals.get('customer_rank', -1) > 0):
                raise ValidationError('There is no Oracle number, please add one.')
        return super(ResPartner, self).create(vals_list)

    def _invoice_count(self):
        AccountInvoice = self.env['account.move']
        domain = [
            ('move_type', 'in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt'))]
        self.invoice_count = AccountInvoice.search_count(domain)

    @api.depends('total_due', 'credit_limit')
    def _compute_credit_limit_balance(self):
        for partner in self:
            balance = partner.credit_limit - partner.total_due
            if balance <= 0:
                partner.credit_limit_balance = 0
            else:
                partner.credit_limit_balance = balance

    @api.depends('credit_limit_balance')
    def _change_customer_status(self):
        for rec in self:
            if rec.credit_limit_balance < 0:
                rec.status = 'hold'
            elif rec.credit_limit_balance == 0:
                rec.status = 'credit'
            else:
                rec.status = 'active'

    @api.onchange('email')
    def validate_mail(self):
        if self.email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
            if match == None:
                raise ValidationError('Not a valid E-mail')

    def _get_contact_name(self, partner, name):
        res = super()._get_contact_name(partner, name)
        if partner.company_id and partner.company_id.visible_customize_fields:
            return name
        return res

    @api.depends('customer_type_id', 'vendor_type_id')
    def _compute_appear_license(self):
        """ get appear license based on customer or vendor """
        for record in self:
            appear_license = False
            if record.customer_type_id and record.customer_type_id.appear_license:
                appear_license = True
            if record.vendor_type_id and record.vendor_type_id.appear_license:
                appear_license = True
            record.appear_license = appear_license
