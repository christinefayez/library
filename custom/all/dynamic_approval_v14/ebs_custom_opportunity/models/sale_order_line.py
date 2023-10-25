from odoo import fields, api, models


class SaleOrderLineExt(models.Model):
    _inherit = 'sale.order.line'

    def _default_custom_charge(self):
        """ get default custom charge from company """
        return self.env.company.default_sale_order_custom_charge_percentage

    def _default_moh_charge(self):
        """ get default custom charge from company """
        return self.env.company.default_sale_order_moh_charge_percentage

    visible_customize_fields = fields.Boolean(related="company_id.visible_customize_fields")
    visible_ehs_only_customize_fields = fields.Boolean(related="company_id.visible_ehs_only_customize_fields")
    supplier_id = fields.Many2one('res.partner', string="Supplier", readonly=False)
    supplier_payment_term_id = fields.Many2one(
        'account.payment.term', string='Supplier Payment Terms', check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        compute='_compute_supplier_payment_term_id', readonly=False)

    unit_buying_price = fields.Float(string='Unit Buying Price', digits='Product Price')
    expected_supplier_discount = fields.Float(string='Expected Supplier Discount (%)', digits='Discount', default=0.0)
    unit_buying_after_discount = fields.Float(string='Unit Buying Price after discount', digits='Product Price',
                                              compute='_compute_unit_buying_after_discount', store=True, )

    delivery_within = fields.Selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')],
                                       string="Delivery With In")
    finance_charge = fields.Float(string='Finance Charge (%)', digits='Discount', default=0.0)
    freight_charge_amt = fields.Float(string='Freight Charge Amount', digits='Product Price')
    moh_charge = fields.Float(string='MOH Charge (%)', digits='Discount',
                              default=lambda lead: lead._default_moh_charge())
    custom_charge = fields.Float(string='Custom Charge (%)', digits='Discount',
                                 default=lambda lead: lead._default_custom_charge())
    installation_charge_provision = fields.Float(string='Installation Charge Provision (%)', digits='Discount',
                                                 default=0.0)

    landed_cost_per_unit = fields.Float(string='Landed Cost Per Unit', digits='Product Price',
                                        compute='_compute_landed_cost_per_unit', readonly=False, store=False)
    total_landed_cost = fields.Float(digits='Product Price', compute='_compute_total_landed_cost',
                                     store=True, readonly=False)
    warranty_duration = fields.Selection([('one_year', '1 Year'),
                                          ('two_year', '2 Years'),
                                          ('three_year', '3 Years'),
                                          ('four_year', '4 Years'),
                                          ('five_year', '5 Years'),
                                          ('six_year', '6 Years'),
                                          ('seven_year', '7 Years')])
    is_product_available = fields.Boolean(related="order_id.is_product_available", store=True, )
    margin = fields.Float(string="Gross Margin Amount")
    product_part_number = fields.Char(
        related='product_id.product_tmpl_id.part_number',
    )
    product_origin = fields.Char(compute='_compute_product_origin')

    expect_delivery_date = fields.Date(
        string='Expected Delivery Date', )
    actual_delivery_date = fields.Date(
        string='Actual Delivery Date', )

    @api.depends('freight_charge_amt', 'moh_charge', 'custom_charge', 'finance_charge', 'unit_buying_after_discount',
                 'installation_charge_provision', 'product_uom_qty', 'unit_buying_price', 'expected_supplier_discount')
    def _compute_landed_cost_per_unit(self):
        """
        Compute Landed Cost Per Unit
        :return: {}
        """
        for record in self:
            unit_buying_after_discount = record.unit_buying_price * (
                    1 - (record.expected_supplier_discount / 100))
            moh_charge = unit_buying_after_discount * (record.moh_charge / 100)
            installation_charge_provision = unit_buying_after_discount * (record.installation_charge_provision / 100)
            finance_charge = unit_buying_after_discount * (record.finance_charge / 100)
            custom_charge = unit_buying_after_discount * (record.custom_charge / 100)
            all_charges = unit_buying_after_discount + moh_charge + installation_charge_provision + finance_charge + custom_charge

            record.landed_cost_per_unit = all_charges + record.freight_charge_amt

    @api.depends('landed_cost_per_unit', 'product_uom_qty')
    def _compute_total_landed_cost(self):
        """ update total landed cost """
        for record in self:
            record.total_landed_cost = record.landed_cost_per_unit * record.product_uom_qty

    @api.model_create_multi
    def create(self, vals_list):
        product_obj = self.env['product.product']
        for values in vals_list:
            product = product_obj.browse(values.get('product_id', False))
            if product:
                values.update({'supplier_id': product.supplier_name.id,
                               'supplier_payment_term_id': product.supplier_name.property_payment_term_id.id,
                               'name': product.product_description if product.product_description else values.get(
                                   'name', ''),
                               })
        return super(SaleOrderLineExt, self).create(vals_list)

    @api.model
    def fields_get(self, fields=None, attributes=None):
        fields_to_hide = ['supplier_payment_term_id',
                          'delivery_within']
        if self.env.company.visible_customize_fields != True:
            res = super(SaleOrderLineExt, self).fields_get()
            for field in fields_to_hide:
                if res.get(field):
                    res.get(field)['searchable'] = False
                    res.get(field)['sortable'] = False
                    res.get(field)['invisible'] = True
            return res
        else:
            res = super(SaleOrderLineExt, self).fields_get()
            return res

    @api.depends('product_id')
    def _compute_supplier_payment_term_id(self):
        """ Get Supplier Payment Term from product's supplier name. """
        for rec in self:
            rec.supplier_payment_term_id = False
            if rec.product_id:
                if rec.product_id.supplier_name:
                    rec.supplier_payment_term_id = rec.product_id.supplier_name.property_payment_term_id.id \
                        if rec.product_id.supplier_name.property_payment_term_id else False

    @api.model
    def create(self, vals):
        product_template_id = vals.get('product_template_id')
        product = self.env['product.template'].browse(product_template_id)

        vals['supplier_id'] = product.supplier_name.id if product.supplier_name else \
            product.seller_ids[0].name.id if product.seller_ids else False
        return super(SaleOrderLineExt, self).create(vals)

    def write(self, vals):
        if vals.get('product_template_id'):
            product_template_id = vals.get('product_template_id')
            product = self.env['product.template'].browse(product_template_id)

            vals['supplier_id'] = product.supplier_name.id if product.supplier_name else \
                product.seller_ids[0].name.id if product.seller_ids else False
        return super(SaleOrderLineExt, self).write(vals)

    @api.onchange('product_template_id', 'product_id')
    def get_product_unit_buying_price(self):
        for rec in self:
            if rec.product_template_id.seller_ids:
                rec.supplier_id = rec.product_template_id.supplier_name.id if rec.product_template_id.supplier_name else \
                rec.product_template_id.seller_ids[0].name.id if rec.product_template_id.seller_ids else False
                rec.unit_buying_price = rec.product_template_id.seller_ids.filtered(lambda l: l.name.id == rec.supplier_id.id).price

    @api.depends('unit_buying_price', 'expected_supplier_discount')
    def _compute_unit_buying_after_discount(self):
        """
        compute unit buying after discount
        Unit Buying Price * (1-Expected Supplier Discount (%))
        """
        for record in self:
            record.unit_buying_after_discount = record.unit_buying_price * (
                    1 - (record.expected_supplier_discount / 100))

    @api.depends('price_total', 'total_landed_cost')
    def _compute_margin(self):
        """ override to change computation """
        for line in self:
            line.margin = line.price_total - line.total_landed_cost
            line.margin_percent = line.price_total and line.margin / line.price_total

    def _compute_product_origin(self):
        """ return value of selection """
        for record in self:
            origins = ''
            if record.product_id and record.product_id.origins:
                # if record.product_id.origins == 'us':
                #     origins = 'USA'
                # if record.product_id.origins == 'china':
                #     origins = 'China'
                origins = dict(self.env['product.product'].fields_get(allfields=['origins'])['origins']['selection'])[
                    record.product_id.origins]
                # origins = dict(self.env['product.product']._fields['origins'].selection).get(record.product_id.origins)
            record.product_origin = origins
