# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleType(models.Model):
    _name = 'archives.sale_type'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名销售类型"),
    ]

    name = fields.Char(string=u'销售类型', required=True)
