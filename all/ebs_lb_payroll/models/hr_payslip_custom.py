# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import date_utils
from odoo.tools.misc import format_date


class PayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    def days360(self, start_date, end_date, method_eu=False):
        start_day = start_date.day
        start_month = start_date.month
        start_year = start_date.year
        end_day = end_date.day
        end_month = end_date.month
        end_year = end_date.year

        if (
                start_day == 31 or
                (
                        method_eu is False and
                        start_month == 2 and (
                                start_day == 29 or (
                                start_day == 28 and
                                start_date.is_leap_year is False
                        )
                        )
                )
        ):
            start_day = 30

        if end_day == 31:
            if method_eu is False and start_day != 30:
                end_day = 1

                if end_month == 12:
                    end_year += 1
                    end_month = 1
                else:
                    end_month += 1
            else:
                end_day = 30

        return (
                end_day + end_month * 30 + end_year * 360 -
                start_day - start_month * 30 - start_year * 360)

    def calculateAdditionalElements(self, payslip, employee, type_code):
        additional_element_ids = self.env['ebspayroll.additional.element.lines'].search(
            [('type.name', '=', type_code), ('payment_date', '>=', payslip.date_from),
             ('payment_date', '<=', payslip.date_to), ('employee', '=', employee.id)])
        return sum(additional_element_ids.mapped('amount_in_currency'))

    def calculateAllowancePayment(self, payslip, employee, type):
        allowance_type = self.env['ebs.payroll.allowance.request.type'].search([('name', '=', type)], limit=1)
        req_allowance = self.env['ebs.payroll.allowance.request'].search([('employee_id', '=', employee.id),
                                                                          ('state', '=', 'financial'),
                                                                          ('request_type', '=', allowance_type.id),
                                                                          ('company_id', '=', payslip.company_id.id),
                                                                          ('payment_date', '>=', payslip.date_from),
                                                                          ('payment_date', '<=', payslip.date_to)])
        req_allowance.write({'payslip_id': payslip.id})
        amount = 0.0
        if req_allowance:
            amount = sum(req_allowance.mapped('amount'))
        return amount

    def calculateAmortizationPayment(self, payslip, employee, type):
        allowance_type = self.env['ebs.payroll.allowance.request.type'].search([('name', '=', type)], limit=1)
        req_line_allowance = self.env['ebs.payroll.allowance.request.lines'].search([
            ('employee_id', '=', employee.id),
            ('parent_type', '=', allowance_type.id),
            ('parent_id.company_id', '=', payslip.company_id.id),
            ('parent_state', '=', 'financial'),
            ('date', '>=', payslip.date_from),
            ('date', '<=', payslip.date_to)])
        req_line_allowance.write({'payslip_id': payslip.id})
        amount = 0.0
        if req_line_allowance:
            amount = sum(req_line_allowance.mapped('amount'))
        return amount

    def calculateRemainingAmortizationPayment(self, payslip, employee, type):
        allowance_type = self.env['ebs.payroll.allowance.request.type'].search([('name', '=', type)], limit=1)

        req_line_allowance = self.env['ebs.payroll.allowance.request.lines'].search([
            ('employee_id', '=', employee.id),
            ('parent_state', '=', 'financial'),
            ('parent_id.company_id', '=', payslip.company_id.id),
            ('parent_type', '=', allowance_type.id),
            ('date', '>=', payslip.date_from),
        ])
        req_line_allowance.write({'payslip_id': payslip.id})
        amount = 0.0
        if req_line_allowance:
            amount = sum(req_line_allowance.mapped('amount'))
        return amount

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        self.company_id = employee.company_id
        if not self.contract_id or self.employee_id != self.contract_id.employee_id:  # Add a default contract if not already defined
            contracts = employee._get_contracts(date_from, date_to)

            if not contracts or not contracts[0].structure_type_id.default_struct_id:
                self.contract_id = False
                self.struct_id = False
                return
            self.contract_id = contracts[0]
            self.struct_id = contracts[0].structure_type_id.default_struct_id

        payslip_name = self.struct_id.payslip_name or _('Salary Slip')
        self.name = '%s - %s - %s' % (
            format_date(self.env, self.date_from, date_format="MMMM"),
            self.employee_id.name or '',
            format_date(self.env, self.date_from, date_format="y")
        )

        if date_to > date_utils.end_of(fields.Date.today(), 'month'):
            self.warning_message = _(
                "This payslip can be erroneous! Work entries may not be generated for the period from %s to %s." %
                (date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1), date_to))
        else:
            self.warning_message = False

        self.worked_days_line_ids = self._get_new_worked_days_lines()