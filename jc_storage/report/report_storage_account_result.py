# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ReportStorageAccountResult(models.TransientModel):
    _name = 'jc_storage.report_storage_account_result'
    _description = u'存储：库存账查询结果'

    user_id = fields.Many2one('res.users', string=u'用户', readonly=True, index=True, default=lambda self: self.env.user)

    goods_id = fields.Many2one('archives.goods', string=u'产品')
    unit_id = fields.Many2one('archives.unit', string=u'单位')
    number_start = fields.Float(digits=dp.get_precision('Quantity'), string=u'期初数量')
    number_add = fields.Float(digits=dp.get_precision('Quantity'), string=u'本期增加')
    number_sub = fields.Float(digits=dp.get_precision('Quantity'), string=u'本期减少')
    number_end = fields.Float(digits=dp.get_precision('Quantity'), string=u'期末数量')
