# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.utils import bill_define


class ReceiptDetail(models.Model):
    _name = 'jc_finance.receipt_detail'
    _description = u'财务：收款单明细'

    receipt_id = fields.Many2one('jc_finance.receipt', string='收款单引用', required=True,
                                 ondelete='cascade', index=True, copy=False)

    # source_bill_type = fields.Selection(bill_define.BILL_TYPE, string=u'来源单据类型', readonly=True, copy=False)
    # source_bill_id = fields.Integer(string="来源单据号", readonly=True, copy=False, default=0)
    # source_detail_id = fields.Integer(string="来源单据明细号", readonly=True, copy=False, default=0)

    subject_id = fields.Many2one('archives.subject', string=u'科目', required=True)
    money = fields.Float(digits=(6, 2), help="金额", string=u'金额', store=True)
    remark = fields.Char(string=u'备注')
