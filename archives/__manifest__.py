# -*- coding: utf-8 -*-
{
    'name': "archives",

    'summary': """
        全部档案模块""",

    'description': """
        全部档案模块，所有模块依赖这个模块
    """,

    'author': "xxb开发",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': '主模块',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/no_page/duty.xml',
        'views/no_page/account.xml',
        'views/no_page/unit.xml',
        'views/no_page/goods_type/goods_type.xml',
        'views/no_page/goods_type/goods_type1.xml',
        'views/no_page/goods_type/goods_type2.xml',
        'views/no_page/goods_type/goods_type3.xml',
        'views/no_page/goods_type/goods_type4.xml',
        'views/no_page/goods_type/goods_type5.xml',
        'views/no_page/goods_type/goods_type6.xml',
        'views/no_page/customer_type/customer_type.xml',
        'views/no_page/customer_type/customer_type1.xml',
        'views/no_page/customer_type/customer_type2.xml',
        'views/no_page/customer_type/customer_type3.xml',
        'views/no_page/customer_type/customer_type4.xml',
        'views/no_page/customer_type/customer_type5.xml',
        'views/no_page/customer_type/customer_type6.xml',
        'views/no_page/zone.xml',
        'views/no_page/zone_type1.xml',
        'views/no_page/zone_type2.xml',

        'views/views.xml',
        'views/company.xml',
        'views/department.xml',
        'views/staff.xml',
        'views/store.xml',
        'views/goods.xml',
        'views/customer.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
