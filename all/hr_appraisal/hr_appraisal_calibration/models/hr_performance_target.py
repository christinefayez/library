# -*- coding: utf-8 -*-

from odoo import models, fields


class HrPerformanceTarget(models.Model):
    _name = 'hr.performance.target'

    name = fields.Char(string="Performance Level")
    min = fields.Integer(string="Minimum Percentage")
    max = fields.Integer(string="Maximum Percentage")
    target = fields.Integer(string="Target")

    calibration_id = fields.Many2one('hr.calibration', string="Calibration")
