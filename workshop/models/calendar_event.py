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
    work_order_ids = fields.One2many('workshop.job.order','appointment_id', string='Work Order')

    def action_create(self):
        '''create the work order from appointment'''
        self.ensure_one()
        self.state='work_order'
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
                'default_job_date':self.start,
                'default_appointment_id':self.id
            }
        }

    def action_confirm(self):
        '''Appointment confirmation'''
        self.state='confirmed'
        for record in self:
            existing_appointments = self.env['calendar.event'].search([
                ('id', '!=', record.id),
                ('job_type_id', '=', record.job_type_id),
                ('start_date', '<', record.stop_date),
                ('stop_date', '>', record.start_date)
            ])
            if existing_appointments:
                if existing_appointments.start_date < fields.Datetime.now:
                    raise ValidationError("Start Date Cannot be past  Date")
                raise ValidationError("Another Appointment is already present")

    def action_cancel(self):
        '''Appointment cancellation'''
        self.state='draft'


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
