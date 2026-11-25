from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomPortal(CustomerPortal):
    '''Adding workshop job order card in customer portal '''

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        workorders = request.env['workshop.job.order'].sudo().search([
            ('customer_id', '=', request.env.user.partner_id.id)
        ])
        values['workorder'] = workorders
        return values

    @http.route(["/my/workshop/<int:sequence>"], type='http', auth='public', methods=['GET'], website=True)
    def workshop_details(self, **kwargs):
        work_orders = request.env['workshop.job.order'].sudo().search([])
        return request.render('workshop.workshop_details_page',
                              {'workorders': work_orders})
