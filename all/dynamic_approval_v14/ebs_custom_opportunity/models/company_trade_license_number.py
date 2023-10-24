from odoo import _, api, fields, models


class CompanyTradingLicenseNumber(models.Model):
    _name = 'company.trade.license.number'

    name = fields.Char()
    company_id = fields.Many2one(
        comodel_name='res.company', required=True, readonly=True,
        default=lambda self: self.env.company)

