# -*- coding: utf-8 -*-

from openerp import models, fields, api

class certifications_certification(models.Model):
	_name = 'certifications.certification'
	
	color = fields.Integer('Color Index')
	parte = fields.Char()
	pozo = fields.Char()
	operadora = fields.Many2one('res.partner',domain = [('is_company','=','True')])
	yacimiento = fields.Selection([('chubut','Chubut'),('santa cruz','Santa Cruz')])
	supervisor = fields.Many2one('certifications.supervisor','Supervisor')
	equipo = fields.Char()
	bombeador = fields.Char()
	operacion = fields.Selection([("op1","op1"),("op2",("op2"))])
	blscemento = fields.Integer()
	fechacierre = fields.Datetime()
	valorServicios = fields.Float()
	valorProductos = fields.Float()
	ValorTotal = fields.Float()
	confirmacion = fields.Char()
	stage = fields.Many2one('certifications.certification.stage','Etapa', required=False, copy=False)
	

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
	
	nombre = fields.Char()
	apellido = fields.Char()
	operacionesHechas = fields.Integer()
	nivelOperacion = fields.Selection([('1','1'),('2','2'),('3','3')])
	
	
	
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


