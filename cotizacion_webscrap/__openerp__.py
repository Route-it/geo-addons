# -*- coding: utf-8 -*-
{
    'name': "cotizacion_webscrap",

    'summary': """
        obtiene la cotizacion del dolar historico""",

    'description': """
        obtiene la cotizacion del dolar historico
    """,

    'author': "Diego Richi",
    'website': "http://www.diegorichi.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'GeoPatagonia',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/vehicle.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}