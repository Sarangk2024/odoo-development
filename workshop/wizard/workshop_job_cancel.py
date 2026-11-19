from odoo import fields, models


class WorkshopJobCancel(models.TransientModel):
    _name = "workshop.job.cancel"
    _description = "Workshop Job Cancel"


    cancel_reason = fields.Char(string="Cancel Reason", required=True)
    sequence = fields.Char(string="Sequence", required=True)
    vin =fields.Char(string="Vin", required=True)
    mode = fields.Char(string="Mode", required=True)
    year = fields.Char(string="Year", required=True)
    image = fields.Binary(string="Image", required=True)