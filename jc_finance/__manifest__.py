# -*- coding: utf-8 -*-
{
    'name': "财务",

    'summary': """
        财务相关""",

    'description': """
        与账务相关的内容，如：销售记账、收款单
    """,

    'author': "xxb开发",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'jc',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['archives', 'base'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',

        'views/views.xml',
        'views/templates.xml',
        'views/sale_account.xml',
        'print/sale_account_report.xml',

        'report/report_sale_statistics/report_sale_statistics.xml',
        'report/report_sale_statistics/report_sale_statistics_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
