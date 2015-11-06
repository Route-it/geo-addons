# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)




class certifications_supervisor(models.Model):
	_name = "certifications.supervisor"
	
	nombre = fields.Char(required=True)
	apellido = fields.Char(required=True)
	numeroSupervisor = fields.Integer()
	operacionesHechas = fields.Integer(readonly=True)
	nivelOperacion = fields.Selection([('1','1'),('2','2'),('3','3')],required=True)
	
	_sql_constraints = [
		('numeroSupervisor_uniq', 'unique(numeroSupervisor)', 'Ese número de supervisor ya existe'),
	]
	
	def name_get(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
	
		res = []
		for record in self.browse(cr, uid, ids, context=context):
			name = record.nombre + ' ' + record.apellido
			res.append((record.id, name))
		
		return res
	
	
