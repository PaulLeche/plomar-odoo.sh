# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
import io
from odoo.tools.misc import formatLang, format_date, xlsxwriter
from datetime import datetime


class AccountReport(models.Model):
    _inherit = 'account.report'
    _description = "Accounting Report"


    def _init_options_buttons(self, options, previous_options=None):
        if self.id == self.env.ref('account_reports.general_ledger_report').id:
            options['buttons'] = [
                {'name': _('PDF'), 'sequence': 10, 'action': 'export_file', 'action_param': 'export_to_pdf', 'file_export_type': _('PDF'), 'branch_allowed': True},
                {'name': _('XLSX'), 'sequence': 20, 'action': 'export_file', 'action_param': 'export_to_xlsx', 'file_export_type': _('XLSX'), 'branch_allowed': True},
                {'name': _('Save'), 'sequence': 100, 'action': 'open_report_export_wizard'},
                {'name': _('LIBRO MAYOR XLSX'), 'sequence': 20, 'action': 'export_file', 'action_param': 'export_to_xlsx_extends', 'file_export_type': _('LIBRO MAYOR XLSX'), 'branch_allowed': True},
                {'name': _('LIBRO MAYOR RESUMEN XLSX'), 'sequence': 20, 'action': 'export_file', 'action_param': 'export_to_xlsx_extends_r', 'file_export_type': _('LIBRO MAYOR RESUMEN XLSX'), 'branch_allowed': True},
            ]
        else:
            options['buttons'] = [
                {'name': _('PDF'), 'sequence': 10, 'action': 'export_file', 'action_param': 'export_to_pdf', 'file_export_type': _('PDF'), 'branch_allowed': True},
                {'name': _('XLSX'), 'sequence': 20, 'action': 'export_file', 'action_param': 'export_to_xlsx', 'file_export_type': _('XLSX'), 'branch_allowed': True},
                {'name': _('Save'), 'sequence': 100, 'action': 'open_report_export_wizard'},
             ]


    # def open_wizard_general_ledger(self, options):
    #     self.ensure_one()
    #     new_context = {
    #         **self._context,
    #         'account_report_generation_options': options,
    #         'default_report_id': self.id,
    #     }
    #     view_id = self.env['ir.model.data']._xmlid_to_res_id('general_ledger_by_dates.wizard_general_ledger')
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _("Libro Mayor"),
    #         'view_mode': 'form',
    #         'res_model': 'wizard.general.ledger',
    #         'views': [[view_id, 'form']],
    #         'target': 'new',
    #         'context': {
    #             'default_options': new_context,
    #         }
    #     }
    # def mayor_book_xls(self, options):
    #     print_options = self.get_options(previous_options={**options, 'export_mode': 'print'})
    #     print_mode_self = self.with_context(no_format=True)
    #     # options['unfold_all'] = True
    #     lines = self._filter_out_folded_children(print_mode_self._get_lines(options))

        # for line in lines:
        #     if type(line["id"]) == str:
        #         if "account_" in line["id"]:
        #             acc_id = int(line["id"][8:])

        # lines = self._get_lines(options)
        # x= lines
    def export_to_xlsx_extends(self, options, response=None):
        self.ensure_one()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {
            'in_memory': True,
            'strings_to_formulas': False,
        })

        print_options = self.get_options(previous_options={**options, 'export_mode': 'print'})
        if print_options['sections']:
            reports_to_print = self.env['account.report'].browse([section['id'] for section in print_options['sections']])
        else:
            reports_to_print = self

        reports_options = []
        for report in reports_to_print:
            report_options = report.get_options(previous_options={**print_options, 'selected_section_id': report.id})
            reports_options.append(report_options)
            report._inject_report_into_xlsx_sheet_extends(report_options, workbook, workbook.add_worksheet(report.name[:31]))

        self._add_options_xlsx_sheet(workbook, reports_options)

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()

        return {
            'file_name': self.get_default_report_filename(options, 'xlsx'),
            'file_content': generated_file,
            'file_type': 'xlsx',
        }

    def export_to_xlsx_extends_r(self, options, response=None):
        self.ensure_one()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {
            'in_memory': True,
            'strings_to_formulas': False,
        })

        print_options = self.get_options(previous_options={**options, 'export_mode': 'print'})
        if print_options['sections']:
            reports_to_print = self.env['account.report'].browse([section['id'] for section in print_options['sections']])
        else:
            reports_to_print = self

        reports_options = []
        for report in reports_to_print:
            report_options = report.get_options(previous_options={**print_options, 'selected_section_id': report.id})
            reports_options.append(report_options)
            report._inject_report_into_xlsx_sheet_extends_r(report_options, workbook, workbook.add_worksheet(report.name[:31]))

        self._add_options_xlsx_sheet(workbook, reports_options)

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()

        return {
            'file_name': 'libro_mayor_resumen',
            'file_content': generated_file,
            'file_type': 'xlsx',
        }

    def _inject_report_into_xlsx_sheet_extends(self, options, workbook, sheet):
        def write_with_colspan(sheet, x, y, value, colspan, style):
            if colspan == 1:
                sheet.write(y, x, value, style)
            else:
                sheet.merge_range(y, x, y, x + colspan - 1, value, style)

        date_default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
        level_0_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#666666'})
        level_1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#666666'})
        level_2_col1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_2_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_2_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_3_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        level_3_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_3_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        bold = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter','border': 1, })
        title_style_total = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2,'bg_color': '#BDD7EE'})
        title_style_header_account = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'bg_color': '#F2F2F2'})
        title_style_header_group = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'bg_color': '#FFD700'})


        print_mode_self = self.with_context(no_format=True)
        lines = self._filter_out_folded_children(print_mode_self._get_lines(options))

        # For reports with lines generated for accounts, the account name and codes are shown in a single column.
        # To help user post-process the report if they need, we should in such a case split the account name and code in two columns.
        account_lines_split_names = {}
        for line in lines:
            line_model = self._get_model_info_from_id(line['id'])[0]
            if line_model == 'account.account':
                # Reuse the _split_code_name to split the name and code in two values.
                account_lines_split_names[line['id']] = self.env['account.account']._split_code_name(line['name'])

        # Set the first column width to 50.
        # If we have account lines and split the name and code in two columns, we will also set the second column.
        if len(account_lines_split_names) > 0:
            sheet.set_column(0, 0, 11)
            sheet.set_column(1, 1, 50)
        else:
            sheet.set_column(0, 0, 50)

        original_x_offset = 1 if len(account_lines_split_names) > 0 else 0

        y_offset = 0
        # 1 and not 0 to leave space for the line name. original_x_offset allows making place for the code column if needed.
        x_offset = original_x_offset + 1

        # Add headers.
        # For this, iterate in the same way as done in main_table_header template
        column_headers_render_data = self._get_column_headers_render_data(options)
        for header_level_index, header_level in enumerate(options['column_headers']):
            for header_to_render in header_level * column_headers_render_data['level_repetitions'][header_level_index]:
                colspan = header_to_render.get('colspan', column_headers_render_data['level_colspan'][header_level_index])
                write_with_colspan(sheet, x_offset, y_offset, header_to_render.get('name', ''), colspan, title_style)
                x_offset += colspan
            if options['show_growth_comparison']:
                write_with_colspan(sheet, x_offset, y_offset, '%', 1, title_style)
            y_offset += 1
            x_offset = original_x_offset + 1

        for subheader in column_headers_render_data['custom_subheaders']:
            colspan = subheader.get('colspan', 1)
            write_with_colspan(sheet, x_offset, y_offset, subheader.get('name', ''), colspan, title_style)
            x_offset += colspan
        y_offset += 1
        x_offset = original_x_offset + 1
        # columnas que se necesita 2 al 8
        x2 = 0
        x3 = 0
        x4 = 0
        x5 = 0
        x6 = 0
        x7 = 0
        x8 = 0
        for column in options['columns']:
            colspan = column.get('colspan', 1)
            # write_with_colspan(sheet, x_offset, y_offset, column.get('name', ''), colspan, title_style)
            column_xls = column.get('name', '')
            if column_xls == 'Fecha de factura':
                x2 = x_offset
            elif column_xls == 'Comunicación':
                x3 = x_offset
            elif column_xls == 'Contacto':
                x4 = x_offset
            elif column_xls == 'Divisa':
                x5 = x_offset
            elif column_xls == 'Debe  ':
                x6 = x_offset
            elif column_xls == 'Haber ':
                x7 = x_offset
            elif column_xls == 'Balance':
                x8 = x_offset
            x_offset += colspan
        y_offset += 1

        if options.get('order_column'):
            lines = self.sort_lines(lines, options)

        # Add lines.
        dict_value = []
        nombre_cuenta = ''
        for y in range(0, len(lines)):
            line = {}
            level = lines[y].get('level')
            if lines[y].get('caret_options'):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style

            # write the first column, with a specific style to manage the indentation
            x_offset = original_x_offset + 1
            if lines[y]['id'] in account_lines_split_names:
                # cabeza de las cuentas
                code, name = account_lines_split_names[lines[y]['id']]
                line['nro_cuenta'] = code
                line['nombre_factura'] = name
                nombre_cuenta = name
                line['nombre_cuenta'] = nombre_cuenta
                # sheet.write(y + y_offset, x_offset - 2, code, col1_style)
                # sheet.write(y + y_offset, x_offset - 1, name, col1_style)
            else:
                if lines[y].get('parent_id') and lines[y]['parent_id'] in account_lines_split_names:
                    # columna 0 nro de cuenta
                    line['nro_cuenta'] = account_lines_split_names[lines[y]['parent_id']][0]
                    # sheet.write(y + y_offset, x_offset - 2, account_lines_split_names[lines[y]['parent_id']][0], col1_style)
                cell_type, cell_value = self._get_cell_type_value(lines[y])
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x_offset - 1, cell_value, date_default_col1_style)
                else:
                    # columna 1 nombre del asiento
                    line['nombre_factura'] = cell_value
                    line['nombre_cuenta'] = nombre_cuenta
                    # sheet.write(y + y_offset, x_offset - 1, cell_value, col1_style)

            #write all the remaining cells
            columns = lines[y]['columns']
            if options['show_growth_comparison'] and 'growth_comparison_data' in lines[y]:
                columns += [lines[y].get('growth_comparison_data')]
            for x, column in enumerate(columns, start=x_offset):
                cell_type, cell_value = self._get_cell_type_value(column)
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, date_default_style)
                else:
                    # resto de las columnas 2 al 8
                    if x == x2:
                        line['fecha_factura'] = cell_value
                    elif x == x3:
                        line['comunicacion'] = cell_value
                    elif x == x4:
                        line['contacto'] = cell_value
                    # elif x == 4:
                    #     line['contacto'] = cell_value
                    elif x == x5:
                        line['divisa'] = 0.0 if cell_value == '' else cell_value
                    elif x == x6:
                        line['debe'] = cell_value
                    elif x == x7:
                        line['haber'] = cell_value
                    elif x == x8:
                        line['balance'] = cell_value
                    # sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, style)
                if x3 == 0:
                    line['comunicacion'] = ''
                if x4 == 0:
                    line['contacto'] = ''
                if x5 == 0:
                    line['divisa'] = 0.0
                if x6 == 0:
                    line['debe'] = 0.0
                if x7 == 0:
                    line['haber'] = 0.0
                if x8 == 0:
                    line['balance'] = 0.0

            dict_value.append(line)

        dict_final = []
        for filter in dict_value:
            if filter.get('fecha_factura', '') != '':
                company_id = self.env.company
                account_id = self.env['account.account'].search([
                    ('code', '=', filter.get('nro_cuenta')),
                    ('company_id', '=', company_id.id)], limit=1)
                id = account_id.id
                if account_id.group_id:
                    grupo_cuenta = account_id.group_id.name
                    code_grupo_cuenta = account_id.group_id.code_prefix_start
                else:
                    grupo_cuenta = 'Sin grupo de cuenta'
                    code_grupo_cuenta = 'Sin codigo'
                line_filter = {
                    'grupo_cuenta': grupo_cuenta,
                    'code_grupo_cuenta': code_grupo_cuenta,
                    'nivel_group': '1',
                    'account_id': id,
                    'nro_cuenta': filter.get('nro_cuenta'),
                    'nombre_factura': filter.get('nombre_factura'),
                    'nombre_cuenta': filter.get('nombre_cuenta'),
                    'nivel_cuenta': '1',
                    'fecha_factura': filter.get('fecha_factura'),
                    'comunicacion': filter.get('comunicacion'),
                    'contacto': filter.get('contacto'),
                    'divisa': filter.get('divisa'),
                    'debe': filter.get('debe'),
                    'haber': filter.get('haber'),
                    'balance': filter.get('balance')
                }
                dict_final.append(line_filter)
        sorted_data = sorted(dict_final, key=lambda d: ((datetime.strptime(d['fecha_factura'],'%d/%m/%Y')), d['grupo_cuenta'],d['nombre_cuenta']))
        total_grupo_cuenta = self.add_summary_dict_group_account(sorted_data)
        total_numero_cuenta = self.add_summary_dict(sorted_data)
        sorted_data = self.uniondict(sorted_data, total_grupo_cuenta, total_numero_cuenta)
        sorted_data = sorted(sorted_data,key=lambda d: ((datetime.strptime(d['fecha_factura'], '%d/%m/%Y')), d['grupo_cuenta'], d['nivel_group'], d['nro_cuenta'], d['nivel_cuenta']))
        # x= sorted_data
        # SIZE OF COLUMNS

        # WIDTH
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 40)
        sheet.set_column('D:D', 50)
        sheet.set_column('E:E', 50)
        sheet.set_column('F:F', 25)
        sheet.set_column('G:G', 25)
        sheet.set_column('H:H', 25)
        sheet.set_column('I:I', 25)
        # SET MENU
        sheet.write('A3', 'Fecha de Factura ', bold)
        sheet.write('B3', 'Cuenta', bold)
        sheet.write('C3', 'Cuenta', bold)
        sheet.write('D3', 'Comunicación', bold)
        sheet.write('E3', 'Contacto', bold)
        sheet.write('F3', 'Divisa', bold)
        sheet.write('G3', 'Debe',bold)
        sheet.write('H3', 'Haber', bold)
        sheet.write('I3', 'Balance', bold)
        row_p = 3
        column_p = 0
        if sorted_data:
            # account1 = None
            fecha_factura1 = None
            divisa = 0.0
            debe = 0.0
            haber = 0.0
            balance = 0.0
            for line in sorted_data:
                fecha_factura2 = line.get('fecha_factura')
                if fecha_factura2 != fecha_factura1 and fecha_factura1:
                    sheet.merge_range(row_p, column_p, row_p, column_p + 4, 'TOTAL ' + fecha_factura1.upper(), title_style_total)
                    sheet.write(row_p, column_p + 5, '{0:,.2f}'.format(divisa), title_style_total)
                    sheet.write(row_p, column_p + 6, '{0:,.2f}'.format(debe), title_style_total)
                    sheet.write(row_p, column_p + 7, '{0:,.2f}'.format(haber), title_style_total)
                    sheet.write(row_p, column_p + 8, '{0:,.2f}'.format(balance), title_style_total)
                    divisa = 0.0
                    debe = 0.0
                    haber = 0.0
                    balance = 0.0
                    row_p += 1
                fecha_factura1 = line.get('fecha_factura')
                if line.get('nivel_group') == '1' and line.get('nivel_cuenta') == '1':
                    # account1 = line.get('nro_cuenta')
                    divisa += line.get('divisa')
                    debe += line.get('debe')
                    haber += line.get('haber')
                    balance += line.get('balance')

                sheet.write(row_p, column_p, line.get('fecha_factura'), style)
                if line.get('nivel_group') == '0' and line.get('nivel_cuenta') == '1':
                    sheet.write(row_p, column_p + 1, line.get('nro_cuenta'), title_style_header_group)
                    sheet.write(row_p, column_p + 2, line.get('nombre_factura'), title_style_header_group)
                else:
                    if line.get('nivel_group') == '1' and line.get('nivel_cuenta') == '0':
                        sheet.write(row_p, column_p + 1, line.get('nro_cuenta'), title_style_header_account)
                        sheet.write(row_p, column_p + 2, line.get('nombre_factura'), title_style_header_account)
                    else:
                        sheet.write(row_p, column_p + 1, line.get('nro_cuenta'), style)
                        sheet.write(row_p, column_p + 2, line.get('nombre_factura'), style)
                sheet.write(row_p, column_p + 3, line.get('comunicacion') if line.get('comunicacion') != '0' else '', style)
                sheet.write(row_p, column_p + 4, line.get('contacto'), style)
                sheet.write(row_p, column_p + 5, '{0:,.2f}'.format(line.get('divisa')), style)
                sheet.write(row_p, column_p + 6, '{0:,.2f}'.format(line.get('debe')), style)
                sheet.write(row_p, column_p + 7, '{0:,.2f}'.format(line.get('haber')), style)
                sheet.write(row_p, column_p + 8, '{0:,.2f}'.format(line.get('balance')), style)
                row_p += 1

            if fecha_factura1:
                sheet.merge_range(row_p, column_p, row_p, column_p + 4, 'TOTAL ' + fecha_factura1.upper(), title_style_total)
                sheet.write(row_p, column_p + 5, '{0:,.2f}'.format(divisa), title_style_total)
                sheet.write(row_p, column_p + 6, '{0:,.2f}'.format(debe), title_style_total)
                sheet.write(row_p, column_p + 7, '{0:,.2f}'.format(haber), title_style_total)
                sheet.write(row_p, column_p + 8, '{0:,.2f}'.format(balance), title_style_total)

    def _inject_report_into_xlsx_sheet_extends_r(self, options, workbook, sheet):
        def write_with_colspan(sheet, x, y, value, colspan, style):
            if colspan == 1:
                sheet.write(y, x, value, style)
            else:
                sheet.merge_range(y, x, y, x + colspan - 1, value, style)

        date_default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
        level_0_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#666666'})
        level_1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#666666'})
        level_2_col1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_2_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_2_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_3_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        level_3_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_3_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        bold = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter','border': 1, })
        title_style_total = workbook.add_format({'font_name': 'Arial', 'align': 'center', 'bold': True, 'bottom': 2,'bg_color': '#BDD7EE'})
        title_style_header_account = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'bg_color': '#F2F2F2'})
        title_style_header_group = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2, 'bg_color': '#FFD700'})


        print_mode_self = self.with_context(no_format=True)
        lines = self._filter_out_folded_children(print_mode_self._get_lines(options))

        # For reports with lines generated for accounts, the account name and codes are shown in a single column.
        # To help user post-process the report if they need, we should in such a case split the account name and code in two columns.
        account_lines_split_names = {}
        for line in lines:
            line_model = self._get_model_info_from_id(line['id'])[0]
            if line_model == 'account.account':
                # Reuse the _split_code_name to split the name and code in two values.
                account_lines_split_names[line['id']] = self.env['account.account']._split_code_name(line['name'])

        # Set the first column width to 50.
        # If we have account lines and split the name and code in two columns, we will also set the second column.
        if len(account_lines_split_names) > 0:
            sheet.set_column(0, 0, 11)
            sheet.set_column(1, 1, 50)
        else:
            sheet.set_column(0, 0, 50)

        original_x_offset = 1 if len(account_lines_split_names) > 0 else 0

        y_offset = 0
        # 1 and not 0 to leave space for the line name. original_x_offset allows making place for the code column if needed.
        x_offset = original_x_offset + 1

        # Add headers.
        # For this, iterate in the same way as done in main_table_header template
        column_headers_render_data = self._get_column_headers_render_data(options)
        for header_level_index, header_level in enumerate(options['column_headers']):
            for header_to_render in header_level * column_headers_render_data['level_repetitions'][header_level_index]:
                colspan = header_to_render.get('colspan', column_headers_render_data['level_colspan'][header_level_index])
                write_with_colspan(sheet, x_offset, y_offset, header_to_render.get('name', ''), colspan, title_style)
                x_offset += colspan
            if options['show_growth_comparison']:
                write_with_colspan(sheet, x_offset, y_offset, '%', 1, title_style)
            y_offset += 1
            x_offset = original_x_offset + 1

        for subheader in column_headers_render_data['custom_subheaders']:
            colspan = subheader.get('colspan', 1)
            write_with_colspan(sheet, x_offset, y_offset, subheader.get('name', ''), colspan, title_style)
            x_offset += colspan
        y_offset += 1
        x_offset = original_x_offset + 1
        # columnas que se necesita 2 al 8
        x2 = 0
        x3 = 0
        x4 = 0
        x5 = 0
        x6 = 0
        x7 = 0
        x8 = 0
        for column in options['columns']:
            colspan = column.get('colspan', 1)
            # write_with_colspan(sheet, x_offset, y_offset, column.get('name', ''), colspan, title_style)
            column_xls = column.get('name', '')
            if column_xls == 'Fecha de factura':
                x2 = x_offset
            elif column_xls == 'Comunicación':
                x3 = x_offset
            elif column_xls == 'Contacto':
                x4 = x_offset
            elif column_xls == 'Divisa':
                x5 = x_offset
            elif column_xls == 'Debe  ':
                x6 = x_offset
            elif column_xls == 'Haber ':
                x7 = x_offset
            elif column_xls == 'Balance':
                x8 = x_offset
            x_offset += colspan
        y_offset += 1

        if options.get('order_column'):
            lines = self.sort_lines(lines, options)

        # Add lines.
        dict_value = []
        nombre_cuenta = ''
        for y in range(0, len(lines)):
            line = {}
            level = lines[y].get('level')
            if lines[y].get('caret_options'):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style

            # write the first column, with a specific style to manage the indentation
            x_offset = original_x_offset + 1
            if lines[y]['id'] in account_lines_split_names:
                # cabeza de las cuentas
                code, name = account_lines_split_names[lines[y]['id']]
                line['nro_cuenta'] = code
                line['nombre_factura'] = name
                nombre_cuenta = name
                line['nombre_cuenta'] = nombre_cuenta
                # sheet.write(y + y_offset, x_offset - 2, code, col1_style)
                # sheet.write(y + y_offset, x_offset - 1, name, col1_style)
            else:
                if lines[y].get('parent_id') and lines[y]['parent_id'] in account_lines_split_names:
                    # columna 0 nro de cuenta
                    line['nro_cuenta'] = account_lines_split_names[lines[y]['parent_id']][0]
                    # sheet.write(y + y_offset, x_offset - 2, account_lines_split_names[lines[y]['parent_id']][0], col1_style)
                cell_type, cell_value = self._get_cell_type_value(lines[y])
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x_offset - 1, cell_value, date_default_col1_style)
                else:
                    # columna 1 nombre del asiento
                    line['nombre_factura'] = cell_value
                    line['nombre_cuenta'] = nombre_cuenta
                    # sheet.write(y + y_offset, x_offset - 1, cell_value, col1_style)

            #write all the remaining cells
            columns = lines[y]['columns']
            if options['show_growth_comparison'] and 'growth_comparison_data' in lines[y]:
                columns += [lines[y].get('growth_comparison_data')]
            for x, column in enumerate(columns, start=x_offset):
                cell_type, cell_value = self._get_cell_type_value(column)
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, date_default_style)
                else:
                    # resto de las columnas 2 al 8
                    if x == x2:
                        line['fecha_factura'] = cell_value
                    elif x == x3:
                        line['comunicacion'] = cell_value
                    elif x == x4:
                        line['contacto'] = cell_value
                    # elif x == 4:
                    #     line['contacto'] = cell_value
                    elif x == x5:
                        line['divisa'] = 0.0 if cell_value == '' else cell_value
                    elif x == x6:
                        line['debe'] = cell_value
                    elif x == x7:
                        line['haber'] = cell_value
                    elif x == x8:
                        line['balance'] = cell_value
                    # sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, style)
                if x3 == 0:
                    line['comunicacion'] = ''
                if x4 == 0:
                    line['contacto'] = ''
                if x5 == 0:
                    line['divisa'] = 0.0
                if x6 == 0:
                    line['debe'] = 0.0
                if x7 == 0:
                    line['haber'] = 0.0
                if x8 == 0:
                    line['balance'] = 0.0

            dict_value.append(line)

        dict_final = []
        for filter in dict_value:
            if filter.get('fecha_factura', '') != '':
                company_id = self.env.company
                account_id = self.env['account.account'].search([
                    ('code', '=', filter.get('nro_cuenta')),
                    ('company_id', '=', company_id.id)], limit=1)
                id = account_id.id
                if account_id.group_id:
                    grupo_cuenta = account_id.group_id.name
                    code_grupo_cuenta = account_id.group_id.code_prefix_start
                else:
                    grupo_cuenta = 'Sin grupo de cuenta'
                    code_grupo_cuenta = 'Sin codigo'
                line_filter = {
                    'grupo_cuenta': grupo_cuenta,
                    'code_grupo_cuenta': code_grupo_cuenta,
                    'nivel_group': '1',
                    'account_id': id,
                    'nro_cuenta': filter.get('nro_cuenta'),
                    'nombre_factura': filter.get('nombre_factura'),
                    'nombre_cuenta': filter.get('nombre_cuenta'),
                    'nivel_cuenta': '1',
                    'fecha_factura': filter.get('fecha_factura'),
                    'comunicacion': filter.get('comunicacion'),
                    'contacto': filter.get('contacto'),
                    'divisa': filter.get('divisa'),
                    'debe': filter.get('debe'),
                    'haber': filter.get('haber'),
                    'balance': filter.get('balance')
                }
                dict_final.append(line_filter)
        sorted_data = sorted(dict_final, key=lambda d: ((datetime.strptime(d['fecha_factura'],'%d/%m/%Y')), d['grupo_cuenta'],d['nombre_cuenta']))
        total_grupo_cuenta = self.add_summary_dict_group_account(sorted_data)
        total_numero_cuenta = self.add_summary_dict(sorted_data)
        sorted_data = self.uniondict(sorted_data, total_grupo_cuenta, total_numero_cuenta)
        sorted_data = sorted(sorted_data,key=lambda d: ((datetime.strptime(d['fecha_factura'], '%d/%m/%Y')), d['grupo_cuenta'], d['nivel_group'], d['nro_cuenta'], d['nivel_cuenta']))
        # x= sorted_data
        # SIZE OF COLUMNS

        # WIDTH
        # sheet.set_column('A:A', 20)
        # sheet.set_column('B:B', 20)
        # sheet.set_column('C:C', 40)
        # sheet.set_column('D:D', 50)
        # sheet.set_column('E:E', 50)
        # sheet.set_column('F:F', 25)
        # sheet.set_column('G:G', 25)
        # sheet.set_column('H:H', 25)
        # sheet.set_column('I:I', 25)

        sheet.set_column('A:A', 40)
        sheet.set_column('B:B', 40)
        sheet.set_column('C:C', 25)
        sheet.set_column('D:D', 25)
        sheet.set_column('E:E', 25)
        sheet.set_column('F:F', 25)

        # SET MENU
        sheet.write('A3', 'Fecha de Factura ', bold)
        # sheet.write('B3', 'Cuenta', bold)
        # sheet.write('C3', 'Cuenta', bold)
        sheet.write('B3', 'Concepto', bold)
        # sheet.write('E3', 'Contacto', bold)
        sheet.write('C3', 'Divisa', bold)
        sheet.write('D3', 'Debe',bold)
        sheet.write('E3', 'Haber', bold)
        sheet.write('F3', 'Balance', bold)
        row_p = 3
        column_p = 0
        if sorted_data:
            # account1 = None
            fecha_factura1 = None
            divisa = 0.0
            debe = 0.0
            haber = 0.0
            balance = 0.0
            for line in sorted_data:
                fecha_factura2 = line.get('fecha_factura')
                if fecha_factura2 != fecha_factura1 and fecha_factura1:
                    sheet.write(row_p, column_p, 'TOTAL ' + fecha_factura1.upper(), title_style_total)
                    sheet.write(row_p, column_p + 1, 'Movimiento del día', title_style_total)
                    sheet.write(row_p, column_p + 2, '{0:,.2f}'.format(divisa), title_style_total)
                    sheet.write(row_p, column_p + 3, '{0:,.2f}'.format(debe), title_style_total)
                    sheet.write(row_p, column_p + 4, '{0:,.2f}'.format(haber), title_style_total)
                    sheet.write(row_p, column_p + 5, '{0:,.2f}'.format(balance), title_style_total)
                    divisa = 0.0
                    debe = 0.0
                    haber = 0.0
                    balance = 0.0
                    row_p += 1
                fecha_factura1 = line.get('fecha_factura')
                if line.get('nivel_group') == '1' and line.get('nivel_cuenta') == '1':
                    # account1 = line.get('nro_cuenta')
                    divisa += line.get('divisa')
                    debe += line.get('debe')
                    haber += line.get('haber')
                    balance += line.get('balance')

                # sheet.write(row_p, column_p, line.get('fecha_factura'), style)
                # if line.get('nivel_group') == '0' and line.get('nivel_cuenta') == '1':
                #     sheet.write(row_p, column_p + 1, line.get('nro_cuenta'), title_style_header_group)
                #     sheet.write(row_p, column_p + 2, line.get('nombre_factura'), title_style_header_group)
                # else:
                #     if line.get('nivel_group') == '1' and line.get('nivel_cuenta') == '0':
                #         sheet.write(row_p, column_p + 1, line.get('nro_cuenta'), title_style_header_account)
                #         sheet.write(row_p, column_p + 2, line.get('nombre_factura'), title_style_header_account)
                #     else:
                #         sheet.write(row_p, column_p + 1, line.get('nro_cuenta'), style)
                #         sheet.write(row_p, column_p + 2, line.get('nombre_factura'), style)
                # sheet.write(row_p, column_p + 3, line.get('comunicacion') if line.get('comunicacion') != '0' else '', style)
                # sheet.write(row_p, column_p + 4, line.get('contacto'), style)
                # sheet.write(row_p, column_p + 5, '{0:,.2f}'.format(line.get('divisa')), style)
                # sheet.write(row_p, column_p + 6, '{0:,.2f}'.format(line.get('debe')), style)
                # sheet.write(row_p, column_p + 7, '{0:,.2f}'.format(line.get('haber')), style)
                # sheet.write(row_p, column_p + 8, '{0:,.2f}'.format(line.get('balance')), style)
                # row_p += 1

            if fecha_factura1:
                sheet.write(row_p, column_p, 'TOTAL ' + fecha_factura1.upper(), title_style_total)
                sheet.write(row_p, column_p + 1, 'Movimiento del día', title_style_total)
                sheet.write(row_p, column_p + 2, '{0:,.2f}'.format(divisa), title_style_total)
                sheet.write(row_p, column_p + 3, '{0:,.2f}'.format(debe), title_style_total)
                sheet.write(row_p, column_p + 4, '{0:,.2f}'.format(haber), title_style_total)
                sheet.write(row_p, column_p + 5, '{0:,.2f}'.format(balance), title_style_total)

    def add_summary_dict(self, sorted_data):
        dict_aux = []
        account1 = None
        account_name = ''
        fecha_factura = ''
        divisa = 0.0
        debe = 0.0
        haber = 0.0
        balance = 0.0
        for line in sorted_data:
            account2 = line.get('nro_cuenta')
            if account2 != account1 and account1:
                l = {
                    'grupo_cuenta': grupo_cuenta,
                    'code_grupo_cuenta': code_grupo_cuenta,
                    'nivel_group': '1',
                    'account_id': 0,
                    'nro_cuenta': account1,
                    'nombre_factura': account_name,
                    'nombre_cuenta': account_name,
                    'nivel_cuenta': '0',
                    'fecha_factura': fecha_factura,
                    'comunicacion': '',
                    'contacto': '',
                    'divisa': divisa,
                    'debe': debe,
                    'haber': haber,
                    'balance': balance,
                }
                dict_aux.append(l)
                divisa = 0.0
                debe = 0.0
                haber = 0.0
                balance = 0.0
            account1 = line.get('nro_cuenta')
            account_name = line.get('nombre_cuenta')
            fecha_factura = line.get('fecha_factura')
            grupo_cuenta = line.get('grupo_cuenta')
            code_grupo_cuenta = line.get('code_grupo_cuenta')
            debe += line.get('debe')
            haber += line.get('haber')
            balance += line.get('balance')
            if line.get('divisa') != '':
                divisa += line.get('divisa')
        if account1:
            l = {
                'grupo_cuenta': grupo_cuenta,
                'code_grupo_cuenta': code_grupo_cuenta,
                'nivel_group': '1',
                'account_id': 0,
                'nro_cuenta': account1,
                'nombre_factura': account_name,
                'nombre_cuenta': account_name,
                'nivel_cuenta': '0',
                'fecha_factura': fecha_factura,
                'comunicacion': '',
                'contacto': '',
                'divisa': divisa,
                'debe': debe,
                'haber': haber,
                'balance': balance,
            }
            dict_aux.append(l)
        total_account = []
        for aux in dict_aux:
            aux1 = {
                'grupo_cuenta': aux.get('grupo_cuenta'),
                'code_grupo_cuenta': aux.get('code_grupo_cuenta'),
                'nivel_group': aux.get('nivel_group'),
                'account_id': aux.get('account_id'),
                'nro_cuenta': aux.get('nro_cuenta'),
                'nombre_factura': aux.get('nombre_factura'),
                'nombre_cuenta': aux.get('nombre_cuenta'),
                'nivel_cuenta':  aux.get('nivel_cuenta'),
                'fecha_factura': aux.get('fecha_factura'),
                'comunicacion': '0',
                'contacto': aux.get('contacto'),
                'divisa': aux.get('divisa'),
                'debe': aux.get('debe'),
                'haber': aux.get('haber'),
                'balance': aux.get('balance')
            }
            total_account.append(aux1)
        return total_account

    def add_summary_dict_group_account(self, sorted_data):
        dict_aux = []
        account1 = None
        fecha_factura1 = None
        account_name = ''
        fecha_factura = ''
        divisa = 0.0
        debe = 0.0
        haber = 0.0
        balance = 0.0
        for line in sorted_data:
            account2 = line.get('grupo_cuenta')
            fecha_factura2 = line.get('fecha_factura')
            if (account2 != account1 or fecha_factura2 != fecha_factura1) and account1:
                l = {
                    'grupo_cuenta': account1,
                    'code_grupo_cuenta': code_grupo_cuenta,
                    'nivel_group': '0',
                    'account_id': 0,
                    'nro_cuenta': nro_cuenta,
                    'nombre_factura': account_name,
                    'nombre_cuenta': nombre_cuenta,
                    'nivel_cuenta': '1',
                    'fecha_factura': fecha_factura1,
                    'comunicacion': '',
                    'contacto': '',
                    'divisa': divisa,
                    'debe': debe,
                    'haber': haber,
                    'balance': balance,
                }
                dict_aux.append(l)
                divisa = 0.0
                debe = 0.0
                haber = 0.0
                balance = 0.0
            account1 = line.get('grupo_cuenta')
            code_grupo_cuenta = line.get('code_grupo_cuenta')
            nro_cuenta = line.get('code_grupo_cuenta')
            account_name = line.get('grupo_cuenta')
            nombre_cuenta = ''
            fecha_factura1 = line.get('fecha_factura')
            debe += line.get('debe')
            haber += line.get('haber')
            balance += line.get('balance')
            if line.get('divisa', '') != '':
                divisa += line.get('divisa')
        if account1:
            l = {
                'grupo_cuenta': account1,
                'code_grupo_cuenta': code_grupo_cuenta,
                'nivel_group': '0',
                'account_id': 0,
                'nro_cuenta': nro_cuenta,
                'nombre_factura': account_name,
                'nombre_cuenta': nombre_cuenta,
                'nivel_cuenta': '1',
                'fecha_factura': fecha_factura1,
                'comunicacion': '',
                'contacto': '',
                'divisa': divisa,
                'debe': debe,
                'haber': haber,
                'balance': balance,
            }
            dict_aux.append(l)
        dict_final = []
        for aux in dict_aux:
            aux1 = {
                'grupo_cuenta': aux.get('grupo_cuenta'),
                'code_grupo_cuenta': aux.get('code_grupo_cuenta'),
                'nivel_group': aux.get('nivel_group'),
                'account_id': aux.get('account_id'),
                'nro_cuenta': aux.get('nro_cuenta'),
                'nombre_factura': aux.get('nombre_factura'),
                'nombre_cuenta': aux.get('nombre_cuenta'),
                'nivel_cuenta': aux.get('nivel_cuenta'),
                'fecha_factura': aux.get('fecha_factura'),
                'comunicacion': aux.get('comunicacion'),
                'contacto': aux.get('contacto'),
                'divisa': aux.get('divisa'),
                'debe': aux.get('debe'),
                'haber': aux.get('haber'),
                'balance': aux.get('balance'),
            }
            dict_final.append(aux1)
        return dict_final


    def uniondict(self, sorted_data, total_grupo_cuenta, total_numero_cuenta):
        for dict1 in total_grupo_cuenta:
            line1 = {
                'grupo_cuenta': dict1.get('grupo_cuenta'),
                'code_grupo_cuenta': dict1.get('code_grupo_cuenta'),
                'nivel_group': dict1.get('nivel_group'),
                'account_id': dict1.get('account_id'),
                'nro_cuenta': dict1.get('nro_cuenta'),
                'nombre_factura': dict1.get('nombre_factura'),
                'nombre_cuenta': dict1.get('nombre_cuenta'),
                'nivel_cuenta': dict1.get('nivel_cuenta'),
                'fecha_factura': dict1.get('fecha_factura'),
                'comunicacion': dict1.get('comunicacion'),
                'contacto': dict1.get('contacto'),
                'divisa': dict1.get('divisa'),
                'debe': dict1.get('debe'),
                'haber': dict1.get('haber'),
                'balance': dict1.get('balance'),
            }
            sorted_data.append(line1)
        for dict2 in total_numero_cuenta:
            line2 = {
                'grupo_cuenta': dict2.get('grupo_cuenta'),
                'code_grupo_cuenta': dict2.get('code_grupo_cuenta'),
                'nivel_group': dict2.get('nivel_group'),
                'account_id': dict2.get('account_id'),
                'nro_cuenta': dict2.get('nro_cuenta'),
                'nombre_factura': dict2.get('nombre_factura'),
                'nombre_cuenta': dict2.get('nombre_cuenta'),
                'nivel_cuenta': dict2.get('nivel_cuenta'),
                'fecha_factura': dict2.get('fecha_factura'),
                'comunicacion': dict2.get('comunicacion'),
                'contacto': dict2.get('contacto'),
                'divisa': dict2.get('divisa'),
                'debe': dict2.get('debe'),
                'haber': dict2.get('haber'),
                'balance': dict2.get('balance'),
            }
            sorted_data.append(line2)
        return sorted_data




