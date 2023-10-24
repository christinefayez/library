# -*- coding: utf-8 -*-
{
    'name': "simplit_hr_overtime",

    'summary': """Automatic Overtime Calculation""",
    'description': """Management of overtime taken by the employees.""",
    'author': "Simplit",
    'website': "http://www.simplit.me",
    'category': 'Hr',
    'version': '12.0.2.4',
    'depends': ['base', 'hr', 'hr_payroll', 'hr_contract', 'hr_attendance',],

    'data': [
        'data/bonus.xml',
        'data/simplit_hr_overtime_data.xml',
        'data/simplit_hr_delaytime_data.xml',
        'security/ir.model.access.csv',
        'views/hr_overtime_view.xml',
        'views/hr_allowed_delay.xml',
        'views/hr_approved_delay_view.xml',
        'views/hr_approved_overtime_view.xml',
        'wizards/overtime_delay_partial_approval_forall.xml',
        # 'views/simplit_payroll_integration.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
