# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomerType2(models.Model):
    _name = 'archives.customer_type2'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名客户分类2"),
    ]

    name = fields.Char(string=u'客户分类2', required=True)
