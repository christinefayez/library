# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Sale Count',
    'description': 'This module allows to display the Total Number of Products Sales Count in the Website.Sales Count on website, Website Sales count, Webshop sales couunt, Sale Count on Webshop, Show sales counter on shop page, purchase counter on shop page, Sales counter on website, Purchase counter on website, show number of sales on website, sales number on website, show number of sales on shop, sales number on shop',
    'license': 'OPL-1',
    'category': 'eCommerce',
    'version': '13.0.0.0',
    'summary': 'Shows Sales/Puchases Counter on website/Shop Page',
    'author': 'BrowseInfo',
    'depends': ['website', 'website_sale'],
    'data': [
        'views/template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_sale_count/static/src/css/custom.css',
        ],
    },
    'application': True,
    'installable': True,
    "images": ['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
