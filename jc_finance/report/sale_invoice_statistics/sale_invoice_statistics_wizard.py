# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleInvoiceStatisticsWizard(models.TransientModel):
    _name = 'jc_finance.sale_invoice_statistics_wizard'
    _description = u'财务：销售发票分析查询条件'

    def _get_default_date_from(self):
        date = fields.Date.from_string(fields.Date.today())
        year = date.strftime('%Y')
        month = date.strftime('%m')
        return '{}-{}-01'.format(year, month)

    date_start = fields.Date(string=u'起始日期', default=_get_default_date_from)
    date_end = fields.Date(string=u'结束日期', default=fields.Date.today)
    # date = fields.Date(string=u'日期')

    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态'
    )
    company_id = fields.Many2one('res.company', string=u'公司',
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    department_id = fields.Many2one('archives.department', string=u'部门',
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())
    staff_id = fields.Many2one('archives.staff', string=u'业务员', domain=[('is_sale_man', '=', True)])
    customer_id = fields.Many2one('archives.customer', string=u'客户',
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())
    type_id = fields.Many2one('archives.common_archive', string=u'发票类型', domain=[('archive_name', '=', 27)])
    remark = fields.Char(string=u'摘要')

    goods_id = fields.Many2one('archives.goods', string=u'产品',
                               domain=lambda self: self.env['archives.organization'].get_goods_organization())

    # 显示字段：
    s_company_id = fields.Boolean(string=u'公司')
    s_department_id = fields.Boolean(string=u'部门')
    s_staff_id = fields.Boolean(string=u'业务员')
    s_customer_id = fields.Boolean(string=u'客户')
    s_type_id = fields.Boolean(string=u'发票类型')
    s_remark = fields.Boolean(string=u'摘要')

    s_goods_id = fields.Boolean(string=u'产品')
    s_number = fields.Boolean(string=u'数量')
    s_price = fields.Boolean(string=u'单价')
    s_money = fields.Boolean(string=u'金额')

    @api.multi
    def query(self):
        show_fields = self._get_show_fields()
        data = self.query_data(show_fields)
        self.clear_data()
        self.insert_data(data, show_fields)
        return self.open_result(show_fields)

    def _get_show_fields(self):
        show_fields = []
        if self.s_company_id:
            show_fields.append('company_id')
        if self.s_department_id:
            show_fields.append('department_id')
        if self.s_staff_id:
            show_fields.append('staff_id')
        if self.s_customer_id:
            show_fields.append('customer_id')
        if self.s_type_id:
            show_fields.append('type_id')
        if self.s_remark:
            show_fields.append('remark')
        if self.s_goods_id:
            show_fields.append('goods_id')
        if self.s_number:
            show_fields.append('number')
        if self.s_price:
            show_fields.append('price')
        if self.s_money:
            show_fields.append('money')
        if not show_fields:
            raise ValidationError('请选择显示字段')
        return show_fields

    def query_data(self, show_fields):
        sql = self.get_sql(show_fields)
        self.env.cr.execute(sql)
        return self.env.cr.fetchall()

    def get_sql(self, show_fields):
        select_and_group = self._get_select_and_group(show_fields)
        condition = self.get_condition()
        if len(condition) > 6:
            condition += ' and '
        else:
            condition += 'where '
        condition += 'number>0'
        sql = 'SELECT {} ' \
              'FROM jc_finance_sale_invoice_statistics ' \
              '{} '. \
            format(select_and_group[0], condition)
        if select_and_group[1]:
            sql += ' group by ' + select_and_group[1]
        return sql

    def _get_select_and_group(self, show_fields):
        arr = []
        group_arr = []
        for f in show_fields:
            if f == 'number':
                arr.append('sum(number)')
            elif f == 'price':
                arr.append('sum(money)/sum(number) as price')
            elif f == 'money':
                arr.append('sum(money)')
            else:
                arr.append(f)
                group_arr.append(f)
        return ','.join(arr), ','.join(group_arr)

    def get_condition(self):
        a = self._get_condition_from_select()
        cs = '' if self.customer_id else self.env[
            'archives.organization'].get_customer_organization_condition_staff('staff_id')
        co = '' if self.customer_id else self.env[
            'archives.organization'].get_customer_organization_condition_organization('customer_organization_id')
        gt = '' if self.goods_id else self.env[
            'archives.organization'].get_goods_organization_condition_goods_type('goods_type_id')
        go = '' if self.goods_id else self.env[
            'archives.organization'].get_goods_organization_condition_organization('goods_organization_id')
        t = SaleInvoiceStatisticsWizard._combine_condition(a, cs)
        t2 = SaleInvoiceStatisticsWizard._combine_condition(t, co)
        t3 = SaleInvoiceStatisticsWizard._combine_condition(t2, gt)
        return SaleInvoiceStatisticsWizard._combine_condition(t3, go)

    @staticmethod
    def _combine_condition(condition, s_no_where):
        if len(s_no_where) == 0:
            return condition
        if len(condition) == 0:
            return 'where ' + s_no_where
        return condition + ' and ' + s_no_where

    def _get_condition_from_select(self):
        if self.customer_id or self.staff_id or self.goods_id or self.date_start or self.date_end or self.bill_state \
                or self.company_id or self.department_id or self.type_id or self.remark:
            condition = 'where '
        else:
            return ''
        if self.customer_id:
            condition += self.get_and(condition)
            condition += 'customer_id = ' + str(self.customer_id.id)
        if self.staff_id:
            condition += self.get_and(condition)
            condition += 'staff_id = ' + str(self.staff_id.id)
        if self.goods_id:
            condition += self.get_and(condition)
            condition += 'goods_id = ' + str(self.goods_id.id)
        if self.date_start:
            condition += self.get_and(condition)
            condition += "date >= '" + str(self.date_start) + "'"
        if self.date_end:
            condition += self.get_and(condition)
            condition += "date <= '" + str(self.date_end) + "'"
        if self.bill_state:
            condition += self.get_and(condition)
            condition += 'bill_state = ' + str(self.bill_state)
        if self.company_id:
            condition += self.get_and(condition)
            condition += 'company_id = ' + str(self.company_id.id)
        if self.department_id:
            condition += self.get_and(condition)
            condition += 'department_id = ' + str(self.department_id.id)
        if self.type_id:
            condition += self.get_and(condition)
            condition += 'type_id = ' + str(self.type_id.id)
        if self.remark:
            condition += self.get_and(condition)
            condition += "remark ilike '%" + self.remark + "%'"
        return condition

    def get_and(self, v):
        if len(v) > 6:
            return ' and '
        return ''

    def clear_data(self):
        sql = 'DELETE FROM jc_finance_sale_invoice_statistics_result WHERE create_uid = ' + str(self._uid)
        self.env.cr.execute(sql)

    def insert_data(self, data, show_fields):
        fields_str = ','.join(show_fields)
        sql_format = 'insert into jc_finance_sale_invoice_statistics_result' \
                     '(create_uid,{}) '.format(fields_str)
        for row in data:
            sql = self.get_insert_sql(row, sql_format, show_fields)
            self.env.cr.execute(sql)
        return

    def get_insert_sql(self, row, sql_format, show_fields):
        values = []
        index = 0
        for f in show_fields:
            if f == 'remark':
                values.append(self.get_data_string(row, index))
            else:
                values.append(str(self.get_data(row, index)))
            index += 1
        return sql_format + 'values(' + str(self._uid) + ',' + ','.join(values) + ')'

    def get_data(self, row, index):
        return row[index] if row[index] else 'null'

    def get_data_string(self, row, index):
        return "'" + str(row[index]) + "'" if row[index] else 'null'

    def open_result(self, show_fields):
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('jc_finance.sale_invoice_statistics_result_action')
        list_view_id = imd.xmlid_to_res_id('jc_finance.sale_invoice_statistics_result_tree')
        kan_ban_view_id = imd.xmlid_to_res_id('jc_finance.sale_invoice_statistics_result_kanban')
        # form_view_id = imd.xmlid_to_res_id('archives.archives_common_goods_edit')

        context = self._get_context(show_fields)

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
            'context': context,
            'res_model': action.res_model,
            'domain': "[('create_uid','=',%s)]" % self._uid,
        }

    def _get_context(self, show_fields):
        context = {}
        for f in show_fields:
            context[f] = 1
        return context
