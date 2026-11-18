# -*- coding: utf-8 -*-

from odoo import fields, models


class JobType(models.Model):
    '''Specify the job type of the workshop Bay'''
    _name = 'job.type'
    _description = 'Job Type'
    _rec_name = 'job_type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    job_type = fields.Char(string="Job Type",
                           help='Give me the job type of the workshop')
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company
    )
