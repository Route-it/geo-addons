# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)

	
class certification_plant(models.Model):
	_name = 'certification.plant'
	_order = 'id'
	_description = "Equipos de trabajo"
	
	name = fields.Char("Nombre")
	description = fields.Text("Descripción")
	type = fields.Selection(string="Tipo (hs por dia)",[("24","24hs"),("12","12hs")])
	
	# asigna un valor al inicio y luego no se toca a menos que sea modificado en la vista.
	default=lambda self: self._get_last_exchange_date()
	
	# computa el valor cada vez, no permite modificacion 
	#compute='set_total_value'	

	# computa el valor cada vez ¿permite modificacion? 
	#compute='set_total_value'	+ store= true
	
	automatic_calculation_hours_by_month =  fields.Boolean("Calcular horas por mes autmaticamente",default=True)
	
	hours_by_month = fields.Integer(string="Tipo (hs por dia)",compute='set_hours_by_month')
	

	@api.one
	@api.constrains('name')
	def validate_name(self):
		if not (bool(self.name) & (len(self.name)>3)):
			raise ValidationError("El nombre debe tener al menos 3 caracteres")
			
	
	
	@api.one
	@api.constrains('name')
	def check_unique_name(self):
		records = self.env['certification.plant'].search([('name','=',self.name)])
		if len(records)>0:
			raise ValidationError("Ya existe un registro con ese nombre, verifique que este activo")