# -*- coding: utf-8 -*-
{
    'name': "Product Losing Report",
    'description': """
        Product Losing Report """,
    'author': "Plennix Company",
    'website': "https://www.plennix.com/",
    'category': 'Inventory',
    'version': '15.0.1',
    'depends': ['sale', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_production_lot.xml',
        'views/product_losing_report.xml',
        'views/stock_valuation.xml'
    ],
}
