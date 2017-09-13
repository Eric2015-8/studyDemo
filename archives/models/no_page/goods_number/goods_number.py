# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import tools
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError


class GoodsNumber(models.Model):
    _name = 'archives.goods_number'
    _description = u'添加存货'
    _auto = False

    name = fields.Char(string=u'物料名称', required=True)
    short_name = fields.Char(string=u'简称')

    # 通用信息
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位')
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位')
    statistics_unit_id = fields.Many2one('archives.unit', string=u'统计单位')

    second_rate = fields.Float(digits=(6, 2), string=u'辅单位转换率', help=u"主单位与辅单位的换算率，如“10”，一件（辅单位）=10公斤（主单位）")
    statistics_rate = fields.Float(digits=(6, 2), string=u'统计单位转换率', help=u"主单位与统计单位的换算率，如“10”，一件（统计单位）=10公斤（主单位）")

    need_second_change = fields.Selection([
        ('1', '是'),
        ('0', '否')
    ], string=u'辅单位是否换算', default='1')

    main_unit_number = fields.Float(digits=(6, 2), string=u'主数量', compute='_compute_main_number')
    second_unit_number = fields.Float(digits=(6, 2), string=u'辅数量', compute='_compute_second_number')
    main_unit_number_string = fields.Char(string=u'主数量')
    second_unit_number_string = fields.Char(string=u'辅数量')

    @api.multi
    def write(self, values):
        # employee_id = values.get('employee_id', False)
        detail = self.env.context.get('detail')
        if not detail:
            raise ValidationError(_('请传递detail参数：detail的“_name”值.'))
        values['billid'] = self.env.context.get('id')
        self.env[detail].create(values)

    @api.onchange('second_unit_number')
    def _onchange_second(self):
        if not self.need_second_change:
            return
        self.main_unit_number = self.second_rate * self.second_unit_number

    @api.onchange('main_unit_number')
    def _onchange_main(self):
        if not self.need_second_change:
            return
        if self.second_rate != 0:
            self.second_unit_number = self.main_unit_number / self.second_rate

    @api.depends('main_unit_number_string')
    def _compute_main_number(self):
        for record in self:
            if not record.main_unit_number_string:
                record.main_unit_number = 0
                continue
            record.main_unit_number = float(record.main_unit_number_string)

    @api.depends('second_unit_number_string')
    def _compute_second_number(self):
        for record in self:
            if not record.second_unit_number_string:
                record.second_unit_number = 0
                continue
            record.second_unit_number = float(record.second_unit_number_string)

    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, 'archives_goods_number')
        cr.execute(
            """
            create or replace view archives_goods_number as (
select
id,
name,
short_name,
main_unit_id,
second_unit_id,
cast(second_rate_string as decimal(6,2)) as second_rate,
need_second_change,
'' as main_unit_number_string,
'' as second_unit_number_string
FROM archives_goods
            )
        """)
