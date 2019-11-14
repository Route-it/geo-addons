# -*- coding: utf-8 -*-
# © 2012 Agile Business Group
# © 2012 Domsense srl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime
import locale
import operator
import os
import re
import time
import openerp.addons.web.http as openerpweb
import openerp.http as http
import openerp.tools as tools
import trml2pdf

from openerp.addons.web.controllers.main import ExcelExport
from openerp.addons.web.controllers.main import Export
from openerp.exceptions import UserError
from openerp.http import request
from openerp.http import request, serialize_exception as _serialize_exception, content_disposition
from openerp.tools.misc import str2bool, xlwt

from lxml  import etree
from cStringIO import StringIO
from xlwt import *


try:
    import json
except ImportError:
    import simplejson as json



def is_hidden_field(fieldname):
    if ((type(fieldname) == unicode) or (type(fieldname) == basestring)):
            return (fieldname.lower() in ('estado','parte'))

    

class ExportGeoPdf(Export):
    fmt = {
        'tag': 'pdf',
        'label': 'PDF',
        'error': None
    }
    
    @property
    def content_type(self):
        return 'application/pdf'
    
    def filename(self, base):
        return base + '.pdf'
    
    def from_data(self, uid, fields, rows, company_name):
        pageSize=[210.0,297.0]
        new_doc = etree.Element("report")
        config = etree.SubElement(new_doc, 'config')
        def _append_node(name, text):
            n = etree.SubElement(config, name)
            n.text = text
        _append_node('date', time.strftime(str(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y'))))
        _append_node('PageSize', '%.2fmm,%.2fmm' % tuple(pageSize))
        _append_node('PageWidth', '%.2f' % (pageSize[0] * 2.8346,))
        _append_node('PageHeight', '%.2f' %(pageSize[1] * 2.8346,))
        _append_node('PageFormat', 'a4')
        _append_node('header-date', time.strftime(str(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y'))))
        _append_node('company', company_name)
        l = []
        t = 0
        temp = []
        tsum = []
        skip_index = []
        header = etree.SubElement(new_doc, 'header')
        i = 0
        for f in fields:
            if f.get('header_data_id', False):
                value = f.get('header_name', "")
                field = etree.SubElement(header, 'field')
                field.text = tools.ustr(value)
            else:
                skip_index.append(i)
            i += 1
        lines = etree.SubElement(new_doc, 'lines')
        for row_lines in rows:
            node_line = etree.SubElement(lines, 'row')
            j = 0
            for row in row_lines:
                if not j in skip_index:
                    para = "yes"
                    tree = "no"
                    value = row.get('data', '')
                    if row.get('bold', False):
                        para = "group"
                    if row.get('number', False):
                        tree = "float"
                    col = etree.SubElement(node_line, 'col', para=para, tree=tree)
                    col.text = tools.ustr(value)
                j += 1
        transform = etree.XSLT(
            etree.parse(os.path.join(tools.config['root_path'],
                                     'addons/base/report/custom_new.xsl')))
        rml = etree.tostring(transform(new_doc))
        self.obj = trml2pdf.parseNode(rml, title='Printscreen')
        return self.obj

class GeoPdfExport(ExportGeoPdf):
    _cp_path = '/web/export/geo_pdf_export'
    
    @openerpweb.route(_cp_path)
    def index(self, req, data, token):
        data = json.loads(data)
        uid = data.get('uid', False)
        model = data.get('model', False)
        Model = request.session.model(model)
        
        headers_fields =  data.get('headers', [])
        headers_to_remove = []
        for field_name in headers_fields:
            if is_hidden_field(field_name['header_name']):
                print field_name['header_name'] + ' si' 
                field_name.pop('header_data_id',False)


        return req.make_response(self.from_data(uid, headers_fields, data.get('rows', []),
                                                data.get('company_name','')),
                                 headers=[('Content-Disposition',
                                           'attachment; filename=%s' %self.filename(model)),
                                          ('Content-Type', self.content_type)],
                                 cookies={'fileToken': bytes(token)})


class ExcelExportView(ExcelExport):
    """
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView, self).__getattribute__(name)
    """    


    def _get_aggregated_line(self, children, field_names, my_group):
        line = []
        group_array_ag = my_group.split(",")
        if len(group_array_ag) > 1:
            line.append(group_array_ag[1]+" ("+str(children[my_group]['datagroup']['length'])+")")
        else:
            line.append(my_group)
        for f in field_names:
            if f != 'Grupo':
                ag = children[my_group]['datagroup']['aggregates']
                #key_ag = ag.keys()[0]
                if f in ag.keys():
                    total = ag.get(f)
                    line.append(total)
                else:
                    line.append('')
        
        return line

    def _get_lines_aggregatted(self, children, field_names, Model, context, order):
        rows = []
        for my_group in children:
            if my_group == 'null':
                ids = children[my_group]['dataset']['ids']
                my_domain = children[my_group]['dataset']['domain']
                field_names.pop(0)
                ids = Model.search(my_domain, offset=0, limit=False, order=order, context=context)
                lines = Model.export_data(ids, field_names, self.raw_data, context=context).get('datas', [])
                for l in lines:
                    l.insert(0,'')                
                rows.extend(lines)
                field_names.insert(0,'Grupo')

            else:    
                if (len(children[my_group]['children']) > 0):
                    print "muestra total y registros"
                    rows.append(self._get_aggregated_line(children, field_names, my_group))
                    rows.extend(self._get_lines_aggregatted(children[my_group]['children'], field_names, Model, context, order))
                elif (children[my_group]['records']['length'] > 0):
                    agg_domain = children[my_group]['datagroup']['domain']
                    ids = Model.search(agg_domain, offset=0, limit=False, order=order, context=context)
                    field_names.pop(0)
                    lines = Model.export_data(ids, field_names, self.raw_data, context=context).get('datas', [])
                    for l in lines:
                        l.insert(0,'')
                    rows.extend(lines)
                    field_names.insert(0,'Grupo')
                    print "muestra registros"
                else:
                    rows.append(self._get_aggregated_line(children, field_names, my_group))
                    print "muestra totales"
        
        return rows

    @http.route('/web/export/geo_xls_export', type='http', auth='user')
    def export_xls_view(self, data, token):
        params = json.loads(data)
        
        #params.get('context').get('group_by') ultimo nivel de agrupamiento
        
        model, fields, ids, domain, grouped, group_by, children,footer_eles = \
            operator.itemgetter('model', 'fields', 'ids', 'domain',
                                'grouped','group_by','children','footer_eles')(
                params)

        try:
            columns_headers = [val['label'].strip() for val in fields]
            field_names = map(operator.itemgetter('name'), fields)
        except:
            columns_headers = params.get('headers', [])
            field_names = fields
                            
        Model = request.session.model(model)
        context = dict(request.context or {}, **params.get('context', {}))
        order = context.get('order',False)

        
        if bool(grouped):
            #(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
            columns_headers.insert(0,'Grupo')
            field_names.insert(0,'Grupo')
            #groups = Model.read_group(domain, field_names, group_by, offset=0, limit=False, orderby=order, context=context,lazy=False)
            #extraer funcion recursiva llamandose con children para soportar grupos anidados.? 
            rows = self._get_lines_aggregatted( children, field_names, Model, context, order)
            
            field_names.pop(0)
            
        else:        
            if (len(ids)>0):
                domain.append(['id','in',ids])
        
            ids = Model.search(domain, offset=0, limit=False, order=order, context=context)

            rows = Model.export_data(ids, field_names, self.raw_data, context=context).get('datas',[]) 
        
        if len(footer_eles) >= 1:
            line = []
            for l in footer_eles:
                    if l.get('number'):
                        line.append(l.get('data'))                
            rows.append(line)
            print "con totales"

        return request.make_response(
            self.from_data_geo_xls(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    
    def _get_row_width(self, rows, fields):
        
        res = {}
        #me quedo con el width de las columnas
        for col, fieldname in enumerate(fields):
            res[fieldname] = len(fieldname)
        
        #busco el valor mas "ancho"
        for row_index, row in enumerate(rows):
            for col, fieldname in enumerate(fields):
                celda = row[col]
                length = 0
                if ((type(celda) == unicode) or (type(celda) == basestring)):
                    length = len(celda)
                elif (type(celda) == datetime.date):
                        length = len(celda.strftime('%d/%m/%Y'))
                elif type(celda) == datetime.datetime:
                        length = len(celda.strftime('%d/%m/%Y %H:%M:%S'))
                elif type(celda) == float:
                        length = len(str(round(celda,2)))
                        
                len_saved = res.get(fieldname)
                if length > len_saved:
                    res[fieldname] = length
        
        return res
    
    
    def from_data_geo_xls(self, fields, rows):
        if len(rows) > 65535:
            raise UserError(_('There are too many rows (%s rows, limit: 65535) to export as Excel 97-2003 (.xls) format. Consider splitting the export.') % len(rows))

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')

        bold_style = xlwt.easyxf('font: bold on;')
        aligment = xlwt.Formatting.Alignment()
        
        aligment.horz = 2 #Alignment.HORIZ_CENTER
        aligment.vert = 1 #Alignment.VERT_CENTER
        bold_style.alignment = aligment

        borders = xlwt.Borders()
        borders.bottom = Borders.THICK
        borders.top = Borders.THICK
        borders.left = Borders.THICK
        borders.right = Borders.THICK
        bold_style.borders = borders
        
        font = xlwt.Font()
        font.bold = True
        font.name = 'Arial'
        #font.height = 200 # por defecto son 10 puntos. 
        #font.colour_index = 23 #dark gray
        font.colour_index = 0 #Black http://www.excelsupersite.com/what-are-the-56-colorindex-colors-in-excel/
        bold_style.font = font
        #Letra de los títulos: En negrita Arial 10 , color negro. Pintar los títulos con ese celeste

        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = xlwt.Style.colour_map["light_turquoise"] 

        bold_style.pattern = pattern

        fields_width_dict = self._get_row_width(rows,fields)
                
        for i, fieldname in enumerate(fields):
            worksheet.write(0, i, fieldname, bold_style)
            if is_hidden_field(fieldname):
                worksheet.col(i).width = 0 
            else:
                worksheet.col(i).width = fields_width_dict.get(fieldname) * 300 #8000 # around 220 pixels

        base_style = xlwt.easyxf('align: wrap yes;font: colour black;')
        borders_cell = xlwt.Borders()
        borders_cell.left = Borders.THICK
        borders_cell.bottom = Borders.THIN
        borders_cell.right = Borders.THICK
        base_style.borders = borders_cell


        """
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='DD/MM/YYYY')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='DD/MM/YYYY HH:mm:SS')
        number_style = xlwt.easyxf('align: wrap yes', num_format_str='#,##0.00')
        integer_style = xlwt.easyxf('align: wrap yes', num_format_str='#0')
        """
        
        for row_index, row in enumerate(rows):
            for cell_index, cell_value in enumerate(row):
                cell_style = base_style
                cell_style.alignment = aligment 
                if isinstance(cell_value, basestring):
                    cell_value = re.sub("\r", " ", cell_value)
                elif isinstance(cell_value, datetime.datetime):
                    cell_style.num_format_str = 'DD/MM/YYYY HH:mm:SS'
                elif isinstance(cell_value, datetime.date):
                    cell_style.num_format_str = 'DD/MM/YYYY'
                elif isinstance(cell_value, float):
                    cell_style.num_format_str = '#,##0.00'
                elif isinstance(cell_value, int):
                    cell_style.num_format_str = '#0'

                if not isinstance(cell_value, unicode):
                    if str(cell_value).lower() == 'false':
                        cell_value = ''       
                worksheet.write(row_index + 1, cell_index, cell_value, cell_style)

        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return data

