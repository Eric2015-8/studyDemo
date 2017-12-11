# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.utils import spell


class BaseInfo(models.Model):
    _name = 'base_info'
    _description = u'档案基类'

    name = fields.Char(string=u'名称', required=True)
    spell = fields.Char(string=u'首拼')

    @api.model
    def create(self, values):
        spell.set_spell(values)
        result = super(BaseInfo, self).create(values)
        return result

    @api.multi
    def write(self, values):
        spell.set_spell(values)
        result = super(BaseInfo, self).write(values)
        return result

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
        return super(BaseInfo, self).copy(default)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('spell', operator, name), ('name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()


class BaseInfoUnique(BaseInfo):
    _name = 'base_info_unique'
    _description = u'档案基类:无重名'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         u"已存在同名档案"),
    ]
