# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ZoneType1(models.Model):
    _name = 'archives.zone_type1'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名地区分类1"),
    ]

    name = fields.Char(string=u'地区分类1', required=True)
