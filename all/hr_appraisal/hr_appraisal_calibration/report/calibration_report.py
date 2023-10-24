from odoo import tools
from odoo import api, fields, models


class CalibrationView(models.Model):
    _name = "calibration.view"
    _description = "Calibration View"
    _auto = False
    _order = 'target'

    id = fields.Integer(string="ID", readonly=True)
    target = fields.Integer(string="Rate", readonly=True)
    target_name = fields.Char(string="Performance Level", readonly=True)
    min_perc = fields.Integer(string="Minimum Percentage", readonly=True)
    max_perc = fields.Integer(string="Maximum Percentage", readonly=True)
    target_appraisals = fields.Integer(string="# of Employees", readonly=True)
    total_appraisals = fields.Integer('Total of Appraisal', readonly=True)
    percentage = fields.Float('%', readonly=True)

    year = fields.Char(string="Year", readonly=True)

    # group = fields.Many2one('hr.department', string='Group', domain=[('type', '=', 'BU')], readonly=True)
    # department = fields.Many2one('hr.department', string='Department', domain=[('type', '=', 'BD')], readonly=True)
    # section = fields.Many2one('hr.department', string='Section', domain=[('type', '=', 'BS')])
    # subsection = fields.Many2one('hr.department', string='Subsection', domain=[('type', '=', 'SS')])
    # employee = fields.Many2one(comodel_name='hr.employee', string='Employee', readonly=True)
    #
    # grade = fields.Many2one(comodel_name='job.grade', string="Employee Grade", readonly=True)
    #
    # job_title = fields.Char(string="Job Title", readonly=True)
    # contract_group = fields.Many2one(comodel_name='hr.contract.group', string='Contract Group', readonly=True)
    # contract_subgroup = fields.Many2one('hr.contract.subgroup', 'Contract Subgroup', readonly=True)

    def init(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:06/09/2020
        Func: This method use for the get fields value for the Calibration View
        :return: N/A
        """
        tools.drop_view_if_exists(self._cr, 'calibration_view')
        # self._cr.execute("""CREATE OR REPLACE VIEW calibration_view AS (SELECT ROW_NUMBER () OVER (ORDER BY ap.id) as id,
        #                                        pt.target AS target,
        #                                        pt.name AS target_name,
        #                                        pt.min AS min_perc,
        #                                        pt.max AS max_perc,
        #                                        (SELECT COUNT(appr.id)
        #                                         FROM   hr_appraisal appr
        #                                         WHERE  appr.id = ap.id
        #                                                    AND appr.hr_overall_rating = pt.target) AS target_appraisals,
        #                                        (SELECT COUNT(appr.id)
        #                                         FROM   hr_appraisal appr
        #                                         WHERE  appr.hr_overall_rating != 0)        AS total_appraisals,
        #                                        CASE
        #                                          WHEN (SELECT COUNT(appr.id)
        #                                                FROM   hr_appraisal appr
        #                                                WHERE  appr.hr_overall_rating != 0) != 0 THEN (
        #                                          (SELECT COUNT(appr.id)
        #                                           FROM   hr_appraisal
        #                                                  appr
        #                                           WHERE  appr.id = ap.id
        #                                                    AND appr.hr_overall_rating = pt.target) /
        #                                            (SELECT COUNT(appr.id)
        #                                             FROM   hr_appraisal appr
        #                                             WHERE  appr.hr_overall_rating != 0) * 100 )
        #                                          ELSE 0
        #                                        END                                             AS percentage,
        #                                        ap.year                                         AS YEAR,
        #                                        ap.GROUP                                        AS GROUP,
        #                                        ap.department                                   AS department,
        #                                        ap.section                                      AS section,
        #                                        ap.subsection                                   AS subsection,
        #                                        ap.employee_id                                  AS employee,
        #                                        ap.employee_grade                               AS grade,
        #                                        ap.employee_job_title                           AS job_title,
        #                                        ct.contract_group                               AS contract_group,
        #                                        ct.contract_subgroup                            AS contract_subgroup
        #                                 FROM   hr_performance_target pt
        #                                        LEFT JOIN hr_calibration cl
        #                                               ON pt.calibration_id = cl.id
        #                                        LEFT JOIN hr_appraisal ap
        #                                               ON ap.year = cl.year
        #                                                  AND ap.stage_id = (SELECT st.id
        #                                                                     FROM   hr_appraisal_stage st
        #                                                                     WHERE  st.is_calibration = true)
        #                                        LEFT JOIN hr_employee em
        #                                               ON em.id = ap.employee_id
        #                                        LEFT JOIN hr_contract ct
        #                                               ON ct.id = em.contract_id
        #                                 WHERE (SELECT COUNT(appr.id)
        #                                         FROM   hr_appraisal appr
        #                                         WHERE  appr.id = ap.id
        #                                                AND appr.hr_overall_rating != 0) != 0
        #                                 ORDER  BY pt.target asc )""")
        self._cr.execute("""CREATE OR REPLACE VIEW calibration_view AS ((select ROW_NUMBER () OVER (ORDER BY pt.target) as id, pt.target as target, pt.name as target_name, pt.min as min_perc, pt.max as max_perc ,
                               (select count(appr.id) from hr_appraisal appr where appr.year = ap.year and appr.hr_overall_rating = pt.target and appr.active = true) as target_appraisals,
                               (select count(appr.id) from hr_appraisal appr where appr.year = ap.year and appr.active = true) as total_appraisals,
                               CASE WHEN (select count(appr.id) from hr_appraisal appr where appr.year = ap.year and appr.active = true) != 0 THEN (
                                (select cast(count(appr.id) as float) from hr_appraisal appr where appr.year = ap.year and appr.hr_overall_rating = pt.target and appr.active = true)
                                /
                                (select count(appr.id) from hr_appraisal appr where appr.year = ap.year and appr.active = true)
                               * 100) ELSE 0 END as percentage,ap.year as year
                        from hr_performance_target pt left join hr_calibration cl on pt.calibration_id = cl.id
                                                      left join hr_appraisal ap on ap.year = cl.year
                        							  left join hr_appraisal_form af on af.id = ap.appraisal_form
 						where af.includes_calibration = true and ap.active = true
 						group by pt.target, pt.name, pt.min, pt.max, ap.year
                        order by pt.target asc)
UNION
(select 1000000 as id, 0 as target, 'No Rating' as target_name, 0 as min_perc, 0 as max_perc ,
                               (select count(appr.id) from hr_appraisal appr where appr.year = ap.year and appr.hr_overall_rating = 0 and appr.active = true) as target_appraisals,
                               (select count(appr.id) from hr_appraisal appr where appr.year = ap.year and appr.active = true) as total_appraisals,
                               CASE WHEN (select count(appr.id) from hr_appraisal appr where appr.year = ap.year and appr.active = true) != 0 THEN (
                                (select cast(count(appr.id) as float) from hr_appraisal appr where appr.year = ap.year and appr.hr_overall_rating = 0 and appr.active = true)
                                /
                                (select count(appr.id) from hr_appraisal appr where appr.year = ap.year and appr.active = true)
                               * 100) ELSE 0 END as percentage,ap.year as year
                        from hr_performance_target pt left join hr_calibration cl on pt.calibration_id = cl.id
                                                      left join hr_appraisal ap on ap.year = cl.year
                       								  left join hr_appraisal_form af on af.id = ap.appraisal_form
 						where af.includes_calibration = true and ap.active = true
 						group by pt.target, pt.name, pt.min, pt.max, ap.year
                        order by pt.target asc))""")
