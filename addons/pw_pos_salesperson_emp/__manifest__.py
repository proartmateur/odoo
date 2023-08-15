# -*- coding: utf-8 -*-
{
    'name': 'POS Salesperson(Employee)',
    'version': '1.0',
    'author': 'Preway IT Solutions',
    'category': 'Point of Sale',
    'depends': ['point_of_sale', 'hr','sale','pos_sale','lunch'],
    'summary': 'This apps helps you set salesperson on pos orderline from pos interface | POS Orderline User | Assign Sales Person on POS | POS Sales Person',
    'description': """
- Odoo POS Orderline user
- Odoo POS Orderline salesperson
- Odoo POS Salesperson
- Odoo POS Item Salesperson
- Odoo POS Item User
- Odoo POS product salesperson
    """,
    'data': [
        'views/pos_config_view.xml',
        'views/sale_order.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pw_pos_salesperson_emp/static/src/js/**/*',
            'pw_pos_salesperson_emp/static/src/xml/**/*',
        ],
    },
    'price': 40.0,
    'currency': "EUR",
    'application': True,
    'installable': True,
    "license": "LGPL-3",
    'live_test_url': 'https://youtu.be/cEwwLz9G3Go',
    "images":["static/description/Banner.png"],
}
