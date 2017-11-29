# -*- coding: utf-8 -*-
{
    'name': "档案",

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
    'category': 'jc',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'report'
                ],

    # always loaded
    'data': [
        'print/print_format.xml',
        'print/print_frame.xml',

        'security/security.xml',
        'security/ir.model.access.csv',
        'views/no_page/duty.xml',
        'views/no_page/account.xml',
        'views/no_page/unit.xml',
        'views/no_page/zone.xml',
        'views/no_page/zone_type1.xml',
        'views/no_page/zone_type2.xml',

        'views/views.xml',
        'views/common_archive.xml',
        'views/department.xml',
        'views/staff.xml',
        'views/store.xml',
        'views/goods.xml',
        'models/no_page/goods_number/goods_number.xml',
        'views/customer.xml',
        'views/templates.xml',
        'views/organization.xml',
        'views/organization_group.xml',
        'views/res_users.xml',
        'wizard/set_customer_setting.xml',
        'views/setting_center.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
