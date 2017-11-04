# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockCheckDetail(models.Model):
    _name = 'jc_storage.stock_check.detail'
    _description = u'仓储：库存盘点明细'

    stock_check_id = fields.Many2one('jc_storage.stock_check', string=u'库存盘点引用', required=True,
                                     ondelete='cascade', index=True, copy=False)

    goods_id = fields.Many2one('archives.goods', string=u'产品', required=True)
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位', compute='_set_second')
    second_unit_number_compute = fields.Float(digits=(6, 2), string=u'账存辅数量')
    second_unit_number = fields.Float(digits=(6, 2), string=u'盘点辅数量')
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位', compute='_set_main')
    main_unit_number_compute = fields.Float(digits=(6, 2), string=u'账存主数量')
    main_unit_number = fields.Float(digits=(6, 2), string=u'盘点主数量')

    remark = fields.Char(string=u'备注')

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

    @api.onchange('goods_id')
    def _onchange_goods(self):
        if self.goods_id.need_change():
            self.second_unit_id = self.goods_id.second_unit_id
        else:
            self.second_unit_id = None
        self.main_unit_id = self.goods_id.main_unit_id

    @api.onchange('second_unit_number', 'second_unit_number_compute')
    def _onchange_second(self):
        if not self.goods_id.need_change():
            return
        self.main_unit_number_compute = self.goods_id.second_rate * self.second_unit_number_compute
        self.main_unit_number = self.goods_id.second_rate * self.second_unit_number

    @api.onchange('main_unit_number', 'main_unit_number_compute')
    def _onchange_main(self):
        if not self.goods_id.need_change():
            return
        if self.goods_id.second_rate != 0:
            self.second_unit_number_compute = self.main_unit_number_compute / self.goods_id.second_rate
            self.second_unit_number = self.main_unit_number / self.goods_id.second_rate
