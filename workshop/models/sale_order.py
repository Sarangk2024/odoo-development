# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    '''inherit sale order model and adding two filed related to our workshop'''
    _inherit = "sale.order"

    job_order_id = fields.Many2one('workshop.job.order', string="Job Order")
    vehicle_id = fields.Many2one('vehicle.management', string="Vehicle")

    @api.onchange('job_order_id')
    def onchange_job_order_id(self):
        '''finding vehicle for the job order'''
        self.vehicle_id = self.job_order_id.vehicle_id

    def _create_invoices(self, final=False, grouped=False):
        '''creating invoice for the sale order'''
        invoices = super()._create_invoices(final=final, grouped=grouped)
        sale_order_invoices = invoices.filtered(
            lambda invoice: self in
                            invoice.invoice_line_ids.sale_line_ids.order_id
        )
        sale_order_invoices.write({
            'job_order_id': self.job_order_id.id,
        })
        return invoices
