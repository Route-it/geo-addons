# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class certifications_certification(models.Model):
	_name = 'certifications.certification'
	
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
	state = fields.Selection([("carga","Carga de Datos"),
							("validado","Validado"),
							("operadora","Proceso de Operadora"),
							("aprobado","Certificacion Aprobada")
							])
	
	
	def set_carga(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'carga'}, context=context)
		
	def set_validado(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'validado'}, context=context)
		
	def set_operadora(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'operadora'}, context=context)
		
	def set_aprobado(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'aprobado'}, context=context)
	
	
	@api.model
	@api.returns('self', lambda value:value.id)
	def create(self, vals):
		superv = self.env['certifications.supervisor'].search([('id','=',vals['supervisor'])])
		vals['parte'] = str(superv.numeroSupervisor) + "." + str(superv.operacionesHechas)
		vals['state'] = 'carga'
		return models.Model.create(self, vals)
	
	def setTotalValue(self):
		self.ValorTotal = self.valorProductos + self.valorServicios


