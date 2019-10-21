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
	active = fields.Boolean("Activo",default=True)

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