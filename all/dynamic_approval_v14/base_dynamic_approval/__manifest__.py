{
    'name': 'Base Advanced Approval',
    'summary': 'Allow to set advanced approval cycle',
    'author': 'Ever Business Solutions',
    'maintainer': 'Abdalla Mohamed',
    'website': 'https://www.everbsgroup.com/',
    'version': '14.0.1.1.1',
    'category': 'Hidden/Tools',
    'license': 'OPL-1',
    'depends': [
        'mail',
        'sale',
    ],
    'data': [
        'security/ir_module_category.xml',
        'security/res_groups.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'wizards/approve_dynamic_approval_wizard.xml',
        'wizards/reject_dynamic_approval_wizard.xml',
        'wizards/recall_dynamic_approval_wizard.xml',
        'views/dynamic_approval.xml',
        'views/dynamic_approval_request.xml',
        'views/ir_ui_menu.xml',
        'views/res_config_settings.xml',
        'data/mail_activity_type.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
