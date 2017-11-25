# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleReturnStore(models.Model):
    _name = 'jc_sale.sale_return.detail'
    _description = u'销售：销售退单明细'

    _inherit = ['goods.detail.mobile']

    sale_return_id = fields.Many2one('jc_sale.sale_return', string=u'销售退库引用', required=True,
                                     ondelete='cascade', index=True, copy=False)

    remark = fields.Char(string=u'备注')
