from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vertical_analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Vertical',
        domain="[('is_vertical','=', True)]",
    )

    # op_partner_id = fields.Many2one(related='opportunity_id.partner_id', store=True, readonly=True,
    #                                 string='Opportunity Customer')
    # primary_supplier = fields.Many2one(related='opportunity_id.primary_supplier', store=True, readonly=True)
    # vertical_id = fields.Many2one(related='opportunity_id.vertical_id', store=True, readonly=True,
    #                               string='Opportunity Vertical')
    # opportunity_classification_id = fields.Many2one(related='opportunity_id.opportunity_classification_id', store=True,
    #                                                 readonly=True)
    # region = fields.Many2one(related='opportunity_id.region', store=True, readonly=True)
    # op_stage_id = fields.Many2one(related='opportunity_id.stage_id', store=True, readonly=True)
    # on_hold = fields.Boolean(related='opportunity_id.on_hold', store=True, readonly=True)
    # is_split = fields.Boolean(related='opportunity_id.is_split', store=True, readonly=True)
    # product_classification = fields.Many2many(
    #     'product.classification',
    #     compute='_compute_opp_product_classification',
    #     store=True, readonly=True)

    # difference_gross_profit = fields.Float(
    #     string='Difference Gross Profit Margin',
    #     compute='_compute_difference_gross_profit_margin',
    #     store=True,
    # )
    # less_gross_profit_margin_percentage = fields.Float(
    #     compute='_compute_difference_gross_profit_margin',
    #     store=True,
    # )

    # @api.depends('vertical_analytic_account_id', 'opportunity_id', 'opportunity_id.margin_percentage',
    #              'opportunity_id.budgeted_gp')
    # def _compute_difference_gross_profit_margin(self):
    #     """ diff gross profit from analytic account and opportunity """
    #     for record in self:
    #         difference = 0
    #         difference_percentage = 0
    #         if record.opportunity_id and record.vertical_analytic_account_id:
    #             if record.margin_percentage != 0:
    #                 difference = \
    #                     (record.opportunity_id.budgeted_gp / record.opportunity_id.margin_percentage) * 100
    #             if (record.opportunity_id.margin_percentage < record.opportunity_id.budgeted_gp) and (
    #                     record.opportunity_id.budgeted_gp != 0):
    #                 difference_percentage = (difference / record.opportunity_id.budgeted_gp) * 100
    #         record.difference_gross_profit = difference
    #         record.less_gross_profit_margin_percentage = difference_percentage

    # @api.onchange('opportunity_id')
    # def _onchange_opportunity(self):
    #     """ update vertical based on changes in salesperson """
    #     for record in self:
    #         vertical_analytic_account_id = record.vertical_analytic_account_id
    #         if record.opportunity_id and record.opportunity_id.get_vertical():
    #             vertical_analytic_account_id = record.opportunity_id.get_vertical()
    #         record.vertical_analytic_account_id = \
    #             vertical_analytic_account_id.id if vertical_analytic_account_id else False
    #
    # @api.depends('opportunity_id', )
    # def _compute_opp_product_classification(self):
    #     for order in self:
    #         order.product_classification = self.opportunity_id.product_classification.ids
