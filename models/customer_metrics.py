from odoo import models, fields, api


class ResPartnerCustomerMetrics(models.Model):
    _name = "res.partner.customer_metrics"
    _description = "Customer Metrics"

    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, ondelete="cascade"
    )
    total_sales = fields.Float(
        string="Total Sales", compute="_compute_total_sales", store=True
    )
    order_count = fields.Integer(
        string="Order Count", compute="_compute_order_count", store=True
    )

    # Compute total sales
    @api.depends("customer_id")
    def _compute_total_sales(self):
        for record in self:
            sale_orders = self.env["sale.order"].search(
                [("partner_id", "=", record.customer_id.id)]
            )
            record.total_sales = sum(sale_orders.mapped("amount_total"))

    # Compute order count
    @api.depends("customer_id")
    def _compute_order_count(self):
        for record in self:
            record.order_count = self.env["sale.order"].search_count(
                [("partner_id", "=", record.customer_id.id)]
            )

    # Get top 5 customers
    def get_top_customers(self):
        return self.search([], order="total_sales desc", limit=5)

    # Auto-create metrics for existing customers when the module is installed
    def _auto_create_customer_metrics(self):
        partners = self.env["res.partner"].search([])
        for partner in partners:
            self._update_or_create_metrics(partner.id)

    # Create or update a metric record for a specific partner
    def _update_or_create_metrics(self, partner_id):
        metric = self.search([("customer_id", "=", partner_id)], limit=1)
        if not metric:
            metric = self.create({"customer_id": partner_id})
        metric._compute_total_sales()
        metric._compute_order_count()

    @api.model
    def init(self):
        self._auto_create_customer_metrics()
