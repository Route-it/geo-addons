# -*- coding: utf-8 -*-
{
    'name': "Certificaciones GeoPatagonia",
    'version': '0.1',
    'author': 'Route IT',
    'website': 'https://www.routeit.com.ar',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Project Management',
    'summary': """
        Modulo de manejo de proyectos para certificaciones de GeoPatagonia
    """,

    'description': """
        Long description of module's purpose
    """,

    # any module necessary for this one to work correctly
    'depends': [],
    # ['project'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/certification.xml',
        'views/supervisor.xml',
        'views/task.xml',
        'views/menu.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}