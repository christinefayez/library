from odoo import fields, models


class MajorKeyAccount(models.Model):
    _name = 'key.account'
    _description = 'Key Account'

    name = fields.Char()
    active = fields.Boolean(default=True)
