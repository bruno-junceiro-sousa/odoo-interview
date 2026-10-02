from odoo.exceptions import ValidationError, UserError
from .common import SprintTestCommon



class TestSprintLifecycle(SprintTestCommon):


    def test_start_sprint_from_open(self):

        sprint = self._create_sprint(state='open')
        sprint.action_start()
        
        self.assertEqual(sprint.state, 'active')


    def test_cannot_start_sprint_twice(self):

        sprint = self._create_sprint(state='active')

        with self.assertRaises(UserError):
            sprint.action_start()



    def test_cannot_close_sprint_not_active(self):

        sprint = self._create_sprint(state='open')

        with self.assertRaises(UserError):
            sprint.action_close()


    def test_reopen_closed_sprint(self):

        sprint = self._create_sprint(state='closed')
        sprint.action_reopen()

        self.assertEqual(sprint.state, 'open')


    def test_cannot_have_two_active_sprints_same_project(self):

        self._create_sprint(state='active')
        sprint_2 = self._create_sprint(state='open', start_offset=15, end_offset=28)

        with self.assertRaises(ValidationError):
            sprint_2.action_start()


    def test_two_active_sprints_different_projects_allowed(self):
        
        other_project = self.env['project.project'].create({'name': 'Other Project'})
        self._create_sprint(state='active')
        sprint_other = self._create_sprint(state='open', project=other_project)
        sprint_other.action_start()

        self.assertEqual(sprint_other.state, 'active')


    def test_date_start_after_date_end_raises(self):

        with self.assertRaises(ValidationError):
            self._create_sprint(start_offset=10, end_offset=0)


    def test_close_sprint_moves_unfinished_tasks_to_next_open_sprint(self):

        sprint_active = self._create_sprint(state='active', start_offset=0, end_offset=14)
        sprint_next = self._create_sprint(state='open', start_offset=15, end_offset=28)

        task_done = self._create_task('Done task', sprint=sprint_active, stage=self.stage_done)
        task_pending = self._create_task('Pending task', sprint=sprint_active, stage=self.stage_todo)

        sprint_active.action_close()

        self.assertEqual(sprint_active.state, 'closed')
        self.assertEqual(task_done.sprint_id, sprint_active, "Tasks that are Done should stay in the closed sprint.")
        self.assertEqual(task_pending.sprint_id, sprint_next, "Unfinished tasks should migrate to the next open sprint.")


    def test_close_sprint_moves_unfinished_tasks_to_backlog_when_no_next_sprint(self):

        sprint_active = self._create_sprint(state='active')
        task_pending = self._create_task('Pending task', sprint=sprint_active, stage=self.stage_todo)

        sprint_active.action_close()

        self.assertFalse(task_pending.sprint_id, "Without a open sprint, tasks should go to the backlog.")


    def test_close_sprint_picks_earliest_next_open_sprint(self):

        sprint_active = self._create_sprint(state='active', start_offset=0, end_offset=14)
        sprint_far = self._create_sprint(state='open', start_offset=30, end_offset=44)
        sprint_near = self._create_sprint(state='open', start_offset=15, end_offset=28)

        task_pending = self._create_task('Pending task', sprint=sprint_active, stage=self.stage_todo)
        sprint_active.action_close()

        self.assertEqual(task_pending.sprint_id, sprint_near)


    def test_task_sprint_must_belong_to_same_project(self):

        other_project = self.env['project.project'].create({'name': 'Other Project'})
        sprint = self._create_sprint(state='open')
        task = self._create_task('Cross project task', project=other_project)

        with self.assertRaises(ValidationError):
            task.sprint_id = sprint.id