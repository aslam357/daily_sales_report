from odoo import models, fields, api
from io import BytesIO
import xlwt
import base64

class DailySalesReportWizard(models.TransientModel):
    _name = 'daily.sales.report.wizard'
    _description = 'Daily Sales Report Wizard'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    salesperson_id = fields.Many2one('res.users')
    include_paid_orders = fields.Boolean()
    include_delivery_status = fields.Boolean(string="Show Delivery Status")
    include_taxes = fields.Boolean(string="Include Taxes")

    def action_generate_report(self):
        domain = [
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
            ('state', '=', 'sale')  
        ]
        if self.salesperson_id:
            domain.append(('user_id', '=', self.salesperson_id.id))
        
        if self.include_paid_orders:
            domain.append(('is_paid', '=', True))

        orders = self.env['sale.order'].search(domain)

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Daily Sales Report')
        
        title_style = xlwt.easyxf('font: bold 1, height 320; align: horiz center; pattern: pattern solid, fore_colour light_blue')
        subheader_style = xlwt.easyxf('font: bold 1; align: horiz left')
        header_style = xlwt.easyxf('font: bold 1; borders: bottom thick, top thick, left thick, right thick; align: horiz center')
        data_style = xlwt.easyxf('borders: bottom thin, top thin, left thin, right thin')
        currency_style = xlwt.easyxf('borders: bottom thin, top thin, left thin, right thin; align: horiz right', num_format_str='#,##0.00')
        worksheet.write_merge(0, 0, 0, 6, 'Daily Sales Report', title_style)
        worksheet.write_merge(2, 2, 0, 6, f'Date From: {self.date_from} To: {self.date_to}', subheader_style)
           
        headers = ['No', 'Date', 'Ref. No.', 'Document No', 'Customer', 'Sales Person', 'Total', 'VAT', 'Net Total', 'Payment Status', 'Delivery Status']
        for col, header in enumerate(headers):
            worksheet.write(4, col, header, header_style)

        total_untaxed = total_vat = total_net = 0.0
        delivery_status_selection = dict(self.env['sale.order'].fields_get(allfields=['delivery_status'])['delivery_status']['selection'])
        
        for row, order in enumerate(orders, start=5):
            worksheet.write(row, 0, row - 4, data_style)
            worksheet.write(row, 1, order.date_order.strftime('%m/%d/%Y') if order.date_order else '', data_style)
            worksheet.write(row, 2, order.name or '', data_style)
            worksheet.write(row, 3, order.name or '', data_style)
            worksheet.write(row, 4, order.partner_id.name or '', data_style)
            worksheet.write(row, 5, order.user_id.name or '', data_style)
            worksheet.write(row, 6, order.amount_total, currency_style)
            worksheet.write(row, 7, order.amount_tax, currency_style)
            worksheet.write(row, 8, order.amount_untaxed, currency_style)
            worksheet.write(row, 9, 'Paid' if order.is_paid else 'Not Paid', data_style)
            worksheet.write(row, 10, delivery_status_selection.get(order.delivery_status, ''), data_style)

            total_untaxed += order.amount_untaxed
            total_vat += order.amount_tax
            total_net += order.amount_total

        header_row = len(orders) + 6
        worksheet.write_merge(header_row, header_row, 0, 1, 'Total Summary', title_style)

        summary_labels = ['Total Untaxed', 'Total VAT', 'Net Total']
        summary_values = [total_untaxed, total_vat, total_net]

        start_row = header_row + 3
        for i, label in enumerate(summary_labels):
            worksheet.write(start_row + i, 0, label, subheader_style)
            worksheet.write(start_row + i, 1, summary_values[i], currency_style)

        file_stream = BytesIO()
        workbook.save(file_stream)
        file_stream.seek(0)
        file_content = base64.b64encode(file_stream.read())
        file_stream.close()

        attachment = self.env['ir.attachment'].create({
            'name': 'Daily_Sales_Report.xls',
            'type': 'binary',
            'datas': file_content,
            'mimetype': 'application/x-excel'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'new'
        }
