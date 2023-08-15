# -*- coding: utf-8 -*-
{
    'name': 'Restrict POS Refund with Password',
    'version': '1.0',
    'author': 'Preway IT Solutions',
    'category': 'Point of Sale',
    'depends': ['point_of_sale','pos_hr'],
    'summary': 'This module helps you to restrict refund with Password on pos shop | Restrict POS Refund | POS Refund Password | POS Password Protected refund',
    'description': """
- Restrict POS Refund
    """,
    "data": [
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pw_pos_restrict_refund/static/src/js/TicketScreen.js',
            'pw_pos_restrict_refund/static/src/js/numpadwidgetreturn.js',
            'pw_pos_restrict_refund/static/src/js/model.js',
            'pw_pos_restrict_refund/static/src/js/Loginscreen.js',
            'pw_pos_restrict_refund/static/src/xml/pos_hr.xml',
        ],
    },
    'price': 20.0,
    'currency': "EUR",
    'application': True,
    'installable': True,
    "license": "LGPL-3",
    "images":["static/description/Banner.png"],
}
