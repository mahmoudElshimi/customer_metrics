from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        record = super(SaleOrder, self).create(vals)
        record._update_customer_metrics()
        return record

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        self._update_customer_metrics()
        return res

    def _update_customer_metrics(self):
        for order in self:
            metrics = (
                self.env["res.partner.customer_metrics"]
                .sudo()
                .search([("customer_id", "=", order.partner_id.id)], limit=1)
            )

            if not metrics:
                # If no record exists, create it using sudo() to bypass security restrictions
                metrics = (
                    self.env["res.partner.customer_metrics"]
                    .sudo()
                    .create(
                        {
                            "customer_id": order.partner_id.id,
                        }
                    )
                )

            sales = self.env["sale.order"].search(
                [("partner_id", "=", order.partner_id.id)]
            )
            metrics.sudo().write(
                {
                    "total_sales": sum(sales.mapped("amount_total")),
                    "order_count": len(sales),
                }
            )
