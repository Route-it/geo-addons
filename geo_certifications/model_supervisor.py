# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)




class certifications_supervisor(models.Model):
	_name = "certifications.supervisor"

	_order = 'nombre asc'


	_rec_name = "nombre"

	active = fields.Boolean(default=True,string="Activo")	
	nombre = fields.Char(required=True)
	apellido = fields.Char(required=True)
	numeroSupervisor = fields.Integer(string="Número Supervisor")
	operacionesHechas = fields.Integer(readonly=True,string="Operaciones Hechas")
	nivelOperacion = fields.Selection([('1','1'),('2','2'),('3','3')],required=True, string="Nivel de Operación")
	
	_sql_constraints = [
		('numeroSupervisor_uniq', 'unique("numeroSupervisor")', 'Ese numero de supervisor ya existe'),
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
	
	@api.model
	def name_search(self, name='', args=None, operator='ilike', limit=100):
		if not args:
			args = []
		if name:
			args += ['|',("nombre", operator, name),("apellido", operator, name)] # domain o client_id o name
		return super(certifications_supervisor, self).name_search(name, args=args, operator=operator, limit=limit)
	
