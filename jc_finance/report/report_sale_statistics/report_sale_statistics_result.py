# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ReportStorageAccountResult(models.TransientModel):
    _name = 'jc_finance.report_sale_statistics_result'
    _description = u'财务：销售统计查询结果'

    user_id = fields.Many2one('res.users', string=u'用户', readonly=True, index=True, default=lambda self: self.env.user)

    customer_id = fields.Many2one('archives.customer', string=u'客户',
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())
    staff_id = fields.Many2one('archives.staff', string=u'销售员')

    date = fields.Date(string=u'日期', default=fields.Date.today)
    goods_id = fields.Many2one('archives.goods', string=u'产品')
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位')
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位')
    second_unit_number = fields.Float(digits=dp.get_precision('Quantity'), string=u'辅数量')
    main_unit_number = fields.Float(digits=dp.get_precision('Quantity'), string=u'主数量')
    money = fields.Float(digits=(6, 2), help="金额", string=u'金额')
