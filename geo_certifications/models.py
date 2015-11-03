# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class geo_certifications(models.Model):
	_name = 'certifications.certification'
	
	parte = fields.Char(readonly=True)
	pozo = fields.Char()
	operadora = fields.Many2one('res.partner',domain = [('is_company','=','True')])
	yacimiento = fields.Selection([('chubut','Chubut'),('santa cruz','Santa Cruz')])
	supervisor = fields.Many2one('certifications.supervisor')
	equipo = fields.Char()
	bombeador = fields.Char()
	operacion = fields.Selection([("op1","op1"),("op2",("op2"))])
	blscemento = fields.Integer()
	fechacierre = fields.Datetime()
	valorSerrvicios = fields.Float()
	valorProductos = fields.Float()
	ValorTotal = fields.Float()
	confirmacion = fields.Char()
	
	@api.model
	@api.returns('self', lambda value:value.id)
	def create(self, vals):
		_logger.debug("modificando")
		superv = self.env['certifications.supervisor'].search([('id','=',self.supervisor._uid)])
		vals['parte'] = str(superv.numeroSupervisor) + "." + str(superv.operacionesHechas)
		return models.Model.create(self, vals)
	

class GeoCertificationSupervisor(models.Model):
	_name = "certifications.supervisor"
	
	nombre = fields.Char()
	apellido = fields.Char()
	numeroSupervisor = fields.Integer()
	operacionesHechas = fields.Integer()
	nivelOperacion = fields.Selection([('1','1'),('2','2'),('3','3')])
	