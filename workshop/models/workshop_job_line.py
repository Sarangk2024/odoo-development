# -*- coding: utf-8 -*-

from odoo import fields, models, api


class WorkshopJobLine(models.Model):
    '''workshop job lines to manage workshop'''
    _name = 'workshop.job.line'
    _description = 'Workshop Job Line'

    _quantity_min = models.Constraint(
        'CHECK(self.quantity >= 1)', 'Quantity Should not be less than 1'
    )

    product_id = fields.Many2one('product.product', string='Product Name',
                                 required=True)
    quantity = fields.Integer(string='Quantity', required=True, default=1)
    product_unit_price = fields.Float(string='Unit Price', required=True)
    line_subtotal = fields.Float(string='Subtotal')
    job_order_line_id = fields.Many2one('workshop.job.order',
                                        string='Job Order')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        '''Finding product unit price while updating product and line total'''
        self.product_unit_price = self.product_id.list_price
        self.line_subtotal = self.quantity * self.product_id.list_price

    @api.onchange('product_unit_price', 'quantity')
    def _onchange_product_unit_price_quantity(self):
        '''Finding line subtotal from quantity and  unit price while updating product quantity or unit price and checking the quantity'''
        self.quantity = max(self.quantity, 1)
        self.line_subtotal = self.quantity * self.product_unit_price
