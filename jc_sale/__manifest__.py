# -*- coding: utf-8 -*-
{
    'name': "销售",

    'summary': """
        销售相关""",

    'description': """
        销售的内容如：销售订单、销售价格，其使用对象为销售人员
    """,

    'author': "xxb开发",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': '子模块',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['archives',
                'decimal_precision',
                'report',
                'base'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        # 'data/sale_setting_center.xml',
        # 'wizard/add_goods.xml',

        'views/views.xml',
        'views/templates.xml',

        'views/sale_forecast.xml',
        'print/sale_forecast_report.xml',
        'views/sale_order.xml',
        'print/sale_order_report.xml',
        'report/report_sale_order.xml',
        'views/class_price.xml',
        'views/sale_setting_center.xml',
        'views/sale_setting_center_sale_type.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
