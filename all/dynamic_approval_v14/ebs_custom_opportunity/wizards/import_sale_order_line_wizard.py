import base64
import os
import xlsxwriter
import xlrd
from odoo.exceptions import UserError, Warning
import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ImportSaleOrderData(models.TransientModel):
    _name = 'import.sale.order.data'

    choose_file = fields.Binary('Choose File')
    file_name = fields.Char('File Name')
    sale_id = fields.Many2one('sale.order', string='Sales Order')

    def import_sale_order_data(self):
        try:
            decoded_data = base64.decodebytes(self.choose_file)
            book = xlrd.open_workbook(file_contents=decoded_data or b'')
        except FileNotFoundError:
            raise UserError('No such file or directory found. \n%s.' % self.file_name)
        except xlrd.biffh.XLRDError:
            raise UserError('Only excel files are supported.')
        for sheet in book.sheets():
            try:
                if sheet.name == 'Sheet1':
                    if sheet.nrows <= 1:
                        raise UserError("You should add some lines at the sheet")
                    for row in range(sheet.nrows):
                        if row >= 1:
                            row_values = sheet.row_values(row)
                            if row_values[0] != '':
                                self.create_section(row_values[0])
                            self.create_list_val(row_values[1:])
            except IndexError:
                pass
    def create_section(self, data):
        sol_val = {'display_type': 'line_section',
                   'name': str(data),
                   'order_id': self.sale_id.id}
        sale_id = self.env['sale.order.line'].create(sol_val)
        return

    def create_list_val(self, data):
        product = self.env['product.product'].search([('name', '=', data[0])], limit=1)
        part_number = self.env['product.template'].search([('part_number', '=', data[1])], limit=1)
        if not product:
            if part_number:
                product = part_number.product_variant_ids
            else:
                raise Warning('Product not found, please check your sheet')
        if not data[1]:
            raise Warning('Part number is empty, please check your sheet')

        vertical = False
        if self.sale_id.opportunity_id:
            default_cost_revenue_dists = self.sale_id.opportunity_id.cost_revenue_ids.filtered(lambda line: line.is_added_automatically)
            if default_cost_revenue_dists:
                vertical = default_cost_revenue_dists[0]
        elif self.sale_id.revised_order_id.opportunity_id:
            default_cost_revenue_dists = self.sale_id.revised_order_id.opportunity_id.cost_revenue_ids.filtered(lambda line: line.is_added_automatically)
            if default_cost_revenue_dists:
                vertical = default_cost_revenue_dists[0]


        tax = self.env['account.tax'].search([('name', '=', data[10])], limit=1)

        sol_val = {'product_id': product.id if product else False,
                   'product_uom_qty': data[2],
                   'unit_buying_price': data[3],
                   'price_unit': data[4],
                   'warranty_charge_percentage': str(float(data[5])) if data[5] else str(0.0),
                   'freight_charge_amt': data[6],
                   'finance_charge': data[7],
                   'moh_charge': data[8],
                   'custom_charge': data[9],
                   'tax_id': [tax.id] if tax else False,
                   'cost_revenue_dist_id': vertical.id if vertical else False,
                   'order_id': self.sale_id.id}
        sale_line = self.env['sale.order.line'].create(sol_val)
        return

    def download_sale_order_data(self):
        report_file_name = self.prepare_excel_report()
        # Create Attachment
        attachment = self.create_attachment(report_file_name)
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'download',
        }

    def prepare_excel_report(self):
        file_name = 'ebs_accounting_report.xlsx'
        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet()

        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)
        worksheet.set_zoom(80)
        worksheet.set_column(0, 0, 17)
        worksheet.set_column(1, 1, 17)
        worksheet.set_column(2, 2, 17)
        worksheet.set_column(3, 3, 17)
        worksheet.set_column(4, 4, 17)
        worksheet.set_column(5, 5, 17)
        worksheet.set_column(6, 6, 17)
        worksheet.set_column(7, 7, 17)
        worksheet.set_column(8, 8, 24)
        worksheet.set_column(9, 9, 25)
        worksheet.set_column(10, 10, 25)
        worksheet.set_column(11, 11, 25)

        worksheet.set_row(0, 20)

        header_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True})

        worksheet.write(0, 0, 'Section', header_format)
        worksheet.write(0, 1, 'Product', header_format)
        worksheet.write(0, 2, 'Part No.', header_format)
        worksheet.write(0, 3, 'Quantity', header_format)
        worksheet.write(0, 4, 'Unit Buying Price', header_format)
        worksheet.write(0, 5, 'Unit Price', header_format)
        worksheet.write(0, 6, 'Warranty Charge (%)', header_format)
        worksheet.write(0, 7, 'Freight Charge Amount', header_format)
        worksheet.write(0, 8, 'Finance Charge (%)', header_format)
        worksheet.write(0, 9, 'MOH Charge (%)', header_format)
        worksheet.write(0, 10, 'Custom Charge (%)', header_format)
        worksheet.write(0, 11, 'Taxes', header_format)
        data_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        workbook.close()
        return file_name

    def create_attachment(self, file_name):
        """
        Delete file created in tmp dir, Delete old attachment and create attachment for download report
        :param file_name: file name string
        :return: attachment ir.attachment object
        """
        ir_attachment_obj = self.env['ir.attachment']
        # Read File data
        with open(file_name, "rb+") as file:
            file_data = base64.encodebytes(file.read())
            file.close()

        # Remove tmp file
        os.remove(file_name)

        # Delete Old Attachment
        attachments = ir_attachment_obj.search([('name', '=ilike', 'sale_order_line_date.xlsx'),
                                                ('res_model', '=', 'sale.order.line')])
        attachments and attachments.unlink()

        return ir_attachment_obj.create({
            'name': 'sale_order_line_date.xlsx',
            'datas': file_data,
            'res_model': 'sale.order.line',
            'type': 'binary'
        })
