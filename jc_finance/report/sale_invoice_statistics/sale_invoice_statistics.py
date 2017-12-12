# -*- coding: utf-8 -*-

from odoo import tools
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api


class SaleInvoiceStatistics(models.Model):
    _name = 'jc_finance.sale_invoice_statistics'
    _description = u'财务：销售发票分析视图'
    _auto = False

    date = fields.Date(string=u'日期')
    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态'
    )
    company_id = fields.Many2one('res.company', string=u'公司')
    department_id = fields.Many2one('archives.department', string=u'部门')
    staff_id = fields.Many2one('archives.staff', string=u'业务员', domain=[('is_sale_man', '=', True)])
    customer_id = fields.Many2one('archives.customer', string=u'客户')
    type_id = fields.Many2one('archives.common_archive', string=u'发票类型', domain=[('archive_name', '=', 27)])
    remark = fields.Char(string=u'摘要')

    goods_id = fields.Many2one('archives.goods', string=u'产品')
    number = fields.Float(digits=(6, 2), string=u'数量')
    # price = fields.Float(digits=(6, 2), string=u'单价')
    money = fields.Float(digits=(6, 2), string=u'金额')

    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, 'jc_finance_sale_invoice_statistics')
        cr.execute(
            """
            create or replace view jc_finance_sale_invoice_statistics as (
select
b.date,
b.bill_state,
b.company_id,
b.department_id,
b.staff_id,
b.customer_id,
b.type_id,
b.remark,
d.goods_id,
d.number,
d.money
FROM jc_finance_sale_invoice b
LEFT JOIN jc_finance_sale_invoice_invoice_detail d ON d.sale_invoice_id = b.id
            )
        """)
