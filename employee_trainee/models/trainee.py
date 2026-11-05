from odoo import models, fields

class EmployeeTrainee(models.Model):
    _name = 'employee.trainee'
    _description = 'Employee trainee'

    name = fields.Char(string='Name')
    # email = fields.Char(string='Email')
    # phone = fields.Char(string='Phone')