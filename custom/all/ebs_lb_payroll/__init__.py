# -*- coding: utf-8 -*-
# from odoo import api, fields, tools
from . import controllers
from . import models

# data_paths = [
#     'data/ebspayroll.governorate.csv',
#     'data/ebspayroll.districts.csv',
#     'data/ebspayroll.real.estate.area.csv',
#     'data/ebspayroll.district.towns.csv',
#     'data/ebspayroll.commissioning.area.csv',
#     'data/ebspayroll.legal.types.csv'
# ]
#
#
# def add_leb_payroll_data_pre(cr):
#     print('herer')
#     from odoo import api, SUPERUSER_ID
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     installed_module_ids = env['ir.module.module'].search([('state', '=', 'installed'),
#                                                            ('name', '=', 'ebs_lb_payroll')])
#     if len(installed_module_ids) > 0:
#         for path in data_paths:
#             print(path)
#             tools.convert_file(cr, 'ebs_lb_payroll', path, None, mode='init', noupdate=True, kind='init', report=None)
#
#
# def add_leb_payroll_data(cr, registry):
#     for path in data_paths:
#         print(path)
#         tools.convert_file(cr, 'ebs_lb_payroll', path, None, mode='init', noupdate=True, kind='init', report=None)
