from psycopg2 import IntegrityError
from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError, UserError



class ProjectSprint(models.Model):

    _name = 'project.sprint'
    _description = 'Project Sprint'
    _inherit = ['mail.thread','mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char(
        required=True,
        tracking=True
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
        tracking=True,
        copy=False
    )

    task_ids = fields.One2many(
        'project.task',
        'sprint_id',
        string='Tasks'
    )

    task_count = fields.Integer(
        compute='_compute_task_count'
    )


    def init(self):

        tools.create_index(
            self.env.cr,
            'project_sprint_single_active_idx',
            self._table,
            ['project_id'],
            where="state = 'active'",
            unique=True
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


    @api.constrains('state', 'project_id')
    def _check_single_active_sprint(self):

        for sprint in self.filtered(lambda x: x.state == 'active'):
            other_active = self.search_count([
                ('project_id', '=', sprint.project_id.id),
                ('state', '=', 'active'),
                ('id', '!=', sprint.id)
            ])

            if other_active:
                raise ValidationError(
                    "Project '%s' already has an active sprint. "
                    "You must close it before starting a new one."
                    % sprint.project_id.display_name
                )


    def action_start(self):
        
        for sprint in self:
            if sprint.state != 'open':
                raise UserError('Only open sprints can be started.')

            active_sprint = self.search([
                ('project_id', '=', sprint.project_id.id),
                ('state', '=', 'active')
            ], limit=1)

            if active_sprint:
                raise ValidationError(
                    "Project '%s' already has an active sprint (%s). "
                    "You must close it before starting a new one."
                    % (sprint.project_id.display_name, active_sprint.name)
                )

        try:
            with self.env.cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                self.write({'state': 'active'})
        except IntegrityError:
            self.invalidate_recordset()
            # INFO: Clears the cache after the savepoint rollback

            raise ValidationError(
                "Another sprint became active for this project in the meantime. "
                "Please refresh and try again."
            )


    def action_close(self):
        
        for sprint in self:
            if sprint.state != 'active':
                raise UserError('Only active sprints can be closed.')

            unfinished_tasks = sprint.task_ids.filtered(lambda x: not x.is_closed)
            next_sprint = self.search(
                [
                    ('project_id', '=', sprint.project_id.id),
                    ('state', '=', 'open'),
                    ('date_start', '>', sprint.date_start),
                ], 
                order='date_start asc',
                limit=1
            )

            if unfinished_tasks:
                unfinished_tasks.write({'sprint_id': next_sprint.id})
                new_destination = next_sprint.name if next_sprint else 'Backlog'
                sprint.message_post(
                    body="%(count)s unfinished task(s) moved to: %(dest)s"
                        % {'count': len(unfinished_tasks), 'dest': new_destination}
                )

            sprint.state = 'closed'


    def action_reopen(self):

        self.filtered(lambda x: x.state == 'closed').write({'state': 'open'})


    def action_view_tasks(self):
        
        self.ensure_one()
        
        action = self.env['ir.actions.act_window']._for_xml_id('project.action_view_task')
        action['domain'] = [('sprint_id', '=', self.id)]
        action['context'] = {
            'default_sprint_id': self.id,
            'default_project_id': self.project_id.id
        }

        return action


    def action_open_add_tasks_wizard(self):

        self.ensure_one()
        
        return {
            'name': _('Add Tasks from Backlog'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.sprint.add.tasks.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sprint_id': self.id},
        }