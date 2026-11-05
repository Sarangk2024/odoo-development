from odoo import fields, models, api


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _rec_name = 'tag_name'
    _order = 'tag_name'

    tag_name = fields.Char(string='Tag')
    sequence = fields.Integer(string='Sequence', default=1)
    color = fields.Integer(string='Colour')

    _tag_unique = models.Constraint(
        'unique(tag_name)', 'Tag should be unique'
    )
