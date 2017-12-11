# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import base_infor


class Store(base_infor.BaseInfoUnique):
    _name = 'archives.store'
    _description = u'档案：仓库'

    short_name = fields.Char(string=u'简称', help=u'用于报表显示')

    company_id = fields.Many2one('res.company', string=u'公司', index=True)
    address = fields.Char(string=u'仓库地址')

    active_batch = fields.Boolean('启用批次')

    active_goods_position = fields.Boolean('启用货位')
    goods_position_id_default = fields.Many2one('archives.goods_position', string=u'默认货位')  # TODO: 重命名
    goods_position_detail = fields.One2many('archives.store.goods_position.detail', 'store_id', string=u'仓库_货位明细',
                                            copy=True)

    @api.model
    def create(self, values):
        result = super(Store, self).create(values)
        self._check_goods_position()
        return result

    @api.multi
    def write(self, values):
        result = super(Store, self).write(values)
        self._check_goods_position()
        return result

    def _check_goods_position(self):
        if not self.active_goods_position:
            if self.goods_position_id_default:
                self.d = None
            return
        if not self.goods_position_id_default:
            return
        if self.goods_position_id_default not in self.goods_position_detail.mapped('goods_position_id'):
            raise ValidationError('{默认货位}必须在{货位}中')
        return
