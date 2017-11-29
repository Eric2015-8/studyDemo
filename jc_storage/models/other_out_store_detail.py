# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OtherInStoreDetail(models.Model):
    _name = 'jc_storage.other_out_store.detail'
    _description = u'仓储：其他出库明细'

    _inherit = ['goods.detail']

    other_out_store_id = fields.Many2one('jc_storage.other_out_store', string='其他入库引用', required=True,
                                        ondelete='cascade', index=True, copy=False)

    cost = fields.Float(digits=(6, 2), help="成本单价", string=u'成本单价')

    goods_position_id = fields.Many2one('archives.goods_position', string=u'货位')
    # goods_batch_id = fields.Many2one('archives.goods_batch', string=u'批次')

    remark = fields.Char(string=u'备注')
