# -*- coding: utf-8 -*-
{
    "name": "审批",
    "version": '11.11',
    "author": 'xxb',
    "website": "http://www.osbzr.com",
    "category": "jc",
    "description": """
    可配置的审批流程
    """,
    "data": [
        'data/data.xml',
        'views/approve.xml',
        'security/ir.model.access.csv',
    ],
    "depends":[
        'archives',
    ],
    'qweb': [
        'static/src/xml/approver.xml',
    ],
}
