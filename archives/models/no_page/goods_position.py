# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GoodsPosition(models.Model):
    _name = 'archives.goods_position'
    #    _sql_constraints = [
    #        ('name_unique',
    #         'UNIQUE(name)',
    #         "已存在相同货位"),
    #    ]

    name = fields.Char(string=u'货位', required=True)
