{
    'name': 'Real Estate',
    'version': '1.2',
    'category': 'new catogory',
    'description': "real estate management",
    'depends': ['base'],

    'data': [
        'security/ir.access.csv',
        'views/real_estate_views.xml',
        'views/real_estate_property_type.xml',
        'views/real_estate_property_tag.xml',
        'views/real_estate_property_offer.xml',
        'views/real_estate_menu.xml',


    ],
    'installable': True,
    'application': True,
}