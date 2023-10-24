from odoo import fields, models


class crmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    lost_competitor_id = fields.Many2one('crm.competitor.reason', 'Competitor Name')
    is_competitor_reason = fields.Boolean(related='lost_reason_id.is_competitor_reason')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)

    def action_lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        leads.action_set_lost(lost_competitor_id=self.lost_competitor_id.id if self.lost_competitor_id else False)
        res = super(crmLeadLost, self).action_lost_reason_apply()
        return res
