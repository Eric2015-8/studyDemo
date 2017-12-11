# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from . import base_infor


class Department(base_infor.BaseInfoUnique):
    _name = 'archives.department'
    _description = u'档案：部门'

    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string=u'公司',
                                 index=True)  # ,default=lambda self:self.evn.user.company_id
    parent_id = fields.Many2one('archives.department', string=u'上级部门', index=True,
                                domain="[('company_id', '=', company_id), ('id', '!=', id)]")

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_(u'错误!与上级部门互为上下级，发生循环.'))
