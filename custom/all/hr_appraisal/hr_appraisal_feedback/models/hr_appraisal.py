from odoo import fields, models, api


class HrAppraisal(models.Model):
    _inherit = 'hr.appraisal'

    related_feedback = fields.One2many('hr.feedback', 'related_appraisal', string="Feedback")

    can_request_feedback = fields.Boolean('Can Request Feedback', compute='_check_stage_rule_request_feedback')

    def _check_stage_rule_request_feedback(self):
        if (self.employee_id.user_id == self.env.user and self.stage_id.employee_request_feedback) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_request_feedback) \
                or self.env.user in self.stage_id.users_request_feedback:
            self.can_request_feedback = True
        else:
            self.can_request_feedback = False

    can_see_feedback = fields.Boolean('Can See Feedback', compute='_check_stage_rule_see_feedback')

    def _check_stage_rule_see_feedback(self):
        if (self.employee_id.user_id == self.env.user and self.stage_id.employee_request_feedback) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_request_feedback) \
                or self.env.user in self.stage_id.users_see_feedback:
            self.can_see_feedback = True
        else:
            self.can_see_feedback = False

#
# class HrAppraisalObjective(models.Model):
#     _inherit = 'hr.appraisal.objective'
#
#     related_feedback = fields.One2many('hr.feedback','related_objectives',string="Feedback")
#
#     can_request_feedback = fields.Boolean('Can Request Feedback', compute='_check_stage_rule_request_feedback')
#
#     def _check_stage_rule_request_feedback(self):
#         if (
#                 self.related_employee.user_id == self.env.user and self.related_appraisal.stage_id.employee_request_feedback) or (
#                 self.related_appraisal.appraisal_manager.user_id == self.env.user and self.related_appraisal.stage_id.manager_request_feedback):
#             self.can_request_feedback = True
#         else:
#             self.can_request_feedback = False
