# -*- coding: utf-8 -*-

from odoo import fields, models

class JobType(models.Model):
    _name = 'job.type'
    _description = 'Workshop Job Type'
    _rec_name = 'job_type_id'

    job_type_id = fields.Char(string="Job Type")