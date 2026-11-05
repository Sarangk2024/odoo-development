{
    'name': "Employee Trainee",
    'version': '1.0',
    'summary': "Manage Trainee",
    'description': "demo module",
    'depends': ['base'],
    'author': "demo author",
    'category': 'Human Resources',

    # data files always loaded at installation
    'data': [
         'security/ir.access.csv',
         'data/default_data.xml',
         'views/tainee_views.xml',
    ],
    # data files containing optionally loaded demonstration data
    'installable': True,
    'application': True,
}