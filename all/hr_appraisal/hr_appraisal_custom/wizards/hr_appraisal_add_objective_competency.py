from odoo import _, fields, models
from odoo.exceptions import ValidationError


class HrAppraisalAddObjectiveCompetency(models.TransientModel):
    _name = 'hr.appraisal.add.objective.competency'
    _description = 'HR AppraisalWizard Add Objective and Competency'

    type = fields.Selection(
        selection=[('objective', 'Objective'),
                   ('competency', 'Competency'),
                   ],
        required=True,
        default='objective',
    )
    name = fields.Char(
        required=True,
    )
    weight = fields.Float(
        required=True,
    )
    description = fields.Text(
        required=True,
    )

    def action_create(self):
        """ create objective or competency """
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
        appraisal = self.env[active_model].browse(active_id)
        if self.type == 'objective':
            if not appraisal.can_add_objectives:
                raise ValidationError(_('You are not allowed to add objective'))
            self.env['hr.appraisal.objective'].create({
                'related_appraisal': appraisal.id,
                'title': self.name,
                'weight': self.weight,
                'description': self.description,
            })
        if self.type == 'competency':
            if not appraisal.can_add_competencies:
                raise ValidationError(_('You are not allowed to add competency'))
            self.env['hr.appraisal.competency'].create({
                'related_appraisal_id': appraisal.id,
                'title': self.name,
                'weight': self.weight,
                'description': self.description
            })
