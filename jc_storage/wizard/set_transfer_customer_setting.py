# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

need_set_fields = ['out_store_id', 'in_store_id', 'transfer_out_type_id', 'transfer_in_type_id', 'company_id',
                   'out_unit_id', 'in_unit_id', 'out_staff_id', 'int_staff_id', 'department_id']


class SetCustomerSetting(models.TransientModel):
    _name = 'jc_storage.set_transfer_customer_setting'

    user_id = fields.Many2one('res.users', string=u'用户', readonly=True, index=True, default=lambda self: self.env.user)

    table = fields.Char(string=u'表名', index=True)

    table_show_name = fields.Char(string=u'表名', readonly=True)

    out_store_id = fields.Many2one('archives.store', string=u'调出仓库', required=True,
                                   domain=lambda self: self.env['archives.organization'].get_store_organization())
    in_store_id = fields.Many2one('archives.store', string=u'调入仓库', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_store_organization())
    transfer_out_type_id = fields.Many2one('archives.common_archive', string=u'调出类型', required=True,
                                           domain="[('archive_name','=',20)]")
    transfer_in_type_id = fields.Many2one('archives.common_archive', string=u'调入类型', required=True,
                                          domain="[('archive_name','=',21)]")

    out_unit_id = fields.Many2one('archives.customer', string=u'调出单位', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())
    in_unit_id = fields.Many2one('archives.customer', string=u'调入单位', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_customer_organization())

    out_staff_id = fields.Many2one('archives.staff', string=u'调出员工')
    int_staff_id = fields.Many2one('archives.staff', string=u'调入员工', required=True)
    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())

    def set_default(self, res, table, fields_):
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
