# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import bill_define


class SaleAccountDetail(models.Model):
    _name = 'jc_finance.sale_account.detail'
    _description = u'财务：销售账单明细'

    _inherit = ['goods.detail.mobile']

    sale_account_id = fields.Many2one('jc_finance.sale_account', string='销售账单引用', required=True,
                                      ondelete='cascade', index=True, copy=False)

    source_bill_type = fields.Selection(bill_define.BILL_TYPE, string=u'来源单据类型', readonly=True, copy=False)
    source_bill_id = fields.Integer(string="来源单据号", readonly=True, copy=False, default=0)
    source_detail_id = fields.Integer(string="来源单据明细号", readonly=True, copy=False, default=0)

    remark = fields.Char(string=u'备注')
