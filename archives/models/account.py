# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Account(models.Model):
    _name = 'archives.account'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在相同账户"),
    ]

    name = fields.Char(string=u'账户', required=True)
    bank_id = fields.Many2one('archives.bank', string=u'开户行')
    number = fields.Integer(string=u'帐号')
    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    remark = fields.Char(string=u'摘要')
