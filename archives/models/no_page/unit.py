# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Unit(models.Model):
    _name = 'archives.unit'
    _description = u'无菜单档案：单位'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名单位"),
    ]

    name = fields.Char(string=u'单位', required=True)

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
        return super(Unit, self).copy(default)
