# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


def get_id(bill, field):
    attr = getattr(bill, field, False)
    if attr:
        return attr.id
    return False


class Approve(models.AbstractModel):
    '''
    针对系统内的单据增加审批流程控制
    增加两个字段：_to_approver_ids 记录还有谁需要审批（用来判断审批是否结束）
                 _approver_num 整个流程涉及的审批者数量（用来判断审批是否开始）
    '''
    _name = 'jc_approve'

    @api.one
    @api.depends('_to_approver_ids', '_approver_num')
    def _get_approve_state(self):
        """计算审批状态"""
        to_approver = len(self._to_approver_ids)
        if not to_approver:
            self._approve_state = u'已审批'
        elif to_approver == self._approver_num:
            self._approve_state = u'已提交'
        else:
            self._approve_state = u'审批中'

    _to_approver_ids = fields.One2many('approve.approver', 'res_id', readonly='1',
                                       domain=lambda self: [('model', '=', self._name)], auto_join=True, string='待审批人')
    _approver_num = fields.Integer(string='总审批人数')
    _approve_state = fields.Char(u'审批状态',
                                 compute='_get_approve_state')

    """[(审批组,序号)]"""

    def __get_groups__(self, process_bill):
        """
        得到当前审批流的审批组与序号
        :param process_bill:审批流
        :return:[(审批组,序号)]
        """
        groups = []
        if process_bill:
            [groups.append((line.group_id, line.sequence)) for line in self.env['approve.process_line'].search(
                [('process_id', '=', process_bill.id)], order='sequence')]
        return groups

    """[(用户，审批组序号，审批组)]"""

    def __get_users__(self, groups):
        users = []
        for group, sequence in groups:
            [(users.append((user, sequence, group.id)))
             for user in group.users]
        return users

    def __get_user_manager__(self, thread_row, process_bill):
        '''
        如此流程需要记录创建者的部门经理审批，取得部门经理用户
        '''
        return_vals = False  # TODO:增加对部门经理的支持
        # if process_bill.is_department_approve:
        #     staff_row = self.env['staff'].search([('user_id', '=', thread_row.create_uid.id)])
        #     if staff_row and getattr(staff_row, 'parent_id', False):
        #         return_vals = staff_row.parent_id.user_id
        return return_vals

    def __add_approver__(self, thread_row, model_name):
        # TODO 加上当前用户的部门经理
        approver_bills = []
        users = []
        process_bill = self.env['approve.process'].search(
            [('model_id.model', '=', model_name), ('type_id', '=', get_id(thread_row, 'type_id'))])
        groups = self.__get_groups__(process_bill)
        department_manager = self.__get_user_manager__(thread_row, process_bill)
        if department_manager:
            users.append((department_manager, 0, False))
        users.extend(self.__get_users__(groups))
        [approver_bills.append(self.env['approve.approver'].create(
            {'user_id': user.id,
             'res_id': thread_row.id,
             'model_type': thread_row._description,
             'record_name': getattr(thread_row, 'name', ''),
             'creator': thread_row.create_uid.id,
             'sequence': sequence,
             'group_id': groud_id,
             'model': thread_row._name})) for user, sequence, groud_id in users]
        return [{'id': row.id, 'display_name': row.user_id.name} for row in approver_bills]

    def __get_approver_send_message__(self, active_id, active_model, operate):
        bill = self.env[active_model].browse(active_id)
        user = self.env['res.users'].browse(self.env.uid)
        message_text = u"%s %s %s %s" % (user.name, operate, bill._name, bill.name)
        return message_text

    def __is_departement_manager__(self, department_row):
        return_vals = department_row.id
        if department_row:
            department_row.unlink()
        return return_vals

    def __has_manager__(self, active_id, active_model):
        department_row = self.env['approve.approver'].search([('model', '=', active_model),
                                                              ('res_id', '=', active_id),
                                                              ('sequence', '=', 0), ('group_id', '=', False)])
        return department_row

    @api.model
    def process_approve(self, active_id, active_model):
        return_vals = []
        message = ''
        manger_row = self.__has_manager__(active_id, active_model)
        model_row = self.env[active_model].browse(active_id)
        if (manger_row and manger_row.user_id.id == self.env.uid) or not manger_row:
            manger_user = []
            if manger_row:
                manger_user = [manger_row.user_id.id]
                return_vals.append(self.__is_departement_manager__(manger_row))
            users, can_clean_groups = (self.__get_user_group__(active_id, active_model, manger_user, model_row))
            return_vals.extend(self.__remove_approver__(active_id, active_model, users, can_clean_groups))
            if return_vals:
                message = self.__get_approver_send_message__(active_id, active_model, u'同意')
            else:
                return_vals = u'您不是这张单据的下一个审批者'
        else:
            return_vals = u'您不是这张单据的下一个审批者'
        # model_row.do_check()
        return return_vals, message or ''

    @api.model
    def process_refuse(self, active_id, active_model):
        message = ''
        bill = self.env[active_model].browse(active_id)
        users, groups = self.__get_user_group__(active_id, active_model, [], bill)
        approver_bills = self.env['approve.approver'].search([('model', '=', active_model),
                                                              ('res_id', '=', active_id)])
        if bill._approver_num == len(bill._to_approver_ids):
            return_vals = u'您是第一批需要审批的人，无需拒绝！'
        elif approver_bills and users:
            approver_bills.unlink()
            message = self.__get_approver_send_message__(active_id, active_model, u'拒绝')
            return_vals = self.__add_approver__(bill, active_model)

        else:
            return_vals = u'已经通过不能拒绝！'
        return return_vals, message or ''

    @api.model
    def create(self, vals):
        thread_row = super(Approve, self).create(vals)
        approvers = self.__add_approver__(thread_row, self._name)
        thread_row._approver_num = len(approvers)
        return thread_row

    @api.multi
    def write(self, vals):
        '''
        如果单据的审批流程已经开始（第一个人同意了才算开始） —— 至少一个审批人已经审批通过，不允许对此单据进行修改。
        '''
        for th in self:
            ignore_fields = ['_approver_num',
                             '_to_approver_ids',
                             'message_ids',
                             'message_follower_ids',
                             'message_partner_ids',
                             'message_channel_ids',
                             'approve_uid',
                             'approve_date',
                             ]
            if any([vals.has_key(x) for x in ignore_fields]) or not th._approver_num:
                continue
            change_state = vals.get('bill_state', False)

            # 已提交，审核时报错
            if len(th._to_approver_ids) == th._approver_num and change_state:
                raise ValidationError(u"审批后才能审核")
            # 已审批
            if not len(th._to_approver_ids):
                if not change_state:
                    raise ValidationError(u'已审批不可修改')
                if change_state == 1:
                    vals.update({
                        '_approver_num': len(self.__add_approver__(th, th._name)),
                    })
            # 审批中，审核时报错，修改其他字段报错
            elif len(th._to_approver_ids) < th._approver_num:
                if change_state:
                    raise ValidationError(u"审批后才能审核")
                raise ValidationError(u"审批中不可修改")

        thread_row = super(Approve, self).write(vals)
        return thread_row

    @api.multi
    def unlink(self):
        for th in self:
            if not len(th._to_approver_ids) and th._approver_num:
                raise ValidationError(u"已审批不可删除")
            if len(th._to_approver_ids) < th._approver_num:
                raise ValidationError(u"审批中不可删除")
            for approver in th._to_approver_ids:
                approver.unlink()
        return super(Approve, self).unlink()

    def __get_user_group__(self, active_id, active_model, users, bill):
        all_groups = []
        process_bill = self.env['approve.process'].search([('model_id.model', '=', active_model),
                                                           ('type_id', '=', get_id(bill, 'type_id'))])
        line_rows = self.env['approve.process_line'].search(
            [('process_id', '=', process_bill.id)], order='sequence')
        least_num = 'default_vals'
        for line in line_rows:
            approver_s = self.env['approve.approver'].search([('model', '=', active_model),
                                                              ('group_id', '=', line.group_id.id),
                                                              ('res_id', '=', active_id)])

            if least_num == 'default_vals' and approver_s:
                least_num = line.sequence
            if least_num == line.sequence and self.env.uid in [user.id for user in line.group_id.users]:
                users = [self.env.uid]
            if not line.is_all_approve:
                all_groups.append(line.group_id)
        can_clean_groups = []
        for group in all_groups:
            all_group_user = [user.id for user in group.users]
            if len(list(set(all_group_user).difference(users))) != len(all_group_user):
                can_clean_groups.append(group.id)
        return users, can_clean_groups

    def __get_remove_approver__(self, thread_row, user_ids, can_clean_groups):
        """
        去除审批人 - if 判断当前用户是否属于当前状态的审批人 里面
                        取得 当前用户在审批人里面的记录 （或者全组一人审批即可的 情况下  这个组里面其他人）
                    else:
                        判断 是否轮到当前用户审批 否则跳出循环

                    如果是全组审批并且取得一个审批人记录 就跳出循环

        :param thread_row:
        :param user_ids: 当前状态的审批人们
        :param is_all_approve:
        :param sequence:
        :return: 审批人 对应的记录
        """
        remove_approve, return_vals = [], []
        for approver in thread_row._to_approver_ids:
            if approver.user_id.id in user_ids or approver.group_id.id in can_clean_groups:
                remove_approve.append(approver)
                return_vals.append(approver.id)
        return return_vals, remove_approve

    @api.model
    def __remove_approver__(self, active_id, active_model, user_ids, can_clean_groups):
        return_vals = False
        if active_id:
            thread_row = self.env[active_model].browse(active_id)
            return_vals, remove_approvers = self.__get_remove_approver__(thread_row, user_ids, can_clean_groups)
            if remove_approvers:
                [approver.unlink() for approver in remove_approvers]
        return return_vals


class approver(models.Model):
    '''
    单据的待审批者
    '''
    _name = 'approve.approver'
    _rec_name = 'user_id'
    _order = 'model, res_id, sequence'

    model_type = fields.Char(u'单据类型')
    record_name = fields.Char(u'编号')
    creator = fields.Many2one('res.users', u'申请人')
    model = fields.Char('模型', index=True)
    res_id = fields.Integer('ID', index=True)
    group_id = fields.Many2one('res.groups', string=u'审批组')
    user_id = fields.Many2one('res.users', string=u'用户')
    sequence = fields.Integer(string=u'顺序')

    @api.multi
    def goto(self):
        self.ensure_one()
        views = self.env['ir.ui.view'].search([('model', '=', self.model), ('type', '=', 'form')])
        if getattr(self.env[self.model].browse(self.res_id), 'is_return', False):
            for v in views:
                if '_return_' in v.xml_id:
                    vid = v.id
                    break
        else:
            vid = views[0].id

        return {
            'name': u'审批',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self.model,
            'view_id': False,
            'views': [(vid, 'form')],
            'type': 'ir.actions.act_window',
            'res_id': self.res_id,
        }

    @api.model_cr
    def init(self):
        self._cr.execute(
            """SELECT indexname FROM pg_indexes WHERE indexname = 'approve_approver_model_res_id_idx'""")
        if not self._cr.fetchone():
            self._cr.execute(
                """CREATE INDEX approve_approver_model_res_id_idx ON approve_approver (model, res_id)""")


class process(models.Model):
    '''
    可供用户自定义的审批流程，可控制是否需部门经理审批。注意此规则只对修改之后新建（或被拒绝）的单据有效
    '''
    _name = 'approve.process'
    _description = u'审批规则'
    _rec_name = 'model_id'
    model_id = fields.Many2one('ir.model', u'单据', required=True)
    # type = fields.Char(u'类型', help=u'有些单据根据type字段区分具体流程')
    type_id = fields.Many2one('archives.common_archive', string=u'类型', help=u'有些单据根据类型字段区分具体流程')
    is_department_approve = fields.Boolean(string=u'部门经理审批')
    line_ids = fields.One2many('approve.process_line', 'process_id', string=u'审批组')
    active = fields.Boolean(u'启用', default=True)

    @api.one
    @api.constrains('model_id', 'type_id')
    def check_model_id(self):
        records = self.search([
            ('model_id', '=', self.model_id.id),
            ('type_id', '=', self.type_id.id),
            ('id', '!=', self.id)])
        if records:
            raise ValidationError(u'同种单据的审批规则必须唯一')

    @api.model
    def create(self, vals):
        """
        新建审批配置规则，如果配置的模型有type字段而规则未输入type，保存时给出提示
        """
        process_id = super(process, self).create(vals)
        model = self.env[process_id.model_id.model]
        if hasattr(model, 'type_id') and not process_id.type_id:
            raise ValidationError(u'请输入类型')
        return process_id


class process_line(models.Model):
    '''
    可控制由哪些审批组审批，各自的审批顺序是什么，组内用户都需要审还是一位代表审批即可
    '''
    _name = 'approve.process_line'
    _description = u'审批规则行'
    _order = 'sequence'

    sequence = fields.Integer(string='序号')
    group_id = fields.Many2one('res.groups', string=u'审批组', required=True)
    is_all_approve = fields.Boolean(string=u'是否需要本组用户全部审批')
    process_id = fields.Many2one('approve.process', u'审批规则')
