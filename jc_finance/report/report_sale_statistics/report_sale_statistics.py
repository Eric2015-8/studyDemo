# -*- coding: utf-8 -*-

from odoo import tools
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api


class ReportSaleStatistics(models.Model):
    _name = 'jc_finance.report_sale_statistics'
    _description = u'财务：销售统计视图'
    _auto = False

    customer_id = fields.Many2one('archives.customer', string=u'客户')
    staff_id = fields.Many2one('archives.staff', string=u'销售员')

    date = fields.Date(string=u'日期', default=fields.Date.today)
    goods_id = fields.Many2one('archives.goods', string=u'产品')
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位')
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位')
    second_unit_number = fields.Float(digits=dp.get_precision('Quantity'), string=u'辅数量')
    main_unit_number = fields.Float(digits=dp.get_precision('Quantity'), string=u'主数量')
    money = fields.Float(digits=(6, 2), help="金额", string=u'金额')

    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, 'jc_finance_report_sale_statistics')
        cr.execute(
            """
            create or replace view jc_finance_report_sale_statistics as (
select
b.customer_id,
b.staff_id,
b.date,
d.goods_id,
g.second_unit_id,
g.main_unit_id,
sum(d.second_unit_number) second_unit_number,
sum(d.main_unit_number) main_unit_number,
sum(d.money) money
FROM jc_finance_sale_account b
LEFT JOIN jc_finance_sale_account_detail d ON d.sale_account_id = b.id
LEFT JOIN archives_goods g on d.goods_id = g.id
where d.id is not null and (b.bill_state=10 or b.bill_state=20)
group by b.customer_id,b.staff_id,b.date,d.goods_id,g.second_unit_id,g.main_unit_id
            )
        """)
