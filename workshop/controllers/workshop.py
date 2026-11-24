# from odoo import http
# from odoo.http import request
#
# class Workshop(http.Controller):
#     '''controller for workshop details'''
#
#     @http.route('/workshop', type='http', auth='public',methods=["GET"] ,website=True)
#     def workshop_details(self , **kwargs):
#         workshop_details = request.env['workshop.job.order'].sudo().search([])
#
#         return  request.render('workshop.workshop_details_page', {'my_details': workshop_details})
#


from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        values['workshop_job_order'] = request.env[
            'workshop.job.order'].sudo().search_count([])
        print(values)
        return values
