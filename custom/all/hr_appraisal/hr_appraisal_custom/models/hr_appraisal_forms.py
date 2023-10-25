from odoo import fields, models, api


class Survey(models.Model):
    _inherit = 'survey.survey'

    category = fields.Selection(selection=[('hr_appraisal', 'Appraisal')])


class HrAppraisalRules(models.Model):
    _name = "hr.appraisal.rules"

    from_value = fields.Float('From value', default=0.0)
    to_value = fields.Float('To value', default=0.0)
    value = fields.Float('Round to', default=0.0)
    related_forms = fields.Many2one('hr.appraisal.form', 'Related Form')


class HrAppraisalForms(models.Model):
    _name = 'hr.appraisal.form'

    name = fields.Char('Name')
    from_grade_num = fields.Integer('From Grade')
    to_grade_num = fields.Integer('To Grade')
    starting_stage = fields.Many2one('hr.appraisal.stage', 'Starting Stage')
    all_stages = fields.Many2many(comodel_name='hr.appraisal.stage', string='All Stages')
    max_objective = fields.Integer('Max Objectives', default=10)
    min_objective = fields.Integer('Min Objectives', default=7)
    max_competency = fields.Integer('Max Competencies', default=10)
    min_competency = fields.Integer('Min Competencies', default=7)
    related_contract_subgroup = fields.Many2many('hr.contract.subgroup', string="Contract Subgroup")
    default_related_objective = fields.One2many('hr.appraisal.objective', 'related_appraisal_forms',
                                                'Default Appraisal Objectives')
    default_related_competency = fields.One2many(
        comodel_name='hr.appraisal.competency',
        inverse_name='related_appraisal_form_id',
        string='Default Appraisal Competency',
    )
    default_survey_id = fields.Many2one('survey.survey', string="Appraisal Manager Evaluation Survey",
                                        domain=[('category', '=', 'hr_appraisal')], required=False)
    period_id = fields.Many2one('hr.appraisal.period', 'Period', required=True)
    calculation_rules = fields.One2many('hr.appraisal.rules', 'related_forms', string="Calculation Rules")
    filter_by = fields.Selection([('grade_ids','Job Grades'),('job_ids','Job Positions')], default=False, required=True)
    grade_ids = fields.Many2many(
        comodel_name='job.grade',
        string='Grades')
    job_ids = fields.Many2many(
        comodel_name='hr.job',
        string='Job Positions')
    @api.onchange('filter_by')
    def clear_un_wanted_field(self):
        if self.filter_by == 'grade_ids':
            self.job_ids = False
        if self.filter_by == 'job_ids':
            self.grade_ids = False
    active = fields.Boolean('Active', default=True)
    includes_calibration = fields.Boolean('Includes Calibration', default=False)
    always_release_ratings = fields.Boolean('Always Release Ratings', default=False)
