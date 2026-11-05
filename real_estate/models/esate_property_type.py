from odoo import models, fields, api


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _rec_name = 'property_type'
    _order = 'property_type'


    property_type = fields.Char(string='Property Type', required=True)

    offer_count = fields.Integer(string='Total', compute='_compute_offer_count')

    property_type_ids = fields.One2many('estate.property','property_type_id',string='Properties')

    _property_type_unique = models.Constraint(
        'unique(property_type)', 'Property Type should be unique'

    )
    offer_ids =fields.One2many('estate.property.offer','property_type_id',string='Offers')

    @api.depends('property_type_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.property_type_ids)