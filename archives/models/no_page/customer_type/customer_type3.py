# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomerType3(models.Model):
    _name = 'archives.customer_type3'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名客户分类3"),
    ]

    name = fields.Char(string=u'客户分类3', required=True)
