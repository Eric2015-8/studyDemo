# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import base_infor

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
    (17, '存货权限'),
    (18, '入库类型'),
    (19, '价格分类'),
    (20, '调出类型'),
    (21, '调入类型'),
    (23, '科目'),
    (24, '收款类型'),
    (25, '付款类型'),
    (26, '记账类型'),
    (27, '销售发票'),
    (28, '转款类型'),
    (29, '转账类型'),
]


# customer_organization_ids = fields.Many2many('archives.common_archive', 'archives_organization_customer_rel',
#                                              string=u'客户权限', domain=[('archive_name','=',16)])

# organization_id = fields.Many2one('archives.common_archive', string=u'客户权限', domain=[('archive_name','=',16)])


class CommonArchive(base_infor.BaseInfo):
    _name = 'archives.common_archive'
    _description = u'档案：通用档案'

    archive_name = fields.Selection(ARCHIVE_NAME, string=u'档案名称', require=True, default=1)

    @api.constrains('name')
    def _check_name(self):
        all_data = self.env['archives.common_archive'].search(
            [('archive_name', '=', self.archive_name), ('name', '=', self.name), ('id', '!=', self.id)])
        if not all_data:
            return
        raise ValidationError('名称已存在')
