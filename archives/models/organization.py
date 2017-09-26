# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Organization(models.Model):
    _name = 'archives.organization'
    _description = u'档案：数据权限'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(user_id)',
         "已为该用户授权"),
    ]

    name = fields.Char(string=u'预报编号', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('新建'))

    user_id = fields.Many2one('res.users', string=u'用户', required=True, ondelete='cascade')

    active_customer_staff = fields.Boolean('启用客户销售人员权限')
    active_customer = fields.Boolean('启用客户权限')

    customer_staff_ids = fields.Many2many('archives.staff', string=u'销售员', domain="[('is_sale_man','=',True)]")

    customer_organization_ids = fields.Many2many('archives.common_archive', string=u'客户权限', domain="[('archive_name','=',16)]")

    def _set_user_organization(self, bill):
        self.env['res.users'].search([('id', '=', bill.user_id.id)]).write({'organization_id': bill.id, })

    def _clear_user_organization(self):
        self.env['res.users'].search([('id', '=', self.user_id.id)]).write({'organization_id': None, })

    def _set_name(self, values):
        values['name'] = self.env['res.users'].browse(values['user_id']).name

    @api.model
    def create(self, values):
        self._set_name(values)
        result = super(Organization, self).create(values)
        self._set_user_organization(result)
        return result

    @api.multi
    def unlink(self):
        self._clear_user_organization()
        return super(Organization, self).unlink()
