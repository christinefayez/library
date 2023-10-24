# -*- coding: utf-8 -*-
{
    'name': "EBS - Payroll",

    'summary': """
        EBS modification for payroll""",

    'description': """
    EBS modification for payroll
    """,

    'author': "jaafar khansa",
    'website': "http://www.ever-bs.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list

    'version': '0.0.6',

    # any module necessary for this one to work correctly
    'category': 'Payroll Localization',
    'depends': ['hr_payroll', 'hr_employee_custom', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ebs_hr_security.xml',
        'views/account_move_line.xml',
        'views/additional_elements_types_views.xml',
        'views/additional_elements_view.xml',
        'views/allowance_request_type_view.xml',
        'views/hr_hour_ratio.xml',
        'views/allowance_request_view.xml',
        'views/menus.xml',
    ]
}
