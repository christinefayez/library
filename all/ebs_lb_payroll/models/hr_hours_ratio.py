# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HoursRatio(models.Model):
    _name = 'hr.hours.ratio'

    name = fields.Char("Name")
    hour_ratio = fields.Float("Hour Ratio")
    hours_type = fields.Selection([('overtime','Overtime'), ('delay','Delay')],string="Hour Type")
    day_type = fields.Selection([('weekend','Weekend'), ('working day','Working Day'),
                                 ('public holiday','Public Holiday')],string="Day Type")
    # day_period = fields.Selection([('morning','Morning'),('afternoon','Night'),('all_day','Any Time Of Day')],default="all_day")
    time_frame = fields.Selection([('15:19','From 3 PM to 7 PM'),('19:7','From 7 PM to 7 AM')])
    assign_type = fields.Selection([('departments','Departments'),('employees','Employees'),('grades','Grades')],string="Apply On")
    department_ids = fields.Many2many('hr.department',string='Departments')
    employee_ids = fields.Many2many('hr.employee',string="Employees")
    grade_ids = fields.Many2many('job.grade',string="Grades")
