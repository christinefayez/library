{
    'name': 'Analytic Account Dynamic Approval',
    'summary': 'Allow to set user and link to role at analytic account',
    'author': 'Ever Business Solutions',
    'maintainer': 'Abdalla Mohamed',
    'website': 'https://www.everbsgroup.com/',
    'version': '14.0.1.0.0',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'depends': [
        'analytic',
        'base_dynamic_approval_role',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_analytic_account.xml',
        'views/account_analytic_account_approval_role.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
