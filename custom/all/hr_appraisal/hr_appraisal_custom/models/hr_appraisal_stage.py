from odoo import fields, models, api


class HrAppraisalStage(models.Model):
    _name = 'hr.appraisal.stage'

    name = fields.Char("Stage Name", required=True, translate=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")

    can_complete = fields.Boolean(
        string='Can Complete Appraisal',
        required=True, default=False)

    # Appraisal
    employee_allowed_edit = fields.Boolean(string="Employee")
    manager_allowed_edit = fields.Boolean(string="Manager")
    users_allowed_edit = fields.Many2many(relation="user_appraisal_allowed_1", comodel_name='res.users',
                                          string="Users")

    employee_can_add_objective = fields.Boolean(string="Employee")
    manager_can_add_objective = fields.Boolean(string="Manager ")
    users_can_add_objective = fields.Many2many(relation="user_appraisal_allowed_2", comodel_name='res.users',
                                               string="Users")

    employee_can_comment_objective_hr = fields.Boolean(string="Employee")
    manager_can_comment_objective_hr = fields.Boolean(string="Manager")
    users_can_comment_objective_hr = fields.Many2many(relation="user_appraisal_allowed_3", comodel_name='res.users',
                                                      string="Users")

    employee_can_comment_objective_manager = fields.Boolean(string="Employee")
    manager_can_comment_objective_manager = fields.Boolean(string="Manager")
    users_can_comment_objective_manager = fields.Many2many(relation="user_appraisal_allowed_4",
                                                           comodel_name='res.users',
                                                           string="Users")

    employee_can_comment_objective_employee = fields.Boolean(string="Employee")
    manager_can_comment_objective_employee = fields.Boolean(string="Manager")
    users_can_comment_objective_employee = fields.Many2many(relation="user_appraisal_allowed_5",
                                                            comodel_name='res.users',
                                                            string="Users")

    employee_can_see_comment_objective_hr = fields.Boolean(string="Employee")
    manager_can_see_comment_objective_hr = fields.Boolean(string="Manager")
    users_can_see_comment_objective_hr = fields.Many2many(relation="user_appraisal_allowed_6", comodel_name='res.users',

                                                          string="Users")
    employee_can_see_comment_objective_manager = fields.Boolean(string="Employee")
    manager_can_see_comment_objective_manager = fields.Boolean(string="Manager")
    users_can_see_comment_objective_manager = fields.Many2many(relation="user_appraisal_allowed_7",
                                                               comodel_name='res.users',
                                                               string="Users")

    employee_can_see_comment_objective_employee = fields.Boolean(string="Employee")
    manager_can_see_comment_objective_employee = fields.Boolean(string="Manager")
    users_can_see_comment_objective_employee = fields.Many2many(relation="user_appraisal_allowed_8",
                                                                comodel_name='res.users',
                                                                string="Users")

    employee_can_comment_form_hr = fields.Boolean(string="Employee")
    manager_can_comment_form_hr = fields.Boolean(string="Manager")
    users_can_comment_form_hr = fields.Many2many(relation="user_appraisal_allowed_9", comodel_name='res.users',
                                                 string="Users")

    employee_can_comment_form_manager = fields.Boolean(string="Employee")
    manager_can_comment_form_manager = fields.Boolean(string="Manager")
    users_can_comment_form_manager = fields.Many2many(relation="user_appraisal_allowed_10",
                                                      comodel_name='res.users',
                                                      string="Users")

    employee_can_comment_form_employee = fields.Boolean(string="Employee")
    manager_can_comment_form_employee = fields.Boolean(string="Manager")
    users_can_comment_form_employee = fields.Many2many(relation="user_appraisal_allowed_11",
                                                       comodel_name='res.users',
                                                       string="Users")

    employee_can_see_comment_form_hr = fields.Boolean(string="Employee")
    manager_can_see_comment_form_hr = fields.Boolean(string="Manager")
    users_can_see_comment_form_hr = fields.Many2many(relation="user_appraisal_allowed_12", comodel_name='res.users',

                                                     string="Users")
    employee_can_see_comment_form_manager = fields.Boolean(string="Employee")
    manager_can_see_comment_form_manager = fields.Boolean(string="Manager")
    users_can_see_comment_form_manager = fields.Many2many(relation="user_appraisal_allowed_13",
                                                          comodel_name='res.users',
                                                          string="Users")

    employee_can_see_comment_form_employee = fields.Boolean(string="Employee")
    manager_can_see_comment_form_employee = fields.Boolean(string="Manager")
    users_can_see_comment_form_employee = fields.Many2many(relation="user_appraisal_allowed_14",
                                                           comodel_name='res.users',
                                                           string="Users")

    employee_can_modifiy_training = fields.Boolean(string="Employee")
    manager_can_modifiy_training = fields.Boolean(string="Manager")
    users_can_modifiy_training = fields.Many2many(relation="user_appraisal_allowed_15",
                                                  comodel_name='res.users',
                                                  string="Users")

    employee_request_feedback = fields.Boolean(string="Employee")
    manager_request_feedback = fields.Boolean(string="Manager")
    users_request_feedback = fields.Many2many(relation="user_appraisal_allowed_16",
                                              comodel_name='res.users',
                                              string="Users")

    employee_see_feedback = fields.Boolean(string="Employee")
    manager_see_feedback = fields.Boolean(string="Manager")
    users_see_feedback = fields.Many2many(relation="user_appraisal_allowed_17",
                                          comodel_name='res.users',
                                          string="Users")

    employee_take_survey = fields.Boolean(string="Employee", default=False)
    manager_take_survey = fields.Boolean(string="Manager", default=False)
    users_take_survey = fields.Many2many(relation="user_appraisal_allowed_18",
                                         comodel_name='res.users',
                                         string="Users", default=False)
    employee_see_survey = fields.Boolean(string="Employee", default=False)
    manager_see_survey = fields.Boolean(string="Manager", default=False)
    users_see_survey = fields.Many2many(relation="user_appraisal_allowed_19",
                                        comodel_name='res.users',
                                        string="Users", default=False)

    employee_allowed_forward = fields.Boolean(string="Employee")
    manager_allowed_forward = fields.Boolean(string="Manager")
    users_allowed_forward = fields.Many2many(relation="user_appraisal_allowed_20",
                                             comodel_name='res.users',
                                             string="Users")

    log_note_backward = fields.Boolean(string="Log Reason")
    employee_allowed_backward = fields.Boolean(string="Employee")
    manager_allowed_backward = fields.Boolean(string="Manager")
    users_allowed_backward = fields.Many2many(relation="user_appraisal_allowed_21",
                                              comodel_name='res.users',
                                              string="Users")

    employee_can_approve_approve = fields.Boolean(string="Employee")
    manager_can_approve_approve = fields.Boolean(string="Manager")
    users_can_approve_approve = fields.Many2many(relation="user_appraisal_allowed_22",
                                                 comodel_name='res.users',
                                                 string="Users")

    employee_rating_manager_add = fields.Boolean(string="Employee")
    manager_rating_manager_add = fields.Boolean(string="Manager")
    users_rating_manager_add = fields.Many2many(relation="user_appraisal_allowed_23",
                                                comodel_name='res.users',
                                                string="Users")

    employee_rating_employee_add = fields.Boolean(string="Employee")
    manager_rating_employee_add = fields.Boolean(string="Manager")
    users_rating_employee_add = fields.Many2many(relation="user_appraisal_allowed_24",
                                                 comodel_name='res.users',
                                                 string="Users")

    employee_rating_hr_add = fields.Boolean(string="Employee")
    manager_rating_hr_add = fields.Boolean(string="Manager")
    users_rating_hr_add = fields.Many2many(relation="user_appraisal_allowed_25",
                                           comodel_name='res.users',
                                           string="Users")

    employee_rating_manager_see = fields.Boolean(string="Employee")
    manager_rating_manager_see = fields.Boolean(string="Manager")
    users_rating_manager_see = fields.Many2many(relation="user_appraisal_allowed_26",
                                                comodel_name='res.users',
                                                string="Users")

    employee_rating_manager_see_rounded = fields.Boolean(string="Employee")
    manager_rating_manager_see_rounded = fields.Boolean(string="Manager")
    users_rating_manager_see_rounded = fields.Many2many(relation="user_appraisal_allowed_50",
                                                        comodel_name='res.users',
                                                        string="Users")

    employee_rating_employee_see = fields.Boolean(string="Employee")
    manager_rating_employee_see = fields.Boolean(string="Manager")
    users_rating_employee_see = fields.Many2many(relation="user_appraisal_allowed_27",
                                                 comodel_name='res.users',
                                                 string="Users")

    employee_rating_hr_see = fields.Boolean(string="Employee")
    manager_rating_hr_see = fields.Boolean(string="Manager")
    users_rating_hr_see = fields.Many2many(relation="user_appraisal_allowed_28",
                                           comodel_name='res.users',
                                           string="Users")

    # pip fields
    employee_area_development_see = fields.Boolean(string="Employee")
    manager_area_development_see = fields.Boolean(string="Manager")
    users_area_development_see = fields.Many2many(relation="user_appraisal_allowed_29",
                                                  comodel_name='res.users',
                                                  string="Users")

    employee_area_development_add = fields.Boolean(string="Employee")
    manager_area_development_add = fields.Boolean(string="Manager")
    users_area_development_add = fields.Many2many(relation="user_appraisal_allowed_31",
                                                  comodel_name='res.users',
                                                  string="Users")

    employee_first_manager_review_see = fields.Boolean(string="Employee")
    manager_first_manager_review_see = fields.Boolean(string="Manager")
    users_first_manager_review_see = fields.Many2many(relation="user_appraisal_allowed_32",
                                                      comodel_name='res.users',
                                                      string="Users")

    employee_first_manager_review_add = fields.Boolean(string="Employee")
    manager_first_manager_review_add = fields.Boolean(string="Manager")
    users_first_manager_review_add = fields.Many2many(relation="user_appraisal_allowed_33",
                                                      comodel_name='res.users',
                                                      string="Users")

    employee_first_employee_review_see = fields.Boolean(string="Employee")
    manager_first_employee_review_see = fields.Boolean(string="Manager")
    users_first_employee_review_see = fields.Many2many(relation="user_appraisal_allowed_34",
                                                       comodel_name='res.users',
                                                       string="Users")

    employee_first_employee_review_add = fields.Boolean(string="Employee")
    manager_first_employee_review_add = fields.Boolean(string="Manager")
    users_first_employee_review_add = fields.Many2many(relation="user_appraisal_allowed_35",
                                                       comodel_name='res.users',
                                                       string="Users")

    employee_second_manager_review_see = fields.Boolean(string="Employee")
    manager_second_manager_review_see = fields.Boolean(string="Manager")
    users_second_manager_review_see = fields.Many2many(relation="user_appraisal_allowed_36",
                                                       comodel_name='res.users',
                                                       string="Users")

    employee_second_manager_review_add = fields.Boolean(string="Employee")
    manager_second_manager_review_add = fields.Boolean(string="Manager")
    users_second_manager_review_add = fields.Many2many(relation="user_appraisal_allowed_37",
                                                       comodel_name='res.users',
                                                       string="Users")

    employee_second_employee_review_see = fields.Boolean(string="Employee")
    manager_second_employee_review_see = fields.Boolean(string="Manager")
    users_second_employee_review_see = fields.Many2many(relation="user_appraisal_allowed_38",
                                                        comodel_name='res.users',
                                                        string="Users")

    employee_second_employee_review_add = fields.Boolean(string="Employee")
    manager_second_employee_review_add = fields.Boolean(string="Manager")
    users_second_employee_review_add = fields.Many2many(relation="user_appraisal_allowed_39",
                                                        comodel_name='res.users',
                                                        string="Users")

    employee_third_manager_review_see = fields.Boolean(string="Employee")
    manager_third_manager_review_see = fields.Boolean(string="Manager")
    users_third_manager_review_see = fields.Many2many(relation="user_appraisal_allowed_40",
                                                      comodel_name='res.users',
                                                      string="Users")

    employee_third_manager_review_add = fields.Boolean(string="Employee")
    manager_third_manager_review_add = fields.Boolean(string="Manager")
    users_third_manager_review_add = fields.Many2many(relation="user_appraisal_allowed_41",
                                                      comodel_name='res.users',
                                                      string="Users")

    employee_third_employee_review_see = fields.Boolean(string="Employee")
    manager_third_employee_review_see = fields.Boolean(string="Manager")
    users_third_employee_review_see = fields.Many2many(relation="user_appraisal_allowed_42",
                                                       comodel_name='res.users',
                                                       string="Users")

    employee_third_employee_review_add = fields.Boolean(string="Employee")
    manager_third_employee_review_add = fields.Boolean(string="Manager")
    users_third_employee_review_add = fields.Many2many(relation="user_appraisal_allowed_43",
                                                       comodel_name='res.users',
                                                       string="Users")

    employee_manager_final_decision_see = fields.Boolean(string="Employee")
    manager_manager_final_decision_see = fields.Boolean(string="Manager")
    users_manager_final_decision_see = fields.Many2many(relation="user_appraisal_allowed_44",
                                                        comodel_name='res.users',
                                                        string="Users")

    employee_manager_final_decision_add = fields.Boolean(string="Employee")
    manager_manager_final_decision_add = fields.Boolean(string="Manager")
    users_manager_final_decision_add = fields.Many2many(relation="user_appraisal_allowed_45",
                                                        comodel_name='res.users',
                                                        string="Users")

    employee_manager_final_comments_see = fields.Boolean(string="Employee")
    manager_manager_final_comments_see = fields.Boolean(string="Manager")
    users_manager_final_comments_see = fields.Many2many(relation="user_appraisal_allowed_46",
                                                        comodel_name='res.users',
                                                        string="Users")

    employee_manager_final_comments_add = fields.Boolean(string="Employee")
    manager_manager_final_comments_add = fields.Boolean(string="Manager")
    users_manager_final_comments_add = fields.Many2many(relation="user_appraisal_allowed_47",
                                                        comodel_name='res.users',
                                                        string="Users")

    employee_can_approve_approve_competency = fields.Boolean(
        string="Employee",
    )
    manager_can_approve_approve_competency = fields.Boolean(
        string="Manager",
    )
    users_can_approve_approve_competency = fields.Many2many(
        relation="user_appraisal_allowed_48",
        comodel_name='res.users',
        string="Users",
    )
    employee_can_add_competency = fields.Boolean(
        string="Employee",
    )
    manager_can_add_competency = fields.Boolean(
        string="Manager",
    )
    users_can_add_competency = fields.Many2many(
        relation="user_appraisal_allowed_49",
        comodel_name='res.users',
        string="Users",
    )

    employee_can_comment_competency_hr = fields.Boolean(
        string="Employee",
    )
    manager_can_comment_competency_hr = fields.Boolean(
        string="Manager",
    )
    users_can_comment_competency_hr = fields.Many2many(
        relation="user_appraisal_allowed_51",
        comodel_name='res.users',
        string="Users",
    )

    employee_can_comment_competency_manager = fields.Boolean(
        string="Employee",
    )
    manager_can_comment_competency_manager = fields.Boolean(
        string="Manager",
    )
    users_can_comment_competency_manager = fields.Many2many(
        relation="user_appraisal_allowed_52",
        comodel_name='res.users',
        string="Users",
    )

    employee_can_comment_competency_employee = fields.Boolean(
        string="Employee",
    )
    manager_can_comment_competency_employee = fields.Boolean(
        string="Manager",
    )
    users_can_comment_competency_employee = fields.Many2many(
        relation="user_appraisal_allowed_53",
        comodel_name='res.users',
        string="Users",
    )

    employee_can_see_comment_competency_hr = fields.Boolean(
        string="Employee",
    )
    manager_can_see_comment_competency_hr = fields.Boolean(
        string="Manager",
    )
    users_can_see_comment_competency_hr = fields.Many2many(
        relation="user_appraisal_allowed_54",
        comodel_name='res.users',
        string="Users",
    )
    employee_can_see_comment_competency_manager = fields.Boolean(
        string="Employee",
    )
    manager_can_see_comment_competency_manager = fields.Boolean(
        string="Manager",
    )
    users_can_see_comment_competency_manager = fields.Many2many(
        relation="user_appraisal_allowed_55",
        comodel_name='res.users',
        string="Users",
    )

    employee_can_see_comment_competency_employee = fields.Boolean(
        string="Employee",
    )
    manager_can_see_comment_competency_employee = fields.Boolean(
        string="Manager",
    )
    users_can_see_comment_competency_employee = fields.Many2many(
        relation="user_appraisal_allowed_56",
        comodel_name='res.users',
        string="Users",
    )
