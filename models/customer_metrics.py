from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
BATCH_SIZE = 10000

class ResPartnerCustomerMetrics(models.Model):
    _name = "res.partner.customer_metrics"
    _description = "Customer Metrics"

    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, ondelete="cascade"
    )
    total_sales = fields.Float(string="Total Sales", compute="_compute_total_sales", readonly=True, store=True)
    order_count = fields.Integer(string="Order Count", compute="_compute_order_count", readonly=True, store=True)

    @api.depends("customer_id")
    def _compute_total_sales(self):
        for record in self:
            sales = self.env["sale.order"].search([("partner_id", "=", record.customer_id.id)])
            record.total_sales = sum(sales.mapped("amount_total"))

    @api.depends("customer_id")
    def _compute_order_count(self):
        for record in self:
            record.order_count = self.env["sale.order"].search_count([("partner_id", "=", record.customer_id.id)])

    @api.model
    def _auto_create_customer_metrics(self):
        """Batch process customer metrics asynchronously using a cron job."""
        partner_model = self.env["res.partner"]
        customer_metrics_model = self.env["res.partner.customer_metrics"].sudo()

        total_partners = partner_model.search_count([])
        _logger.info(f"Starting Customer Metrics Initialization: {total_partners} customers found.")

        for offset in range(0, total_partners, BATCH_SIZE):
            partners = partner_model.search([], offset=offset, limit=BATCH_SIZE)
            existing_customers = customer_metrics_model.search([("customer_id", "in", partners.ids)])
            existing_ids = set(existing_customers.mapped("customer_id.id"))
            new_partners = [partner.id for partner in partners if partner.id not in existing_ids]

            if new_partners:
                customer_metrics_model.create([{"customer_id": pid} for pid in new_partners])
                self.env.cr.commit()  # Commit after processing each batch

            _logger.info(f"Processed {offset + len(partners)}/{total_partners} customers...")

        _logger.info("Customer Metrics Initialization Completed.")

    @api.model
    def init(self):
        cron = self.env.ref("customer_metrics.ir_cron_customer_metrics_init", raise_if_not_found=False)
        if cron:
            cron.sudo().write({"active": True})

