from odoo import models, fields, api

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Low'),
    ('2', 'Medium'),
    ('3', 'Height')
]


class Project(models.Model):
    _inherit = 'project.project'
    _order = "priority desc,sequence, name, id"

    priority = fields.Selection(AVAILABLE_PRIORITIES, "Priority", default='0')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    priority = fields.Selection(related='project_id.priority', string="Priority", default='0', readonly=0,store=True)
