# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MemoTicketDetail(models.Model):
    _name = 'jc_finance.memo_ticket_detail'
    _description = u'财务：记账单明细'

    memo_ticket_id = fields.Many2one('jc_finance.memo_ticket', string=u'记账单引用', required=True,
                                     ondelete='cascade', index=True, copy=False)

    subject_id = fields.Many2one('archives.subject', string=u'科目', required=True)
    money = fields.Float(digits=(6, 2), help="金额", string=u'金额', store=True)
    remark = fields.Char(string=u'备注')
