# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReportStorageAccountWizard(models.TransientModel):
    _name = 'jc_finance.report_sale_statistics_wizard'
    _description = u'存储：销售统计查询条件'

    def _get_default_date_from(self):
        date = fields.Date.from_string(fields.Date.today())
        year = date.strftime('%Y')
        month = date.strftime('%m')
        return '{}-{}-01'.format(year, month)

    customer_id = fields.Many2one('archives.customer', string=u'客户',
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())
    staff_id = fields.Many2one('archives.staff', string=u'销售员')
    goods_id = fields.Many2one('archives.goods', string=u'产品')

    date_start = fields.Date(string=u'起始日期', default=_get_default_date_from)
    date_end = fields.Date(string=u'结束日期', default=fields.Date.today)

    type_id = fields.Selection([
        ('customer', '客户'),
        ('staff', '销售员'),
        ('goods', '产品')
    ], string=u'类型', default='customer')

    @api.multi
    def query(self):
        data = self.query_data()
        self.clear_data()
        self.insert_data(data)
        return self.open_result()

    def query_data(self):
        sql = self.get_sql()
        self.env.cr.execute(sql)
        return self.env.cr.fetchall()

    def get_sql(self):
        if self.type_id == 'customer':
            _field = 'customer_id'
        elif self.type_id == 'staff':
            _field = 'staff_id'
        else:
            _field = 'goods_id'
        condition = self.get_condition()
        return 'SELECT {0},second_unit_id,main_unit_id,sum(second_unit_number),sum(main_unit_number),sum(money) ' \
               'FROM jc_finance_report_sale_statistics ' \
               '{1} ' \
               'group by {0},second_unit_id,main_unit_id '. \
            format(_field, condition)

    def get_condition(self):
        if self.customer_id or self.staff_id or self.goods_id or self.date_start or self.date_end:
            condition = 'where '
        else:
            return ''
        if self.customer_id:
            condition += self.get_and(condition)
            condition += 'customer_id = ' + str(self.customer_id.id)
        if self.staff_id:
            condition += self.get_and(condition)
            condition += 'staff_id = ' + str(self.staff_id.id)
        if self.customer_id:
            condition += self.get_and(condition)
            condition += 'goods_id = ' + str(self.goods_id.id)
        if self.date_start:
            condition += self.get_and(condition)
            condition += "date >= '" + str(self.date_start) + "'"
        if self.date_end:
            condition += self.get_and(condition)
            condition += "date <= '" + str(self.date_end) + "'"
        return condition

    def get_and(self, v):
        if len(v) > 6:
            return ' and '
        return ''

    def clear_data(self):
        sql = 'DELETE FROM jc_finance_report_sale_statistics_result WHERE create_uid = ' + str(self._uid)
        self.env.cr.execute(sql)

    def insert_data(self, data):
        sql_format = 'insert into jc_finance_report_sale_statistics_result' \
                     '(create_uid,customer_id,staff_id,goods_id,second_unit_id,main_unit_id,' \
                     'second_unit_number,main_unit_number,money) ' \
                     + self.get_values_format()
        for row in data:
            sql = self.get_insert_sql(row, sql_format)
            self.env.cr.execute(sql)
        return

    def get_values_format(self):
        if self.type_id == 'customer':
            return 'values({0},{1},null,null,{2},{3},{4},{5},{6})'
        elif self.type_id == 'staff':
            return 'values({0},null,{1},null,{2},{3},{4},{5},{6})'
        else:
            return 'values({0},null,null,{1},{2},{3},{4},{5},{6})'

    def get_insert_sql(self, row, sql_format):
        return sql_format.format(self._uid,
                                 self.get_data(row, 0), self.get_data(row, 1), self.get_data(row, 2),
                                 self.get_data(row, 3), self.get_data(row, 4), self.get_data(row, 5))

    def get_data(self, row, index):
        return row[index] if row[index] else 'null'

    def open_result(self):
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('jc_finance.report_sale_statistics_result_action')
        list_view_id = imd.xmlid_to_res_id('jc_finance.report_sale_statistics_result_tree')
        kan_ban_view_id = imd.xmlid_to_res_id('jc_finance.report_sale_statistics_result_kanban')
        # form_view_id = imd.xmlid_to_res_id('archives.archives_common_goods_edit')

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            # 'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'views': [[list_view_id, 'tree'], [kan_ban_view_id, 'kanban']],
            'target': action.target,
            # 'context': action.context,
            # 'context': {
            #     'create_uid': self.env.uid,
            # },
            'res_model': action.res_model,
        }
