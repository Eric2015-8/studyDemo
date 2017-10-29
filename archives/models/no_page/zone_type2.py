# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ZoneType2(models.Model):
    _name = 'archives.zone_type2'
    _description = u'无菜单档案：地区分类2'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名地区分类2"),
    ]

    name = fields.Char(string=u'地区分类2', required=True)

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(ZoneType2, self).copy(default)
