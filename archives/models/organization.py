# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from . import utils


class Organization(models.Model):
    _name = 'archives.organization'
    _description = u'档案：数据权限'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(user_id)',
         "已为该用户授权"),
    ]

    name = fields.Char(string=u'数据权限名称', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('新建'))  # 使用用户名
    spell = fields.Char(string=u'首拼')

    user_id = fields.Many2one('res.users', string=u'用户', required=True, ondelete='cascade')

    group_id = fields.Many2one('archives.organization_group', string=u'数据权限组', ondelete='cascade')

    # 客户权限的设置

    active_customer_staff = fields.Boolean('启用客户销售人员权限')
    active_customer = fields.Boolean('启用客户权限')

    customer_staff_ids = fields.Many2many('archives.staff', string=u'销售员', domain="[('is_sale_man','=',True)]")

    customer_organization_ids = fields.Many2many('archives.common_archive', 'archives_organization_customer_rel',
                                                 string=u'客户权限', domain="[('archive_name','=',16)]")

    # 存货权限的设置

    active_goods_goods_type = fields.Boolean('启用存货存货类型权限')
    active_goods = fields.Boolean('启用存货权限')

    goods_goods_type_ids = fields.Many2many('archives.common_archive', 'archives_organization_goods_type_rel',
                                            string=u'物料分类', domain="[('archive_name','=',9)]")

    goods_organization_ids = fields.Many2many('archives.common_archive', 'archives_organization_goods_rel',
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

    def _set_user_organization(self, bill):
        self.env['res.users'].search([('id', '=', bill.user_id.id)]).write({'organization_id': bill.id, })

    def _clear_user_organization(self):
        self.env['res.users'].search([('id', '=', self.user_id.id)]).write({'organization_id': None, })

    def _set_name(self, values):
        values['name'] = self.env['res.users'].browse(values['user_id']).name

    # 得到受权限控制的：客户
    def get_customer_organization(self):
        user = self.env.user
        result = []
        if not user.organization_id:
            return result
        if user.organization_id.active_customer_staff:
            ids = []
            for detail in user.organization_id.customer_staff_ids:
                ids.append(detail.id)
            result.append(('staff_id', 'in', ids))
        if user.organization_id.active_customer:
            ids = []
            for detail in user.organization_id.customer_organization_ids:
                ids.append(detail.id)
            result.append(('organization_id', 'in', ids))
        return result

    # 得到受权限控制的：存货
    def get_goods_organization(self):
        user = self.env.user
        result = []
        if not user.organization_id:
            return result
        if user.organization_id.active_goods_goods_type:
            ids = []
            for detail in user.organization_id.goods_goods_type_ids:
                ids.append(detail.id)
            result.append(('goods_type_id', 'in', ids))
        if user.organization_id.active_goods:
            ids = []
            for detail in user.organization_id.goods_organization_ids:
                ids.append(detail.id)
            result.append(('organization_id', 'in', ids))
        return result

    # 得到受权限控制的：公司
    def get_company_organization(self):
        user = self.env.user
        result = []
        if not user.organization_id:
            return result
        if user.organization_id.active_company:
            ids = []
            for detail in user.organization_id.company_ids:
                ids.append(detail.id)
            result.append(('id', 'in', ids))
        return result

    # 得到受权限控制的：仓库
    def get_store_organization(self):
        user = self.env.user
        result = []
        if not user.organization_id:
            return result
        if user.organization_id.active_store:
            ids = []
            for detail in user.organization_id.store_ids:
                ids.append(detail.id)
            result.append(('id', 'in', ids))
        return result

    def get_store_organization_condition(self, store_field):
        user = self.env.user
        if not user.organization_id:
            return ''
        if user.organization_id.active_store:
            ids = []
            for detail in user.organization_id.store_ids:
                ids.append(str(detail.id))
            if len(ids) == 0:
                return store_field + ' = 0'
            return '{} in ({})'.format(store_field, ','.join(ids))
        return ''

    # 得到受权限控制的：部门
    def get_department_organization(self):
        user = self.env.user
        result = []
        if not user.organization_id:
            return result
        if user.organization_id.active_department:
            ids = []
            for detail in user.organization_id.department_ids:
                ids.append(detail.id)
            result.append(('id', 'in', ids))
        return result

    @api.multi
    def load_group(self):
        if not self.group_id:
            return
        group = self.env['archives.organization_group'].search([('id', '=', self.group_id.id)])
        values = self._get_organization(group)
        super(Organization, self).write(values)

    def _get_organization(self, bill):
        return {
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
            'company_ids': [[6, False, bill.goods_goods_type_ids.ids]],
            # 仓库权限的设置
            'active_store': bill.active_store,
            'store_ids': [[6, False, bill.goods_goods_type_ids.ids]],
            # 部门权限的设置
            'active_department': bill.active_department,
            'department_ids': [[6, False, bill.goods_goods_type_ids.ids]],
        }

    @api.model
    def create(self, values):
        self._set_name(values)  # 不要与下一行颠倒
        utils.set_spell(values)  # 不要与上一行颠倒
        result = super(Organization, self).create(values)
        self._set_user_organization(result)
        return result

    @api.multi
    def unlink(self):
        self._clear_user_organization()
        return super(Organization, self).unlink()

    @api.multi
    def write(self, values):
        utils.set_spell(values)
        return super(Organization, self).write(values)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('spell', operator, name), ('name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
