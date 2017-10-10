# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models
# from . import utils


class Users(models.Model):
    _name = 'res.users'
    _inherit = ['res.users']

    # spell = fields.Char(string=u'首拼')

    organization_id = fields.Many2one('archives.organization', string=u'权限单据ID', ondelete='cascade', copy=False)
    # active_customer_staff = fields.Boolean('启用客户销售人员权限')
    # active_customer = fields.Boolean('启用客户权限')
    #
    # organization_customer_staff = fields.One2many('res.users.organization_customer_staff', 'user_id',
    #                                               string=u'数据权限_客户销售人员权限明细', copy=True)

    # @api.model
    # def create(self, values):
    #     utils.set_spell(values)
    #     return super(Users, self).create(values)
    #
    # @api.multi
    # def write(self, values):
    #     utils.set_spell(values)
    #     return super(Users, self).write(values)
