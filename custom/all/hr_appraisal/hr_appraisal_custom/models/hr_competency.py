from odoo import fields, models, api
from odoo.exceptions import AccessError


class HrCompetencyCategory(models.Model):
    _name = 'hr.competency.category'
    _description = 'HR Competency Category'

    name = fields.Char(
        string='Competency',
    )


class HrCompetency(models.Model):
    _name = 'hr.competency'
    _description = 'HR Competency'

    code = fields.Char()
    name = fields.Char(
        string='Competency',
    )
    description = fields.Text()
    category = fields.Many2one(
        comodel_name='hr.competency.category',
        string='Competency Category')


class HrAppraisalCompetency(models.Model):
    _name = 'hr.appraisal.competency'
    _description = 'HR Appraisal Competency'

    changed_employee_rate = fields.Boolean(default=False)
    @api.onchange('employee_rate_id')
    def change_flag_employee_change(self):
        if self.related_appraisal_id:
            self.changed_employee_rate = True
    changed_manager_rate = fields.Boolean(default=False)
    @api.onchange('manager_rate_id')
    def change_flag_manager_change(self):
        if self.related_appraisal_id:
            self.changed_manager_rate = True
    name = fields.Many2one(
        comodel_name='hr.competency',
        string='Competency',
    )
    title = fields.Text(
        string='Competency',
        required=True,
    )
    manager_rate_id = fields.Many2one(
        comodel_name='hr.appraisal.rate',
        string='Manager Rating',
        ondelete='restrict',
    )
    outcome_percentage = fields.Float(
        compute='_compute_outcome_percentage',
        store=True,
    )
    employee_rate_id = fields.Many2one(
        comodel_name='hr.appraisal.rate',
        string='Employee Rating',
        ondelete='restrict',
    )
    weight = fields.Float(
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('deleted', 'Deleted'),
        ],
        default='active',
    )
    fixed = fields.Boolean(
        string='Default Competency',
    )
    related_appraisal_id = fields.Many2one(
        comodel_name='hr.appraisal',
        ondelete='cascade',
    )
    related_appraisal_form_id = fields.Many2one(
        comodel_name='hr.appraisal.form',
        ondelete='restrict',
    )
    related_employee_id = fields.Many2one(
        related="related_appraisal_id.employee_id",
    )
    manager_comment = fields.Text()
    employee_comment = fields.Text()
    hr_comment = fields.Text(
        string='HR Comment',
    )
    description = fields.Text(
        required=True,
    )
    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        relation="ebs_mod_m2m_hr_appraisal_competency",
        column1="appraisal_competency_id",
        column2="attachment_id",
        string="Employee Attachment",
    )
    can_approve_competencies = fields.Boolean(
          compute='_check_stage_rule_approve_competencies',
    )
    can_comment_competency_hr = fields.Boolean(
        string='Can HR Comment',
        compute='_check_stage_rule_hr_comment',
    )
    can_comment_competency_manager = fields.Boolean(
        string='Can Manager Comment',
        compute='_check_stage_rule_manager_comment',
    )
    can_comment_competency_employee = fields.Boolean(
        string='Can Employee Comment',
        compute='_check_stage_rule_employee_comment',
    )
    can_see_comment_competency_hr = fields.Boolean(
        string='Can See HR Comment',
        compute='_check_stage_rule_hr_see_comment',
    )
    can_see_comment_competency_manager = fields.Boolean(
        string='Can See Manager Comment',
        compute='_check_stage_rule_manager_see_comment',
    )
    can_see_comment_competency_employee = fields.Boolean(
        string='Can See Employee Comment',
        compute='_check_stage_rule_employee_see_comment',
    )
    can_rate_competency_manager = fields.Boolean(
        string='Can Manager Rate',
        compute='_check_stage_rule_manager_rate',
    )
    can_rate_competency_employee = fields.Boolean(
        string='Can Employee Rate',
        compute='_check_stage_rule_employee_rate',
    )
    can_see_rate_competency_manager = fields.Boolean(
        string='Can See Manager Rate',
        compute='_check_stage_rule_manager_see_rate',
    )
    can_see_rate_competency_employee = fields.Boolean(
        string='Can See Employee Rate',
        compute='_check_stage_rule_employee_see_rate',
    )

    @api.depends('manager_rate_id', 'weight')
    def _compute_outcome_percentage(self):
        """ compute percentage from rate """
        for record in self:
            outcome_percentage = 0
            if record.manager_rate_id:
                outcome_percentage = record.weight * (record.manager_rate_id.percentage / 100)
            record.outcome_percentage = outcome_percentage

    def name_get(self):
        """ change name of record to be title """
        return [(value.id, "%s" % value.title) for value in self]

    def unlink(self):
        """ restrict remove fixed=True record """
        for rec in self:
            if rec.fixed:
                raise AccessError("Fixed Competencies Cannot be deleted")
        return super(HrAppraisalCompetency, self).unlink()

    def write(self, vals):
        """ log changes in record in appraisal """
        log_post = False
        for rec in self:
            log = 'Competency: ' + (
                vals.get('title') if vals.get('title') is not None else rec.title) + " : "

            if vals.get('title') is not None:
                log += '<br/>' + 'Title: ' + (rec.title if rec.title else '') + ' → ' + vals.get('title', '')
                log_post = True

            if vals.get('weight') is not None:
                log += '<br/>' + 'Weight: ' + (str(rec.weight) if rec.weight else '') + ' → ' + str(
                    vals.get('weight', ''))
                log_post = True

            if vals.get('description') is not None:
                log += '<br/>' + 'Description: ' + (rec.description if rec.description else '') + ' → ' + vals.get(
                    'description', '')
                log_post = True

            if vals.get('employee_comment') is not None:
                log += '<br/>' + 'Employee Comment: ' + (
                    rec.employee_comment if rec.employee_comment else '') + ' → ' + vals.get('employee_comment', '')
                log_post = True

            if vals.get('employee_rate_id') is not None:
                new_employee_rate = ''
                if 'employee_rate_id' in vals and vals.get('employee_rate_id'):
                    new_employee_rate = self.env['hr.appraisal.rate'].browse(vals.get('employee_rate_id')).name
                log += '<br/>' + 'Employee Rating: ' + (
                    rec.employee_rate_id.name if rec.employee_rate_id else '') + ' → ' + new_employee_rate
                log_post = True

            if vals.get('manager_comment') is not None:
                log += '<br/>' + 'Manager Comment: ' + (
                    rec.manager_comment if rec.manager_comment else '') + ' → ' + vals.get(
                    'manager_comment', '')
                log_post = True

            if vals.get('manager_rate_id') is not None:
                new_manger_rate = ''
                if 'manager_rate_id' in vals and vals.get('manager_rate_id'):
                    new_manger_rate = self.env['hr.appraisal.rate'].browse(vals.get('manager_rate_id')).name
                log += '<br/>' + 'Manager Rating: ' + (
                    rec.manager_rate_id.name if rec.manager_rate_id else '') + ' → ' + new_manger_rate
                log_post = True

            if vals.get('hr_comment') is not None:
                log += '<br/>' + 'HR Comment: ' + (rec.hr_comment if rec.hr_comment else '') + ' → ' + vals.get(
                    'hr_comment', '')
                log_post = True

            if rec.fixed:
                title = vals.get('title', '')
                weight = vals.get('weight', '')
                description = vals.get('description', '')
                if title != '' or weight != '' or description != '':
                    raise AccessError("Fixed Competencies Cannot be edited")

        res = super(HrAppraisalCompetency, self).write(vals)

        if log_post and rec.related_appraisal_id:
            rec.related_appraisal_id.message_post(body=log)

        return res

    def state_delete(self):
        """ update state to delete and restrict delete if fixed=True """
        if self.fixed:
            raise AccessError("Fixed Competencies Cannot be deleted")
        self.write({'state': 'deleted'})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def state_restore(self):
        """ update state to active """
        self.write({'state': 'active'})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def _check_stage_rule_approve_competencies(self):
        for rec in self:
            if (
                    rec.related_employee_id.user_id == rec.env.user and rec.related_appraisal_id.stage_id.employee_can_approve_approve_competency) or (
                    rec.related_appraisal_id.appraisal_manager.user_id == rec.env.user and rec.related_appraisal_id.stage_id.manager_can_approve_approve_competency) \
                    or rec.env.user in rec.related_appraisal_id.stage_id.users_can_approve_approve_competency:
                rec.can_approve_competencies = True
            else:
                rec.can_approve_competencies = False


    def _check_stage_rule_hr_comment(self):
        for rec in self:
            if (
                    rec.related_employee_id.user_id == rec.env.user and rec.related_appraisal_id.stage_id.employee_can_comment_competency_hr) or (
                    rec.related_appraisal_id.appraisal_manager.user_id == rec.env.user and rec.related_appraisal_id.stage_id.manager_can_comment_competency_hr) \
                    or rec.env.user in rec.related_appraisal_id.stage_id.users_can_comment_competency_hr:
                rec.can_comment_competency_hr = True
            else:
                rec.can_comment_competency_hr = False


    def _check_stage_rule_manager_comment(self):
        for rec in self:
            if (
                    rec.related_employee_id.user_id == rec.env.user and rec.related_appraisal_id.stage_id.employee_can_comment_competency_manager) or (
                    rec.related_appraisal_id.appraisal_manager.user_id == rec.env.user and rec.related_appraisal_id.stage_id.manager_can_comment_competency_manager) \
                    or rec.env.user in rec.related_appraisal_id.stage_id.users_can_comment_competency_manager:
                rec.can_comment_competency_manager = True
            else:
                rec.can_comment_competency_manager = False


    def _check_stage_rule_employee_comment(self):
        for rec in self:
            if (
                    rec.related_employee_id.user_id == rec.env.user and rec.related_appraisal_id.stage_id.employee_can_comment_competency_employee) or (
                    rec.related_appraisal_id.appraisal_manager.user_id == rec.env.user and rec.related_appraisal_id.stage_id.manager_can_comment_competency_employee) \
                    or rec.env.user in rec.related_appraisal_id.stage_id.users_can_comment_competency_employee:
                rec.can_comment_competency_employee = True
            else:
                rec.can_comment_competency_employee = False


    def _check_stage_rule_hr_see_comment(self):
        for rec in self:
            if (
                    rec.related_employee_id.user_id == rec.env.user and rec.related_appraisal_id.stage_id.employee_can_see_comment_competency_hr) or (
                    rec.related_appraisal_id.appraisal_manager.user_id == rec.env.user and rec.related_appraisal_id.stage_id.manager_can_see_comment_competency_hr) \
                    or rec.env.user in rec.related_appraisal_id.stage_id.users_can_see_comment_competency_hr:
                rec.can_see_comment_competency_hr = True
            else:
                rec.can_see_comment_competency_hr = False

    can_see_comment_competency_manager = fields.Boolean('Can See Manager Comment',
                                                        compute='_check_stage_rule_manager_see_comment')
    can_see_comment_competency_employee = fields.Boolean('Can See Employee Comment',
                                                         compute='_check_stage_rule_employee_see_comment')
    can_rate_objective_manager = fields.Boolean('Can Manager Rate', compute='_check_stage_rule_manager_rate')


    def _check_stage_rule_manager_see_comment(self):
        for rec in self:
            if (
                    rec.related_employee_id.user_id == rec.env.user and rec.related_appraisal_id.stage_id.employee_can_see_comment_competency_manager) or (
                    rec.related_appraisal_id.appraisal_manager.user_id == rec.env.user and rec.related_appraisal_id.stage_id.manager_can_see_comment_competency_manager) \
                    or rec.env.user in rec.related_appraisal_id.stage_id.users_can_see_comment_competency_manager:
                rec.can_see_comment_competency_manager = True
            else:
                rec.can_see_comment_competency_manager = False

    #
    def _check_stage_rule_employee_see_comment(self):
        for rec in self:
            if (
                    rec.related_employee_id.user_id == rec.env.user and rec.related_appraisal_id.stage_id.employee_can_see_comment_competency_employee) or (
                    rec.related_appraisal_id.appraisal_manager.user_id == rec.env.user and rec.related_appraisal_id.stage_id.manager_can_see_comment_competency_employee) \
                    or rec.env.user in rec.related_appraisal_id.stage_id.users_can_see_comment_competency_employee:
                rec.can_see_comment_competency_employee = True
            else:
                rec.can_see_comment_competency_employee = False


    def _check_stage_rule_manager_rate(self):
        for rec in self:
            if (
                    rec.related_employee_id.user_id == rec.env.user and rec.related_appraisal_id.stage_id.employee_rating_manager_add) or (
                    rec.related_appraisal_id.appraisal_manager.user_id == rec.env.user and rec.related_appraisal_id.stage_id.manager_rating_manager_add) \
                    or rec.env.user in rec.related_appraisal_id.stage_id.users_rating_manager_add:
                rec.can_rate_competency_manager = True
            else:
                rec.can_rate_competency_manager = False


    def _check_stage_rule_employee_rate(self):
        for rec in self:
            if (
                    rec.related_employee_id.user_id == rec.env.user and rec.related_appraisal_id.stage_id.employee_rating_employee_add) or (
                    rec.related_appraisal_id.appraisal_manager.user_id == rec.env.user and rec.related_appraisal_id.stage_id.manager_rating_employee_add) \
                    or rec.env.user in rec.related_appraisal_id.stage_id.users_rating_employee_add:
                rec.can_rate_competency_employee = True
            else:
                rec.can_rate_competency_employee = False


    def _check_stage_rule_manager_see_rate(self):
        for rec in self:
            if (
                    rec.related_employee_id.user_id == rec.env.user and rec.related_appraisal_id.stage_id.employee_rating_manager_see) or (
                    rec.related_appraisal_id.appraisal_manager.user_id == rec.env.user and rec.related_appraisal_id.stage_id.manager_rating_manager_see) \
                    or rec.env.user in rec.related_appraisal_id.stage_id.users_rating_manager_see:
                rec.can_see_rate_competency_manager = True
            else:
                rec.can_see_rate_competency_manager = False


    def _check_stage_rule_employee_see_rate(self):
        for rec in self:
            if (
                    rec.related_employee_id.user_id == rec.env.user and rec.related_appraisal_id.stage_id.employee_rating_employee_see) or (
                    rec.related_appraisal_id.appraisal_manager.user_id == rec.env.user and rec.related_appraisal_id.stage_id.manager_rating_employee_see) \
                    or rec.env.user in rec.related_appraisal_id.stage_id.users_rating_employee_see:
                rec.can_see_rate_competency_employee = True
            else:
                rec.can_see_rate_competency_employee = False
