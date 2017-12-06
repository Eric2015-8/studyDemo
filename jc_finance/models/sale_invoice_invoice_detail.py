# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleInvoiceInvoiceDetail(models.Model):
    _name = 'jc_finance.sale_invoice_invoice_detail'
    _description = u'财务：销售发票-发票明细'

    sale_invoice_id = fields.Many2one('jc_finance.sale_invoice', string=u'销售发票引用', required=True,
                                      ondelete='cascade', index=True, copy=False)

    goods_id = fields.Many2one('archives.goods', string=u'产品', required=True,
                               domain=lambda self: self.env['archives.organization'].get_goods_organization())
    goods_invoice = fields.Char(string=u'开票产品')
    number = fields.Float(digits=(6, 2), string=u'数量')
    number2 = fields.Float(digits=(6, 2), string=u'辅助数量')
    price = fields.Float(digits=(6, 2), help="单价", string=u'单价', readonly=True)
    money = fields.Float(digits=(6, 2), help="金额", string=u'金额')
    remark = fields.Char(string=u'备注')

    main_unit_id = fields.Many2one('archives.unit', string=u'主单位', compute='_set_main', store=True)

    @api.depends('goods_id')
    def _set_main(self):
        for record in self:
            record.main_unit_id = record.goods_id.main_unit_id
