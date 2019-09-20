# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)

	
class certification_contract(models.Model):
	_name = 'certification.contract'
	_order = 'id'
	
	name = fields.Char("Nombre")
	description = fields.Text("Descripcion")
	active = fields.Boolean("Activo",default=True)

			

	@api.one
	@api.constrains('name')
	def validate_dates(self):
		if not (bool(self.name) & (len(self.name)>3)):
			raise ValidationError("El nombre debe tener al menos 3 caracteres")
			

	
	
	@api.one
	@api.constrains('name')
	def check_unique_name(self):
		records = self.env['certification.contract'].search([('name','=',self.name)])
		if len(records)>0:
			raise ValidationError("Ya existe un registro con ese nombre, verifique que este activo")