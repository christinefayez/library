from odoo import fields, models


class CrmTag(models.Model):
    _inherit = 'crm.tag'
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
    # handle case need add same name in other company
    _sql_constraints = [
        ('name_uniq', 'unique (name, company_id)', "The name must be unique per company !"),
    ]
