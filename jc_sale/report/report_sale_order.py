# -*- coding: utf-8 -*-

from odoo import tools
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api


class ReportSaleOrder(models.Model):
    _name = 'report.sale_order'
    _description = u'销售订单分析表'
    _auto = False

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
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位', compute='_set_main')
    main_unit_number = fields.Float(digits=dp.get_precision('Quantity'), string=u'主数量')
    price = fields.Float(u'单价', digits=dp.get_precision('Price'))
    money = fields.Float(digits=dp.get_precision('Amount'), string=u'金额')
    remark_detail = fields.Char(string=u'备注')

    # department_id = fields.Many2one('staff.department', u'部门')
    # user_id = fields.Many2one('res.users', u'销售员')
    # goods = fields.Char(u'商品名')
    # goods_id = fields.Many2one('goods', u'商品')
    # brand_id = fields.Many2one('core.value', u'品牌')
    # location = fields.Char(u'库位')
    # uom = fields.Char(u'单位')
    # uos = fields.Char(u'辅助单位')
    # lot = fields.Char(u'批号')
    # attribute_id = fields.Char(u'属性')
    # warehouse = fields.Char(u'仓库')
    # goods_qty = fields.Float(u'数量', digits=dp.get_precision('Quantity'))
    # goods_uos_qty = fields.Float(u'辅助单位数量', digits=dp.get_precision('Quantity'))
    # price = fields.Float(u'单价', digits=dp.get_precision('Price'))
    # amount = fields.Float(u'销售收入', digits=dp.get_precision('Amount'))
    # tax_amount = fields.Float(u'税额', digits=dp.get_precision('Amount'))
    # subtotal = fields.Float(u'价税合计', digits=dp.get_precision('Amount'))
    # margin = fields.Float(u'毛利', digits=dp.get_precision('Amount'))

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
b.ID,
b.bill_state,
b.customer_id,
b.date,
b.sale_type_id,
b.remark,
b.company_id,
b.staff_id,
b.store_id,
d.goods_id,
--d.second_unit_id,
sum(d.second_unit_number) second_unit_number,
--d.main_unit_id,
sum(d.main_unit_number) main_unit_number,
d.price,
--sum(d.money),
d.remark remark_detail
FROM jc_sale_sale_order b 
LEFT JOIN jc_sale_sale_order_detail d ON d.sale_order_id = b.id
group by b.id,b.bill_state,b.customer_id,b.date,b.sale_type_id,b.remark,b.company_id,b.staff_id,b.store_id,d.goods_id,d.price,d.remark

            )
        """)
