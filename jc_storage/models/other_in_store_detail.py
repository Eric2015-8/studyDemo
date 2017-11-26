# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OtherInStoreDetail(models.Model):
    _name = 'jc_storage.other_in_store.detail'
    _description = u'仓储：其他入库明细'

    _inherit = ['goods.detail']

    other_in_store_id = fields.Many2one('jc_storage.other_in_store', string=u'其他入库引用', required=True,
                                        ondelete='cascade', index=True, copy=False)

    store_id = fields.Many2one('archives.store', string=u'仓库', related='other_in_store_id.store_id')
    active_goods_position = fields.Boolean(u'启用货位', related='other_in_store_id.store_id.active_goods_position')

    # goods_position_id = fields.Many2one('archives.store.goods_position.detail', string=u'货位'
    #                                     # , domain=[('store_id', '=', store_id)]
    #                                     )
    # goods_batch_id = fields.Many2one('archives.goods_batch', string=u'批次')

    remark = fields.Char(string=u'备注')

    # @api.onchange('goods_id', 'other_in_store_id.store_id')
    # def _set_goods_position(self):
    #     position_pair = self._get_goods_position_info()
    #     for r in self:
    #         r.store_id = r.other_in_store_id.store_id
    #         r.active_goods_position = r.other_in_store_id.store_id.active_goods_position
    #     if not position_pair[0] or not position_pair[1]:
    #         return
    #     for record in self:
    #         if not record.goods_position_id:
    #             record.goods_position_id = position_pair[1]

    def _get_goods_position_info(self):
        need_set = False
        goods_position_id_default = 0
        for r in self:
            if not r.other_in_store_id.store_id:
                break
            need_set = r.other_in_store_id.store_id.active_goods_position
            goods_position_id_default = r.other_in_store_id.store_id.goods_position_id_default
            break
        return need_set, goods_position_id_default
