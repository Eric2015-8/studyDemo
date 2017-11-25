# -*- coding: utf-8 -*-

from odoo import models, fields, api
from goods_detail import GoodsDetail


class GoodsDetailMobile(GoodsDetail):
    _name = 'goods.detail.mobile'
    _description = u'存货明细，含数量单价金额，用于手机'

    _inherit = ['goods.detail']

    second_unit_number_tmp = fields.Char(string=u'辅数量')
    main_unit_number_tmp = fields.Char(string=u'主数量')

    price_tmp = fields.Char(string=u'单价')

    def _compute_money(self):
        self.money = self.price * self.main_unit_number

    @api.onchange('second_unit_number_tmp')
    def _onchange_for_second_unit_number_from_tmp(self):
        self.second_unit_number = float(self.second_unit_number_tmp)
        if not self.goods_id.need_change():
            return
        self.main_unit_number = self.goods_id.second_rate * self.second_unit_number
        self.main_unit_number_tmp = str(self.main_unit_number)
        self._compute_money()

    @api.onchange('main_unit_number_tmp')
    def _onchange_for_main_unit_number_from_tmp(self):
        self.main_unit_number = float(self.main_unit_number_tmp)
        self._compute_money()
        if not self.goods_id.need_change():
            return
        if self.goods_id.second_rate != 0:
            self.second_unit_number = self.main_unit_number / self.goods_id.second_rate
            self.second_unit_number_tmp = str(self.second_unit_number)

    @api.onchange('price_tmp')
    def _onchange_for_price_from_tmp(self):
        self.price = float(self.price_tmp)
        self._compute_money()

    @api.model
    def create(self, values):
        GoodsDetailMobile._set_tmp_for_number(values)
        return super(GoodsDetailMobile, self).create(values)

    @staticmethod
    def _set_tmp_for_number(values):
        if 'second_unit_number' in values:
            values['second_unit_number_tmp'] = str(values['second_unit_number'])
        if 'main_unit_number' in values:
            values['main_unit_number_tmp'] = str(values['main_unit_number'])
        if 'price' in values:
            values['price_tmp'] = str(values['price'])

    @api.multi
    def write(self, values):
        GoodsDetailMobile._set_tmp_for_number(values)
        return super(GoodsDetailMobile, self).write(values)
