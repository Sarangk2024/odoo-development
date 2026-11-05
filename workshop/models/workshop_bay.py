# -*- coding: utf-8 -*-

from odoo import models,fields, api

class WorkshopBay(models.Model):
    _name = 'workshop.bay'
    _description = 'Workshop management'
    _rec_name = 'bay_type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bay_name = fields.Char(string='Bay Name' ,help='Give me the name of the bay like Washing Bay, Wheel Alignment',required=True,tracking=True)

    Assigned_employee_id = fields.Many2one('res.partner' ,string='Assigned Employee',tracking=True)

    bay_type = fields.Selection([
        ('general', 'General'),
        ('express', 'Express'),
        ('alignment', 'Alignment'),
        ('wash', 'Wash'),
        ('painting', 'Painting'),
    ],string='Bay Type', required=True, default='general')

    bay_status = fields.Selection([
        ('free', 'Free'),
        ('occupied', 'Occupied'),
        ('closed', 'Closed'),
    ],string='Bay Status', required=True, default='free',tracking=True)

    active = fields.Boolean(default=True)

    ongoing_job_id = fields.Many2one('workshop.job.order' ,string='Job')

    job_type_id = fields.Many2many('job.type',string='Job Type')


    def submit_button_action(self):
        for record in self:
            record.bay_status = 'occupied'

    def cancel_button_action(self):
        for record in self:
            record.bay_status = 'free'