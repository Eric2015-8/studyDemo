# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GoodsType6(models.Model):
    _name = 'archives.goods_type6'
    #    _sql_constraints = [
    #        ('name_unique',
    #         'UNIQUE(name)',
    #         "已存在相同物料分类6"),
    #    ]

    name = fields.Char(string=u'物料分类6', required=True)
