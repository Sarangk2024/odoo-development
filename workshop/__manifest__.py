# -*- coding: utf-8 -*-
{
    'name': 'Workshop',
    'version': '20.0.0.0.1',
    'summary': 'Workshop management ERP',
    'description': """Workshop management is a ERP software that centralise all the operations like service, repaires, etc.""",
    'sequence': 1,
    'depends': [
        'base',
        'mail',
        'hr',
        'sale',
        'account',
    ],

    'data': [
        'security/ir.access.csv',
        'views/workshop_bay_views.xml',
        'views/vehicle_management_views.xml',
        'views/workshop_job_order_views.xml',
        'views/job_type_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'data/job_type_data.xml',
        'data/workshop_bay_data.xml',
        'data/sequence_data.xml',
        'views/workshop_menu.xml',
    ],

    'installable': True,
    'application': True,
}