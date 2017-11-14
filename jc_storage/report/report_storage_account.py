# -*- coding: utf-8 -*-

from odoo import tools
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api


class ReportStorageAccount(models.Model):
    _name = 'jc_storage.report_storage_account'
    _description = u'存储：库存账视图'
    _auto = False

    date = fields.Date(string=u'日期', default=fields.Date.today)
    store_id = fields.Many2one('archives.store', string=u'仓库')
    goods_id = fields.Many2one('archives.goods', string=u'产品')
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位')
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位')
    second_unit_number_add = fields.Float(digits=dp.get_precision('Quantity'), string=u'辅数量增加')
    main_unit_number_add = fields.Float(digits=dp.get_precision('Quantity'), string=u'主数量增加')
    second_unit_number_sub = fields.Float(digits=dp.get_precision('Quantity'), string=u'辅数量减少')
    main_unit_number_sub = fields.Float(digits=dp.get_precision('Quantity'), string=u'主数量减少')
    second_unit_number_balance = fields.Float(digits=dp.get_precision('Quantity'), string=u'辅数量')
    main_unit_number_balance = fields.Float(digits=dp.get_precision('Quantity'), string=u'主数量')

    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, 'jc_storage_report_storage_account')
        cr.execute(
            """
            create or replace view jc_storage_report_storage_account as (
--其他入库
select
b.date,
b.store_id,
d.goods_id,
g.second_unit_id,
g.main_unit_id,
sum(d.second_unit_number) second_unit_number_add,
sum(d.main_unit_number) main_unit_number_add,
null as second_unit_number_sub,
null as main_unit_number_sub,
sum(d.second_unit_number) second_unit_number_balance,
sum(d.main_unit_number) main_unit_number_balance
FROM jc_storage_other_in_store b 
LEFT JOIN jc_storage_other_in_store_detail d ON d.other_in_store_id = b.id
LEFT JOIN archives_goods g on d.goods_id = g.id
where d.id is not null and (b.bill_state=10 or b.bill_state=20)
group by b.date,b.store_id,d.goods_id,g.second_unit_id,g.main_unit_id

union all
--其他出库
select
b.date,
b.store_id,
d.goods_id,
g.second_unit_id,
g.main_unit_id,
null as second_unit_number_add,
null as main_unit_number_add,
sum(d.second_unit_number) second_unit_number_sub,
sum(d.main_unit_number) main_unit_number_sub,
sum(-1*d.second_unit_number) second_unit_number_balance,
sum(-1*d.main_unit_number) main_unit_number_balance
FROM jc_storage_other_out_store b 
LEFT JOIN jc_storage_other_out_store_detail d ON d.other_out_store_id = b.id
LEFT JOIN archives_goods g on d.goods_id = g.id
where d.id is not null and (b.bill_state=10 or b.bill_state=20)
group by b.date,b.store_id,d.goods_id,g.second_unit_id,g.main_unit_id

union all
--销售出库
select
b.out_store_date,
b.store_id,
d.goods_id,
g.second_unit_id,
g.main_unit_id,
null as second_unit_number_add,
null as main_unit_number_add,
sum(d.second_unit_number) second_unit_number_sub,
sum(d.main_unit_number) main_unit_number_sub,
sum(-1*d.second_unit_number) second_unit_number_balance,
sum(-1*d.main_unit_number) main_unit_number_balance
FROM jc_storage_sale_out_store b 
LEFT JOIN jc_storage_sale_out_store_detail d ON d.sale_out_store_id = b.id
LEFT JOIN archives_goods g on d.goods_id = g.id
where d.id is not null and (b.bill_state=10 or b.bill_state=20)
group by b.out_store_date,b.store_id,d.goods_id,g.second_unit_id,g.main_unit_id

union all
--调拨出库
select
b.date,
b.out_store_id,
d.goods_id,
g.second_unit_id,
g.main_unit_id,
null as second_unit_number_add,
null as main_unit_number_add,
sum(d.second_unit_number) second_unit_number_sub,
sum(d.main_unit_number) main_unit_number_sub,
sum(-1*d.second_unit_number) second_unit_number_balance,
sum(-1*d.main_unit_number) main_unit_number_balance
FROM jc_storage_transfer_out b 
LEFT JOIN jc_storage_transfer_out_detail d ON d.transfer_out_id = b.id
LEFT JOIN archives_goods g on d.goods_id = g.id
where d.id is not null and (b.bill_state=10 or b.bill_state=20)
group by b.date,b.out_store_id,d.goods_id,g.second_unit_id,g.main_unit_id

union all
--调拨入库
select
b.date,
b.in_store_id,
d.goods_id,
g.second_unit_id,
g.main_unit_id,
sum(d.second_unit_number) second_unit_number_add,
sum(d.main_unit_number) main_unit_number_add,
null as second_unit_number_sub,
null as main_unit_number_sub,
sum(d.second_unit_number) second_unit_number_balance,
sum(d.main_unit_number) main_unit_number_balance
FROM jc_storage_transfer_in b 
LEFT JOIN jc_storage_transfer_in_detail d ON d.transfer_in_id = b.id
LEFT JOIN archives_goods g on d.goods_id = g.id
where d.id is not null and (b.bill_state=10 or b.bill_state=20)
group by b.date,b.in_store_id,d.goods_id,g.second_unit_id,g.main_unit_id

union all
--销售退库
select
b.date,
b.store_id,
d.goods_id,
g.second_unit_id,
g.main_unit_id,
sum(d.second_unit_number) second_unit_number_add,
sum(d.main_unit_number) main_unit_number_add,
null as second_unit_number_sub,
null as main_unit_number_sub,
sum(d.second_unit_number) second_unit_number_balance,
sum(d.main_unit_number) main_unit_number_balance
FROM jc_storage_sale_return_store b 
LEFT JOIN jc_storage_sale_return_store_detail d ON d.sale_return_store_id = b.id
LEFT JOIN archives_goods g on d.goods_id = g.id
where d.id is not null and (b.bill_state=10 or b.bill_state=20)
group by b.date,b.store_id,d.goods_id,g.second_unit_id,g.main_unit_id

union all
--库存盘点
select
b.stock_date,
b.store_id,
d.goods_id,
g.second_unit_id,
g.main_unit_id,
null as second_unit_number_add,
null as main_unit_number_add,
sum(d.second_unit_number_compute-d.second_unit_number) second_unit_number_sub,
sum(d.main_unit_number_compute-d.main_unit_number) main_unit_number_sub,
sum(d.second_unit_number-d.second_unit_number_compute) second_unit_number_balance,
sum(d.main_unit_number-d.main_unit_number_compute) main_unit_number_balance
FROM jc_storage_stock_check b 
LEFT JOIN jc_storage_stock_check_detail d ON d.stock_check_id = b.id
LEFT JOIN archives_goods g on d.goods_id = g.id
where d.id is not null and (b.bill_state=10 or b.bill_state=20)
group by b.stock_date,b.store_id,d.goods_id,g.second_unit_id,g.main_unit_id
            )
        """)
