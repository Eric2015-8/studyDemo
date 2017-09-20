# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CommonArchive(models.Model):
    _name = 'archives.common_archive'
    _description = u'档案：通用档案'

    name = fields.Char(string=u'名称', required=True)

    archive_name = fields.Selection(
        [(1, '销售类型')],
        string=u'档案名称', require=True, default=1
    )

    @api.constrains('name')
    def _check_name(self):
        all_data = self.env['archives.common_archive'].search(
            [('archive_name', '=', self.archive_name), ('name', '=', self.name), ('id', '!=', self.id)])
        if not all_data:
            return
        raise ValidationError('名称已存在')
