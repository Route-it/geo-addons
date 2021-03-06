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
    'depends': ['mail','web_m2x_options'],
    # ['project'],

    # always loaded
    'data': [
        'security/base_security.xml',
        'security/menu_security.xml',
        'security/profiles_security.xml',
        'views/certification-ceyf.xml',
        'views/certification-coiled-tubing.xml',
        'views/coiled-tubing-time-losed.xml',
        'views/supervisor.xml',
        'views/contract.xml',
        'views/plant.xml',
        'views/task.xml',
        'views/menu.xml',
        'views/res_partner_company_operator.xml',
        'views/web_ct_style.xml',
        'security/ir.model.access.csv',
        'data/plants.xml',
        'data/ir_cron.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
    'application': True,
    'installable': True,

}