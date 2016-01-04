# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class certifications_certification_task(models.Model):
	_name = 'certifications.certification.task'
	
	name = fields.Char(required=True)
	description = fields.Text(required=True)
	certification = fields.Many2one('certifications.certification',required=True)
	
	color = fields.Integer('Color Index')
	
	fechaFin = fields.Datetime()
	
	operadora = fields.Char("Operadora", help="La operadora a la que pertenece esta tarea", related='certification.operadora.name')

	stage = fields.Many2one('certifications.certification.task.stage','Etapa', required=True, copy=False)
	
	def _read_group_stage_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
		if context is None:
			context = {}
		stage_obj = self.pool.get('certifications.certification.task.stage')
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


