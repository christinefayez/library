from odoo import fields, _, models


class CrmCompetitorReason(models.Model):
    _name = "crm.competitor.reason"
    _description = 'Opp. Lost for another competitor'

    name = fields.Char('Description', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='res_partner_competitor_reason_rel',
        column1='competitor_id',
        column2='partner_id',
        string='Partner(s)',
    )
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)

    def action_lost_leads(self):
        return {
            'name': _('Leads'),
            'view_mode': 'tree,form',
            'domain': [],
            'res_model': 'crm.lead',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'active_test': False}
        }
