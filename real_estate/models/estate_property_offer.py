from datetime import timedelta
from odoo.exceptions import UserError
from odoo import api, fields, models


class RealEstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'RealEstate Property Offer'
    _order = 'price desc'

    price = fields.Float(string='Price')
    validity = fields.Integer(string='Validity Date', default=7)
    deadline = fields.Datetime(string='Deadline', compute='_compute_deadline', inverse='_inverse_deadline')

    status = fields.Selection([
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('refused', 'Refused'),
    ], default='pending')

    partner_id = fields.Many2one('res.partner', string='Customer')
    property_id = fields.Many2one('estate.property', string='Property')

    property_type_id = fields.Many2one('estate.property.type', string='Type')

    # deadline computation for offer model
    @api.depends('create_date', 'validity')
    def _compute_deadline(self):
        for offer in self:
            if offer.create_date:
                offer.deadline = offer.create_date + timedelta(days=offer.validity)
            else:
                offer.deadline = fields.Date.today() + timedelta(days=offer.validity)

    # inverse deadline for offer model
    def _inverse_deadline(self):
        for offer in self:
            if offer.create_date:
                offer.validity = (offer.deadline.date() - offer.create_date.date()).days
            else:
                offer.validity = (offer.deadline.date() - fields.Datetime.now().date()).days

    # when clicking Accept offer
    def confirm_action(self):
        for offer in self:
            if "confirmed" in offer.property_id.offer_id.mapped("status"):
                raise UserError("This Property Alredy Accepted One Offer")

            else:
                offer.status = 'confirmed'
                offer.property_id.state = 'offer_accepted'
                offer.property_id.price = offer.price
                offer.property_id.buyer_id = offer.partner_id

                other_offers = offer.property_id.offer_id - offer
                other_offers.status = 'refused'

    # when clicking refuse Offer
    def refuse_action(self):
        for offer in self:
            property_record = offer.property_id
            offer.status = 'refused'

            confirmed_offer = property_record.offer_id.filtered(lambda item: item.status == 'confirmed')
            if not confirmed_offer:
                property_record.price = 0
                property_record.buyer_id = False
                property_record.state = 'offer_received' if property_record.offer_id.filtered(
                    lambda item: item.status == 'pending') else 'new'

        return True

    @api.model_create_multi
    def create(self, vals_list):
        offers = super().create(vals_list)

        for offer in offers:
            if offer.property_id.state == 'new':
                offer.property_id.state = 'offer_received'

        return offers
