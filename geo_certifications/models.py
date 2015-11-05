# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class certifications_certification(models.Model):
	_name = 'certifications.certification'
	
	color = fields.Integer('Color Index')
	parte = fields.Char(readonly=True)
	pozo = fields.Char(required=True)
	operadora = fields.Many2one('res.partner',domain = [('is_company','=','True')],required=True)
	yacimiento = fields.Selection([('chubut','Chubut'),('santa cruz','Santa Cruz')],required=True)
	supervisor = fields.Many2one('certifications.supervisor','Supervisor',required=True)
	equipo = fields.Char(required=True)
	bombeador = fields.Char(required=True)
	operacion = fields.Selection([("op1","op1"),("op2",("op2"))],required=True)
	blscemento = fields.Integer(required=True)
	fechacierre = fields.Datetime(readonly=True)
	valorServicios = fields.Float(required=True)
	valorProductos = fields.Float(required=True)
	ValorTotal = fields.Float(readonly=True,compute='setTotalValue')
	confirmacion = fields.Char()
	stage = fields.Many2one('certifications.certification.stage','Etapa', required=False, copy=False)
	
	@api.model
	@api.returns('self', lambda value:value.id)
	def create(self, vals):
		superv = self.env['certifications.supervisor'].search([('id','=',vals['supervisor'])])
		vals['parte'] = str(superv.numeroSupervisor) + "." + str(superv.operacionesHechas)
		return models.Model.create(self, vals)
	
	def setTotalValue(self):
		self.ValorTotal = self.valorProductos + self.valorServicios

	def _read_group_stage_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
		if context is None:
			context = {}
		stage_obj = self.pool.get('certifications.certification.stage')
		order = stage_obj._order
#		access_rights_uid = access_rights_uid or uid
		if read_group_order == 'stage_id desc':
			order = '%s desc' % order
		search_domain = []
		stage_ids = stage_obj._search(cr, None, search_domain, order=order, access_rights_uid=access_rights_uid, context=context)
		result = stage_obj.name_get(cr, access_rights_uid, stage_ids, context=context)
		# restore order of the search
		result.sort(lambda x, y: cmp(stage_ids.index(x[0]), stage_ids.index(y[0])))

		fold = {}
		for stage in stage_obj.browse(cr, access_rights_uid, stage_ids, context=context):
			fold[stage.id] = stage.fold or False
		return result, fold

	_group_by_full = {
		'stage': _read_group_stage_ids,
	}





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
	
	
	
class certifications_certification_type(models.Model):
	_name = 'certifications.certification.stage'
	_description = 'Etapa del Proyecto'
	_order = 'sequence'
	name = fields.Char('Nombre de la etapa', required=True, translate=True)
	description = fields.Text('Descripcion', translate=True)
	sequence = fields.Integer('Secuencia')
	certifications_ids = fields.Many2many('certifications.certification', 'cert_type_rel', 'stage_id', 'certification_id', 'Certificaciones')
	fold = fields.Boolean('Replegada',
                               help='Esta estapa esta replegada en la vista de kanban cuando no hay'
                               'registros que mostrar.')


