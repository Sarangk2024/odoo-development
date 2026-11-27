# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class WorkshopPortal(CustomerPortal):
    '''Adding workshop job order card in customer portal '''
    @http.route(["/my/workshop"], type='http', auth='user', methods=['GET'],
                website=True)
    def workshop_details(self, **kwargs):
        '''For showing the work order details in the customer portal list view controller'''
        if request.env.user.has_group(
                "workshop.group_workshop_manager"):
            work_orders = request.env['workshop.job.order'].sudo().search([])
        else:
            work_orders = request.env['workshop.job.order'].sudo().search(
                [('customer_id', '=', request.env.user.partner_id.id)])
        return request.render('workshop.workshop_details_page',
                              {
                                  'workorders': work_orders,
                                  'page_name': 'Workshop'
                              })

    @http.route(["/my/workshop/<int:id>"], type="http", auth="user",
                methods=['GET'],website=True)
    def pworkshop_order_page(self, id, **kw):
        '''detailed work order detailes pagecontroller '''
        work_details =request.env['workshop.job.order'].sudo().browse(id)
        lines = work_details.job_order_line_ids

        return request.render('workshop.workshop_work_order_details_page',
                              {
                                  'workdetails': work_details,
                                  'page_name': 'Workshop_details',
                                  'lines': lines
                              })

