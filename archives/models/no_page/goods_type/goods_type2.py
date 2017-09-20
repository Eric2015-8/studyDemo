# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GoodsType2(models.Model):
    _name = 'archives.goods_type2'
    _description = u'无菜单档案：物料分类2'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名物料分类2"),
    ]

    name = fields.Char(string=u'物料分类2', required=True)
