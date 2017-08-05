# -*- coding: utf-8 -*-
{
    'name': "仓储",

    'summary': """
        库存相关""",

    'description': """
        与库存相关的单据，如：其它入库、销售出库，其使用对象为仓库人员
    """,

    'author': "xxb开发",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': '子模块',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
