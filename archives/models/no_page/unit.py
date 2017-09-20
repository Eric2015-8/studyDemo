# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Unit(models.Model):
    _name = 'archives.unit'
    _description = u'无菜单档案：单位'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名单位"),
    ]

    name = fields.Char(string=u'单位', required=True)
