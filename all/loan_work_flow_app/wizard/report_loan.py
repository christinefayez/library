from odoo import models, fields, api
from odoo.tools.image import image_data_uri


class LoanReport(models.TransientModel):
    _name = 'loan.report.wizard'

    loan_id = fields.Many2one(comodel_name="hr.loan")

    def action_print_report(self):
        print('in pdf', self.loan_id)
        vals_lst = []

        for line in self.loan_id.loan_lines:
            v = {
                'date': line.date,
                'amount': line.amount
            }
            vals_lst.append(v)
        data_vals = {
            'employee': self.loan_id.employee_id.name,
            'department': self.loan_id.department_id.name,
            'loan_amount': self.loan_id.loan_amount,
            'payment_date': str(self.loan_id.payment_date),
            'date': str(self.loan_id.date),
            'job_position': self.loan_id.job_position,
            'installment': self.loan_id.installment,
            'total_amount': self.loan_id.total_amount,
            'total_paid': self.loan_id.total_paid_amount,
            'balance_amount': self.loan_id.balance_amount,
            'dof_user_id': self.loan_id.dof_user_id.name,
            'dof_signature': self.loan_id.dof_user_id.purchase_signature,
            'doo_user_id': self.loan_id.doo_user_id.name,
            'doo_signature': self.loan_id.doo_user_id.purchase_signature,
            'ceo_user_id': self.loan_id.ceo_user_id.name,
            'ceo_signature': self.loan_id.ceo_user_id.purchase_signature,
            'create_user_id': self.loan_id.create_uid.name,
            'create_user_signature': self.loan_id.create_uid.purchase_signature,
            'loan_description':self.loan_id.loan_description,
            'lines': vals_lst
        }
        print(data_vals)
        print(data_vals['doo_signature'])
        data = {
            'form': self.read()[0],
            'model': 'loan.report.wizard',
            'data_vals': data_vals,

        }

        return self.env.ref('loan_work_flow_app.print_loan_report_id').report_action(None, data=data)
