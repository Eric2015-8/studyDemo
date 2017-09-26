# -*- coding: utf-8 -*-

@staticmethod
def get_customer_organization(user):
    result = []
    if not user.organization_id:
        return result
    if user.organization_id.active_customer_staff:
        ids = []
        for detail in user.organization_id.customer_staff_ids:
            ids.append(detail.id)
        result.append(('staff_id', 'in', ids))
    if user.organization_id.active_customer:
        ids = []
        for detail in user.organization_id.customer_organization_ids:
            ids.append(detail.id)
        result.append(('organization_id', 'in', ids))
    return result
