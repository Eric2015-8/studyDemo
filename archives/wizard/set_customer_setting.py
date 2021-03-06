# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SetCustomerSetting(models.TransientModel):
    _name = 'archives.set_customer_setting'

    user_id = fields.Many2one('res.users', string=u'用户', readonly=True, index=True, default=lambda self: self.env.user)

    table = fields.Char(string=u'表名', index=True)

    table_show_name = fields.Char(string=u'表名', readonly=True)

    customer_id = fields.Many2one('archives.customer', string=u'客户',
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())

    type_id = fields.Many2one('archives.common_archive', string=u'销售类型', domain=[('archive_name', '=', 1)])

    company_id = fields.Many2one('res.company', string=u'公司',
                                 default=lambda self: self.env['res.company']._company_default_get())

    staff_id = fields.Many2one('archives.staff', string=u'销售员')

    store_id = fields.Many2one('archives.store', string=u'仓库')

    department_id = fields.Many2one('archives.department', string=u'部门')

    in_store_type_id = fields.Many2one('archives.common_archive', string=u'入库类型', domain=[('archive_name', '=', 18)])

    # 设置默认值
    def set_default(self, res, table, fields_, need_set_fields, type_id_field='type_id'):
        if not need_set_fields:
            return None
        setting = self.env["archives.customer_setting"].search(
            [('user_id', '=', self.env.user.id), ('table', '=', table)])
        if not setting:
            return None
        if not setting.customer_setting_detail:
            return None
        for f in need_set_fields:  # TODO:优化：将need_set_fields与setting.customer_setting_detail匹配起来后赋值
            if f not in fields_:
                continue
            judge = type_id_field if f == 'type_id' else f
            for detail in setting.customer_setting_detail:
                if detail.field == judge:
                    res[f] = detail.value
                    break
            if f == 'company_id' and (not res.has_key('company_id') or not res['company_id']):
                res['company_id'] = self.env['res.company']._company_default_get()
        return None

    # 为空时，设置默认值
    def set_default_if_empty(self, res, table, need_set_fields, type_id_field='type_id'):
        if not need_set_fields:
            return None
        setting = self.env["archives.customer_setting"].search(
            [('user_id', '=', self.env.user.id), ('table', '=', table)])
        if not setting:
            return None
        if not setting.customer_setting_detail:
            return None
        for f in need_set_fields:  # TODO:优化：将need_set_fields与setting.customer_setting_detail匹配起来后赋值
            if res.has_key(f) and res[f]:
                continue
            judge = type_id_field if f == 'type_id' else f
            for detail in setting.customer_setting_detail:
                if detail.field == judge:
                    res[f] = detail.value
                    break
            if f == 'company_id' and (not res.has_key('company_id') or not res['company_id']):
                res['company_id'] = self.env['res.company']._company_default_get()
        return None

    # 打开设置对话框
    def send_and_open(self, need_set_fields, table, table_show_name, type_id_field='type_id'):
        if type_id_field != 'type_id' and 'type_id' in need_set_fields:
            index = need_set_fields.index('type_id')
            need_set_fields[index] = type_id_field
        context = {
            'default_user_id': self.env.user.id,
            'default_table': table,
            'default_table_show_name': table_show_name,
        }
        for f in need_set_fields:
            context[f] = True
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
        self.create_setting_detail_if_need(setting.id, 'customer_id', self.customer_id.id)
        self.create_setting_detail_if_need(setting.id, 'type_id', self.type_id.id)
        self.create_setting_detail_if_need(setting.id, 'company_id', self.company_id.id)
        self.create_setting_detail_if_need(setting.id, 'staff_id', self.staff_id.id)
        self.create_setting_detail_if_need(setting.id, 'store_id', self.store_id.id)
        self.create_setting_detail_if_need(setting.id, 'department_id', self.department_id.id)
        self.create_setting_detail_if_need(setting.id, 'in_store_type_id', self.in_store_type_id.id)

    def create_setting_detail_if_need(self, setting_id, field, value):
        if not self.env.context.get(field, False):
            return
        values = {
            'customer_setting_id': setting_id,
            'field': field,
            'value': value,
        }
        self.env['archives.customer_setting.detail'].create(values)
