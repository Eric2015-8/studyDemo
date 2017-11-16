# -*- coding: utf-8 -*-
{
    'name': "仓储",

    'summary': """
        库存相关""",

    'description': """
        与库存相关的单据，如：其他入库、销售出库，其使用对象为仓库人员
    """,

    'author': "xxb开发",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'jc',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['archives',
                'decimal_precision',
                'base'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',

        'wizard/set_transfer_customer_setting.xml',

        'views/views.xml',
        'views/templates.xml',
        'views/other_in_store.xml',
        'print/other_in_store_report.xml',
        'views/other_out_store.xml',
        'print/other_out_store_report.xml',
        'views/sale_out_store.xml',
        'print/sale_out_store_report.xml',
        'views/transfer_out.xml',
        'print/transfer_out_report.xml',
        'views/transfer_in.xml',
        'print/transfer_in_report.xml',
        'views/sale_return_store.xml',
        'print/sale_return_store_report.xml',
        'views/stock_check.xml',
        'print/stock_check_report.xml',

        'views/storage_setting_center_transfer_out_type.xml',
        'views/storage_setting_center.xml',

        'report/report_storage_account.xml',
        'report/report_storage_account_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
