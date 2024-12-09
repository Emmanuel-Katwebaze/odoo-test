from odoo import fields, models, api

class Brand(models.Model):
    _name = 'liquor_store.brand'
    _description = 'Brand'
    
    name = fields.Char('Brand Name', required=True)
    description = fields.Text('Description', required=True)
    quantity = fields.Integer('Quantity', compute='_compute_quantity')
    bottle_ids = fields.One2many('liquor_store.bottle', 'brand', string='Bottles')
    sold_bottle_count = fields.Integer('Sold Bottle Count', compute='_compute_sold_bottle_count')

    @api.depends('bottle_ids.status')
    def _compute_quantity(self):
        for brand in self:
            available_bottles = brand.bottle_ids.filtered(lambda b: b.status == 'available')
            brand.quantity = len(available_bottles)
            if not available_bottles:
                brand.quantity = 0
                
    @api.depends('bottle_ids.status')
    def _compute_sold_bottle_count(self):
        for brand in self:
            sold_bottles = brand.bottle_ids.filtered(lambda b: b.status == 'sold')
            brand.sold_bottle_count = len(sold_bottles)
