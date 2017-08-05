# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GoodsType1(models.Model):
    _name = 'archives.goods_type1'
    #    _sql_constraints = [
    #        ('name_unique',
    #         'UNIQUE(name)',
    #         "已存在相同物料分类1"),
    #    ]

    name = fields.Char(string=u'物料分类1', required=True)
