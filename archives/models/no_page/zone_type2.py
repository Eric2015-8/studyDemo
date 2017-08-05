# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ZoneType2(models.Model):
    _name = 'archives.zone_type2'
    #    _sql_constraints = [
    #        ('name_unique',
    #         'UNIQUE(name)',
    #         "已存在相同地区分类2"),
    #    ]

    name = fields.Char(string=u'地区分类2', required=True)
