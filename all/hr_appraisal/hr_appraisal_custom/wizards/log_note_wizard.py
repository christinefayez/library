from odoo import fields, models, api


class LogNoteWizard(models.TransientModel):
    _name = 'log.note.wizard'
    _description = 'Description'

    reason = fields.Text('Reason', required=True)
    related_appraisal = fields.Many2one('hr.appraisal', 'Related Appraisal')

    def log_and_move_backward(self):
        for rec in self:
            # appraisal = self.env['hr.appraisal'].browse(self._context.get('active_ids'))
            if rec.reason:
                rec.related_appraisal.message_post(body=rec.reason)
            rec.related_appraisal.move_previous_stage()

            view = self.env.ref('sh_message.sh_message_wizard')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['message'] = 'Thank you, the form has been submitted to previous stage.'
            return {
                'name': 'Success',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sh.message.wizard',
                'views': [(view.id, 'form')],
                'view_id': view_id,
                'target': 'new',
                'context': context,
            }
