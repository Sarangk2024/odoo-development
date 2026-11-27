# -*- coding: utf-8 -*-
import base64

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, \
    pager as portal_pager


class WorkshopPortal(CustomerPortal):
    '''Adding workshop job order card in customer portal '''

    @http.route(['/my/workshop', '/my/workshop/page/<int:page>'], type='http',
                auth='user', methods=['GET'],
                website=True)
    def workshop_details(self, page=1,sortby='id', **kwargs):
        '''For showing the work order details in the customer portal list view controller'''

        if request.env.user.has_group(
                "workshop.group_workshop_manager"):
            work_order_count = request.env[
                'workshop.job.order'].sudo().search_count([])
        else:
            work_order_count = request.env[
                'workshop.job.order'].sudo().search_count(
                [('customer_id', '=', request.env.user.partner_id.id)])

        pager = portal_pager(
            url="/my/workshop",
            page=page,
            step=5,
            total=work_order_count,
            url_args={'sortby': sortby},
        )

        searchbar_sortings = {
            'id': {'label': 'ID', 'order': 'id'},
            'job_date': {'label': 'Date', 'order': 'job_date'},

            'state': {'label': 'Status', 'order': 'state'},
        }
        sort_order = searchbar_sortings[sortby]['order']


        if request.env.user.has_group(
                "workshop.group_workshop_manager"):
            work_orders = request.env['workshop.job.order'].sudo().search([],limit=5,offset=pager['offset'],order=sort_order)
        else:
            work_orders = request.env['workshop.job.order'].sudo().search(
                [('customer_id', '=', request.env.user.partner_id.id)],limit=2,offset=pager['offset'],order=sort_order)

        return request.render('workshop.workshop_details_page',
                              {
                                  'workorders': work_orders,
                                  'page_name': 'Workshop',
                                  'pager': pager,
                                  'sortby': sortby,
                                  'searchbar_sortings': searchbar_sortings,
                              })

    @http.route(["/my/workshop/<int:id>"], type="http", auth="user",
                methods=['GET'], website=True)
    def pworkshop_order_page(self, id, **kw):
        '''detailed work order detailes pagecontroller '''
        work_details = request.env['workshop.job.order'].sudo().browse(id)
        binary_img= self.convert_to_binary(work_details)
        lines = work_details.job_order_line_ids

        return request.render('workshop.workshop_work_order_details_page',
                              {
                                  'workdetails': work_details,
                                  'page_name': 'Workshop_details',
                                  'lines': lines,
                                  'binary_img': binary_img,
                              })

    def convert_to_binary(self):
        for attachment in self.attachment_ids:
            return  base64.b64decode(attachment)
