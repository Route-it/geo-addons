# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning
from calendar import monthrange
import logging
import json
import locale
from datetime import date,datetime
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

	
class certification_plant(models.Model):
	_name = 'certification.plant'
	_order = 'name'
	_description = "Equipos de trabajo"
	
	_group_by_full = {'equipo'}
	
	name = fields.Char("Nombre")
	description = fields.Text("Descripcion")
	type = fields.Selection([("24","24hs"),("12","12hs")],string="Horas por dia",default="12")

	automatic_calculation_hours_by_month =  fields.Boolean("Calcular horas por mes automaticamente",default=True)
	
	hours_by_month = fields.Integer(string="Horas por mes",default=lambda self: self._set_hours_by_month())
	
	kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')
	
	hours_by_month2 = fields.Integer(compute="_set_hours_by_month")
	hours_by_month3 = fields.Integer(compute="_set_hours_by_month")
	hours_by_month4 = fields.Integer(compute="_set_hours_by_month")
	hours_by_month5 = fields.Integer(compute="_set_hours_by_month")
	hours_by_month6 = fields.Integer(compute="_set_hours_by_month")
	
	eficiencia1 = fields.Float(compute="_set_eficiencia")
	eficiencia2 = fields.Float(compute="_set_eficiencia")
	eficiencia3 = fields.Float(compute="_set_eficiencia")
	eficiencia4 = fields.Float(compute="_set_eficiencia")
	eficiencia5 = fields.Float(compute="_set_eficiencia") 
	eficiencia6 = fields.Float(compute="_set_eficiencia")
		
	#data.append({'label': _('Past'), 'value':0.0, 'type': 'past'})
	@api.one
	def _kanban_dashboard_graph(self):
		data = []
		
		now = datetime.now()
		for i in range(5,-1,-1):
			my_month = now - relativedelta(months=i)
			mes, eficiencia_mes = self._get_eficiencia_by_month(my_month)
			data.append({'label':mes,'value':eficiencia_mes})
		
		self.kanban_dashboard_graph = json.dumps([{'values': data}])
		
		return self.kanban_dashboard_graph


	def _get_eficiencia_by_month(self,my_month):
		loc = locale.getlocale(locale.LC_TIME)
		try:
			locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
		except: pass	

		mes = my_month.strftime('%B').capitalize()
		
		try:
			locale.setlocale(locale.LC_TIME, loc[0]+'.'+loc[1])	
		except: pass	
		
		coiled_tubing_time_losed_ids = self.env['certifications.coiled_tubing_time_losed'].search([('mes','=',mes),('equipo','=',self.id)])
		
		eficiencia = 0
		
		horas_operativas = 0
		horas_perdidas = 0
		for ct_tl in coiled_tubing_time_losed_ids:
			horas_operativas = horas_operativas + ct_tl.operating_hours
			horas_perdidas = horas_perdidas + ct_tl.time_losed_quantity
		
		
		hours_by_month = self._get_hours_by_month_for_month(my_month)
		#if ((horas_operativas-horas_perdidas)>0) & bool(hours_by_month):
			#eficiencia = round(((horas_operativas-horas_perdidas)/(hours_by_month*1.0))*100,1)
		if ((horas_operativas)>0) & bool(hours_by_month):
			eficiencia = round(((horas_operativas)/(hours_by_month*1.0))*100,1)
		return mes, eficiencia
	
	#@api.depends('equipo','operating_hours','certification_coiled_tubing_id.operating_hours','certification_coiled_tubing_id','time_losed_quantity')
	@api.depends('type','hours_by_month','automatic_calculation_hours_by_month')
	@api.one
	def _set_eficiencia(self):
		now = datetime.now()
		switcher = {}
		for i in range(6):
			my_month = now - relativedelta(months=i)
			switcher[i] = self._get_eficiencia_by_month(my_month)

		self.eficiencia1 = switcher.get(0,0)[1]
		self.eficiencia2 = switcher.get(1,0)[1]
		self.eficiencia3 = switcher.get(2,0)[1]
		self.eficiencia4 = switcher.get(3,0)[1]
		self.eficiencia5 = switcher.get(4,0)[1]
		self.eficiencia6 = switcher.get(5,0)[1]
	

	# asigna un valor al inicio y luego no se toca a menos que sea modificado en la vista.
	# default=lambda self: self._get_last_exchange_date()
	
	# computa el valor cada vez, no permite modificacion 
	#compute='set_total_value'	

	# computa el valor cada vez ¿permite modificacion? 
	#compute='set_total_value'	+ store= true
	def _get_hours_by_month_for_month(self,date_param,type_param=None):
		hours_by_month = False
		if self.automatic_calculation_hours_by_month:
			weekday, days_in_month = monthrange(date_param.year, date_param.month)
			my_type = type_param if type_param is not None else self.type
			hours_by_month = int(my_type) * days_in_month if (my_type) else 0
		if not bool(hours_by_month): 
			return self.hours_by_month
		return hours_by_month
		
	@api.onchange('type','automatic_calculation_hours_by_month')
	@api.one
	def _set_hours_by_month(self,type=None):
		now = date.today()
		self.hours_by_month = self._get_hours_by_month_for_month(now,type)
		self.hours_by_month2 = self._get_hours_by_month_for_month(now - relativedelta(months=1),type)
		self.hours_by_month3 = self._get_hours_by_month_for_month(now - relativedelta(months=2),type)
		self.hours_by_month4 = self._get_hours_by_month_for_month(now - relativedelta(months=3),type)
		self.hours_by_month5 = self._get_hours_by_month_for_month(now - relativedelta(months=4),type)
		self.hours_by_month6 = self._get_hours_by_month_for_month(now - relativedelta(months=5),type)
		return self.hours_by_month 
		
	

	@api.one
	@api.constrains('name')
	def validate_name(self):
		if not (bool(self.name) & (len(self.name)>3)):
			raise ValidationError("El nombre debe tener al menos 3 caracteres")
			
	
	
	@api.one
	@api.constrains('name')
	def check_unique_name(self):
		records = self.env['certification.plant'].search([('name','=',self.name)])
		if len(records)>1:
			raise ValidationError("Ya existe un registro con ese nombre, verifique que este activo")
		
	@api.multi
	def write(self, vals):
		#if vals.get('hours_by_month') is None:
		#	vals['hours_by_month'] = 
		#self._set_hours_by_month(vals.get('type',None)) 
		
		res = super(certification_plant, self).write(vals)
		
		return res
