# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _name = 'jc_sale.sale_order'

    forecast_id = fields.Many2one('jc_sale.sale_forecast', string=u'销售预报单ID')

    customer_id = fields.Many2one('archives.customer', string=u'客户名称', required=True)
    date = fields.Date(string=u'日期', required=True, default=fields.Date.today)
    saleType_id = fields.Many2one('archives.sale_type', string=u'销售类型', required=True)
    remark = fields.Char(string=u'摘要')

    sale_order_detail = fields.One2many('jc_sale.sale_order.detail', 'sale_order_id', string=u'销售订单明细', copy=True)

    company_id = fields.Many2one('archives.company', string=u'公司')
    staff_id = fields.Many2one('archives.staff', related='customer_id.staff_id', string=u'销售员', required=True)
    store_id = fields.Many2one('archives.store', string=u'仓库')
