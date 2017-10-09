# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import utils

ARCHIVE_NAME = [
    (1, '销售类型'),
    (2, '客户分类'),
    (3, '客户分类1'),
    (4, '客户分类2'),
    (5, '客户分类3'),
    (6, '客户分类4'),
    (7, '客户分类5'),
    (8, '客户分类6'),
    (9, '物料分类'),
    (10, '物料分类1'),
    (11, '物料分类2'),
    (12, '物料分类3'),
    (13, '物料分类4'),
    (14, '物料分类5'),
    (15, '物料分类6'),
    (16, '客户权限'),
]


class CommonArchive(models.Model):
    _name = 'archives.common_archive'
    _description = u'档案：通用档案'

    name = fields.Char(string=u'名称', required=True, copy=False)
    spell = fields.Char(string=u'首拼')

    archive_name = fields.Selection(ARCHIVE_NAME, string=u'档案名称', require=True, default=1)

    @api.constrains('name')
    def _check_name(self):
        all_data = self.env['archives.common_archive'].search(
            [('archive_name', '=', self.archive_name), ('name', '=', self.name), ('id', '!=', self.id)])
        if not all_data:
            return
        raise ValidationError('名称已存在')

    @api.model
    def create(self, values):
        utils.set_spell(values)
        return super(CommonArchive, self).create(values)

    @api.multi
    def write(self, values):
        utils.set_spell(values)
        return super(CommonArchive, self).write(values)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('spell', operator, name), ('name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
