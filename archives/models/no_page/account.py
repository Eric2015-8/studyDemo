# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Account(models.Model):
    _name = 'archives.account'
    _description = u'无菜单档案：账号'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名账号"),
    ]

    name = fields.Char(string=u'账号', required=True)
