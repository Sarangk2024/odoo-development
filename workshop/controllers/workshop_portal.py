# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class WorkshopPortal(CustomerPortal):
    '''Adding workshop job order card in customer portal '''

    @http.route(["/my/workshop"], type='http', auth='user', methods=['GET'],
                website=True)
    def workshop_details(self, page=1, filterby=None, groupby='none',
                         sortby='date', **kwargs):
        '''For showing the work order details in the customer portal list view '''

        if request.env.user.has_group(
                "workshop.group_workshop_manager"):
            work_orders = request.env['workshop.job.order'].sudo().search([])
        else:
            work_orders = request.env['workshop.job.order'].sudo().search(
                [('customer_id', '=', request.env.user.partner_id.id)])

        return request.render('workshop.workshop_details_page',
                              {
                                  'workorders': work_orders,
                                  'page_name': 'Workshop',
                              })