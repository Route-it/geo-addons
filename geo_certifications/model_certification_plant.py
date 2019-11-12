# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning
from calendar import monthrange
import logging
import json
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
	
	
	eficiencia = fields.Float(string="Eficiencia",compute="_set_eficiencia")
	
	#data.append({'label': _('Past'), 'value':0.0, 'type': 'past'})
	@api.one
	def _kanban_dashboard_graph(self):
		data = []
		
		now = datetime.now()
		for i in range(6):
			my_month = now - relativedelta(months=i)
			mes = my_month.strftime('%B').capitalize()
			eficiencia_mes = self._get_eficiencia_by_month(mes)
			data.append({'label':mes,'value':eficiencia_mes})
		
		self.kanban_dashboard_graph = json.dumps([{'values': data}])
		
		return self.kanban_dashboard_graph


	kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')
	
	
	def _get_eficiencia_by_month(self,mes):
		coiled_tubing_time_losed_ids = self.env['certifications.coiled_tubing_time_losed'].search([('mes','=',mes),('equipo','=',self.id)])
		
		eficiencia = 0
		
		horas_operativas = 0
		horas_perdidas = 0
		for ct_tl in coiled_tubing_time_losed_ids:
			horas_operativas = horas_operativas + ct_tl.operating_hours
			horas_perdidas = horas_perdidas + ct_tl.time_losed_quantity
		
		if ((horas_operativas-horas_perdidas)>0) & bool(self.hours_by_month):
			eficiencia = round(((horas_operativas-horas_perdidas)/(self.hours_by_month*1.0))*100,2)
		return eficiencia
	
	#@api.depends('equipo','operating_hours','certification_coiled_tubing_id.operating_hours','certification_coiled_tubing_id','time_losed_quantity')
	@api.depends('type','hours_by_month','automatic_calculation_hours_by_month')
	@api.one
	def _set_eficiencia(self):
		eficiencia = 0
		now = datetime.now()
		for i in range(6):
			my_month = now - relativedelta(months=i)
			mes = my_month.strftime('%B').capitalize()
			eficiencia_mes = self._get_eficiencia_by_month(mes)
			eficiencia = eficiencia + eficiencia_mes

		self.eficiencia = round((eficiencia/6*1.0),2)
		
		return self.eficiencia
		
	
	# asigna un valor al inicio y luego no se toca a menos que sea modificado en la vista.
	# default=lambda self: self._get_last_exchange_date()
	
	# computa el valor cada vez, no permite modificacion 
	#compute='set_total_value'	

	# computa el valor cada vez ¿permite modificacion? 
	#compute='set_total_value'	+ store= true
	
	@api.onchange('type','automatic_calculation_hours_by_month')
	@api.one
	def _set_hours_by_month(self):
		if self.automatic_calculation_hours_by_month:
			weekday, days_in_month = monthrange(date.today().year, date.today().month)
			
			
			self.hours_by_month = int(self.type) * days_in_month if (self.type) else 0
		return self.hours_by_month
		
	automatic_calculation_hours_by_month =  fields.Boolean("Calcular horas por mes automaticamente",default=True)
	
	hours_by_month = fields.Integer(string="Horas por mes",default=lambda self: self._set_hours_by_month())
	

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
		if vals.get('hours_by_month') is None:
			vals['hours_by_month'] = self._set_hours_by_month()[0] 
		
		res = super(certification_plant, self).write(vals)
		
		return res
