# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Zone(models.Model):
    _name = 'archives.zone'
    _description = u'无菜单档案：地区'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名地区"),
    ]

    name = fields.Char(string=u'地区', required=True)
