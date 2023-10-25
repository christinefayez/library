from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class HrAppraisalScoreRange(models.Model):
    _name = 'hr.appraisal.score.range'
    _description = 'HR Appraisal Score Range'
    _order = 'sequence, id'

    sequence = fields.Integer(
        index=True,
        default=10,
    )
    name = fields.Char(
        required=True,
    )
    percentage_from = fields.Float(
        required=True,
    )
    percentage_to = fields.Float(
        required=True,
    )

    @api.constrains('percentage_from', 'percentage_to')
    def _check_percentage_overlap(self):
        """ restrict add record overlap other record """
        for record in self:
            domain = [
                ('percentage_from', '<', record.percentage_to),
                ('percentage_to', '>', record.percentage_from),
                ('id', '!=', record.id),
            ]
            score_ranges = self.search_count(domain)
            if score_ranges:
                raise ValidationError(_('You can not have 2 score range that overlap percentage.'))
