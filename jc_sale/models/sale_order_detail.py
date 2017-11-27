# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import bill_define


class SaleOrderDetail(models.Model):
    _name = 'jc_sale.sale_order.detail'
    _description = u'销售：销售订单明细'

    _inherit = ['goods.detail.mobile']

    sale_order_id = fields.Many2one('jc_sale.sale_order', string='销售订单引用', required=True,
                                    ondelete='cascade', index=True, copy=False)

    source_bill_type = fields.Selection(bill_define.BILL_TYPE, string=u'来源单据类型', readonly=True, copy=False)
    source_bill_id = fields.Integer(string="来源单据号", readonly=True, copy=False, default=0)
    source_detail_id = fields.Integer(string="来源单据明细号", readonly=True, copy=False, default=0)

    price_type_id = fields.Many2one('archives.common_archive', string=u'价类', domain="[('archive_name','=',19)]")
    class_price_id = fields.Many2one('jc_sale.class_price', string='价格单号')
    origin_price = fields.Float(digits=(6, 2), help="原价", string=u'原价')
    transfer_price = fields.Float(digits=(6, 2), help="运价", string=u'运价')

    remark = fields.Char(string=u'备注')

    def _compute_money2(self):
        self.money = (self.price + self.transfer_price) * self.main_unit_number

    @api.onchange('second_unit_number_tmp')
    def _onchange_for_second_unit_number_from_tmp2(self):
        if not self.goods_id.need_change():
            return
        self._compute_money2()

    @api.onchange('main_unit_number_tmp')
    def _onchange_for_main_unit_number_from_tmp2(self):
        self._compute_money2()

    @api.onchange('price_tmp')
    def _onchange_for_price_from_tmp2(self):
        self._compute_money2()

    @api.onchange('price', 'main_unit_number', 'transfer_price')
    def _onchange_for_money2(self):
        self._compute_money2()
