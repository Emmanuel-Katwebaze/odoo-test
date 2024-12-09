# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo Liquor Store Management System',
    'depends' : ['mail', 'base', 'web', 'sale', 'board'],
    'version': '1.0.0',
    'sequence': 1,
    'author': 'Omni Software Ltd, Uganda',
    # 'live_test_url': 'https://www.youtube.com/watch?v=0kaHMTtn7oY',
    'summary': 'Comprehensive Management System for Liquor Stores',
    'description': """
    Odoo 17 Community Edition Liquor Store Management System

    Features:
    - Brand Management
    - Bottle Inventory Tracking
    - Customer Management
    - Supplier Transactions
    - Sales Order Processing
    - Invoicing
    - Reporting and Analytics
    - Sales Dashboard
    """,
    'website': 'https://omnitech.co.ug/',
    'data': [
        'security/access_groups.xml',
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'data/sequence_data.xml',
        'views/liquor_store_brand.xml',
        'views/liquor_store_bottles.xml',
        'views/liquor_store_bottle_size.xml',
        'views/liquor_store_customer.xml',
        'views/liquor_store_supplier.xml',
        'views/liquor_store_rfq.xml',
        'views/liquor_store_invoices.xml',
        'views/liquor_store_sales.xml',
        'views/liquor_store_sales_order_reporting.xml',
        'views/liquor_store_sales_analysis.xml',
        'views/liquor_store_supplier_transaction.xml',
        'views/sales_dashboard.xml',
        'views/liquor_store_menus.xml',
        'reports/sales_orders_report_template.xml',
        'reports/report.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
    'installable': True,
    'assets': {
        'web.assets_backend': [
            'liquor_store/static/src/components/**/*.js',
            'liquor_store/static/src/components/**/*.xml',
            'liquor_store/static/src/components/**/*.scss',
        ],
    },
    'images': ['static/description/banner.jpg'],
}