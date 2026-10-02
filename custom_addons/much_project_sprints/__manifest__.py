{
    'name': 'Much Project Sprints',
    'version': '1.0',
    'category': 'Project',
    'summary': 'Organize project tasks into sprints',
    'description': """
        Adds sprint management to standard Odoo Projects.
        Allows teams to group tasks into sprints with a simple lifecycle:
        Open -> Active -> Closed.
    """,
    'author': 'Bruno Junceiro Sousa',
    'depends': ['project'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/project_sprint_views.xml',
        'views/project_task_views.xml',
        'views/project_sprint_add_tasks_wizard_views.xml'
    ],
    'demo': [
        'demo/sprint_demo.xml'
    ],
    'installable': True,
    'application': False,
}