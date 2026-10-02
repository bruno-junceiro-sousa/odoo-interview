from odoo import models, fields
from odoo.exceptions import UserError


class ProjectSprintAddTasksWizard(models.TransientModel):

    _name = 'project.sprint.add.tasks.wizard'
    _description = 'Add Backlog Tasks to Sprint'

    sprint_id = fields.Many2one('project.sprint', required=True)
    project_id = fields.Many2one(related='sprint_id.project_id')
    task_ids = fields.Many2many(
        'project.task',
        string='Backlog Tasks',
        domain="[('project_id', '=', project_id), ('sprint_id', '=', False)]",
    )

    def action_confirm(self):

        self.ensure_one()

        if self.sprint_id.state != 'open':
            raise UserError("Tasks can only be added while the sprint is open.")
        if not self.task_ids:
            raise UserError("Select at least one task.")
        self.task_ids.write({'sprint_id': self.sprint_id.id})

        return {'type': 'ir.actions.act_window_close'}