# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.utils import bill_define


class AccountBookDetail(models.Model):
    _name = 'archives.account_book_detail'
    _description = u'档案：账本_明细'

    account_book_id = fields.Many2one('archives.account_book', string=u'账本引用', required=True,
                                      ondelete='cascade', index=True, copy=False)

    bill_type_id = fields.Selection(bill_define.BILL_TYPE, string=u'单据', require=True)
    common_archive_id = fields.Many2one('archives.common_archive', string=u'通用档案')
    direct = fields.Selection([
        (1, '借'),
        (2, '贷'),
    ], string=u'借贷方向', require=True)
