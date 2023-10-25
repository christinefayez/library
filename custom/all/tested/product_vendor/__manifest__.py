# -*- coding: utf-8 -*-
{
    'name': "Product Vendor",
    'summary': """
        """,

   
    'author': "",
    
    'version': '0.1',
    'depends': ['base','product','sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
    ],

    'installable': True,
    'application': True,

}
