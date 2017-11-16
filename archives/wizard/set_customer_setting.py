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
    is_show_customer_id = fields.Boolean(u'是否显示客户', default=lambda self: self._is_show('customer_id'))

    type_id = fields.Many2one('archives.common_archive', string=u'销售类型', domain=[('archive_name', '=', 1)])
    is_show_type_id = fields.Boolean(u'是否显示销售类型', default=lambda self: self._is_show('type_id'))

    company_id = fields.Many2one('res.company', string=u'公司',
                                 default=lambda self: self.env['res.company']._company_default_get())
    is_show_company_id = fields.Boolean(u'是否显示公司', default=lambda self: self._is_show('company_id'))

    staff_id = fields.Many2one('archives.staff', string=u'销售员')
    is_show_staff_id = fields.Boolean(u'是否显示销售员', default=lambda self: self._is_show('staff_id'))

    store_id = fields.Many2one('archives.store', string=u'仓库')
    is_show_store_id = fields.Boolean(u'是否显示仓库', default=lambda self: self._is_show('store_id'))

    department_id = fields.Many2one('archives.department', string=u'部门')
    is_show_department_id = fields.Boolean(u'是否显示部门', default=lambda self: self._is_show('department_id'))

    in_store_type_id = fields.Many2one('archives.common_archive', string=u'入库类型', domain=[('archive_name', '=', 18)])
    is_show_in_store_type_id = fields.Boolean(u'是否显示入库类型', default=lambda self: self._is_show('in_store_type_id'))

    sale_return_type_id = fields.Many2one('archives.common_archive', string=u'销售退货类型',
                                          domain="[('archive_name','=',22)]")
    is_show_sale_return_type_id = fields.Boolean(u'是否显示销售退货类型',
                                                 default=lambda self: self._is_show('sale_return_type_id'))

    def _is_show(self, field):
        if 'need_set_fields' not in self.env.context:  # 之所以添加这个判断，是因为添加新字段后升级，会报错
            return False
        return field in self.env.context['need_set_fields']

    def set_default(self, res, table, fields_, need_set_fields):
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
            for detail in setting.customer_setting_detail:
                if detail.field == f:
                    res[f] = detail.value
                    break
            if f == 'company_id' and (not res.has_key('company_id') or not res['company_id']):
                res['company_id'] = self.env['res.company']._company_default_get()
        return None

    def set_default_if_empty(self, res, table, need_set_fields):
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
            for detail in setting.customer_setting_detail:
                if detail.field == f:
                    res[f] = detail.value
                    break
            if f == 'company_id' and (not res.has_key('company_id') or not res['company_id']):
                res['company_id'] = self.env['res.company']._company_default_get()
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
        if self.is_show_customer_id:
            self.create_setting_detail(setting.id, 'customer_id', self.customer_id.id)
        if self.is_show_type_id:
            self.create_setting_detail(setting.id, 'type_id', self.type_id.id)
        if self.is_show_company_id:
            self.create_setting_detail(setting.id, 'company_id', self.company_id.id)
        if self.is_show_staff_id:
            self.create_setting_detail(setting.id, 'staff_id', self.staff_id.id)
        if self.is_show_store_id:
            self.create_setting_detail(setting.id, 'store_id', self.store_id.id)
        if self.is_show_department_id:
            self.create_setting_detail(setting.id, 'department_id', self.department_id.id)
        if self.is_show_in_store_type_id:
            self.create_setting_detail(setting.id, 'in_store_type_id', self.in_store_type_id.id)
        if self.is_show_sale_return_type_id:
            self.create_setting_detail(setting.id, 'sale_return_type_id', self.sale_return_type_id.id)

    def create_setting_detail(self, setting_id, field, value):
        values = {
            'customer_setting_id': setting_id,
            'field': field,
            'value': value,
        }
        self.env['archives.customer_setting.detail'].create(values)
