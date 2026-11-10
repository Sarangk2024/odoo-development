# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class WorkshopJobOrder(models.Model):
    '''manage workshop job order model'''
    _name = "workshop.job.order"
    _description = "Workshop Job"
    _rec_name = 'sequence'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Char(string=" ", default="New",
                           copy=False, readonly=True)
    customer_id = fields.Many2one(comodel_name='res.partner', string="Customer",
                                  tracking=True, required=True)
    phone_number = fields.Char(string="Phone Number", related="customer_id.phone")
    vehicle_id = fields.Many2one(comodel_name='vehicle.management',
                                 string="Vehicle", ondelete='restrict',
                                 required=True,
                                 domain="[('owner_id', '=',customer_id )] if customer_id else []")
    mechanic_ids = fields.Many2many(comodel_name='hr.employee',
                                    string="Mechanics", tracking=True,
                                    required=True)
    bay_id = fields.Many2one(comodel_name='workshop.bay', string="Bay",
                             tracking=True, required=True,
                             domain="[('job_type_ids','in',job_type_id)] if job_type_id else []")
    job_date = fields.Date(string="Job Date", required=True,
                           default=fields.Date.today())
    customer_notes = fields.Text(string="Customer Notes",
                                 help="Customer's reported issue")
    image_id = fields.Many2many('ir.attachment',string="Vehicle Image")
    warranty_status = fields.Boolean(string="Under Warranty",
                                     help='indicating whether the vehicle is under warranty')
    repair_instructions = fields.Html(string="Repair Instructions")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('invoiced', 'Invoiced')
    ], default='draft', string="Job Order Status", tracking=True, readonly=True)
    total_amount = fields.Float(string="Total Amount",
                                compute='_compute_total_amount', store=True)
    active = fields.Boolean(default=True)
    invoice_id = fields.Many2one('account.move', string="Invoice",
                                 readonly=True, copy=False)
    job_type_id = fields.Many2one('job.type', help="Specify the job type")
    job_order_line_ids = fields.One2many('workshop.job.line',
                                         "job_order_line_id",
                                         string="Job Lines")

    @api.model_create_multi
    def create(self, vals_list):
        ''' custom sequence  generation logic'''
        for val in vals_list:
            if val.get('sequence', 'New') == 'New':
                val['sequence'] = self.env['ir.sequence'].next_by_code(
                    'workshop.job.order') or 'New'
            return super().create(val)

    def action_confirm(self):
        ''' confirm work action. changing the state to confirmed  and checking if the order line is empty or not'''
        if self.job_order_line_ids:
            self.state = 'confirmed'
        else:
            raise UserError('Job Order Lines cannot be Empty')

    def action_cancel(self):
        '''cancel work action. changing the state to canceled and updating the ongoing job status'''
        self.state = 'draft'
        self.bay_id.bay_status = 'free'

    def action_start(self):
        '''start button function set the bay status to occupied and set the ongoing job and bay availability check'''
        if self.bay_id.bay_status == 'free':
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

    @api.onchange('customer_id')
    def onchange_customer_id(self):
        '''getting phone number of the selected customer and there vehicles'''
        if self.customer_id:
            self.phone_number = self.customer_id.phone

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        '''finding customer from vehicle'''
        if self.vehicle_id:
            self.customer_id = self.vehicle_id.owner_id

    @api.onchange('job_type_id')
    def onchange_job_type_id(self):
        '''resetting bay type and job type'''
        if self.job_type_id:
            self.bay_id = None
        else:
            self.bay_id = None
            self.job_type_id = None

    @api.depends('job_order_line_ids.line_subtotal')
    def _compute_total_amount(self):
        '''finding total amount from order lines'''
        for record in self:
            total = 0
            for line in record.job_order_line_ids:
                total += line.line_subtotal
            record.total_amount = total

    def action_invoiced(self):
        '''setinig the job as done and chnage the bay availability'''
        self.bay_id.bay_status = 'free'
        self.state = 'invoiced'
