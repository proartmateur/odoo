# -*- coding: utf-8 -*-
{
    'name': "Pedidos",
    'summary': """Pedidos""",
    'description': """
        Pedidos
    """,
    'website': 'http://spellboundss.com/',
    'maintainer': 'Spellbound Soft Solutions',
    'company': 'Spellbound Soft Solutions',
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','product','sale','sales_team','pw_pos_restrict_refund','point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/product.xml',
        'views/order.xml',
        'views/request_pedidos.xml',
        'views/product_category_view.xml',
        'views/menu.xml',
        'views/sale_order.xml',
        'report/pedidos_report_template.xml',
        'report/pedidos_report_action.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pedidos/static/src/core/**/*',
            'pedidos/static/src/components/*',
            'pedidos/static/src/mixins/*.js',
            'pedidos/static/src/views/*',
            'pedidos/static/src/scss/pedidos_view.scss',
            'pedidos/static/src/scss/pedidos_kanban.scss',

        ],
        
        'point_of_sale.assets': [
            'pedidos/static/src/js/pediosSaleOrderManagementScreenn.js',


            'pedidos/static/src/js/pos/models.js',
            'pedidos/static/src/js/pos/numpadwidgetreturn.js',
            'pedidos/static/src/js/pos/add_qtypop.js',
            #'pedidos/static/src/js/pos/Orderline.js',
            'pedidos/static/src/js/pos/intinputbox.js',
            'pedidos/static/src/xml/Orderline.xml',
        ],
        
    },
    'installable': True,
    'application': True,
}
