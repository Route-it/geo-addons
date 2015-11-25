# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date

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
	operacion = fields.Selection([("guia","Guía"),("fit","FIT"),("pit","PIT"),("lot","LOT"),
								("aislacion","Aislación"),("intermedia","Intermedia"),
								("estimulacion acida","Estimulación ácida"),("estimulacion gas oil","Estimulación con gas oil"),
								("presion","Presión"),("patagoniano","Patagoniano"),("tapon balanceado","Tapón balanceado"),
								("prueba de valvulas","Prueba de válvulas"),("venta de productos","Venta de productos"),
								("alquiler de cisterna","Alquiler de cisterna"),("ahogo","Ahogo")],required=True)
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
							],readonly=True)
	
	
	def set_carga(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'carga'}, context=context)
		
	def set_validado(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'validado'}, context=context)
		
	def set_operadora(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'operadora'}, context=context)
		
	def set_aprobado(self, cr, uid, ids, context=None):
		for record in self.browse(cr, uid, ids, context=context):
			if not record.confirmacion:
				raise ValidationError('Debe agregar el número de confirmación')
				return
			record.supervisor.operacionesHechas+=1
			record.fechacierre = date.today()
		return self.write(cr, uid, ids, {'state': 'aprobado'}, context=context)
	
	def name_get(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
	
		res = []
		for record in self.browse(cr, uid, ids, context=context):
			name = record.parte
			res.append((record.id, name))
		
		return res
	
	@api.model
	@api.returns('self', lambda value:value.id)
	def create(self, vals):
		superv = self.env['certifications.supervisor'].search([('id','=',vals['supervisor'])])
		vals['parte'] = str(superv.numeroSupervisor) + "." + str(superv.operacionesHechas)
		vals['state'] = 'carga'
		return models.Model.create(self, vals)
	
	def setTotalValue(self):
		self.ValorTotal = self.valorProductos + self.valorServicios


