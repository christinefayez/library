{
    'name': 'Sale Analytic Account (Vertical) Integration',
    'summary': 'Allow to set analytic account (Vertical) in sales order',
    'author': 'Ever Business Solutions',
    'maintainer': 'Abdalla Mohamed',
    'website': 'https://www.everbsgroup.com/',
    'version': '14.0.1.0.0',
    'category': 'Hidden/Tools',
    'license': 'OPL-1',
    'depends': [
        'sale',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/crm_lead.xml',
        'views/sale_order.xml',
        'views/account_analytic_account.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
