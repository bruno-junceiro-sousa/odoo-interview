from odoo.exceptions import AccessError
from .common import SprintTestCommon



class TestSprintSecurity(SprintTestCommon):


    def test_regular_user_can_read_sprint(self):

        sprint = self._create_sprint(state='open')
        sprint.with_user(self.regular_user).read(['name', 'state'])


    def test_regular_user_cannot_create_sprint(self):

        with self.assertRaises(AccessError):
            self.env['project.sprint'].with_user(self.regular_user).create({
                'name': 'Unauthorized Sprint',
                'project_id': self.project.id,
                'date_start': self.today,
                'date_end': self.today,
            })


    def test_regular_user_cannot_start_sprint_via_rpc(self):

        sprint = self._create_sprint(state='open')

        with self.assertRaises(AccessError):
            sprint.with_user(self.regular_user).action_start()


    def test_manager_can_create_and_start_sprint(self):

        sprint = self.env['project.sprint'].with_user(self.manager).create({
            'name': 'Manager Sprint',
            'project_id': self.project.id,
            'date_start': self.today,
            'date_end': self.today,
        })

        sprint.with_user(self.manager).action_start()

        self.assertEqual(sprint.state, 'active')


    def test_regular_user_cannot_open_backlog_wizard(self):

        sprint = self._create_sprint(state='open')
        
        with self.assertRaises(AccessError):
            self.env['project.sprint.add.tasks.wizard'].with_user(self.regular_user).create({
                'sprint_id': sprint.id,
            })