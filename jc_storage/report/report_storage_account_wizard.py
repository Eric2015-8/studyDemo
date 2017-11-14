# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ReportStorageAccountWizard(models.TransientModel):
    _name = 'jc_storage.report_storage_account_wizard'
    _description = u'存储：库存账查询条件'

    user_id = fields.Many2one('res.users', string=u'用户', readonly=True, index=True, default=lambda self: self.env.user)

    store_id = fields.Many2one('archives.store', string=u'仓库',
                               domain=lambda self: self.env['archives.organization'].get_store_organization())

    date_start = fields.Date(string=u'起始日期', default=fields.Date.today)
    date_end = fields.Date(string=u'结束日期', default=fields.Date.today)
    unit_id = fields.Selection([
        ('main', '主单位'),
        ('second', '辅单位')
    ], string=u'单位', default='main')

    def send_and_open(self, table, table_show_name):
        context = {
            'default_user_id': self.env.user.id,
            'default_table': table,
            'default_table_show_name': table_show_name,
        }
        setting = self.env["archives.customer_setting"].search(
            [('user_id', '=', self.env.user.id), ('table', '=', table)])
        if setting and setting.customer_setting_detail:
            for detail in setting.customer_setting_detail:
                context['default_' + detail.field] = detail.value
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'jc_storage.set_transfer_customer_setting',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': context
        }

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
        unit_field = 'main_unit_id' if self.unit_id == 'main' else 'second_unit_id'
        number_field = self.get_number_field()
        start = self.get_start(number_field)
        add = self.get_add(number_field)
        sub = self.get_sub(number_field)
        end = self.get_end(number_field)
        condition = self.get_condition()
        group = 'group by goods_id,' + unit_field
        return 'SELECT goods_id,{0},{1},{2},{3},{4} FROM jc_storage_report_storage_account {5} {6}'. \
            format(unit_field, start, add, sub, end, condition, group)

    def get_start(self, number_field):
        if self.date_start:
            return "sum(case when date < '{0}' then {1} end)".format(self.date_start, number_field[2])
        else:
            return "null"

    def get_add(self, number_field):
        return self.get_current(number_field[0])

    def get_sub(self, number_field):
        return self.get_current(number_field[1])

    def get_current(self, field_):
        if self.date_start and self.date_end:
            return "sum(case when date >= '{0}' and date <= '{1}' then {2} end)" \
                .format(self.date_start, self.date_end, field_)
        elif self.date_start and not self.date_end:
            return "sum(case when date >= '{0}' then {1} end)".format(self.date_start, field_)
        elif not self.date_start and self.date_end:
            return "sum(case when date <= '{0}' then {1} end)".format(self.date_end, field_)
        else:
            return 'sum({0})'.format(field_)

    def get_end(self, number_field):
        if self.date_end:
            return "sum(case when date <= '{0}' then {1} end)".format(self.date_end, number_field[2])
        return 'sum({0})'.format(number_field[2])

    def get_condition(self):
        if self.store_id:
            return 'WHERE store_id = ' + str(self.store_id.id)
        return ''

    def get_number_field(self):
        if self.unit_id == 'main':
            return 'main_unit_number_add', 'main_unit_number_sub', 'main_unit_number_balance'
        return 'second_unit_number_add', 'second_unit_number_sub', 'second_unit_number_balance'

    def clear_data(self):
        sql = 'DELETE FROM jc_storage_report_storage_account_result WHERE user_id = ' + str(self.user_id.id)
        self.env.cr.execute(sql)

    def insert_data(self, data):
        sql_format = 'insert into jc_storage_report_storage_account_result' \
                     '(user_id,goods_id,unit_id,number_start,number_add,number_sub,number_end) ' \
                     'values({0},{1},{2},{3},{4},{5},{6})'
        for row in data:
            sql = self.get_insert_sql(row, sql_format)
            self.env.cr.execute(sql)
        return

    def get_insert_sql(self, row, sql_format):
        return sql_format.format(self.user_id.id,
                                 self.get_data(row, 0), self.get_data(row, 1), self.get_data(row, 2),
                                 self.get_data(row, 3), self.get_data(row, 4), self.get_data(row, 5))

    def get_data(self, row, index):
        return row[index] if row[index] else 'null'

    def open_result(self):
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('jc_storage.report_storage_account_action')
        list_view_id = imd.xmlid_to_res_id('jc_storage.report_storage_account_tree')
        # form_view_id = imd.xmlid_to_res_id('archives.archives_common_goods_edit')

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            # 'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'views': [[list_view_id, 'tree']],
            'target': action.target,
            # 'context': action.context,
            'context': {
                'user_id': self.env.uid,
            },
            'res_model': action.res_model,
        }

    def create_setting(self):
        values = {
            'user_id': self.user_id.id,
            'table': self.table,
            'table_show_name': self.table_show_name,
        }
        setting = self.env['archives.customer_setting'].create(values)
        self.create_setting_detail(setting.id, 'out_store_id', self.out_store_id.id)
        self.create_setting_detail(setting.id, 'in_store_id', self.in_store_id.id)
        self.create_setting_detail(setting.id, 'transfer_out_type_id', self.transfer_out_type_id.id)
        self.create_setting_detail(setting.id, 'transfer_in_type_id', self.transfer_in_type_id.id)
        self.create_setting_detail(setting.id, 'company_id', self.company_id.id)
        self.create_setting_detail(setting.id, 'out_unit_id', self.out_unit_id.id)
        self.create_setting_detail(setting.id, 'in_unit_id', self.in_unit_id.id)
        self.create_setting_detail(setting.id, 'out_staff_id', self.out_staff_id.id)
        self.create_setting_detail(setting.id, 'int_staff_id', self.int_staff_id.id)
        self.create_setting_detail(setting.id, 'department_id', self.department_id.id)

    def create_setting_detail(self, setting_id, field, value):
        values = {
            'customer_setting_id': setting_id,
            'field': field,
            'value': value,
        }
        self.env['archives.customer_setting.detail'].create(values)
