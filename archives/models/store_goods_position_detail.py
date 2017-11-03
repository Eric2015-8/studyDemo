# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import utils
from odoo.exceptions import ValidationError


class StoreGoodsPositionDetail(models.Model):
    _name = 'archives.store.goods_position.detail'
    _description = u'档案：仓库_货位明细'

    store_id = fields.Many2one('archives.store', string=u'仓库引用', required=True,
                               ondelete='cascade', index=True, copy=False)
    goods_position_id = fields.Many2one('archives.goods_position', string=u'货位')
