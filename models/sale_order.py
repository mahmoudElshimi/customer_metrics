from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        if order.partner_id:
            self.env["res.partner.customer_metrics"]._update_or_create_metrics(order.partner_id.id)
        return order

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if "partner_id" in vals or "amount_total" in vals:
            for order in self:
                self.env["res.partner.customer_metrics"]._update_or_create_metrics(order.partner_id.id)
        return res

    def unlink(self):
        partners = self.mapped("partner_id")
        res = super(SaleOrder, self).unlink()
        for partner in partners:
            self.env["res.partner.customer_metrics"]._update_or_create_metrics(partner.id)
        return res

