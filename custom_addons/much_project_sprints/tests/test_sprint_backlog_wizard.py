from odoo.exceptions import UserError
from .common import SprintTestCommon



class TestSprintBacklogWizard(SprintTestCommon):


    def test_wizard_assigns_tasks_to_open_sprint(self):

        sprint = self._create_sprint(state='open')
        task_1 = self._create_task('Backlog task 1')
        task_2 = self._create_task('Backlog task 2')

        wizard = self.env['project.sprint.add.tasks.wizard'].create({
            'sprint_id': sprint.id,
            'task_ids': [(6, 0, [task_1.id, task_2.id])],
        })
        wizard.action_confirm()

        self.assertEqual(task_1.sprint_id, sprint)
        self.assertEqual(task_2.sprint_id, sprint)


    def test_wizard_rejects_when_sprint_not_planned(self):

        sprint = self._create_sprint(state='active')
        task = self._create_task('Backlog task')

        wizard = self.env['project.sprint.add.tasks.wizard'].create({
            'sprint_id': sprint.id,
            'task_ids': [(6, 0, [task.id])],
        })

        with self.assertRaises(UserError):
            wizard.action_confirm()


    def test_wizard_rejects_empty_selection(self):

        sprint = self._create_sprint(state='open')
        wizard = self.env['project.sprint.add.tasks.wizard'].create({
            'sprint_id': sprint.id,
        })

        with self.assertRaises(UserError):
            wizard.action_confirm()


    def test_backlog_domain_excludes_tasks_already_in_sprint(self):

        sprint = self._create_sprint(state='open')
        other_sprint = self._create_sprint(state='open', start_offset=15, end_offset=28)
        task_in_other_sprint = self._create_task('Already assigned', sprint=other_sprint)
        task_backlog = self._create_task('In backlog')

        wizard = self.env['project.sprint.add.tasks.wizard'].create({
            'sprint_id': sprint.id,
        })

        self.assertNotIn(task_in_other_sprint, self.env['project.task'].search([
            ('project_id', '=', wizard.project_id.id), ('sprint_id', '=', False)
        ]))
        
        self.assertIn(task_backlog, self.env['project.task'].search([
            ('project_id', '=', wizard.project_id.id), ('sprint_id', '=', False)
        ]))