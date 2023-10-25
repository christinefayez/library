from odoo import fields, models, api
from odoo.exceptions import ValidationError, AccessError


class HrObjectiveCategory(models.Model):
    _name = 'hr.objective.category'

    name = fields.Char('Category')


class HrObjective(models.Model):
    _name = 'hr.objective'

    code = fields.Char('Code')
    name = fields.Char('Objective')
    description = fields.Text('Description')
    category = fields.Many2one('hr.objective.category', 'Category')


rating_values = [
    ('0', 'Select Rating'),
    ('1', '1 - Not Satisfied'),
    ('2', '2 - Needs Improvements'),
    ('3', '3 - Satisfied'),
    ('4', '4 - Very Satisfied'),
    ('5', '5 - Excellent'),
]


class HrAppraisalObjective(models.Model):
    _name = 'hr.appraisal.objective'

    changed_employee_rate = fields.Boolean(default=False)
    @api.onchange('employee_rate_id')
    def change_flag_employee_change(self):
        if self.related_appraisal:
            self.changed_employee_rate = True
    changed_manager_rate = fields.Boolean(default=False)
    @api.onchange('manager_rate_id')
    def change_flag_manager_change(self):
        if self.related_appraisal:
            self.changed_manager_rate = True
    name = fields.Many2one('hr.objective', 'Objective', required=False)
    title = fields.Text(string='Objective', required=True)
    # manager_rating = fields.Selection(rating_values, 'Manager Rating', default='0')
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
    weight = fields.Float('Weight', required=True)
    state = fields.Selection([('active', 'Active'), ('deleted', 'Deleted')], 'State',
                             default='active')
    fixed = fields.Boolean('Default Objective')
    related_employee = fields.Many2one(related="related_appraisal.employee_id")
    related_appraisal = fields.Many2one('hr.appraisal', 'Related Appraisal')
    related_appraisal_forms = fields.Many2one('hr.appraisal.form', 'Related Appraisal Forms')
    manager_comment = fields.Text('Manager Comment')
    employee_comment = fields.Text('Employee Comment')
    hr_comment = fields.Text('HR Comment')
    # comments = fields.One2many('hr.appraisal.comment', 'related_objective', 'Comments')
    description = fields.Text(string="Description", readonly=False, required=True)
    attachment_ids = fields.Many2many(comodel_name="ir.attachment",
                                      relation="ebs_mod_m2m_hr_appraisal_objective",
                                      column1="appraisal_objective_id",
                                      column2="attachment_id",
                                      string="Employee Attachment"
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
        return [(value.id, "%s" % value.title) for value in self]

    def unlink(self):
        for rec in self:
            if rec.fixed:
                raise AccessError("Fixed Objectives Cannot be deleted")
        return super(HrAppraisalObjective, self).unlink()

    def write(self, vals):
        log_post = False
        for rec in self:
            log = 'Objective: ' + (
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
                    rec.employee_rate_id.name if rec.employee_rate_id else '') + ' → ' + new_manger_rate
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
                    raise AccessError("Fixed Objectives Cannot be edited")

        res = super(HrAppraisalObjective, self).write(vals)

        if log_post and rec.related_appraisal:
            rec.related_appraisal.message_post(body=log)

        return res

    # @api.onchange('manager_rating', 'employee_rating')
    # def onchange_rating(self):
    #     if self.manager_rating > 5 or self.manager_rating < 0 or self.employee_rating > 5 or self.employee_rating < 0:
    #         raise ValidationError("Rating must be between 0 and 5 !")

    # def state_approve(self):
    #     for rec in self:
    #         rec.state = 'approved'
    #
    # def state_disapprove(self):
    #     self.state = 'pending'

    def state_delete(self):
        if self.fixed:
            raise AccessError("Fixed Objectives Cannot be deleted")
        self.write({'state': 'deleted'})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def state_restore(self):
        self.write({'state': 'active'})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    can_approve_objectives = fields.Boolean('Can Approve Objectives', compute='_check_stage_rule_approve_objectives')

    def _check_stage_rule_approve_objectives(self):
        for rec in self:
            if (
                    rec.related_employee.user_id == rec.env.user and rec.related_appraisal.stage_id.employee_can_approve_approve) or (
                    rec.related_appraisal.appraisal_manager.user_id == rec.env.user and rec.related_appraisal.stage_id.manager_can_approve_approve) \
                    or rec.env.user in rec.related_appraisal.stage_id.users_can_approve_approve:
                rec.can_approve_objectives = True
            else:
                rec.can_approve_objectives = False

    can_comment_objective_hr = fields.Boolean('Can HR Comment', compute='_check_stage_rule_hr_comment')

    def _check_stage_rule_hr_comment(self):
        for rec in self:
            if (
                    rec.related_employee.user_id == rec.env.user and rec.related_appraisal.stage_id.employee_can_comment_objective_hr) or (
                    rec.related_appraisal.appraisal_manager.user_id == rec.env.user and rec.related_appraisal.stage_id.manager_can_comment_objective_hr) \
                    or rec.env.user in rec.related_appraisal.stage_id.users_can_comment_objective_hr:
                rec.can_comment_objective_hr = True
            else:
                rec.can_comment_objective_hr = False

    can_comment_objective_manager = fields.Boolean('Can Manager Comment', compute='_check_stage_rule_manager_comment')

    def _check_stage_rule_manager_comment(self):
        for rec in self:
            if (
                    rec.related_employee.user_id == rec.env.user and rec.related_appraisal.stage_id.employee_can_comment_objective_manager) or (
                    rec.related_appraisal.appraisal_manager.user_id == rec.env.user and rec.related_appraisal.stage_id.manager_can_comment_objective_manager) \
                    or rec.env.user in rec.related_appraisal.stage_id.users_can_comment_objective_manager:
                rec.can_comment_objective_manager = True
            else:
                rec.can_comment_objective_manager = False

    can_comment_objective_employee = fields.Boolean('Can Employee Comment',
                                                    compute='_check_stage_rule_employee_comment')


    def _check_stage_rule_employee_comment(self):
        for rec in self:
            if (
                    rec.related_employee.user_id == rec.env.user and rec.related_appraisal.stage_id.employee_can_comment_objective_employee) or (
                    rec.related_appraisal.appraisal_manager.user_id == rec.env.user and rec.related_appraisal.stage_id.manager_can_comment_objective_employee) \
                    or rec.env.user in rec.related_appraisal.stage_id.users_can_comment_objective_employee:
                rec.can_comment_objective_employee = True
            else:
                rec.can_comment_objective_employee = False

    can_see_comment_objective_hr = fields.Boolean('Can See HR Comment', compute='_check_stage_rule_hr_see_comment')


    def _check_stage_rule_hr_see_comment(self):
        for rec in self:
            if (
                    rec.related_employee.user_id == rec.env.user and rec.related_appraisal.stage_id.employee_can_see_comment_objective_hr) or (
                    rec.related_appraisal.appraisal_manager.user_id == rec.env.user and rec.related_appraisal.stage_id.manager_can_see_comment_objective_hr) \
                    or rec.env.user in rec.related_appraisal.stage_id.users_can_see_comment_objective_hr:
                rec.can_see_comment_objective_hr = True
            else:
                rec.can_see_comment_objective_hr = False

    can_see_comment_objective_manager = fields.Boolean('Can See Manager Comment',
                                                       compute='_check_stage_rule_manager_see_comment')


    def _check_stage_rule_manager_see_comment(self):
        for rec in self:
            if (
                    rec.related_employee.user_id == rec.env.user and rec.related_appraisal.stage_id.employee_can_see_comment_objective_manager) or (
                    rec.related_appraisal.appraisal_manager.user_id == rec.env.user and rec.related_appraisal.stage_id.manager_can_see_comment_objective_manager) \
                    or rec.env.user in rec.related_appraisal.stage_id.users_can_see_comment_objective_manager:
                rec.can_see_comment_objective_manager = True
            else:
                rec.can_see_comment_objective_manager = False

    can_see_comment_objective_employee = fields.Boolean('Can See Employee Comment',
                                                        compute='_check_stage_rule_employee_see_comment')

    #
    def _check_stage_rule_employee_see_comment(self):
        for rec in self:
            if (
                    rec.related_employee.user_id == rec.env.user and rec.related_appraisal.stage_id.employee_can_see_comment_objective_employee) or (
                    rec.related_appraisal.appraisal_manager.user_id == rec.env.user and rec.related_appraisal.stage_id.manager_can_see_comment_objective_employee) \
                    or rec.env.user in rec.related_appraisal.stage_id.users_can_see_comment_objective_employee:
                rec.can_see_comment_objective_employee = True
            else:
                rec.can_see_comment_objective_employee = False

    can_rate_objective_manager = fields.Boolean('Can Manager Rate', compute='_check_stage_rule_manager_rate')


    def _check_stage_rule_manager_rate(self):
        for rec in self:
            if (
                    rec.related_employee.user_id == rec.env.user and rec.related_appraisal.stage_id.employee_rating_manager_add) or (
                    rec.related_appraisal.appraisal_manager.user_id == rec.env.user and rec.related_appraisal.stage_id.manager_rating_manager_add) \
                    or rec.env.user in rec.related_appraisal.stage_id.users_rating_manager_add:
                rec.can_rate_objective_manager = True
            else:
                rec.can_rate_objective_manager = False

    can_rate_objective_employee = fields.Boolean('Can Employee Rate', compute='_check_stage_rule_employee_rate')


    def _check_stage_rule_employee_rate(self):
        for rec in self:
            if (
                    rec.related_employee.user_id == rec.env.user and rec.related_appraisal.stage_id.employee_rating_employee_add) or (
                    rec.related_appraisal.appraisal_manager.user_id == rec.env.user and rec.related_appraisal.stage_id.manager_rating_employee_add) \
                    or rec.env.user in rec.related_appraisal.stage_id.users_rating_employee_add:
                rec.can_rate_objective_employee = True
            else:
                rec.can_rate_objective_employee = False

    can_see_rate_objective_manager = fields.Boolean('Can See Manager Rate',
                                                    compute='_check_stage_rule_manager_see_rate')

    def _check_stage_rule_manager_see_rate(self):
        for rec in self:
            if (
                    rec.related_employee.user_id == rec.env.user and rec.related_appraisal.stage_id.employee_rating_manager_see) or (
                    rec.related_appraisal.appraisal_manager.user_id == rec.env.user and rec.related_appraisal.stage_id.manager_rating_manager_see) \
                    or rec.env.user in rec.related_appraisal.stage_id.users_rating_manager_see:
                rec.can_see_rate_objective_manager = True
            else:
                rec.can_see_rate_objective_manager = False

    can_see_rate_objective_employee = fields.Boolean('Can See Employee Rate',
                                                     compute='_check_stage_rule_employee_see_rate')


    def _check_stage_rule_employee_see_rate(self):
        for rec in self:
            if (
                    rec.related_employee.user_id == rec.env.user and rec.related_appraisal.stage_id.employee_rating_employee_see) or (
                    rec.related_appraisal.appraisal_manager.user_id == rec.env.user and rec.related_appraisal.stage_id.manager_rating_employee_see) \
                    or rec.env.user in rec.related_appraisal.stage_id.users_rating_employee_see:
                rec.can_see_rate_objective_employee = True
            else:
                rec.can_see_rate_objective_employee = False
