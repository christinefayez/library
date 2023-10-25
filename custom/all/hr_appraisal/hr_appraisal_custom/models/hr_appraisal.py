# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import AccessError, ValidationError, UserError


# class HrAppraisalComment(models.Model):
#     _name = "hr.appraisal.comment"
#
#     name = fields.Char('Comment')
#     user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id)
#     related_objective = fields.Many2one('hr.appraisal.objective', 'Related Objective')
#     related_appraisal = fields.Many2one('hr.appraisal', 'Related Appraisal')
#
#     def write(self, vals):
#         if self.user_id.id != self.env.user.id:
#             if len(vals) == 1 and not vals.get('related_appraisal') and not vals.get('related_objective'):
#                 raise UserError('Only comment owner can modified!')
#             elif len(vals) > 1:
#                 raise UserError('Only comment owner can modified!')
#         return super(HrAppraisalComment, self).write(vals)

APPRAISAL_STATES = [
        ('new', 'To Start'),
        ('pending', 'Appraisal Sent'),
        ('done', 'Done'),
        ('cancel', "Cancelled"),
    ]

class HrAppraisalQuarter(models.Model):
    _name = 'hr.appraisal.quarter'

    name = fields.Char(required=True)
    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)
    starting_date = fields.Date(required=True)
    period_id = fields.Many2one('hr.appraisal.period', required=True)

class HrAppraisalPeriod(models.Model):
    _name = 'hr.appraisal.period'

    name = fields.Char('Period')

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    year = fields.Char(
        string='Year',
        required=False)
    quarter_lines = fields.One2many('hr.appraisal.quarter', 'period_id', required=True)

    @api.onchange('from_date', 'to_date')
    def _onchange_date(self):
        for rec in self:
            if rec.from_date and rec.to_date:
                rec.name = "Appraisal %s / %s" % (rec.from_date, rec.to_date)


class HrAppraisal(models.Model):
    _inherit = "hr.appraisal"

    def cron_start_appraisal(self):
        for rec in self.env['hr.appraisal'].search([('related_quarter.starting_date','<=',fields.Date.today()),('state','=','new')]):
            rec.button_send_appraisal()

    # def _default_stage_id(self):
    #     return self.env['hr.appraisal.stage'].search([], order='sequence asc', limit=1).id

    changed_employee_rate = fields.Integer()
    changed_manager_rate = fields.Integer()

    # @api.onchange('appraisal_edit_objectives.employee_rate_id','appraisal_edit_competency_ids.employee_rate_id')
    # def change_flag_employee_change(self):
    #     self.changed_employee_rate += 1
    # @api.onchange('appraisal_edit_objectives.manager_rate_id','appraisal_edit_competency_ids.manager_rate_id')
    # def change_flag_manager_change(self):
    #     self.changed_manager_rate += 1

    def write(self, vals):
        res = super(HrAppraisal, self).write(vals)
        # self.env.cr.commit()
        for rec in self:
            if any(rec.appraisal_edit_competency_ids.mapped('changed_employee_rate')) == True or any(rec.appraisal_edit_objectives.mapped('changed_employee_rate')) == True:
                template_id = self.env.ref('hr_appraisal_custom.send_new_email_for_manager_rate_employee')
                if template_id:
                    template_id.send_mail(rec.id, force_send=True)
                for line in rec.appraisal_edit_competency_ids:
                    line.changed_employee_rate = False
                for line in rec.appraisal_edit_objectives:
                    line.changed_employee_rate = False

            if any(rec.appraisal_edit_competency_ids.mapped('changed_manager_rate')) == True or any(rec.appraisal_edit_objectives.mapped('changed_manager_rate')) == True:
                template_id = self.env.ref('hr_appraisal_custom.send_new_email_for_hr_rate_manager')
                if template_id:
                    template_id.send_mail(rec.id, force_send=True)
                for line in rec.appraisal_edit_competency_ids:
                    line.changed_manager_rate = False
                for line in rec.appraisal_edit_objectives:
                    line.changed_manager_rate = False
        return res
    appraisal_objectives = fields.One2many('hr.appraisal.objective', 'related_appraisal',
                                           domain=[('state', '!=', 'deleted')], string='Appraisal Objectives')
    appraisal_edit_objectives = fields.One2many('hr.appraisal.objective', 'related_appraisal',
                                                domain=[('state', '!=', 'deleted')], string='Appraisal Edit Objectives')
    deleted_appraisal_objectives = fields.One2many('hr.appraisal.objective', 'related_appraisal',
                                                   domain=[('state', '=', 'deleted')],
                                                   string='Deleted Appraisal Objectives')
    appraisal_competency_ids = fields.One2many(
        comodel_name='hr.appraisal.competency',
        inverse_name='related_appraisal_id',
        domain=[('state', '!=', 'deleted')],
        string='Appraisal Competencies',
    )
    appraisal_edit_competency_ids = fields.One2many(
        comodel_name='hr.appraisal.competency',
        inverse_name='related_appraisal_id',
        domain=[('state', '!=', 'deleted')],
        string='Appraisal Edit Competencies',
    )
    deleted_appraisal_competency_ids = fields.One2many(
        comodel_name='hr.appraisal.competency',
        inverse_name='related_appraisal_id',
        domain=[('state', '=', 'deleted')],
        string='Deleted Appraisal Competencies',
    )
    appraisal_training = fields.One2many('hr.training', 'related_appraisal', string='Appraisal Training')

    appraisal_form = fields.Many2one('hr.appraisal.form', 'Appraisal Form', required=True)
    states = fields.Selection(APPRAISAL_STATES, compute='_get_status')
    # related_period = fields.Many2one(related='appraisal_form.period_id')
    related_period = fields.Many2one('hr.appraisal.period')
    related_quarter = fields.Many2one('hr.appraisal.quarter')

    employee_grade = fields.Integer(string="Employee Grade")
    contract_subgroup = fields.Many2one('hr.contract.subgroup', string="Employee Type")

    # comments = fields.One2many('hr.appraisal.comment', 'related_appraisal', 'Comments')

    current_manager = fields.Many2one('hr.employee', 'Current Manager')

    stage_id = fields.Many2one('hr.appraisal.stage', 'Stage', ondelete='restrict', tracking=True,
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids')
                               # default=_default_stage_id)

    appraisal_manager = fields.Many2one('hr.employee', 'Appraisal Manager',
                                        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    total_sum_weight = fields.Float('Total Weight Sum', compute="_calculate_total_weight")
    total_sum_weight_objective = fields.Float('Total Weight Sum Objectives', compute="_calculate_total_weight")
    total_sum_weight_competency = fields.Float('Total Weight Sum Competencies', compute="_calculate_total_weight")
    total_sum_outcome = fields.Float('Outcome Percentage', compute="_calculate_total_outcome", store=True)
    final_score_outcome = fields.Char('Final Score', compute="_calculate_total_outcome", store=True)

    employee_overall_rating = fields.Float('Employee Rating', compute="calculate_employee_overall_rating", store=True)

    employee_overall_rating_rounded = fields.Float('Employee Rating Rounded',
                                                   compute="calculate_employee_overall_rating", store=True)

    overall_rating = fields.Float('Manager Rating', compute="calculate_overall_rating", store=True)

    overall_rating_rounded = fields.Float('Manager Rating Rounded', compute="calculate_overall_rating", store=True)

    hr_overall_rating = fields.Float('HR Final Rating', default=0.0)

    hr_overall_rating_final = fields.Float('HR Overall Rating Final', compute="calculate_hr_overall_rating", store=True)

    manager_comment = fields.Text('Manager Comment')

    employee_comment = fields.Text('Employee Comment')

    hr_comment = fields.Text('HR Comment')

    survey_id = fields.Many2one('survey.survey', string="Survey",
                                domain=[('category', '=', 'hr_appraisal')], readonly=False
                                )
    response_id = fields.Many2one('survey.user_input', "Response", ondelete="set null", readonly=True,
                                  )

    employee_oc_id = fields.Many2one('hr.department')
    employee_system_id = fields.Char()
    # employee_strata_id = fields.Char(related='employee_id.strata_id')
    employee_job_title = fields.Many2one(string="Job Title", related='employee_id.contract_id.job_title', store=True)
    group = fields.Many2one('hr.department')
    department = fields.Many2one('hr.department')
    section = fields.Many2one('hr.department')
    subsection = fields.Many2one('hr.department')

    total_count_objectives = fields.Float('Total Count Objectives', compute="_calculate_total_count")
    total_count_competency = fields.Float(
        string='Total Count Competencies',
        compute="_calculate_total_count",
    )

    previous_stage_id = fields.Many2one(
        comodel_name='hr.appraisal.stage',
        string='Previous Stage',
        required=False, compute='get_previous_stage')
    next_stage_id = fields.Many2one(
        comodel_name='hr.appraisal.stage',
        string='Next Stage',
        required=False, compute='get_next_stage')
    # year = fields.Char(related='related_period.year', store=True)
    year = fields.Char(string='Year')
    can_complete = fields.Boolean(related='stage_id.can_complete')
    is_completed = fields.Boolean(
        string='Is Completed',
        required=True, default=False)

    # pip fields
    area_development = fields.Text('Employee Areas of Development')

    first_manager_review = fields.Text('1st Month Review By Manager Comments')
    first_employee_review = fields.Text('1st Month Employee Review')

    second_manager_review = fields.Text('2nd Month Review By Manager Comments')
    second_employee_review = fields.Text('2nd Month Employee Review')

    third_manager_review = fields.Text('3rd Month Review By Manager Comments')
    third_employee_review = fields.Text('3rd Month Employee Review')

    manager_final_decision = fields.Selection(string='Manager Final Decision',
                                              selection=[('pass', 'Pass PIP'),
                                                         ('fail', 'Fail PIP')])
    manager_final_comments = fields.Text('Manager Final Comments')

    @api.depends('state')
    @api.onchange('state')
    def _get_status(self):
        for rec in self:
            if rec.state:
                rec.states = rec.state

    def action_complete_appraisal(self):
        pass

    def get_previous_stage(self):
        self = self.sudo()
        for rec in self:
            stage = self.env['hr.appraisal.stage'].search(
                [('sequence', '>', rec.stage_id.sequence), ('id', 'in', rec.appraisal_form.all_stages.ids)],
                order='sequence asc',
                limit=1)
            if stage:
                rec.previous_stage_id = stage.id
            else:
                rec.previous_stage_id = False

    def get_next_stage(self):
        self = self.sudo()
        for rec in self:
            stage = self.env['hr.appraisal.stage'].search(
                [('sequence', '<', rec.stage_id.sequence), ('id', 'in', rec.appraisal_form.all_stages.ids)],
                order='sequence desc', limit=1)
            if stage:
                rec.next_stage_id = stage.id
            else:
                rec.next_stage_id = False

    @api.onchange('appraisal_form')
    def _onchange_appraisal_form(self):
        for rec in self:
            if rec.appraisal_form:
                # if rec.appraisal_form.period_id:
                #     rec.date_close = rec.appraisal_form.period_id.to_date
                # if rec.appraisal_form.default_survey_id:
                #     rec.survey_id = rec.appraisal_form.default_survey_id.id
                if rec.appraisal_form.starting_stage:
                    rec.stage_id = rec.appraisal_form.starting_stage.id
                if rec.appraisal_form.default_related_objective:
                    rec.appraisal_objectives.unlink()
                    for line in rec.appraisal_form.default_related_objective:
                        linecopy = line.copy()
                        linecopy.related_appraisal_forms = None
                        linecopy.fixed = True
                        rec.appraisal_objectives |= linecopy
                if rec.appraisal_form.default_related_competency:
                    rec.appraisal_competency_ids.unlink()
                    for line in rec.appraisal_form.default_related_competency:
                        linecopy = line.copy()
                        linecopy.related_appraisal_form_id = None
                        linecopy.fixed = True
                        rec.appraisal_competency_ids |= linecopy

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for rec in self:
            rec = rec.sudo()
            if rec.employee_id:
                rec.current_manager = rec.employee_id.parent_id.id
                rec.appraisal_manager = rec.employee_id.parent_id.id
                rec.employee_oc_id = rec.employee_id.department_id
                rec.employee_system_id = rec.employee_id.system_id
                rec.current_manager = rec.employee_id.parent_id
                if rec.employee_id.contract_id:
                    rec.group = rec.employee_id.contract_id.group
                    rec.section = rec.employee_id.contract_id.section
                    rec.subsection = rec.employee_id.contract_id.subsection
                    rec.department = rec.employee_id.contract_id.department
                    rec.contract_subgroup = rec.employee_id.contract_id.contract_subgroup


    @api.onchange('current_manager')
    def _onchange_manager_id(self):
        for rec in self:
            rec = rec.sudo()
            if not rec.stage_id.can_complete:
                rec.appraisal_manager = rec.current_manager.id
        # return {'domain': {
        #     'appraisal_form': [('from_grade_num', '<=', rec.employee_grade),
        #                        ('to_grade_num', '>=', rec.employee_grade),
        #                        ('related_contract_subgroup.id', '=', (rec.contract_subgroup.id)),
        #                        ]}}
        # return {'domain': {
        #     'appraisal_form': [('grade_ids.id', '=', (rec.employee_grade.id)),
        #                        ('related_contract_subgroup.id', '=', (rec.contract_subgroup.id)),
        #                        ]}}

    # def action_start_survey(self):
    #     self.ensure_one()
    #     # create a response and link it to this applicant
    #     if not self.response_id:
    #         response = self.survey_id._create_answer(partner=self.env.user.partner_id)
    #         self.response_id = response.id
    #     else:
    #         response = self.response_id
    #     # grab the token of the response and start surveying
    #     action = self.survey_id.with_context(survey_token=response.token).action_start_survey()
    #     action.update({'target': 'new'})
    #     return action
    #
    # def action_print_survey(self):
    #     """ If response is available then print this response otherwise print survey form (print template of the survey) """
    #     self.ensure_one()
    #     if not self.response_id:
    #         action = self.survey_id.action_print_survey()
    #         action.update({'target': 'new'})
    #         return action
    #     else:
    #         response = self.response_id
    #         action = self.survey_id.with_context(survey_token=response.token).action_print_survey()
    #         action.update({'target': 'new'})
    #         return action

    @api.depends('appraisal_objectives.employee_rate_id', 'appraisal_objectives.weight', 'appraisal_competency_ids',
                 'appraisal_competency_ids.employee_rate_id')
    def calculate_employee_overall_rating(self):
        for rec in self:
            appraisal_objectives = rec.appraisal_objectives.filtered(lambda line: line.employee_rate_id)
            appraisal_competencies = rec.appraisal_competency_ids.filtered(lambda line: line.employee_rate_id)
            total = sum([(x.employee_rate_id.percentage * (x.weight / 100)) for x in appraisal_objectives]) + \
                    sum([(x.employee_rate_id.percentage * (x.weight / 100)) for x in appraisal_competencies])
            rounded = rec.appraisal_form.calculation_rules.filtered(
                lambda x: x.from_value <= total and x.to_value >= total).value
            rec.employee_overall_rating = total
            rec.employee_overall_rating_rounded = rounded

    @api.depends('appraisal_objectives.manager_rate_id', 'appraisal_objectives.weight', 'appraisal_competency_ids',
                 'appraisal_competency_ids.employee_rate_id')
    def calculate_overall_rating(self):
        for rec in self:
            appraisal_objectives = rec.appraisal_objectives.filtered(lambda line: line.manager_rate_id)
            appraisal_competencies = rec.appraisal_competency_ids.filtered(lambda line: line.manager_rate_id)
            total = sum([(x.manager_rate_id.percentage * (x.weight / 100)) for x in appraisal_objectives]) + \
                    sum([(x.manager_rate_id.percentage * (x.weight / 100)) for x in appraisal_competencies])
            rounded = rec.appraisal_form.calculation_rules.filtered(
                lambda x: x.from_value <= total and x.to_value >= total).value
            rec.overall_rating = total
            rec.overall_rating_rounded = rounded

    @api.depends('overall_rating_rounded', 'hr_overall_rating')
    def calculate_hr_overall_rating(self):
        for rec in self:
            if rec.hr_overall_rating:
                rec.hr_overall_rating_final = rec.hr_overall_rating
            else:
                rec.hr_overall_rating_final = rec.overall_rating_rounded

    @api.onchange('hr_overall_rating')
    def oncahnge_hr_overall_rating(self):
        for rec in self:
            if rec.hr_overall_rating:
                rec.hr_overall_rating_final = rec.hr_overall_rating

    # @api.constrains('appraisal_objectives')
    def _check_objective_counts(self):
        if len(self.appraisal_objectives) > self.appraisal_form.max_objective or len(
                self.appraisal_objectives) < self.appraisal_form.min_objective:
            raise ValidationError("Objective must be between %s and %s" % (
                self.appraisal_form.min_objective, self.appraisal_form.max_objective))

    def _check_competency_counts(self):
        if len(self.appraisal_competency_ids) > self.appraisal_form.max_competency or len(
                self.appraisal_competency_ids) < self.appraisal_form.min_competency:
            raise ValidationError("Competency must be between %s and %s" % (
                self.appraisal_form.min_competency, self.appraisal_form.max_competency))

    # def check_total_weight(self):
    #     if sum(self.appraisal_objectives.mapped('weight')) < self.appraisal_form.total_weight or sum(
    #             self.appraisal_objectives.mapped('weight')) > self.appraisal_form.total_weight:
    #         raise ValidationError("Total Objective Weight must be equal to %s" % (self.appraisal_form.total_weight))

    def approve_all_objectives(self):
        for rec in self:
            rec.appraisal_objectives.state_approve()

    @api.depends('appraisal_edit_objectives', 'appraisal_edit_objectives.weight', 'appraisal_competency_ids',
                 'appraisal_competency_ids.weight')
    def _calculate_total_weight(self):
        for rec in self:
            total_sum_weight_objective = sum(rec.appraisal_objectives.mapped('weight'))
            total_sum_weight_competency = sum(rec.appraisal_competency_ids.mapped('weight'))
            rec.total_sum_weight_objective = total_sum_weight_objective
            rec.total_sum_weight_competency = total_sum_weight_competency
            rec.total_sum_weight =  total_sum_weight_objective + total_sum_weight_competency

    @api.depends('appraisal_edit_objectives', 'appraisal_edit_objectives.outcome_percentage',
                 'appraisal_competency_ids', 'appraisal_competency_ids.outcome_percentage')
    def _calculate_total_outcome(self):
        for rec in self:
            total_sum_outcome = sum(rec.appraisal_edit_objectives.mapped('outcome_percentage')) + \
                                   sum(rec.appraisal_competency_ids.mapped('outcome_percentage'))
            score_range = self.env['hr.appraisal.score.range'].search([
                ('percentage_from', '<=', total_sum_outcome),
                ('percentage_to', '>', total_sum_outcome),
            ], limit=1)
            final_score_outcome = ''
            if score_range:
                final_score_outcome = score_range.name
            rec.final_score_outcome = final_score_outcome
            rec.total_sum_outcome = total_sum_outcome

    @api.depends('appraisal_edit_objectives', 'appraisal_edit_competency_ids')
    def _calculate_total_count(self):
        for rec in self:
            rec.total_count_objectives = len(self.appraisal_edit_objectives)
            rec.total_count_competency = len(self.appraisal_edit_competency_ids)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # retrieve job_id from the context and write the domain: ids + contextual columns (job or default)
        search_domain = []
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def stage_changed_notification(self):
        for rec in self:
            rec.message_notify(
                partner_ids=rec.employee_id.user_partner_id.ids,
                body=("New stage %s") % (
                    rec.stage_id.name),
                subject="Appraisal", email_layout_xmlid='mail.mail_notification_light')
            rec.message_notify(
                partner_ids=rec.appraisal_manager.user_partner_id.ids,
                body=("%s - New Stage %s") % (
                    rec.employee_id.name, rec.stage_id.name),
                subject="Appraisal", email_layout_xmlid='mail.mail_notification_light')

    # def check_survey_done(self):
    #     for rec in self:
    #         if rec.stage_id.employee_take_survey or rec.stage_id.manager_take_survey or rec.stage_id.users_take_survey:
    #             if not rec.response_id:
    #                 raise ValidationError('Survey Must be filled before moving Forward!')

    # def check_survey_done(self):
    #     for rec in self:
    #         if rec.stage_id.employee_take_survey or rec.stage_id.manager_take_survey or rec.stage_id.users_take_survey:
    #             if not rec.response_id:
    #                 raise ValidationError('Survey Must be filled before moving Forward!')

    def check_comments_added(self):
        for rec in self:
            if rec.stage_id.employee_can_comment_form_hr or rec.stage_id.manager_can_comment_form_hr or rec.stage_id.users_can_comment_form_hr:
                if not rec.hr_comment:
                    raise ValidationError('HR Comment on the appraisal form is required before moving forward')
            if rec.stage_id.employee_can_comment_form_manager or rec.stage_id.manager_can_comment_form_manager or rec.stage_id.users_can_comment_form_manager:
                if not rec.manager_comment:
                    raise ValidationError('Manager Comment on the appraisal form is required before moving forward')
            if rec.stage_id.employee_can_comment_form_employee or rec.stage_id.manager_can_comment_form_employee or rec.stage_id.users_can_comment_form_employee:
                if not rec.employee_comment:
                    raise ValidationError('Employee Comment on the appraisal form is required before moving forward')
            if rec.stage_id.employee_can_comment_objective_hr or rec.stage_id.manager_can_comment_objective_hr or rec.stage_id.users_can_comment_objective_hr:
                for line in rec.appraisal_edit_objectives:
                    if not line.hr_comment:
                        raise ValidationError('HR Comments on each objective is required before moving forward')
            if rec.stage_id.employee_can_comment_objective_manager or rec.stage_id.manager_can_comment_objective_manager or rec.stage_id.users_can_comment_objective_manager:
                for line in rec.appraisal_edit_objectives:
                    if not line.manager_comment:
                        raise ValidationError(
                            'Manager Comments on each objective is required before moving forward')
            if rec.stage_id.employee_can_comment_objective_employee or rec.stage_id.manager_can_comment_objective_employee or rec.stage_id.users_can_comment_objective_employee:
                for line in rec.appraisal_edit_objectives:
                    if not line.employee_comment:
                        raise ValidationError(
                            'Employee Comments on each objective is required before moving forward')
            if rec.stage_id.employee_rating_manager_add or rec.stage_id.manager_rating_manager_add or rec.stage_id.users_rating_manager_add:
                for line in rec.appraisal_edit_objectives:
                    if not line.manager_rate_id:
                        raise ValidationError('Manager Ratings on each objective is required before moving forward')
            if rec.stage_id.employee_rating_employee_add or rec.stage_id.manager_rating_employee_add or rec.stage_id.users_rating_employee_add:
                for line in rec.appraisal_edit_objectives:
                    if not line.employee_rate_id:
                        raise ValidationError(
                            'Employee Ratings on each objective is required before moving forward')

            if rec.stage_id.employee_area_development_add or rec.stage_id.manager_area_development_add or rec.stage_id.users_area_development_add:
                if not rec.area_development:
                    raise ValidationError(
                        'Employee Areas of Development on the appraisal form is required before moving forward')
            if rec.stage_id.employee_first_manager_review_add or rec.stage_id.manager_first_manager_review_add or rec.stage_id.users_first_manager_review_add:
                if not rec.first_manager_review:
                    raise ValidationError(
                        '1st Month Review By Manager Comments on the appraisal form is required before moving forward')
            if rec.stage_id.employee_first_employee_review_add or rec.stage_id.manager_first_employee_review_add or rec.stage_id.users_first_employee_review_add:
                if not rec.first_employee_review:
                    raise ValidationError(
                        '1st Month Employee Review on the appraisal form is required before moving forward')
            if rec.stage_id.employee_second_manager_review_add or rec.stage_id.manager_second_manager_review_add or rec.stage_id.users_second_manager_review_add:
                if not rec.second_manager_review:
                    raise ValidationError(
                        '2nd Month Review By Manager Comments on the appraisal form is required before moving forward')
            if rec.stage_id.employee_second_employee_review_add or rec.stage_id.manager_second_employee_review_add or rec.stage_id.users_second_employee_review_add:
                if not rec.second_employee_review:
                    raise ValidationError(
                        '2nd Month Employee Review on the appraisal form is required before moving forward')
            if rec.stage_id.employee_third_manager_review_add or rec.stage_id.manager_third_manager_review_add or rec.stage_id.users_third_manager_review_add:
                if not rec.third_manager_review:
                    raise ValidationError(
                        '3rd Month Review By Manager Comments on the appraisal form is required before moving forward')
            if rec.stage_id.employee_third_employee_review_add or rec.stage_id.manager_third_employee_review_add or rec.stage_id.users_third_employee_review_add:
                if not rec.third_employee_review:
                    raise ValidationError(
                        '3rd Month Employee Review on the appraisal form is required before moving forward')
            if rec.stage_id.employee_manager_final_decision_add or rec.stage_id.manager_manager_final_decision_add or rec.stage_id.users_manager_final_decision_add:
                if not rec.manager_final_decision:
                    raise ValidationError(
                        'Manager Final Decision on the appraisal form is required before moving forward')
            if rec.stage_id.employee_manager_final_comments_add or rec.stage_id.manager_manager_final_comments_add or rec.stage_id.users_manager_final_comments_add:
                if not rec.manager_final_comments:
                    raise ValidationError(
                        'Manager Final Comments on the appraisal form is required before moving forward')

    def check_trainings_added(self):
        for rec in self:
            if rec.stage_id.employee_can_modifiy_training or rec.stage_id.manager_can_modifiy_training or rec.stage_id.users_can_modifiy_training:
                if len(rec.appraisal_training) == 0:
                    raise ValidationError('Trainings are required before moving forward')

    def move_next_stage(self):
        self = self.sudo()
        self._check_objective_counts()
        self._check_competency_counts()
        # self.check_survey_done()
        self.check_comments_added()
        self.check_trainings_added()
        stage = self.env['hr.appraisal.stage'].search(
            [('sequence', '>', self.stage_id.sequence), ('id', 'in', self.appraisal_form.all_stages.ids)],
            order='sequence asc',
            limit=1)
        if stage:
            self.stage_id = stage.id
            # self.stage_changed_notification()
            if stage.can_complete:
                self.action_complete_appraisal()
            view = self.env.ref('sh_message.sh_message_wizard')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['message'] = 'Thank you, the form has been submitted to next stage.'
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

    def log_or_move_previous_stage(self):
        self = self.sudo()
        if self.stage_id.log_note_backward:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Log Reason',
                'res_model': 'log.note.wizard',
                'view_mode': 'form',
                'target': 'new',
                'view_id': self.env.ref('hr_appraisal_custom.log_note_wizard_view_form').id,
                'context': {
                    'default_related_appraisal': self.id,
                }
            }
        self.move_previous_stage()

    def move_previous_stage(self):
        stage = self.env['hr.appraisal.stage'].search(
            [('sequence', '<', self.stage_id.sequence), ('id', 'in', self.appraisal_form.all_stages.ids)],
            order='sequence desc', limit=1)
        if stage:
            self.stage_id = stage.id
            # self.stage_changed_notification()

    can_move_forward = fields.Boolean('Can Move Forward', compute='_check_stage_rule_move_forward')

    def _check_stage_rule_move_forward(self):
        if (self.employee_id.user_id == self.env.user and self.stage_id.employee_allowed_forward) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_allowed_forward) \
                or self.env.user in self.stage_id.users_allowed_forward:
            self.can_move_forward = True
        else:
            self.can_move_forward = False

    can_move_previous = fields.Boolean('Can Move Previous', compute='_check_stage_rule_move_previous')

    def _check_stage_rule_move_previous(self):
        if (self.employee_id.user_id == self.env.user and self.stage_id.employee_allowed_backward) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_allowed_backward) \
                or self.env.user in self.stage_id.users_allowed_backward:
            self.can_move_previous = True
        else:
            self.can_move_previous = False

    can_add_objectives = fields.Boolean('Can Add Objectives', compute='_check_stage_rule_add_objectives')

    def _check_stage_rule_add_objectives(self):
        if (self.employee_id.user_id == self.env.user and self.stage_id.employee_can_add_objective) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_add_objective) \
                or self.env.user in self.stage_id.users_can_add_objective:
            self.can_add_objectives = True
        else:
            self.can_add_objectives = False

    can_add_competencies = fields.Boolean('Can Add Competencies', compute='_check_stage_rule_add_competencies')

    def _check_stage_rule_add_competencies(self):
        if (self.employee_id.user_id == self.env.user and self.stage_id.employee_can_add_competency) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_add_competency) \
                or self.env.user in self.stage_id.users_can_add_competency:
            self.can_add_competencies = True
        else:
            self.can_add_competencies = False

    can_edit_appraisal = fields.Boolean('Can Edit Appraisal', compute='_check_stage_rule_edit_appraisal')

    def _check_stage_rule_edit_appraisal(self):
        if (self.employee_id.user_id == self.env.user and self.stage_id.employee_allowed_edit) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_allowed_edit) \
                or self.env.user in self.stage_id.users_allowed_edit:
            self.can_edit_appraisal = True
        else:
            self.can_edit_appraisal = False

    can_comment_hr = fields.Boolean('Can HR Comment', compute='_check_stage_rule_hr_comment')

    def _check_stage_rule_hr_comment(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_can_comment_form_hr) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_comment_form_hr) \
                or self.env.user in self.stage_id.users_can_comment_form_hr:
            self.can_comment_hr = True
        else:
            self.can_comment_hr = False

    can_comment_manager = fields.Boolean('Can Manager Comment', compute='_check_stage_rule_manager_comment')

    def _check_stage_rule_manager_comment(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_can_comment_form_manager) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_comment_form_manager) \
                or self.env.user in self.stage_id.users_can_comment_form_manager:
            self.can_comment_manager = True
        else:
            self.can_comment_manager = False

    can_comment_employee = fields.Boolean('Can Employee Comment', compute='_check_stage_rule_employee_comment')

    def _check_stage_rule_employee_comment(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_can_comment_form_employee) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_comment_form_employee) \
                or self.env.user in self.stage_id.users_can_comment_form_employee:
            self.can_comment_employee = True
        else:
            self.can_comment_employee = False

    can_see_comment_hr = fields.Boolean('Can See HR Comment', compute='_check_stage_rule_hr_see_comment')

    def _check_stage_rule_hr_see_comment(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_can_see_comment_form_hr) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_see_comment_form_hr) \
                or self.env.user in self.stage_id.users_can_see_comment_form_hr:
            self.can_see_comment_hr = True
        else:
            self.can_see_comment_hr = False

    can_see_comment_manager = fields.Boolean('Can See Manager Comment', compute='_check_stage_rule_manager_see_comment')

    def _check_stage_rule_manager_see_comment(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_can_see_comment_form_manager) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_see_comment_form_manager) \
                or self.env.user in self.stage_id.users_can_see_comment_form_manager:
            self.can_see_comment_manager = True
        else:
            self.can_see_comment_manager = False

    can_see_comment_employee = fields.Boolean('Can See Employee Comment',
                                              compute='_check_stage_rule_employee_see_comment')

    def _check_stage_rule_employee_see_comment(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_can_see_comment_form_employee) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_see_comment_form_employee) \
                or self.env.user in self.stage_id.users_can_see_comment_form_employee:
            self.can_see_comment_employee = True
        else:
            self.can_see_comment_employee = False

    can_training = fields.Boolean('Can Edit Training', compute='_check_stage_rule_training')

    def _check_stage_rule_training(self):
        if (self.employee_id.user_id == self.env.user and self.stage_id.employee_can_modifiy_training) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_modifiy_training) \
                or self.env.user in self.stage_id.users_can_modifiy_training:
            self.can_training = True
        else:
            self.can_training = False

    can_approve_objectives = fields.Boolean('Can Approve Objectives', compute='_check_stage_rule_approve_objectives')

    def _check_stage_rule_approve_objectives(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_can_approve_approve) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_approve_approve) \
                or self.env.user in self.stage_id.users_can_approve_approve:
            self.can_approve_objectives = True
        else:
            self.can_approve_objectives = False

    can_take_survey = fields.Boolean('Can Take Survey', compute='_check_stage_rule_take_survey')

    def _check_stage_rule_take_survey(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_take_survey) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_take_survey) \
                or self.env.user in self.stage_id.users_take_survey:
            self.can_take_survey = True
        else:
            self.can_take_survey = False

    can_print_survey = fields.Boolean('Can See Survey', compute='_check_stage_rule_see_survey')

    def _check_stage_rule_see_survey(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_see_survey) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_see_survey) \
                or self.env.user in self.stage_id.users_see_survey:
            self.can_print_survey = True
        else:
            self.can_print_survey = False

    can_rate_hr = fields.Boolean('Can HR Rate', compute='_check_stage_rule_hr_rate')

    def _check_stage_rule_hr_rate(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_rating_hr_add) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_rating_hr_add) \
                or self.env.user in self.stage_id.users_rating_hr_add:
            self.can_rate_hr = True
        else:
            self.can_rate_hr = False

    can_see_rate_hr = fields.Boolean('Can See HR Rate', compute='_check_stage_rule_hr_see_rate')

    def _check_stage_rule_hr_see_rate(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_rating_hr_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_rating_hr_see) \
                or self.env.user in self.stage_id.users_rating_hr_see:
            self.can_see_rate_hr = True
        else:
            self.can_see_rate_hr = False

    can_see_rate_manager = fields.Boolean('Can See Manager Rate', compute='_check_stage_rule_manager_see_rate')

    def _check_stage_rule_manager_see_rate(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_rating_manager_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_rating_manager_see) \
                or self.env.user in self.stage_id.users_rating_manager_see:
            self.can_see_rate_manager = True
        else:
            self.can_see_rate_manager = False

    can_see_rate_manager_rounded = fields.Boolean('Can See Manager Rate Rounded',
                                                  compute='_check_stage_rule_manager_see_rate_rounded')

    def _check_stage_rule_manager_see_rate_rounded(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_rating_manager_see_rounded) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_rating_manager_see_rounded) \
                or self.env.user in self.stage_id.users_rating_manager_see_rounded:
            self.can_see_rate_manager_rounded = True
        else:
            self.can_see_rate_manager_rounded = False

    can_see_rate_employee = fields.Boolean('Can See Employee Rate', compute='_check_stage_rule_employee_see_rate')

    def _check_stage_rule_employee_see_rate(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_rating_employee_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_rating_employee_see) \
                or self.env.user in self.stage_id.users_rating_employee_see:
            self.can_see_rate_employee = True
        else:
            self.can_see_rate_employee = False

    can_see_comment_objective_hr = fields.Boolean('Can See HR Comment',
                                                  compute='_check_stage_rule_hr_see_objective_comment')

    def _check_stage_rule_hr_see_objective_comment(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_can_see_comment_objective_hr) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_see_comment_objective_hr) \
                or self.env.user in self.stage_id.users_can_see_comment_objective_hr:
            self.can_see_comment_objective_hr = True
        else:
            self.can_see_comment_objective_hr = False

    can_see_comment_objective_manager = fields.Boolean('Can See Manager Comment',
                                                       compute='_check_stage_rule_manager_see_objective_comment')

    def _check_stage_rule_manager_see_objective_comment(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_can_see_comment_objective_manager) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_see_comment_objective_manager) \
                or self.env.user in self.stage_id.users_can_see_comment_objective_manager:
            self.can_see_comment_objective_manager = True
        else:
            self.can_see_comment_objective_manager = False

    can_see_comment_objective_employee = fields.Boolean('Can See Employee Comment',
                                                        compute='_check_stage_rule_employee_see_objective_comment')

    def _check_stage_rule_employee_see_objective_comment(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_can_see_comment_objective_employee) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_see_comment_objective_employee) \
                or self.env.user in self.stage_id.users_can_see_comment_objective_employee:
            self.can_see_comment_objective_employee = True
        else:
            self.can_see_comment_objective_employee = False

    can_see_rate_objective_manager = fields.Boolean('Can See Manager Rate',
                                                    compute='_check_stage_rule_manager_see_objective_rate')

    def _check_stage_rule_manager_see_objective_rate(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_rating_manager_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_rating_manager_see) \
                or self.env.user in self.stage_id.users_rating_manager_see:
            self.can_see_rate_objective_manager = True
        else:
            self.can_see_rate_objective_manager = False

    can_see_rate_objective_employee = fields.Boolean('Can See Employee Rate',
                                                     compute='_check_stage_rule_employee_objective_see_rate')

    def _check_stage_rule_employee_objective_see_rate(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_rating_employee_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_rating_employee_see) \
                or self.env.user in self.stage_id.users_rating_employee_see:
            self.can_see_rate_objective_employee = True
        else:
            self.can_see_rate_objective_employee = False

    can_see_comment_competency_hr = fields.Boolean('Can See HR Comment',
                                                  compute='_check_stage_rule_hr_see_competency_comment')

    def _check_stage_rule_hr_see_competency_comment(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_can_see_comment_competency_hr) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_see_comment_competency_hr) \
                or self.env.user in self.stage_id.users_can_see_comment_competency_hr:
            self.can_see_comment_competency_hr = True
        else:
            self.can_see_comment_competency_hr = False

    can_see_comment_competency_manager = fields.Boolean('Can See Manager Comment',
                                                       compute='_check_stage_rule_manager_see_competency_comment')

    def _check_stage_rule_manager_see_competency_comment(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_can_see_comment_competency_manager) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_see_comment_competency_manager) \
                or self.env.user in self.stage_id.users_can_see_comment_competency_manager:
            self.can_see_comment_competency_manager = True
        else:
            self.can_see_comment_competency_manager = False

    can_see_comment_competency_employee = fields.Boolean('Can See Employee Comment',
                                                        compute='_check_stage_rule_employee_see_competency_comment')

    def _check_stage_rule_employee_see_competency_comment(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_can_see_comment_competency_employee) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_can_see_comment_competency_employee) \
                or self.env.user in self.stage_id.users_can_see_comment_competency_employee:
            self.can_see_comment_competency_employee = True
        else:
            self.can_see_comment_competency_employee = False

    can_see_rate_competency_manager = fields.Boolean('Can See Manager Rate',
                                                    compute='_check_stage_rule_manager_see_competency_rate')

    def _check_stage_rule_manager_see_competency_rate(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_rating_manager_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_rating_manager_see) \
                or self.env.user in self.stage_id.users_rating_manager_see:
            self.can_see_rate_competency_manager = True
        else:
            self.can_see_rate_competency_manager = False

    can_see_rate_competency_employee = fields.Boolean('Can See Employee Rate',
                                                      compute='_check_stage_rule_employee_competency_see_rate')

    def _check_stage_rule_employee_competency_see_rate(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_rating_employee_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_rating_employee_see) \
                or self.env.user in self.stage_id.users_rating_employee_see:
            self.can_see_rate_competency_employee = True
        else:
            self.can_see_rate_competency_employee = False

    def _get_objectives(self):
        # line = [{'name': "Objective", 'weight': "Weight", 'description': "Description", 'e_rating': "Employee Rating",
        #          'e_comment': "Employee Comment", 'm_rating': "Manager Rating",
        #          'm_comment': "Manager Comment", 'h_comment': "HR Comment",
        #          'bold': True}]
        line = []

        for obj in self.appraisal_edit_objectives.filtered(lambda x: x.state == 'active'):
            line.append(
                {'name': obj.title, 'weight': obj.weight, 'description': obj.description,
                 'e_rating': obj.employee_rate_id.percentage,
                 'e_comment': obj.employee_comment, 'm_rating': obj.manager_rate_id.percentage,
                 'm_comment': obj.manager_comment, 'h_comment': obj.hr_comment,
                 'bold': False})
            # line.append(
            #     {'name': "Objective", 'weight': "Weight", 'description': "Description", 'e_rating': "Employee Rating",
            #      'e_comment': "Employee Comment", 'm_rating': "Manager Rating",
            #      'm_comment': "Manager Comment", 'h_comment': "HR Comment",
            #      'bold': True})

        return line

    def _get_trainings(self):
        full_date_format = '%d/%m/%Y'
        line = [{'name': "Training Name", 'status': "Status", 'from_date': "From Date", 'to_date': "To Date",
                 'description': "Description", 'bold': True}]

        for obj in self.appraisal_training:
            line.append(
                {'name': obj.name, 'status': obj.status.name,
                 'from_date': obj.from_date.strftime(full_date_format) if obj.from_date else '',
                 'to_date': obj.to_date.strftime(full_date_format) if obj.to_date else '', 'description': obj.desc,
                 'bold': False})

        return line

    def _get_feedbacks(self):
        line = [
            {'name': "Name", 'user': "Responsible User", 'type': "Feedback Type", 'feedback': "Feedback", 'bold': True}]

        for obj in self.related_feedback:
            line.append(
                {'name': obj.name, 'user': obj.user_id.name,
                 'type': dict(self.related_feedback._fields['feedback_type'].selection).get(obj.feedback_type),
                 'feedback': obj.feedback,
                 'bold': False})

        return line

    can_add_area_development = fields.Boolean('Can Add Area of Development',
                                              compute='_check_stage_rule_add_area_development')

    def _check_stage_rule_add_area_development(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_area_development_add) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_area_development_add) \
                or self.env.user in self.stage_id.users_area_development_add:
            self.can_add_area_development = True
        else:
            self.can_add_area_development = False

    can_see_area_development = fields.Boolean('Can See Area of Development',
                                              compute='_check_stage_rule_see_area_development')

    def _check_stage_rule_see_area_development(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_area_development_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_area_development_see) \
                or self.env.user in self.stage_id.users_area_development_see:
            self.can_see_area_development = True
        else:
            self.can_see_area_development = False

    can_add_first_manager_review = fields.Boolean('Can Add 1st month Review by Manager Comments',
                                                  compute='_check_stage_rule_add_first_manager_review')

    def _check_stage_rule_add_first_manager_review(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_first_manager_review_add) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_first_manager_review_add) \
                or self.env.user in self.stage_id.users_first_manager_review_add:
            self.can_add_first_manager_review = True
        else:
            self.can_add_first_manager_review = False

    can_see_first_manager_review = fields.Boolean('Can See 1st month Review by Manager Comments',
                                                  compute='_check_stage_rule_see_first_manager_review')

    def _check_stage_rule_see_first_manager_review(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_first_manager_review_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_first_manager_review_see) \
                or self.env.user in self.stage_id.users_first_manager_review_see:
            self.can_see_first_manager_review = True
        else:
            self.can_see_first_manager_review = False

    can_add_first_employee_review = fields.Boolean('Can Add 1st month Employee Review',
                                                   compute='_check_stage_rule_add_first_employee_review')

    def _check_stage_rule_add_first_employee_review(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_first_employee_review_add) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_first_employee_review_add) \
                or self.env.user in self.stage_id.users_first_employee_review_add:
            self.can_add_first_employee_review = True
        else:
            self.can_add_first_employee_review = False

    can_see_first_employee_review = fields.Boolean('Can See 1st month Employee Review',
                                                   compute='_check_stage_rule_see_first_employee_review')

    def _check_stage_rule_see_first_employee_review(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_first_employee_review_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_first_employee_review_see) \
                or self.env.user in self.stage_id.users_first_employee_review_see:
            self.can_see_first_employee_review = True
        else:
            self.can_see_first_employee_review = False

    can_add_second_manager_review = fields.Boolean('Can Add 2nd month Review by Manager Comments',
                                                   compute='_check_stage_rule_add_second_manager_review')

    def _check_stage_rule_add_second_manager_review(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_second_manager_review_add) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_second_manager_review_add) \
                or self.env.user in self.stage_id.users_second_manager_review_add:
            self.can_add_second_manager_review = True
        else:
            self.can_add_second_manager_review = False

    can_see_second_manager_review = fields.Boolean('Can See 2nd month Review by Manager Comments',
                                                   compute='_check_stage_rule_see_second_manager_review')

    def _check_stage_rule_see_second_manager_review(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_second_manager_review_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_second_manager_review_see) \
                or self.env.user in self.stage_id.users_second_manager_review_see:
            self.can_see_second_manager_review = True
        else:
            self.can_see_second_manager_review = False

    can_add_second_employee_review = fields.Boolean('Can Add 2nd month Employee Review',
                                                    compute='_check_stage_rule_add_second_employee_review')

    def _check_stage_rule_add_second_employee_review(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_second_employee_review_add) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_second_employee_review_add) \
                or self.env.user in self.stage_id.users_second_employee_review_add:
            self.can_add_second_employee_review = True
        else:
            self.can_add_second_employee_review = False

    can_see_second_employee_review = fields.Boolean('Can See 2nd month Employee Review',
                                                    compute='_check_stage_rule_see_second_employee_review')

    def _check_stage_rule_see_second_employee_review(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_second_employee_review_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_second_employee_review_see) \
                or self.env.user in self.stage_id.users_second_employee_review_see:
            self.can_see_second_employee_review = True
        else:
            self.can_see_second_employee_review = False

    can_add_third_manager_review = fields.Boolean('Can Add 3rd month Review by Manager Comments',
                                                  compute='_check_stage_rule_add_third_manager_review')

    def _check_stage_rule_add_third_manager_review(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_third_manager_review_add) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_third_manager_review_add) \
                or self.env.user in self.stage_id.users_third_manager_review_add:
            self.can_add_third_manager_review = True
        else:
            self.can_add_third_manager_review = False

    can_see_third_manager_review = fields.Boolean('Can See 3rd month Review by Manager Comments',
                                                  compute='_check_stage_rule_see_third_manager_review')

    def _check_stage_rule_see_third_manager_review(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_third_manager_review_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_third_manager_review_see) \
                or self.env.user in self.stage_id.users_third_manager_review_see:
            self.can_see_third_manager_review = True
        else:
            self.can_see_third_manager_review = False

    can_add_third_employee_review = fields.Boolean('Can Add 3rd month Employee Review',
                                                   compute='_check_stage_rule_add_third_employee_review')

    def _check_stage_rule_add_third_employee_review(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_third_employee_review_add) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_third_employee_review_add) \
                or self.env.user in self.stage_id.users_third_employee_review_add:
            self.can_add_third_employee_review = True
        else:
            self.can_add_third_employee_review = False

    can_see_third_employee_review = fields.Boolean('Can See 3rd month Employee Review',
                                                   compute='_check_stage_rule_see_third_employee_review')

    def _check_stage_rule_see_third_employee_review(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_third_employee_review_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_third_employee_review_see) \
                or self.env.user in self.stage_id.users_third_employee_review_see:
            self.can_see_third_employee_review = True
        else:
            self.can_see_third_employee_review = False

    can_add_manager_final_decision = fields.Boolean('Can Add Manager Final Decision',
                                                    compute='_check_stage_rule_add_manager_final_decision')

    def _check_stage_rule_add_manager_final_decision(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_manager_final_decision_add) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_manager_final_decision_add) \
                or self.env.user in self.stage_id.users_manager_final_decision_add:
            self.can_add_manager_final_decision = True
        else:
            self.can_add_manager_final_decision = False

    can_see_manager_final_decision = fields.Boolean('Can See Manager Final Decision',
                                                    compute='_check_stage_rule_see_manager_final_decision')

    def _check_stage_rule_see_manager_final_decision(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_manager_final_decision_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_manager_final_decision_see) \
                or self.env.user in self.stage_id.users_manager_final_decision_see:
            self.can_see_manager_final_decision = True
        else:
            self.can_see_manager_final_decision = False

    can_add_manager_final_comments = fields.Boolean('Can Add Manager Final Comments',
                                                    compute='_check_stage_rule_add_manager_final_comments')

    def _check_stage_rule_add_manager_final_comments(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_manager_final_comments_add) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_manager_final_comments_add) \
                or self.env.user in self.stage_id.users_manager_final_comments_add:
            self.can_add_manager_final_comments = True
        else:
            self.can_add_manager_final_comments = False

    can_see_manager_final_comments = fields.Boolean('Can See Manager Final Comments',
                                                    compute='_check_stage_rule_see_manager_final_comments')

    def _check_stage_rule_see_manager_final_comments(self):
        if (
                self.employee_id.user_id == self.env.user and self.stage_id.employee_manager_final_comments_see) or (
                self.appraisal_manager.user_id == self.env.user and self.stage_id.manager_manager_final_comments_see) \
                or self.env.user in self.stage_id.users_manager_final_comments_see:
            self.can_see_manager_final_comments = True
        else:
            self.can_see_manager_final_comments = False

    def get_url(self):
        appraisal_url = '{}/web#id={}&action={}&model=hr.appraisal&view_type=form&menu_id={}'.format(
            self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            self.id,
            self.env.ref('hr_appraisal.open_view_hr_appraisal_tree').id,
            self.env.ref('hr_appraisal.menu_hr_appraisal_root').id,
        )
        return appraisal_url

    def _send_employee_email(self):
        if self.employee_id.user_id.login:
            template_id = self.env.ref('hr_appraisal_custom.send_new_email_for_create_appraisal_employee')
            if template_id:
                template_id.write({
                    'email_to': self.employee_id.user_id.login
                })
                template_id.send_mail(self.id, force_send=True)

            # if rec.employee_id.user_id.login:
            #     mail_content = \
            #         "<p> Dear {},<br/>" \
            #         "<li>" \
            #         "You Have Assign To New Appraisal <br/> " \
            #         "</li>" \
            #         "<div style='margin: 16px 0px 16px 0px;'>" \
            #         "<a href='{}' class='btn btn-primary' >Appraisal</a>" \
            #         "</div>"\
            #         "</p>" \
            #         "<br/>" \
            #         "<p>Best regards,</p>".format(
            #             rec.employee_id.name,
            #             appraisal_url
            #         )
            #     main_content = {
            #         'subject': _("Appraisal: Assigned"),
            #         'body_html': mail_content,
            #         'email_to': rec.employee_id.user_id.login,
            #     }
            #     self.env['mail.mail'].create(main_content).send()
