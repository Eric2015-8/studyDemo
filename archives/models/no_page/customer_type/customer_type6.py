# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomerType6(models.Model):
    _name = 'archives.customer_type6'
    _description = u'无菜单档案：客户分类6'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名客户分类6"),
    ]

    name = fields.Char(string=u'客户分类6', required=True)
