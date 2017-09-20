# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GoodsType5(models.Model):
    _name = 'archives.goods_type5'
    _description = u'无菜单档案：物料分类5'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名物料分类5"),
    ]

    name = fields.Char(string=u'物料分类5', required=True)
