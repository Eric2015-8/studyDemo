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

    order_number = fields.Float(digits=(6, 2), string=u'订货数量')
    diff_number = fields.Float(digits=(6, 2), string=u'差异数量')

    remark = fields.Char(string=u'备注')

    @api.onchange('order_number', 'main_unit_number')
    def _onchange_for_diff_number(self):
        for detail in self:
            detail.diff_number = detail.order_number - detail.main_unit_number
