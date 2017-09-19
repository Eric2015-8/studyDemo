# -*- coding: utf-8 -*-

from odoo import tools
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api


class ReportSaleOrder(models.Model):
    _name = 'report.sale_order'
    _description = u'销售订单分析表'
    _auto = False

    bill_id = fields.Integer(string=u'ID')
    bill_name = fields.Char(string=u'单据编号')

    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态', require=True, default=1, readonly=True
    )

    customer_id = fields.Many2one('archives.customer', string=u'客户名称')
    date = fields.Date(string=u'日期', default=fields.Date.today)
    sale_type_id = fields.Many2one('archives.sale_type', string=u'销售类型')
    remark = fields.Char(string=u'摘要')
    company_id = fields.Many2one('res.company', string=u'公司')
    staff_id = fields.Many2one('archives.staff', string=u'销售员')
    store_id = fields.Many2one('archives.store', string=u'仓库')
    goods_id = fields.Many2one('archives.goods', string=u'产品')
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位')
    second_unit_number = fields.Float(digits=dp.get_precision('Quantity'), string=u'辅数量')
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位')
    main_unit_number = fields.Float(digits=dp.get_precision('Quantity'), string=u'主数量')
    price = fields.Float(u'单价', digits=dp.get_precision('Price'))
    money = fields.Float(digits=dp.get_precision('Amount'), string=u'金额')
    remark_detail = fields.Char(string=u'备注')

    @api.multi
    def test(self):
        return

    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, 'report_sale_order')
        cr.execute(
            """
            create or replace view report_sale_order as (
select
d.id id,
b.ID bill_id,
b.name bill_name,
b.bill_state,
b.customer_id,
b.date,
b.sale_type_id,
b.remark,
b.company_id,
b.staff_id,
b.store_id,
d.goods_id,
g.second_unit_id,
sum(d.second_unit_number) second_unit_number,
g.main_unit_id,
sum(d.main_unit_number) main_unit_number,
d.price,
sum(d.money) money,
d.remark remark_detail
FROM jc_sale_sale_order b 
LEFT JOIN jc_sale_sale_order_detail d ON d.sale_order_id = b.id
LEFT JOIN archives_goods g on d.goods_id = g.id
where d.id is not null
group by d.id,b.id,b.name,b.bill_state,b.customer_id,b.date,b.sale_type_id,b.remark,b.company_id,b.staff_id,b.store_id,d.goods_id,g.second_unit_id,g.main_unit_id,d.price,d.remark

            )
        """)
