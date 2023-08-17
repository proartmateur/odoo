# -*- coding: utf-8 -*-
{
    'name': "Contacts Sync",

    'summary': """
        Sincronización de contactos entre Odoo y AgendaPro""",

    'description': """
        Permite sincronizar los contactos de Odoo en AgendaPro
    """,

    'author': "Enrique Nieto Martínez",
    'website': "https://millora.com.mx",
    'application': True,

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/contacts_sync_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
