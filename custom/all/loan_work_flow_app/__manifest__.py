# -*- coding: utf-8 -*-
{
    'name': "Loan Work Flow App",
    'description': """
Loan Work Flow App    """,


    'author': "Christine",
    'website': 'https://www.linkedin.com/in/christine-fayez-018593172',
    'category': 'Uncategorized',
    'version': '15.0.1',
    'depends': ['ohrms_loan'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_move_line.xml',
        'views/templates.xml',
        'report/loan_report.xml',
        'wizard/wizard_view.xml'
    ],

}
