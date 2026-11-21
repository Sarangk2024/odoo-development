# -*- coding: utf-8 -*-

from odoo import fields, models, api


class VehicleManagement(models.Model):
    '''Describe the vehicle management'''
    _name = 'vehicle.management'
    _description = 'Vehicle Management'
    _rec_name = 'license_plate'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _license_plate_unique = models.Constraint(
        'unique(license_plate)', 'License Plate should be unique'
    )
    _vin_unique = models.Constraint(
        'unique(vin)', 'Vehicle Identification Number should be unique'
    )

    active = fields.Boolean(default=True)
    license_plate = fields.Char(string='License Plate', required=True,
                                tracking=True, copy=False)
    vin = fields.Char(string='VIN', required=True,
                      help='Vehicle Identification Number', tracking=True)
    make = fields.Char(string='Make', help='Manufacture of the vehicle')
    model = fields.Char(string='Model')
    year = fields.Char(string='Year', help='Year of manufacture of the vehicle')
    colour = fields.Char(string='Colour')
    odometer = fields.Integer(string='Odometer', help='Total Km')
    owner_id = fields.Many2one('res.partner', string='Owner', required=True,
                               tracking=True)
    job_order_ids = fields.One2many('workshop.job.order', 'vehicle_id',
                                    string='Vehicle', required=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company
    )
    history_count = fields.Integer(string='History Count', compute='_compute_history_count')
    appointment_count = fields.Integer(string='Appointment Count',compute='_compute_appointment_count')
    appointment_ids = fields.One2many('calendar.event','vehicle_id',string="Appointment")


    def action_view_vehicle_history(self):
        '''To show the Appointments list view when user click the Appointment smart button'''
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'History',
            'res_model': 'workshop.job.order',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', 'in', self.id)]
        }

    @api.depends('history_count')
    def _compute_history_count(self):
        '''finding customer's appointment count'''
        for record in self:
            record.history_count = len(record.job_order_ids)

    @api.depends('appointment_count')
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
            'domain': [('vehicle_id', '=', self.id)]
        }
