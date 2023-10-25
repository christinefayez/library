from odoo import tools
from odoo import api, fields, models
from datetime import datetime, timedelta


class CalibrationView(models.Model):
    _name = "calibration.report.view"
    _description = "Calibration Report View"
    _order = 'target'

    target = fields.Integer(string="Rate", readonly=True)
    target_name = fields.Char(string="Performance Level", readonly=True)
    min_perc = fields.Integer(string="Minimum Percentage", readonly=True)
    max_perc = fields.Integer(string="Maximum Percentage", readonly=True)
    target_appraisals = fields.Integer(string="# of Employees", readonly=True)
    total_appraisals = fields.Integer('Total of Appraisal', readonly=True)
    percentage = fields.Float('%', readonly=True)

    year = fields.Char(string="Year", readonly=True)

    # contract_subgroups_ids = fields.Many2many(
    #     comodel_name='hr.contract.subgroup',
    #     string='Subgroups')
    random_uid = fields.Char(
        string='Random UID',
        required=False)

    def run_calibration_cleaner(self):
        self = self.sudo()
        calibration_not_grouped = self.env['calibration.report.view'].search(
            [('create_date', '<', datetime.now() - timedelta(days=1))])
        calibration_grouped_d = self.env['calibration.report.view.grouped.d'].search(
            [('create_date', '<', datetime.now() - timedelta(days=1))])
        calibration_grouped_r = self.env['calibration.report.view.grouped.r'].search(
            [('create_date', '<', datetime.now() - timedelta(days=1))])

        for c in calibration_not_grouped:
            c.unlink()
        for c in calibration_grouped_d:
            c.unlink()
        for c in calibration_grouped_r:
            c.unlink()


class CalibrationViewGroupedDepartment(models.Model):
    _name = "calibration.report.view.grouped.d"
    _description = "Calibration Report Grouped Department View"
    _order = 'department,target'

    department = fields.Many2one(comodel_name='hr.department', string='Department', domain=[('type', '=', 'BD')])
    target = fields.Integer(string="Rate", readonly=True)
    target_name = fields.Char(string="Performance Level", readonly=True)
    min_perc = fields.Integer(string="Minimum Percentage", readonly=True)
    max_perc = fields.Integer(string="Maximum Percentage", readonly=True)
    target_appraisals = fields.Integer(string="# of Employees", readonly=True)
    total_appraisals = fields.Integer('Total of Appraisal', readonly=True)
    percentage = fields.Float('%', readonly=True)

    year = fields.Char(string="Year", readonly=True)

    # contract_subgroups_ids = fields.Many2many(
    #     comodel_name='hr.contract.subgroup',
    #     string='Subgroups')
    random_uid = fields.Char(
        string='Random UID',
        required=False)


class CalibrationViewGroupedRating(models.Model):
    _name = "calibration.report.view.grouped.r"
    _description = "Calibration Report Grouped Rating View"
    _order = 'target,department'

    department = fields.Many2one(comodel_name='hr.department', string='Department', domain=[('type', '=', 'BD')])
    target = fields.Integer(string="Rate", readonly=True)
    target_name = fields.Char(string="Performance Level", readonly=True)
    min_perc = fields.Integer(string="Minimum Percentage", readonly=True)
    max_perc = fields.Integer(string="Maximum Percentage", readonly=True)
    target_appraisals = fields.Integer(string="# of Employees", readonly=True)
    total_appraisals = fields.Integer('Total of Appraisal', readonly=True)
    percentage = fields.Float('%', readonly=True)

    year = fields.Char(string="Year", readonly=True)

    # contract_subgroups_ids = fields.Many2many(
    #     comodel_name='hr.contract.subgroup',
    #     string='Subgroups')
    random_uid = fields.Char(
        string='Random UID',
        required=False)
