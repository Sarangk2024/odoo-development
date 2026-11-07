# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class WorkshopJobOrder(models.Model):
    _name = "workshop.job.order"
    _description = "Workshop Job"
    _rec_name = 'sequence'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Char(string="Job Order Sequence" ,default="New" ,copy=False,readonly=True)
    customer_id = fields.Many2one(comodel_name='res.partner', string="Customer",tracking=True, required=True)
    phone_number = fields.Char(string="Phone Number")
    vehicle_id = fields.Many2one(comodel_name='vehicle.management', string="Vehicle",ondelete='restrict', required=True, domain="[('owner_id', '=',customer_id )] if customer_id else []")
    mechanic_ids = fields.Many2many(comodel_name='hr.employee', string="Mechanics",tracking=True, required=True)
    bay_id = fields.Many2one(comodel_name='workshop.bay', string="Bay",tracking=True, required=True ,domain="[('bay_status', '=','free')]")
    job_date = fields.Date(string="Job Date", required=True, default=fields.Date.today())
    customer_notes = fields.Text(string="Customer Notes" , help="Customer's reported issue")
    image_id = fields.Image( string="Vehicle Image")
    warranty_status = fields.Boolean(string="Warranty Status",help='indicating whether the vehicle is under warranty')
    repair_instructions = fields.Html(string="Repair Instructions")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('invoiced', 'Invoiced')
    ],default='draft',string="Job Order Status",tracking=True, readonly=True)
    total_amount = fields.Float(string="Total Amount")
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        ''' custom sequence  generation logic'''
        for val in vals_list:
            if val.get('sequence', 'New') == 'New':
                val['sequence'] = self.env['ir.sequence'].next_by_code('workshop.job.order') or 'New'
            return super(WorkshopJobOrder,self).create(val)
        return 0

    def action_confirm_work(self):
        ''' confirm work action. changing the state to confirmed '''
        self.state = 'confirmed'

    def action_cancel_work(self):
        '''cancel work action. changing the state to canceled and updating the ongoing job status'''
        self.state = 'draft'
        self.bay_id.bay_status='free'
        self.bay_id.ongoing_job_ids=False

    def action_start(self):
        '''start button function set the bay status to occupied and set the ongoing job and bay availability check'''
        if self.bay_id.bay_status =='free':
            self.bay_id.bay_status = 'occupied'
            self.bay_id.ongoing_job_ids = self
            self.state = 'in_progress'
        else:
            raise UserError('Bay is Not Available')

    def action_done(self):
        '''setinig the job as done and chnage the bay availability'''
        if self.bay_id.ongoing_job_ids == self:
            self.bay_id.bay_status = 'free'

        self.state = 'done'

    def action_invoiced(self):
        '''invoice button  logic'''
        if self.state == 'done':
            self.state = 'invoiced'

    @api.onchange('customer_id')
    def find_phone_number(self):
        '''getting phone number of the selected customer and there vehicles'''
        if self.customer_id:
            self.phone_number = self.customer_id.phone
        else:
            self.phone_number = None
            self.vehicle_id = None
        #     self.vehicle_id = False
        #     return {'domain': {'vehicle_id': [('owner_id', '=', self.customer_id)]}}
        # else:
        #     return {'domain': {'vehicle_id': []}}


    @api.onchange('vehicle_id')
    def find_customer(self):
        '''finding customer from vehicle'''
        for record in self:
            if record.vehicle_id:
                record.customer_id = record.vehicle_id.owner_id

    # @api.onchange('bay_id')
    # def find_mechanic(self):
    #     '''finding mechanic from bay'''
    #     self.mechanic_ids= self.bay_id.assigned_employee_id

    # @api.onchange('customer_id')
    # def find_customer(self):
    #     for record in self:
    #         if record.customer_id:
    #             print(record.customer_id)
    #             record.vehicle_id.owner_id = record.customer_id
    #             print(record.vehicle_id.owner_id)
