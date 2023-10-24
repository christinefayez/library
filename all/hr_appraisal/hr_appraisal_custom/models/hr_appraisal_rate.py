from odoo import fields, models


class HrAppraisalRate(models.Model):
    _name = 'hr.appraisal.rate'
    _description = 'HR Appraisal Rate'
    _order = 'name'

    name = fields.Char(
        string='Rate',
        required=True,
    )
    percentage = fields.Float(
        required=True,
    )
    active = fields.Boolean(
        default=True,
    )

