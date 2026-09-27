from odoo import models, fields



class ProjectTask(models.Model):

    _inherit = 'project.task'

    sprint_id = fields.Many2one(
        'project.sprint',
        string='Sprint',
        domain="[('project_id', '=', project_id)]"
    )
    # INFO: the domain guarantees that we can only choose one of the Sprints associated with the the task's project.