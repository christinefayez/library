from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class HrAppraisalRate(models.Model):
    _inherit = 'hr.appraisal.rate'

    number = fields.Float(
        string='Number',
        required=True,
    )

    @api.model
    def create(self, vals):
        res = super(HrAppraisalRate, self).create(vals)
        if res.number == 0.00 and res.percentage == 0.00:
            raise UserError('Please set the Number or the Percentage.')
        return res
