# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    '''inheriting res.partner model and adding vehicle field and vehicle count smart button'''
    _inherit = 'res.partner'

    vehicle_ids = fields.One2many('vehicle.management', 'owner_id',
                                  string='Vehicles')
    vehicle_count = fields.Integer(string='Vehicles',
                                   compute='_compute_vehicle_count')

    appointment_ids = fields.One2many('calendar.event', 'customer_id',
                                      string="Appointment")
    appointment_count = fields.Integer(string='Appointment',
                                       compute='_compute_appointment_count')
    work_orders_ids = fields.One2many('workshop.job.order', 'customer_id')
    work_order_count = fields.Integer(string="Work Order",
                                      compute='_compute_work_order_count')

    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company
    )

    def _compute_vehicle_count(self):
        '''finding customer's vehicle count'''
        for record in self:
            record.vehicle_count = len(record.vehicle_ids)
        print(self.vehicle_count)

    def action_view_vehicles(self):
        '''To show the vehicle list view when user click the vehicle smart button'''
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicles View',
            'res_model': 'vehicle.management',
            'view_mode': 'list',
            'domain': [('owner_id', '=', self.id)]
        }

    def _compute_appointment_count(self):
        '''finding customer's appointment count'''
        for record in self:
            record.appointment_count = len(record.appointment_ids)

    def action_view_appointments(self):
        '''To show the Appointments list view when user click the Appointment smart button'''
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointment View',
            'res_model': 'calendar.event',
            'view_mode': 'list,form',
            'domain': [('customer_id', '=', self.id)]
        }

    def _compute_work_order_count(self):
        '''finding customer's work order's count'''
        for record in self:
            record.work_order_count = len(record.work_orders_ids)

    def action_view_work_orders(self):
        '''To show the work order list view when user click the work order smart button'''
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Work Order View',
            'res_model': 'workshop.job.order',
            'view_mode': 'list,form',
            'domain': [('customer_id', '=', self.id)]
        }
