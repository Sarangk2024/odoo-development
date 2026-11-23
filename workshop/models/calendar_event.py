from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CalendarEvent(models.Model):
    _inherit = ['calendar.event']
    _rec_name = 'sequence'

    sequence = fields.Char(string="Sequence", default="New",
                           copy=False, readonly=True)
    customer_id = fields.Many2one('res.partner', string='Customer')
    vehicle_id = fields.Many2one('vehicle.management', string='Vehicle',
                                 domain="[('owner_id', '=',customer_id )] if customer_id else []")
    job_type_id = fields.Many2one('job.type', string='Job Type')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('work_order', 'Work Order'),
    ], default='draft', string="Job Order Status", readonly=True)
    work_order_ids = fields.One2many('workshop.job.order', 'appointment_id',
                                     string='Work Order')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company
    )

    def action_create(self):
        '''create the work order from appointment'''
        self.ensure_one()
        self.state = 'work_order'

        return {
            "name": "Form From Appointment",
            "type": "ir.actions.act_window",
            "res_model": "workshop.job.order",
            "view_mode": "form",
            "target": "new",
            "context": {
                'default_customer_id': self.customer_id.id,
                'default_vehicle_id': self.vehicle_id.id,
                'default_job_type_id': self.job_type_id.id,
                'default_job_date': self.start,
                'default_appointment_id': self.id
            }
        }

    def action_confirm(self):
        '''Appointment confirmation'''
        self.state = 'confirmed'
        for record in self:
            existing_appointments = self.env['calendar.event'].search([
                ('id', '!=', record.id),
                ('job_type_id', '=', record.job_type_id),
                ('start_date', '<', record.stop_date),
                ('stop_date', '>', record.start_date)
            ])
            if existing_appointments:
                if self.start_date < fields.Datetime.now:
                    raise ValidationError("Start Date Cannot be past  Date")
                raise ValidationError("Another Appointment is already present")

    def action_cancel(self):
        '''Appointment cancellation'''
        self.state = 'draft'

    @api.model_create_multi
    def create(self, vals_list):
        ''' custom sequence  generation logic and create appointments'''
        for val in vals_list:
            if val.get('sequence', 'New') == 'New':
                val['sequence'] = self.env['ir.sequence'].next_by_code(
                    'calendar.event') or 'New'
            return super().create(val)

        return super().create(vals_list)

    def write(self, vals):
        '''Write appointments'''
        return super().write(vals)

    def action_automate_work_appointment(self):
        '''setting the job as done and change the bay availability'''
        email_template = self.env.ref(
            'workshop.email_template_workshop_appointment')

        for record in self:
            if record.customer_id.email:
                email_values = {'email_to': record.customer_id.email}
                email_template.send_mail(
                    record.id,
                    force_send=True, email_values=email_values)

    def _cron_workshop_appointment_reminder(self):
        '''setting appointment reminder'''
        today_start = fields.Date.today()
        records = self.env['calendar.event'].search([
            ('state', '=', 'confirmed'),
        ])
        email_template = self.env.ref(
            'workshop.email_template_workshop_appointment_reminder')

        for record in records:
            if record.customer_id.email and (record.start - timedelta(days=1)).date() == today_start :
                email_values = {'email_to': record.customer_id.email}
                email_template.send_mail(
                    record.id,
                    force_send=True, email_values=email_values)
            if record.work_order_ids.state != 'delivered':
                email_template = self.env.ref(
                    'workshop.email_template_workshop_appointment_reminder_delivery')
                email_values = {'email_to': record.customer_id.email}
                email_template.send_mail(
                    record.id,
                    force_send=True, email_values=email_values)
