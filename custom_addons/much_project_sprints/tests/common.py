from odoo.tests.common import TransactionCase
from odoo.fields import Date
from dateutil.relativedelta import relativedelta



class SprintTestCommon(TransactionCase):


    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        cls.project = cls.env['project.project'].create({
            'name': 'Test Project',
        })

        cls.stage_todo = cls.env['project.task.type'].create({
            'name': 'To Do', 'sequence': 1,
        })
        cls.stage_done = cls.env['project.task.type'].create({
            'name': 'Done', 'sequence': 2, 'fold': True,
        })

        cls.today = Date.context_today(cls.env.user)

        cls.group_manager = cls.env.ref('project.group_project_manager')
        cls.group_user = cls.env.ref('project.group_project_user')

        cls.manager = cls.env['res.users'].create({
            'name': 'Sprint Manager',
            'login': 'sprint_manager@test.com',
            'email': 'sprint_manager@test.com',
            'group_ids': [(6, 0, [cls.group_manager.id])],
        })
        cls.regular_user = cls.env['res.users'].create({
            'name': 'Sprint Dev',
            'login': 'sprint_dev@test.com',
            'email': 'sprint_dev@test.com',
            'group_ids': [(6, 0, [cls.group_user.id])],
        })


    def _create_sprint(self, state='open', start_offset=0, end_offset=14, project=None):

        return self.env['project.sprint'].create({
            'name': f'Sprint {state}',
            'project_id': (project or self.project).id,
            'date_start': self.today + relativedelta(days=start_offset),
            'date_end': self.today + relativedelta(days=end_offset),
            'state': state,
        })

    def _create_task(self, name, sprint=None, stage=None, project=None):

        vals = {
            'name': name,
            'project_id': (project or self.project).id,
            'sprint_id': sprint.id if sprint else False,
            'stage_id': (stage or self.stage_todo).id,
        }
        if stage and stage == self.stage_done:
            vals['state'] = '1_done'

        return self.env['project.task'].create(vals)