# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OtherInStoreDetail(models.Model):
    _name = 'jc_storage.other_in_store.detail'
    _description = u'仓储：其它入库明细'

    other_in_store_id = fields.Many2one('jc_storage.other_in_store', string=u'其它入库引用', required=True,
                                        ondelete='cascade', index=True, copy=False)

    goods_id = fields.Many2one('archives.goods', string=u'产品', required=True)
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位', compute='_set_second')
    second_unit_number = fields.Float(digits=(6, 2), string=u'辅数量')
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位', compute='_set_main')
    main_unit_number = fields.Float(digits=(6, 2), string=u'主数量')

    price = fields.Float(digits=(6, 2), help=u"单价", string=u'单价')
    money = fields.Float(digits=(6, 2), help=u"金额", string=u'金额')

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
        default_goods_position_id = 0
        for r in self:
            if not r.other_in_store_id.store_id:
                break
            need_set = r.other_in_store_id.store_id.active_goods_position
            default_goods_position_id = r.other_in_store_id.store_id.default_goods_position_id
            break
        return need_set, default_goods_position_id

    @api.depends('goods_id')
    def _set_main(self):
        for record in self:
            record.main_unit_id = record.goods_id.main_unit_id

    @api.depends('goods_id')
    def _set_second(self):
        for record in self:
            if record.goods_id.need_change():
                record.second_unit_id = record.goods_id.second_unit_id
            else:
                record.second_unit_id = None

    @api.onchange('price', 'main_unit_number')
    def _onchange_for_money(self):
        self.money = self.price * self.main_unit_number

    @api.onchange('second_unit_number')
    def _onchange_second(self):
        if not self.goods_id.need_change():
            return
        self.main_unit_number = self.goods_id.second_rate * self.second_unit_number

    @api.onchange('main_unit_number')
    def _onchange_main(self):
        if not self.goods_id.need_change():
            return
        if self.goods_id.second_rate != 0:
            self.second_unit_number = self.main_unit_number / self.goods_id.second_rate

    @api.onchange('goods_id')
    def _onchange_goods(self):
        if self.goods_id.need_change():
            self.second_unit_id = self.goods_id.second_unit_id
        else:
            self.second_unit_id = None
        self.main_unit_id = self.goods_id.main_unit_id
