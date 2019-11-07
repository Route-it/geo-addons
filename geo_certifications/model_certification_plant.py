# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning
from calendar import monthrange
import logging
from datetime import date

_logger = logging.getLogger(__name__)

	
class certification_plant(models.Model):
	_name = 'certification.plant'
	_order = 'name'
	_description = "Equipos de trabajo"
	
	_group_by_full = {'equipo'}
	
	name = fields.Char("Nombre")
	description = fields.Text("Descripcion")
	type = fields.Selection([("24","24hs"),("12","12hs")],string="Tipo (hs por dia)",default="12")
	
	# asigna un valor al inicio y luego no se toca a menos que sea modificado en la vista.
	# default=lambda self: self._get_last_exchange_date()
	
	# computa el valor cada vez, no permite modificacion 
	#compute='set_total_value'	

	# computa el valor cada vez ¿permite modificacion? 
	#compute='set_total_value'	+ store= true
	
	@api.depends('type','automatic_calculation_hours_by_month')
	def _set_hours_by_month(self):
		if self.automatic_calculation_hours_by_month:
			weekday, days_in_month = monthrange(date.today().year, date.today().month)
			
			
			self.hours_by_month = int(self.type) * days_in_month if (self.type) else 0
			
		
		
	
	automatic_calculation_hours_by_month =  fields.Boolean("Calcular horas por mes autmaticamente",default=True)
	
	hours_by_month = fields.Integer(string="Tipo (hs por dia)",compute='_set_hours_by_month',default=lambda self: self._set_hours_by_month(),store=True)
	

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
		
		