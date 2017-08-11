# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

class Department(models.Model):
    _name = 'archives.department'
    _sql_constraints = [
       ('name_unique',
        'UNIQUE(name)',
        "已存在同名部门"),
   ]

    name = fields.Char(string=u'部门名称',required=True)
    active=fields.Boolean('Active',default=True)
    company_id=fields.Many2one('archives.company',string=u'公司',index=True)#,default=lambda self:self.evn.user.company_id
    parent_id=fields.Many2one('archives.department',string=u'上级部门',index=True)
    #child_ids=fields.One2many('archive.department',string=u'子部门')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_(u'错误!与上级部门互为上下级，发生循环.'))
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100