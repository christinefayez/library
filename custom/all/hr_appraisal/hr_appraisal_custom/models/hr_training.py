from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError, UserError


class HrAppraisalTraining(models.Model):
    _name = 'hr.training.status'

    name = fields.Char('Status')




class HrAppraisalTraining(models.Model):
    _name = 'hr.training'



    name = fields.Char('Training Name', required=True)
    status = fields.Many2one('hr.training.status', 'Training Status', required=True)
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    desc = fields.Text('Description')
    institute = fields.Char('Institute')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id)
    related_appraisal = fields.Many2one('hr.appraisal', 'Related Appraisal')

    def write(self, vals):
        if self.user_id.id != self.env.user.id:
            if len(vals) == 1 and not vals.get('related_appraisal'):
                raise UserError('Only training owner can modified!')
            elif len(vals) > 1:
                raise UserError('Only training owner can modified!')
        return super(HrAppraisalTraining, self).write(vals)
