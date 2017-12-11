# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from . import base_infor


class OrganizationGroup(base_infor.BaseInfoUnique):
    _name = 'archives.organization_group'
    _description = u'档案：数据权限组'

    user_ids = fields.Many2many('res.users', string=u'用户')

    # 客户权限的设置

    active_customer_staff = fields.Boolean('启用客户销售人员权限')
    active_customer = fields.Boolean('启用客户权限')

    customer_staff_ids = fields.Many2many('archives.staff', string=u'销售员', domain="[('is_sale_man','=',True)]")

    customer_organization_ids = fields.Many2many('archives.common_archive', 'archives_organization_group_customer_rel',
                                                 string=u'客户权限', domain="[('archive_name','=',16)]")

    # 存货权限的设置

    active_goods_goods_type = fields.Boolean('启用存货存货类型权限')
    active_goods = fields.Boolean('启用存货权限')

    goods_goods_type_ids = fields.Many2many('archives.common_archive', 'archives_organization_group_goods_type_rel',
                                            string=u'物料分类', domain="[('archive_name','=',9)]")

    goods_organization_ids = fields.Many2many('archives.common_archive', 'archives_organization_group_goods_rel',
                                              string=u'存货权限', domain="[('archive_name','=',17)]")

    # 公司权限的设置

    active_company = fields.Boolean('启用公司权限')
    company_ids = fields.Many2many('res.company', string=u'公司')

    # 仓库权限的设置

    active_store = fields.Boolean('启用仓库权限')
    store_ids = fields.Many2many('archives.store', string=u'仓库')

    # 部门权限的设置

    active_department = fields.Boolean('启用部门权限')
    department_ids = fields.Many2many('archives.department', string=u'部门')

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
            # 客户权限的设置：
            'active_customer_staff': bill.active_customer_staff,
            'active_customer': bill.active_customer,
            'customer_staff_ids': [[6, False, bill.customer_staff_ids.ids]],
            'customer_organization_ids': [[6, False, bill.customer_organization_ids.ids]],
            # 存货权限的设置：
            'active_goods_goods_type': bill.active_goods_goods_type,
            'active_goods': bill.active_goods,
            'goods_goods_type_ids': [[6, False, bill.goods_goods_type_ids.ids]],
            'goods_organization_ids': [[6, False, bill.goods_organization_ids.ids]],
            # 公司权限的设置
            'active_company': bill.active_company,
            'company_ids': [[6, False, bill.company_ids.ids]],
            # 仓库权限的设置
            'active_store': bill.active_store,
            'store_ids': [[6, False, bill.store_ids.ids]],
            # 部门权限的设置
            'active_department': bill.active_department,
            'department_ids': [[6, False, bill.department_ids.ids]],
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
