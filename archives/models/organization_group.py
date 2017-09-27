# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OrganizationGroup(models.Model):
    _name = 'archives.organization_group'
    _description = u'档案：数据权限组'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(user_id)',
         "已存在相同名称的数据权限组"),
    ]

    name = fields.Char(string=u'名称', required=True, copy=False)

    user_ids = fields.Many2many('res.users', string=u'用户')

    active_customer_staff = fields.Boolean('启用客户销售人员权限')
    active_customer = fields.Boolean('启用客户权限')

    customer_staff_ids = fields.Many2many('archives.staff', string=u'销售员', domain="[('is_sale_man','=',True)]")

    customer_organization_ids = fields.Many2many('archives.common_archive', string=u'客户权限',
                                                 domain="[('archive_name','=',16)]")

    def _del_and_add_organization(self, bill):
        if not bill.user_ids:
            return
        self._delete_exist_organization(bill)
        self._create_organization(bill)

    def _delete_exist_organization(self, bill):
        already_bills = self.env["archives.organization"].search([('user_id', 'in', bill.user_ids.ids)])
        for b in already_bills:
            b.unlink()

    def _create_organization(self, bill):
        for user_id in bill.user_ids.ids:
            values = self._get_organization(user_id, bill)
            self.env['archives.organization'].create(values)

    def _get_organization(self, user_id, bill):
        return {
            'name': 'new',  # 此值随意
            'user_id': user_id,
            'group_id': bill.id,
            'active_customer_staff': bill.active_customer_staff,
            'active_customer': bill.active_customer,
            'customer_staff_ids': [[6, False, bill.customer_staff_ids.ids]],
            'customer_organization_ids': [[6, False, bill.customer_organization_ids.ids]],
        }

    def _get_del_ids(self, values):
        new_user_ids = []  # values:{u'user_ids': [[6, False, [1]]]}
        if values.has_key('user_ids'):
            new_user_ids = values['user_ids'][0][2]
        exist_ids = self.user_ids.ids
        need_del_ids = []
        for id in exist_ids:
            if id not in new_user_ids:
                need_del_ids.append(id)
        return need_del_ids

    def _clear_group_id__organization_group_id(self, user_ids__need_clear_group_id):
        self.env['archives.organization'].search([('user_id', 'in', user_ids__need_clear_group_id)]).write(
            {'group_id': None, })

    @api.model
    def create(self, values):
        result = super(OrganizationGroup, self).create(values)
        self._del_and_add_organization(result)
        return result

    @api.multi
    def write(self, values):
        user_ids__need_clear_group_id = self._get_del_ids(values)
        result = super(OrganizationGroup, self).write(values)

        if user_ids__need_clear_group_id:
            self._clear_group_id__organization_group_id(user_ids__need_clear_group_id)
        bill = self.env["archives.organization_group"].browse(self.id)
        self._del_and_add_organization(bill)
        return result

    @api.multi
    def unlink(self):
        return super(OrganizationGroup, self).unlink()
