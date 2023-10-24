 # -*- coding: utf-8 -*-
{
    'name': "hr_appraisal_calibration Strata",

    'summary': """
    
        """,

    'description': """
        Hr appraisal calibration
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_appraisal_custom','hr_appraisal','hr_document_custom','security_rules','sh_message','hr_approvals'],

    # always loaded
    'data': [
        "views/calibration_reporting_wizard_view.xml",
        "views/hr_calibration.xml",
        "views/appraisal_history.xml",
        "security/ir.model.access.csv",
        "views/hr_appraisal_calibration.xml",
        "views/employee_views.xml",
        "views/calibration_report_table.xml",
        "report/calibration_report.xml",
        "data/cron_jobs.xml"
    ],

}
