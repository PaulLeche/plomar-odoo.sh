# -*- encoding: utf-8 -*-


from odoo import fields, models, api
from datetime import datetime, time

class ReportPlanillaF983(models.AbstractModel):
    _name = 'report.advanced_reports.report_planilla_f983'
    _description = 'report advanced_reports report_planilla_f983'


    def get_uom_id_name(self, product_id):
        uom_name = ''
        if product_id:
            if product_id.uom_id and product_id.uom_id.name:
                uom_name = product_id.uom_id.name
        return uom_name
    def get_category_bien(self, product_id):
        category_bien = ''
        if product_id and product_id.categ_id:
            if product_id.categ_id.parent_id and product_id.categ_id.parent_id.name:
                if 'productos terminados' in product_id.categ_id.parent_id.name.lower():
                    category_bien = '01- productos terminados'
                elif 'productos en proceso' in product_id.categ_id.parent_id.name.lower():
                    category_bien = '02- productos en procesos'
                elif 'materia prima' in product_id.categ_id.parent_id.name.lower():
                    category_bien = '03- Materia Prima'
                elif 'bien para la construcción' in product_id.categ_id.parent_id.name.lower():
                    category_bien = ' 04- Bien para la construcción'
        return category_bien

    def get_reference_books(self, product_id):
        reference_books = ''
        if product_id and product_id.reference_books:
            if product_id.reference_books == 'costs':
                reference_books = '01- Costos'
            elif product_id.reference_books == 'retaceos':
                reference_books = '02- Retaceos'
            elif product_id.reference_books == 'local':
                reference_books = '03- Compras Locales'
        return reference_books


    def get_qty_available_standard_price(self, product_id, date_to_datetime, company_id):
        qty_available = 0.0
        standard_price = 0.0
        valuation_ids = self.env['stock.valuation.layer'].search([('product_id', '=', product_id.id),
                                                              ('create_date', '<=', date_to_datetime),
                                                              ('company_id', '=', company_id.id)])
        if valuation_ids:
            value = sum(valuation.value for valuation in valuation_ids)
            qty_available = sum(valuation.quantity for valuation in valuation_ids)
            if qty_available == 0.0:
                standard_price = (valuation_ids.sorted(key=lambda v: v.create_date, reverse=True)[0]).unit_cost
            else:
                standard_price = value/qty_available
        else:
            qty_available = product_id.qty_available if product_id.qty_available else 0.0
            standard_price = product_id.standard_price if product_id.standard_price else 0.0

        return qty_available, standard_price





    def generate_records(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_from_datetime = datetime.combine(date_from, time.min)
        date_to = record_ids.date_to
        date_to_datetime = datetime.combine(date_to, time.max)
        company_id = record_ids.company_id
        product_template_ids = self.env['product.template'].search([('detailed_type', 'in', ['consu', 'product']),
                                                          ('create_date', '<=', date_to_datetime)], order='name')
        if product_template_ids:
            for product_template_id in product_template_ids:
                product_id = product_template_id.product_variant_id
                if product_template_id.detailed_type in ['consu']:
                    qty_available = product_id.qty_available if product_id.qty_available else 0.0
                    standard_price = product_id.standard_price if product_id.standard_price else 0.0
                else:
                    qty_available, standard_price = self.get_qty_available_standard_price(product_id, date_to_datetime, company_id)
                line = {
                    'product_name': product_id.name if product_id.name else '',
                    'ref_internal': product_id.default_code if product_id.default_code else '',
                    'uom_name': self.get_uom_id_name(product_id),
                    'qty_available': qty_available,
                    'standard_price': standard_price,
                    'cost_total': qty_available*standard_price,
                    'category_bien': self.get_category_bien(product_id),
                    'reference_books': self.get_reference_books(product_id),
                    'fiscal_exercise': date_to.year,

                }
                result.append(line)

        return result, totales




