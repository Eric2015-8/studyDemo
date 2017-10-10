# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from . import utils


class Department(models.Model):
    _name = 'archives.department'
    _description = u'档案：部门'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名部门"),
    ]

    name = fields.Char(string=u'名称', required=True)
    spell = fields.Char(string=u'首拼')

    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string=u'公司',
                                 index=True)  # ,default=lambda self:self.evn.user.company_id
    parent_id = fields.Many2one('archives.department', string=u'上级部门', index=True,
                                domain="[('company_id', '=', company_id), ('id', '!=', id)]")

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_(u'错误!与上级部门互为上下级，发生循环.'))

    @api.model
    def create(self, values):
        utils.set_spell(values)
        return super(Department, self).create(values)

    @api.multi
    def write(self, values):
        utils.set_spell(values)
        return super(Department, self).write(values)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('spell', operator, name), ('name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
