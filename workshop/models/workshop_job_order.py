# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class WorkshopJobOrder(models.Model):
    _name = "workshop.job.order"
    _description = "Workshop Job Order Management"
    _rec_name = 'sequence'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Char(string="Job Order Sequence" ,default="New" ,copy=False,readonly=True)
    customer_id = fields.Many2one(comodel_name='res.partner', string="Customer",tracking=True, required=True)
    phone_number = fields.Char(string="Phone Number")
    vehicle_id = fields.Many2one(comodel_name='vehicle.management', string="Vehicle", ondelete='restrict',required=True)
    mechanic_id = fields.Many2one(comodel_name='hr.employee', string="Mechanic",tracking=True)
    bay_id = fields.Many2one(comodel_name='workshop.bay', string="Bay",tracking=True)
    job_date = fields.Date(string="Job Date", required=True)
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
    ],default='draft',string="Job Order Status",tracking=True)

    total_amount = fields.Float(string="Total Amount")

    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if val.get('sequence', 'New') == 'New':
                val['sequence'] = self.env['ir.sequence'].next_by_code('workshop.job.order') or 'New'
            return super(WorkshopJobOrder,self).create(val)
        return 0

    def confirm_work_action(self):
        for record in self:
            record.state = 'confirmed'

    def cancel_work_action(self):
        for record in self:
            record.state = 'draft'


    def action_start(self):
        for record in self:
            if record.bay_id.bay_status =='free':
                record.bay_id.bay_status = 'occupied'
                record.bay_id.ongoing_job_id = record.id
                record.state = 'in_progress'
            else:
                raise UserError('Bay is Not Available')

    def action_done(self):
        for record in self:
            if record.bay_id.ongoing_job_id == record:
                record.bay_id.bay_status = 'free'
                record.bay_id.ongoing_job_id=False

            record.state = 'done'

    @api.onchange('customer_id')
    def find_phone_number(self):
        if self.customer_id:
            self.phone_number = self.customer_id.phone