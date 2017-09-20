# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomerType4(models.Model):
    _name = 'archives.customer_type4'
    _description = u'无菜单档案：客户分类4'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名客户分类4"),
    ]

    name = fields.Char(string=u'客户分类4', required=True)
