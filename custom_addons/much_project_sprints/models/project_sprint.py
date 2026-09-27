from odoo import models, fields, api
from odoo.exceptions import ValidationError



class ProjectSprint(models.Model):

    _name = 'project.sprint'
    _description = 'Project Sprint'
    _order = 'date_start desc'

    name = fields.Char(
        required=True
    )
    
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True
    )

    date_start = fields.Date(
        string='Start Date',
        required=True
    )

    date_end = fields.Date(
        string='End Date',
        required=True
    )

    state = fields.Selection(
        [
            ('open', 'Open'),
            ('active', 'Active'),
            ('closed', 'Closed'),
        ],
        default='open',
        required=True,
        tracking=True
    )

    task_ids = fields.One2many(
        'project.task',
        'sprint_id',
        string='Tasks'
    )

    task_count = fields.Integer(
        compute='_compute_task_count'
    )


    @api.depends('task_ids')
    def _compute_task_count(self):
        for sprint in self:
            sprint.task_count = len(sprint.task_ids)


    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for sprint in self:
            if sprint.date_start > sprint.date_end:
                raise ValidationError('The start date cannot be later than the end date.')