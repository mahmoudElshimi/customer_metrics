{
    "name": "Customer Metrics",
    "version": "1.0",
    "summary": "Customer Sales Metrics Dashboard",
    "description": "A module to provide customer sales metrics, including total sales and order counts.",
    "author": "Mahmoud ElShimi",
    "website": "mailto:mahmoudelshimi@protonmail.ch",
    "category": "Sales",
    "depends": ["base", "sale"],  
    "license": "Other proprietary",  # See LICENSE(MIT/X) File in the same dir.
    "images": [
        "static/description/icon.png",
    ],
    "data": [
        "security/ir.model.access.csv", # Allow Sales Team to access this model.
        "data/cron.xml"
        "views/customer_metrics_views.xml",  
        "views/menu.xml",
    ],
    "installable": True,
    "application": True,  # I set this to True on purpose to make the module easier to find in the Odoo Apps menu.
}
