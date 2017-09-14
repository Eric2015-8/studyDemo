# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderDetail(models.Model):
    _name = 'jc_sale.sale_order.detail'

    # sale_forecast_detail_id = fields.Many2one('jc_sale.sale_forecast',string=u'销售预报')
    # sale_forecast_id = fields.Integer(string=u'预报单号')
    # sale_forecast_detail_id = fields.Integer(string=u'预报明细号')

    sale_order_id = fields.Many2one('jc_sale.sale_order', string='销售订单引用', required=True,
                                    ondelete='cascade', index=True, copy=False)

    forecast_id = fields.Many2one('jc_sale.sale_forecast', string=u'销售预报单ID')
    forecast_detail_id = fields.Many2one('jc_sale.sale_forecast.detail', string=u'销售预报单明细ID')

    goods_id = fields.Many2one('archives.goods', string=u'产品', required=True)
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位', compute='_set_second')
    second_unit_number = fields.Float(digits=(6, 2), string=u'辅数量')
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位', compute='_set_main')
    main_unit_number = fields.Float(digits=(6, 2), string=u'主数量')

    price = fields.Float(digits=(6, 2), help="单价", string=u'单价')
    money = fields.Float(digits=(6, 2), help="金额", string=u'金额')

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
        if not self.goods_id.need_second_change:
            return
        self.main_unit_number = self.goods_id.second_rate * self.second_unit_number

    @api.onchange('main_unit_number')
    def _onchange_main(self):
        if not self.goods_id.need_second_change:
            return
        if self.goods_id.second_rate != 0:
            self.second_unit_number = self.main_unit_number / self.goods_id.second_rate

    @api.onchange('goods_id')
    def _onchange_goods(self):
        self.second_unit_id = self.goods_id.second_unit_id
        self.main_unit_id = self.goods_id.main_unit_id
