# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import bill_define


class SaleInvoiceBillDetail(models.Model):
    _name = 'jc_finance.sale_invoice_bill_detail'
    _description = u'财务：销售发票-单据明细'

    sale_invoice_id = fields.Many2one('jc_finance.sale_invoice', string=u'销售发票引用', required=True,
                                      ondelete='cascade', index=True, copy=False)
    bill_type_id = fields.Selection(bill_define.BILL_TYPE, string=u'单据类型', readonly=True)
    date = fields.Date(string=u'日期', required=True, default=fields.Date.today, readonly=True)
    goods_id = fields.Many2one('archives.goods', string=u'产品', required=True, readonly=True,
                               domain=lambda self: self.env['archives.organization'].get_goods_organization())
    main_unit_number_total = fields.Float(digits=(6, 2), string=u'数量', readonly=True)
    price = fields.Float(digits=(6, 2), help="单价", string=u'单价', readonly=True)
    money_total = fields.Float(digits=(6, 2), help="金额", string=u'金额', readonly=True)
    main_unit_number_already = fields.Float(digits=(6, 2), string=u'已开票数量', readonly=True)
    money_already = fields.Float(digits=(6, 2), help="金额", string=u'已开票金额', readonly=True)
    main_unit_number = fields.Float(digits=(6, 2), string=u'开票数量')
    money = fields.Float(digits=(6, 2), help="金额", string=u'开票金额', store=True)
    remark = fields.Char(string=u'备注')
