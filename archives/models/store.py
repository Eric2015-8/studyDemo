# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import utils
from odoo.exceptions import ValidationError


class Store(models.Model):
    _name = 'archives.store'
    _description = u'档案：仓库'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名仓库"),
    ]

    name = fields.Char(string=u'名称', required=True)
    short_name = fields.Char(string=u'简称', help=u'用于报表显示')
    spell = fields.Char(string=u'首拼')

    company_id = fields.Many2one('res.company', string=u'公司', index=True)
    address = fields.Char(string=u'仓库地址')

    active_batch = fields.Boolean('启用批次')

    active_goods_position = fields.Boolean('启用货位')
    default_goods_position_id = fields.Many2one('archives.goods_position', string=u'默认货位')
    goods_position_ids = fields.Many2many('archives.goods_position', string=u'货位')

    @api.model
    def create(self, values):
        utils.set_spell(values)
        self._check_goods_position(values)
        return super(Store, self).create(values)

    @api.multi
    def write(self, values):
        utils.set_spell(values)
        self._check_goods_position(values)
        return super(Store, self).write(values)

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
        return super(Store, self).copy(default)

    def _check_goods_position(self, values):
        if (not values.has_key('active_goods_position')) and not self.active_goods_position:  # 未启用货位，并且没有修改该值
            return
        if values.has_key('active_goods_position') and not values['active_goods_position']:  # 修改启用货位值，并且改为不启用
            return
        default_goods_position_id = 0
        if self.default_goods_position_id:
            default_goods_position_id = self.default_goods_position_id.id
        if values.has_key('default_goods_position_id'):
            default_goods_position_id = values['default_goods_position_id']
        if not default_goods_position_id:
            raise ValidationError('请选择默认货位')
        if values.has_key('goods_position_ids'):  # 修改了货位，以修改后的货位为准
            position_ids = values['goods_position_ids'][0][2]  # 格式：goods_position_ids:[[6, False, [3, 2]]];
            if default_goods_position_id not in position_ids:
                raise ValidationError('{默认货位}必须在{货位}中')
        else:
            if default_goods_position_id not in self.goods_position_ids.ids:
                raise ValidationError('{默认货位}必须在{货位}中')
        return

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('spell', operator, name), ('name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
