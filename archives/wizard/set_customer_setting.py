# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SetCustomerSetting(models.TransientModel):
    _name = 'archives.set_customer_setting'

    user_id = fields.Many2one('res.users', string=u'用户', readonly=True, index=True, default=lambda self: self.env.user)

    table = fields.Char(string=u'表名', index=True)

    table_show_name = fields.Char(string=u'表名', readonly=True)

    customer_id = fields.Many2one('archives.customer', string=u'客户名称',
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())
    sale_type_id = fields.Many2one('archives.common_archive', string=u'销售类型', domain=[('archive_name', '=', 1)])
    company_id = fields.Many2one('res.company', string=u'公司',
                                 default=lambda self: self.env['res.company']._company_default_get())
    staff_id = fields.Many2one('archives.staff', string=u'销售员')
    store_id = fields.Many2one('archives.store', string=u'仓库')
    department_id = fields.Many2one('archives.department', string=u'部门')

    def query_default(self, table, field):
        setting = self.env["archives.customer_setting"].search(
            [('user_id', '=', self.env.user.id), ('table', '=', table)])
        if setting and setting.customer_setting_detail:
            for detail in setting.customer_setting_detail:
                if detail.field == field:
                    return detail.value
        return None

    def send_and_open(self, need_set_fields, table, table_show_name):
        context = {
            'need_set_fields': need_set_fields,
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
            'res_model': 'archives.set_customer_setting',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': context
        }

    @api.multi
    def subscribe(self):
        # self.test()
        setting = self.env["archives.customer_setting"].search(
            [('user_id', '=', self.user_id.id), ('table', '=', self.table)])
        if setting:
            setting.unlink()
        self.create_setting()
        return {}

    def create_setting(self):
        values = {
            'user_id': self.user_id.id,
            'table': self.table,
            'table_show_name': self.table_show_name,
        }
        setting = self.env['archives.customer_setting'].create(values)
        self.create_setting_detail(setting.id, 'customer_id', self.customer_id.id)
        self.create_setting_detail(setting.id, 'sale_type_id', self.sale_type_id.id)
        self.create_setting_detail(setting.id, 'company_id', self.company_id.id)
        self.create_setting_detail(setting.id, 'staff_id', self.staff_id.id)
        self.create_setting_detail(setting.id, 'store_id', self.store_id.id)
        self.create_setting_detail(setting.id, 'department_id', self.department_id.id)

    def create_setting_detail(self, setting_id, field, value):
        values = {
            'customer_setting_id': setting_id,
            'field': field,
            'value': value,
        }
        self.env['archives.customer_setting.detail'].create(values)

    def test(self):
        s = ''
        if self.user_id:
            s += 'user_id:' + str(self.user_id.id) + ';--'
        if self.table:
            s += 'table:' + str(self.table) + ';--'
        if self.table_show_name:
            s += 'table_show_name:' + self.table_show_name + ';--'
        if self.customer_id:
            s += 'customer_id:' + str(self.customer_id.id) + ';--'
        if self.sale_type_id:
            s += 'sale_type_id:' + str(self.sale_type_id.id) + ';--'
        if self.company_id:
            s += 'company_id:' + str(self.company_id.id) + ';--'
        if self.staff_id:
            s += 'staff_id:' + str(self.staff_id.id) + ';--'
        if self.store_id:
            s += 'store_id:' + str(self.store_id.id) + ';--'
        if self.department_id:
            s += 'department_id:' + str(self.department_id.id) + ';--'
        raise ValidationError(s)
