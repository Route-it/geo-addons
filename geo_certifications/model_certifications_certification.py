# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date

import logging

_logger = logging.getLogger(__name__)

class certifications_certification(models.Model):
	_name = 'certifications.certification'
	
	parte = fields.Char(required=True,string="Parte")
	fechaRealizacion = fields.Datetime(required=True,string="Fecha de realización")
	pozo = fields.Char(required=True,string="Pozo")
	operadora = fields.Many2one('res.partner',domain = [('is_company','=','True')],required=True,string="Operadora")
	yacimiento = fields.Selection([('chubut','Chubut'),('santa cruz','Santa Cruz')],required=True,string="Yacimiento")
	supervisor = fields.Many2one('certifications.supervisor','Supervisor',required=True)
	equipo = fields.Char(required=True,string="Equipo")
	bombeador = fields.Char(required=True,string="Bombeador")
	operacion = fields.Selection([("guia","Guía"),("fit","FIT"),("pit","PIT"),("lot","LOT"),
								("aislacion","Aislación"),("intermedia","Intermedia"),
								("estimulacion acida","Estimulación ácida"),("estimulacion gas oil","Estimulación con gas oil"),
								("presion","Presión"),("patagoniano","Patagoniano"),("tapon balanceado","Tapón balanceado"),
								("prueba de valvulas","Prueba de válvulas"),("venta de productos","Venta de productos"),
								("alquiler de cisterna","Alquiler de cisterna"),("ahogo","Ahogo")],required=True,string="Operación")
	blscemento = fields.Integer(required=True,string="Bolsas de cemento")
	fechacierre = fields.Datetime(readonly=True,string="Fecha de cierre")
	valorservicios = fields.Float(required=True,string="Valor de servicios",oldname="valorServicios")
	valorproductos = fields.Float(required=True,string="Valor de productos",oldname="valorProductos")
	valortotal = fields.Float(readonly=True,compute='setTotalValue',store=True,string="Valor total",oldname="ValorTotal")
	confirmacion = fields.Char(string="Confirmación")
	state = fields.Selection([("carga","Carga de Datos"),
							("validado","Validado"),
							("operadora","Proceso de Operadora"),
							("aprobado","Certificacion Aprobada")
							],readonly=True,string="Estado")
	
	
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
#		superv = self.env['certifications.supervisor'].search([('id','=',vals['supervisor'])])
#		vals['parte'] = str(superv.numeroSupervisor) + "." + str(superv.operacionesHechas)
		vals['state'] = 'carga'
		return models.Model.create(self, vals)
	
	@api.depends('valorproductos','valorservicios')
	def setTotalValue(self):
		self.valortotal = self.valorproductos + self.valorservicios


