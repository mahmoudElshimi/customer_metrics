from odoo import models, fields, api


class ResPartnerCustomerMetrics(models.Model):
    _name = "res.partner.customer_metrics"
    _description = "Customer Metrics"

    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, ondelete="cascade"
    )
    total_sales = fields.Float(
        string="Total Sales", compute="_compute_total_sales", readonly=True, store=True
    )
    order_count = fields.Integer(
        string="Order Count", compute="_compute_order_count", readonly=True, store=True
    )

    # Compute total sales for the customer
    @api.depends("customer_id")
    def _compute_total_sales(self):
        for record in self:
            sale_orders = self.env["sale.order"].search(
                [("partner_id", "=", record.customer_id.id)]
            )
            record.total_sales = sum(order.amount_total for order in sale_orders)

    # Compute order count for the customer
    @api.depends("customer_id")
    def _compute_order_count(self):
        for record in self:
            record.order_count = self.env["sale.order"].search_count(
                [("partner_id", "=", record.customer_id.id)]
            )

    # Method to get top 5 customers
    def get_top_customers(self):
        top_customers = self.search([], order="total_sales desc", limit=5)
        return [
            {
                "name": customer.customer_id.name,
                "total_sales": customer.total_sales,
                "order_count": customer.order_count,
            }
            for customer in top_customers
        ]

    # INIT The Model with the existing customers
    def _auto_create_customer_metrics(self):
        partners = self.env["res.partner"].search([])
        for partner in partners:
            # Check if a record already exists for this partner
            existing_record = self.search([("customer_id", "=", partner.id)], limit=1)
            if not existing_record:
                # Create a new record iif it doesn't exist
                self.create(
                    {
                        "customer_id": partner.id,
                    }
                )

    def fields_view_get(
        self, view_id=None, view_type="tree", toolbar=False, submenu=False
    ):
        self._auto_create_customer_metrics()
        return super(ResPartnerCustomerMetrics, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )

    # Call _auto_create_customer_metrics before rendering the tree view
    def fields_view_get(
        self, view_id=None, view_type="tree", toolbar=False, submenu=False
    ):
        self._auto_create_customer_metrics()

        # Recompute total_sales and order_count for all records
        records = self.search([])
        records._compute_total_sales()
        records._compute_order_count()

        # Return the original view
        return super(ResPartnerCustomerMetrics, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )

    @api.model
    def init(self):
        self._auto_create_customer_metrics()
