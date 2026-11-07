# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import UserError


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
    license_plate = fields.Char(string='License Plate', required=True ,tracking=True)
    vin = fields.Char(string='VIN', required=True, help='Vehicle Identification Number',tracking=True)
    make =fields.Char(string='Make',help='Manufacture of the vehicle')
    model =fields.Char(string='Model')
    year = fields.Char(string='Year' ,help='Year of manufacture of the vehicle')
    colour = fields.Char(string='Colour')
    odometer = fields.Integer(string='Odometer' ,help='Total Km')
    owner_id = fields.Many2one('res.partner',string='Owner', required=True,tracking=True)
    job_order_ids = fields.One2many('workshop.job.order', 'vehicle_id',string='Vehicle', required=True)

    # def unlink(self):
    #     for record in self:
    #         if record.job_order_ids.vehicle_id:
    #             raise UserError("Cannot Delete Record it already have some job orders, Instead Archive Record")
    #     return super().unlink()
