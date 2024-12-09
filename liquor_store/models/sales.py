from odoo import fields, models, api, exceptions, _

class SalesOrder(models.Model):
    _name = 'liquor_store.sales.order'
    _description = 'Sales Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name_seq'
    
    STATE_SELECTION = [
        ('quotation', 'Quotation'),
        ('quotation_sent', 'Quotation Sent'),
        ('sales_order', 'Sales Order'),
        ('done', 'Done'),
    ]

    name_seq = fields.Char(string='Order Reference', required=True, readonly=True, copy=False, index=True, default=lambda self: _('New'))
    
    customer_id = fields.Many2one('liquor_store.customer', string='Customer', required=True)
    order_line_ids = fields.One2many('liquor_store.sales.order.line', 'order_id', string='Order Lines')
    total_amount = fields.Float(string='Total Sale Amount', compute='_compute_total_amount', store=True)
    state = fields.Selection(STATE_SELECTION, string='Status', default='quotation', readonly=True)
    date = fields.Date('Date Sold', default=fields.Date.today())

    @api.depends('order_line_ids.subtotal')
    def _compute_total_amount(self):
        for order in self:
            order.total_amount = sum(order.order_line_ids.mapped('subtotal'))
            
    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('liquor_store.sales.order.sequence')
        return super(SalesOrder, self).create(vals)

    def action_send_by_email(self):
        self.write({'state': 'quotation_sent'})

    def action_confirm(self):
        self.write({'state': 'sales_order'})

    def action_validate(self):
        self.write({'state': 'done'})
        # self.order_line_ids.mapped('bottle_id').write({'status': 'sold'})
        sold_bottles = self.order_line_ids.filtered(lambda line: line.bottle_id.status == 'sold').mapped('bottle_id')
        sold_bottles.write({'selling_date': self.date})  # Update selling date of sold bottles
        
    def action_return(self):
        self.write({'state': 'quotation'})
        # self.order_line_ids.mapped('bottle_id').write({'status': 'available'})
        returned_bottles = self.order_line_ids.mapped('bottle_id')
        returned_bottles.filtered(lambda bottle: bottle.status == 'sold').write({'selling_date': False})  # Clear selling date of returned bottles
    
    def print_sales_order_report(self):
        report_action = self.env['ir.actions.report'].search([('report_name', '=', 'liquor_store.report_sales_orders')], limit=1)
        if report_action:
            return report_action.report_action(self)
        else:
            raise exceptions.UserError("Report action not found. Please make sure the report action exists.")

class SalesOrderLine(models.Model):
    _name = 'liquor_store.sales.order.line'
    _description = 'Sales Order Line'

    order_id = fields.Many2one('liquor_store.sales.order', string='Sales Order')
    bottle_id = fields.Many2one('liquor_store.bottle', string='Bottle', required=True)
    quantity = fields.Integer(string='Quantity', default=1)
    unit_price = fields.Float(string='Unit Price', compute='_compute_unit_price', store=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
            
    @api.depends('bottle_id')
    def _compute_unit_price(self):
        for line in self:
            line.unit_price = line.bottle_id.selling_price
            
    @api.constrains('bottle_id', 'order_id')
    def _check_unique_bottle_id(self):
        for line in self:
            if line.order_id and line.bottle_id:
                existing_line = self.env['liquor_store.sales.order.line'].search([
                    ('order_id', '=', line.order_id.id),
                    ('bottle_id', '=', line.bottle_id.id),
                    ('id', '!=', line.id),
                ])
                if existing_line:
                    raise exceptions.ValidationError(
                        "You cannot add the same bottle to the order multiple times."
                    )

class Invoice(models.Model):
    _name = 'liquor_store.invoice'
    _description = 'Invoice'

    customer_id = fields.Many2one('liquor_store.customer', string='Customer', required=True)
    invoice_line_ids = fields.One2many('liquor_store.invoice_line', 'invoice_id', string='Invoice Lines')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    tax = fields.Float(string='Tax', required=True, default=0.0)
    total_amount_due = fields.Float(string='Total Amount Due', compute='_compute_total_amount_due', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
    ], string='Status', default='draft', readonly=True)

    @api.depends('invoice_line_ids.subtotal')
    def _compute_subtotal(self):
        for invoice in self:
            invoice.subtotal = sum(invoice.invoice_line_ids.mapped('subtotal'))

    @api.depends('subtotal', 'tax')
    def _compute_total_amount_due(self):
        for invoice in self:
            invoice.total_amount_due = invoice.subtotal + invoice.tax
            
    def action_confirm_invoice(self):
        self.write({'state': 'posted'})

    def action_create_payment_popup(self):
        return {
            'name': 'Create Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'liquor_store.payment',
            'view_mode': 'form',
            'target': 'new',
        }

class InvoiceLine(models.Model):
    _name = 'liquor_store.invoice_line'
    _description = 'Invoice Line'

    invoice_id = fields.Many2one('liquor_store.invoice', string='Invoice')
    bottle_id = fields.Many2one('liquor_store.bottle', string='Bottle', required=True)
    quantity = fields.Integer(string='Quantity', default=1)
    unit_price = fields.Float(string='Unit Price', required=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
