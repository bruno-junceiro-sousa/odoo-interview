from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class ProjectTask(models.Model):

    _inherit = 'project.task'

    sprint_id = fields.Many2one(
        'project.sprint',
        string='Sprint',
        domain="[('project_id', '=', project_id), ('state', '!=', 'closed')]",
        tracking=True,
        index='btree_not_null'
    )
    # INFO: the domain guarantees that we can only choose one of the Sprints associated with the the task's project.


    @api.constrains('sprint_id', 'project_id')
    def _check_sprint_project(self):
        
        for task in self.filtered('sprint_id'):
            if task.sprint_id.project_id != task.project_id:
                raise ValidationError(
                    "The sprint must belong to the same project as the task."
                )


    @api.model
    def _check_sprint_not_closed(self, sprint_ids):
        # INFO: Prevents tasks from being assigned to closed sprints.
        
        sprints = self.env['project.sprint'].browse(filter(None, sprint_ids))
        # INFO: Ignores tasks without a sprint assigned.

        sprints_closed = sprints.filtered(lambda x: x.state == 'closed')
        if sprints_closed:
            raise ValidationError(
                    "You can't assign a task to a closed sprint: %s"
                    % ", ".join(sprints_closed.mapped('display_name'))
            )


    @api.model_create_multi
    def create(self, vals_list):

        self._check_sprint_not_closed(vals.get('sprint_id') for vals in vals_list)
        return super().create(vals_list)


    def write(self, vals):

        new_sprint_id = vals.get('sprint_id')

        if new_sprint_id and any(task.sprint_id.id != new_sprint_id for task in self):
            self._check_sprint_not_closed([vals['sprint_id']])
        return super().write(vals)