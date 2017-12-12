# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import base_infor


class Account(base_infor.BaseInfoUnique):
    _name = 'archives.account'
    _description = u'档案：账户'

    name = fields.Char(string=u'账户', required=True)
    bank_id = fields.Many2one('archives.bank', string=u'开户行')
    number = fields.Integer(string=u'帐号')
    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    remark = fields.Char(string=u'摘要')
