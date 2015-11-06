# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)

	
class certifications_certification_task_type(models.Model):
	_name = 'certifications.certification.task.stage'
	_description = 'Etapa de la tarea'
	_order = 'sequence'
	name = fields.Char('Nombre de la etapa', required=True, translate=True)
	description = fields.Text('Descripcion', translate=True)
	sequence = fields.Integer('Secuencia')
	certifications_ids = fields.Many2many('certifications.certification.task', 'cert_type_rel', 'stage_id', 'task_id', 'Tareas de Certificaciones')
	fold = fields.Boolean('Replegada',
                               help='Esta estapa esta replegada en la vista de kanban cuando no hay'
                               'registros que mostrar.')


