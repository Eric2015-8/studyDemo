# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class SaleInvoiceStatisticsResult(models.TransientModel):
    _name = 'jc_finance.sale_invoice_statistics_result'
    _description = u'财务：销售发票分析查询结果'

    company_id = fields.Many2one('res.company', string=u'公司')
    department_id = fields.Many2one('archives.department', string=u'部门')
    staff_id = fields.Many2one('archives.staff', string=u'业务员', domain=[('is_sale_man', '=', True)])
    customer_id = fields.Many2one('archives.customer', string=u'客户')
    type_id = fields.Many2one('archives.common_archive', string=u'发票类型', domain=[('archive_name', '=', 27)])
    remark = fields.Char(string=u'摘要')

    goods_id = fields.Many2one('archives.goods', string=u'产品')
    number = fields.Float(digits=(6, 2), string=u'数量')
    price = fields.Float(digits=(6, 2), string=u'单价')
    money = fields.Float(digits=(6, 2), string=u'金额')
