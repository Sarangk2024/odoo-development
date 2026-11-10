# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountMove(models.Model):
    '''inheriting account.move model to show the job id in that form view'''
    _inherit = "account.move"

    job_order_id = fields.Many2one('workshop.job.order', string="Job Order")
