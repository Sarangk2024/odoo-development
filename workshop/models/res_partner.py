# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResPartner(models.Model):
    '''inheriting res.partner model and adding vehicle field and vehicle count smart button'''
    _inherit = 'res.partner'

    vehicle_ids = fields.One2many('vehicle.management', 'owner_id',
                                  string='Vehicles')
    vehicle_count = fields.Integer(string='Vehicles',
                                   compute='_compute_vehicle_count', store=True)

    @api.depends('vehicle_ids')
    def _compute_vehicle_count(self):
        '''finding customer vehicle count'''
        for record in self:
            record.vehicle_count = len(record.vehicle_ids)

    def action_view_vehicles(self):
        '''To show the vehicle list view when user click the vehicle smart button'''
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicles View',
            'res_model': 'vehicle.management',
            'view_mode': 'list,form',
            'domain': [('owner_id', '=', self.id)]
        }
