# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command


class WorkshopJobOrder(models.Model):
    '''manage workshop job order model'''
    _name = "workshop.job.order"
    _description = "Workshop Job"
    _rec_name = 'sequence'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Char(string="Sequence", default="New",
                           copy=False, readonly=True)
    customer_id = fields.Many2one(comodel_name='res.partner', string="Customer",
                                  tracking=True, required=True)
    phone_number = fields.Char(string="Phone Number",
                               related="customer_id.phone")
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
    job_date = fields.Datetime(string="Job Date", required=True,
                               default=fields.Datetime.now())
    customer_notes = fields.Text(string="Customer Notes",
                                 help="Customer's reported issue")
    image_id = fields.Many2many('ir.attachment', string="Vehicle Image")
    warranty_status = fields.Boolean(string="Under Warranty",
                                     help='indicating whether the vehicle is under warranty')
    repair_instructions = fields.Html(string="Repair Instructions")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('quotation', 'Quotation'),
        ('invoiced', 'Invoiced')
    ], default='draft', string="Job Order Status", tracking=True, readonly=True)
    total_amount = fields.Float(string="Total Amount",
                                compute='_compute_total_amount', store=True)
    active = fields.Boolean(default=True)
    invoice_ids = fields.One2many('account.move', 'job_order_id',
                                  string="Invoice",
                                  readonly=True,
                                  domain=[('move_type', '=', 'out_invoice')])
    sale_order_ids = fields.One2many('sale.order', 'job_order_id',
                                     string="Sale Order")
    job_type_id = fields.Many2one('job.type', help="Specify the job type")
    job_order_line_ids = fields.One2many('workshop.job.line',
                                         "job_order_line_id",
                                         string="Job Lines")
    invoice_count = fields.Integer(compute='_compute_invoice_count', store=True)
    quotation_count = fields.Integer(compute='_compute_quotation_count',
                                     store=True)

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
            if self.total_amount <= 0:
                raise ValidationError('Total Amount must be greater than 0')
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
        '''setting the job as done and change the bay availability'''
        if self.bay_id.ongoing_job_ids == self:
            self.bay_id.bay_status = 'free'
        self.state = 'done'

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        '''getting phone number of the selected customer and there vehicles'''
        if self.customer_id:
            self.phone_number = self.customer_id.phone

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        '''finding customer from vehicle'''
        if self.vehicle_id:
            self.customer_id = self.vehicle_id.owner_id

    @api.onchange('job_type_id')
    def _onchange_job_type_id(self):
        '''resetting bay type and job type'''
        self.bay_id = None

    @api.depends('job_order_line_ids.line_subtotal')
    def _compute_total_amount(self):
        '''finding total amount from order lines'''
        self.total_amount = sum(
            self.job_order_line_ids.mapped('line_subtotal'))

    @api.onchange('job_date')
    def _onchange_job_date(self):
        """Validate date range and prevent  date from being earlier than today's date."""
        date = fields.Datetime.now()
        if self.job_date.date() < date.date():
            self.job_date = date
            return {
                'warning': {
                    'title': "Invalid Date",
                    'message': "Job Date cannot be earlier than Today.",
                }
            }

    def action_quotation(self):
        '''quotation creation logic for work order'''
        self.state = 'quotation'
        sale_order_lines = []
        for line in self.job_order_line_ids:
            sale_order_lines.append(
                Command.create(
                    {
                        'product_id': line.product_id.id,
                    }
                ))
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer_id.id,
            'order_line': sale_order_lines,
            'job_order_id': self.id,
            "vehicle_id": self.vehicle_id.id,
        })
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Quotation',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'target': 'current',
            'res_id': sale_order.id
        }


    def action_invoiced(self):
        '''invoice creation logic for work order'''
        sale_order = self.env['sale.order'].search([
            ('job_order_id', '=', self.id)
        ])
        if sale_order:
            print("sale order have")
            sale_order.action_confirm()
            invoice = sale_order._create_invoices()
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': invoice.id,
                'view_mode': 'form',
                'target': 'current',
            }

        else:
            sale_order_lines = []
            for line in self.job_order_line_ids:
                sale_order_lines.append(
                    Command.create(
                        {
                            'product_id': line.product_id.id
                        }
                    ))
            sale_order = self.env['sale.order'].create({
                'partner_id': self.customer_id.id,
                'job_order_id': self.id,
                'order_line': sale_order_lines,
            })
            self.ensure_one()
            sale_order.action_confirm()
            invoice = sale_order._create_invoices()
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': invoice.id,
                'view_mode': 'form',
                'target': 'current',
            }

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        '''Finding invoice count for work order'''
        for record in self:
            record.invoice_count = len(record.invoice_ids)
            if record.invoice_count > 0:
                record.state='invoiced'

    @api.depends('sale_order_ids')
    def _compute_quotation_count(self):
        '''Finding quotation count for work order'''
        for record in self:
            record.quotation_count = len(record.sale_order_ids)

    def action_view_invoice(self):
        '''show the invoice while clicking smart button'''
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'name': ' Invoice',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [
                ('job_order_id', '=', self.id),
                ('move_type', '=', 'out_invoice')
            ]
        }

    def action_view_quotation(self):
        '''show the quotation while clicking smart button'''
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'name': ' Quotations',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [
                ('job_order_id', '=', self.id)
            ]
        }
