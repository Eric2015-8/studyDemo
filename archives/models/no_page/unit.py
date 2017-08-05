# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Unit(models.Model):
    _name = 'archives.unit'
    #    _sql_constraints = [
    #        ('name_unique',
    #         'UNIQUE(name)',
    #         "已存在相同单位"),
    #    ]

    name = fields.Char(string=u'单位', required=True)
