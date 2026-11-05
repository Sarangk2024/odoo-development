from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'RealEstate Property management'
    _order = 'id desc'

    _tax_posetive_check = models.Constraint(
        'CHECK(tax>10)', 'Tax should be applied'
    )

    name = fields.Char(string='Name')
    description = fields.Char(string='Description', required=True)

    expected_price = fields.Float(string='Expected Price')
    price = fields.Float(string='Price')
    tax = fields.Integer(string='Tax')
    total = fields.Float(string='Total', compute='_compute_total')

    email = fields.Char(string='Email', copy=False)
    phone = fields.Char(string='Phone')
    garden = fields.Boolean(string='Garden')
    area = fields.Integer(string='Area')
    orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
    ])
    address = fields.Char(string='Address')
    city = fields.Char(string='City', default='Alabama', readonly=True)
    zip_code = fields.Char(string='Zip Code')
    date = fields.Date(string='Date')
    delivery_date = fields.Date(string='Delivery Date',
                                default=lambda self: fields.Date.add(fields.Date.today(), month=3))

    active = fields.Boolean(string='Active', default=True)

    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancel', 'Cancel'),

    ], default='new')

    property_type_id = fields.Many2one('estate.property.type', string='Property Type')

    buyer_id = fields.Many2one('res.partner', string='Buyer')
    sales_person_id = fields.Many2one('res.users', string='Sales Person', default=lambda self: self.env.user)

    tag_id = fields.Many2many('estate.property.tag', string='Tags')

    offer_id = fields.One2many('estate.property.offer', 'property_id', string='Offer')

    best_price = fields.Float(string='Best Price')

    # total price computation
    @api.depends('price', 'tax')
    def _compute_total(self):
        for i in self:
            i.total = i.price + (i.price * i.tax) / 100

    # finding best price
    @api.depends('offer_id.price')
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_id.mapped('price'), default=record.price)

    # changing fields when garden is ticked
    @api.onchange('garden')
    def onchange_garden(self):
        if self.garden:
            self.area = 10
            self.orientation = 'north'
        else:
            self.area = 0
            self.orientation = 'south'

    # submit button action
    def submit_action(self):
        if self.state == 'cancel':
            raise UserError("Property Already Cancelled")
        else:
            self.state = 'sold'

    # cancel button action
    def cancel_action(self):
        if self.state == 'sold':
            raise UserError("Property Already Sold")
        else:
            self.state = 'cancel'

    # selling price check
    @api.constrains('expected_price', 'price')
    def _check_price(self):
        for record in self:
            if record.price and record.price < record.expected_price * 0.9:
                raise ValidationError("selling price cannot be less than expected")


    @api.ondelete(at_uninstall=False)
    def ondelete(self):
        if self.state not in ['cancel', 'new']:
            raise UserError("Property Cannot be deleted")



