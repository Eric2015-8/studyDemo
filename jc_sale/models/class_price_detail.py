# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ClassPriceDetail(models.Model):
    _name = 'jc_sale.class_price.detail'
    _description = u'销售：分类价明细'

    class_price_id = fields.Many2one('jc_sale.class_price', string='分类价引用', required=True,
                                     ondelete='cascade', index=True, copy=False)

    goods_id = fields.Many2one('archives.goods', string=u'产品', required=True,
                               domain=lambda self: self.env['archives.organization'].get_goods_organization())

    price = fields.Float(digits=(6, 2), help="单价", string=u'单价')
