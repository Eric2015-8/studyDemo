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
                'base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/no_page/sale_type.xml',

        'views/views.xml',
        'views/templates.xml',

        'views/sale_forecast.xml',
        'views/sale_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
