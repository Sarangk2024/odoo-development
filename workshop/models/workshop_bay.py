# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError


class WorkshopBay(models.Model):
    '''Describe the Workshop Bay management model'''
    _name = 'workshop.bay'
    _description = 'Bay'
    _rec_name = 'bay_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    bay_name = fields.Char(string='Bay Name',
                           help='Give me the name of the bay like Washing Bay, Wheel Alignment',
                           required=True, tracking=True, copy='False')
    assigned_employee_id = fields.Many2one('hr.employee',
                                           string='Assigned Employee',
                                           tracking=True)
    bay_type = fields.Selection([
        ('general', 'General'),
        ('express', 'Express'),
        ('alignment', 'Alignment'),
        ('wash', 'Wash'),
        ('painting', 'Painting'),
    ], string='Bay Type', required=True, default='general')
    bay_status = fields.Selection([
        ('free', 'Free'),
        ('occupied', 'Occupied'),
        ('closed', 'Closed'),
    ], string='Bay Status', required=True, default='free', tracking=True,
        readonly=True)
    active = fields.Boolean(default=True)
    ongoing_job_ids = fields.One2many('workshop.job.order', 'bay_id',
                                      string='Job',
                                      domain=[('state', '=', 'in_progress')])
    job_type_ids = fields.Many2many('job.type', string='Job Type',
                                    required=True)

    def submit_button_action(self):
        '''submit button action. change the  bay status to occupied'''
        self.bay_status = 'occupied'

    def cancel_button_action(self):
        '''cancel button action. change the  bay status to free and check if the order can be canceled '''
        if "in_progress" in self.ongoing_job_ids.mapped("state"):
            raise UserError("This Bay Already In Progress Job")
        self.bay_status = 'free'
