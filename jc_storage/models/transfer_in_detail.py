# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from . import bill_define


class TransferInDetail(models.Model):
    _name = 'jc_storage.transfer_in.detail'
    _description = u'仓储：调拨入库明细'

    transfer_in_id = fields.Many2one('jc_storage.transfer_in', string=u'调拨入库引用', required=True,
                                     ondelete='cascade', index=True, copy=False)

    source_bill_type = fields.Selection(bill_define.BILL_TYPE, string=u'来源单据类型', readonly=True, copy=False)
    source_bill_id = fields.Integer(string="来源单据号", readonly=True, copy=False, default=0)
    source_detail_id = fields.Integer(string="来源单据明细号", readonly=True, copy=False, default=0)

    goods_id = fields.Many2one('archives.goods', string=u'产品', required=True)
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位', compute='_set_second')
    second_unit_number = fields.Float(digits=(6, 2), string=u'辅数量')
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位', compute='_set_main')
    main_unit_number = fields.Float(digits=(6, 2), string=u'主数量')

    price = fields.Float(digits=(6, 2), help=u"单价", string=u'单价')
    money = fields.Float(digits=(6, 2), help=u"金额", string=u'金额')

    remark = fields.Char(string=u'备注')

    @api.depends('goods_id')
    def _set_main(self):
        for record in self:
            record.main_unit_id = record.goods_id.main_unit_id

    @api.depends('goods_id')
    def _set_second(self):
        for record in self:
            record.second_unit_id = record.goods_id.second_unit_id

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
