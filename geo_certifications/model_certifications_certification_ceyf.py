# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

class certifications_certification_ceyf(models.Model):
	_name= 'certifications.certification_ceyf'
	_inherit = 'certifications.certification'
	
	_description = 'Certificaciones ceyf'

	_order = 'fecha_realizacion desc'

	
	OPERATIONS = [("guia","Guía"),("fit","FIT"),("pit","PIT"),("lot","LOT"),
								("aislacion","Aislación"),("intermedia","Intermedia"),
								("estimulacion acida","Estimulación ácida"),("estimulacion gas oil","Estimulación con gas oil"),
								("presion","Presión"),("patagoniano","Patagoniano"),("tapon balanceado","Tapón balanceado"),
								("prueba de valvulas","Prueba de válvulas"),("venta de productos","Venta de productos"),
								("alquiler de cisterna","Alquiler de cisterna"),("ahogo","Ahogo"),("bombeo","Bombeo"),
								("gel","Gel"),("pozo","Pozo")]
	
	operacion = fields.Selection( OPERATIONS ,required=True,string="Operación")
	
	antique_register = fields.Datetime(string="Registro Antigüo")
	
	evento = fields.Char(string="Evento")
	parte = fields.Char(string="Parte",track_visibility='onchange')
	fecha_realizacion = fields.Date(required=True,string="Fecha de realización",oldname="fechaRealizacion")
	yacimiento = fields.Selection([('chubut','Chubut'),('santa cruz','Santa Cruz')],required=True,string="Yacimiento")
	supervisor_id = fields.Many2one('certifications.supervisor','Supervisor',required=True)
	equipo = fields.Char(required=True,string="Equipo",track_visibility='onchange')
	bombeador = fields.Char(required=True,string="Bombeador")
	blscemento = fields.Integer(required=True,string="Bolsas de cemento")
	
	fecha_cierre = fields.Date(readonly=True,string="Fecha de cierre")
	

	
	#esto cambia segun operadora.
	"""
	PAE			HESOP,	CERTOP		valor $
	YPF			DM,	HABILITA				super class
	SINOPEC		CODIGO 				valor $
	TECPETROL	HOJA DE SERVICIO
	CAPSA							valor $
	ENAP
	OTROS
	"""
	hesop = fields.Char(string="HESOP")
	certop = fields.Char(string="CERTOP")
	codigo = fields.Char(string="CODIGO")
	hoja_de_servicio = fields.Char(string="Hoja de servicio")

	@api.one
	@api.constrains('blscemento')
	def validate_blscemento(self):
		if self.blscemento < 0:
			raise ValidationError("El Valor bolsas de cemento debe ser mayor que 0")
			return
		return
	

	@api.onchange('operadora_id')
	@api.one
	def change_confirmation_with_company_operator(self):
		if self.operadora_id != False:
			if self.operadora_id.company_operator_code != 'ypf':
				self.dm = ''
				self.habilita = ''
			if self.operadora_id.company_operator_code != 'pae':
				self.certop = ''
				self.hesop = ''
			if self.operadora_id.company_operator_code != 'sinopec':
				self.codigo = ''
			if self.operadora_id.company_operator_code != 'tecpetrol':
				self.hoja_de_servicio = ''
				

	@api.one
	def name_get(self):
		try:
			name = self.operadora_id.name+' / '+self.equipo+' / '+self.pozo
		except:
			name = self.operadora_id.name
		return (self.id,name)

	
	def check_fields_for_state(self,fields_to_check,vals):
		yes = True
		for it in fields_to_check:
			yes = (True if (vals.get(it)!=None or eval('self.'+it)!=False) and vals.get(it)!=False else False) and yes			
			#yes = (True if vals.get(it)!=None or eval('self.'+it)!=False else False) and yes
			if not yes: break
		return yes


	"""
	contrato si es YPF, 
	evento si operacion es patagoniano

			#if self.company_operator_code = 'pae' -> certop
			#if self.company_operator_code = 'ypf' -> dm
			#if self.company_operator_code = 'sinopec' -> codigo
			
			if self.company_operator_code = 'pae' -> hesop
			if self.company_operator_code = 'ypf' -> habilita	
	
	"""
	fields_to_check_carga = ['operadora_id','operacion','equipo','pozo',
					'fecha_realizacion','bombeador','yacimiento','supervisor_id',
					'valor_productos']
	fields_to_check_carga_confirmacion = ['certop','dm','codigo']
	fields_to_check_proceso_facturacion = ['hesop','habilita']
	fields_to_check_facturacion = ['invoice_date','invoice_number','valor_total_factura']
	fields_to_check_cobrado = ['invoice_date_charge']
	
	
	@api.multi
	def write(self, vals):
		"""
		Esta condicion funciona pero no la dejamos habilitada ya que impide corregir errores de carga de facturas sobre registros 
		viejos. 
		Se habilitará la funcion para que queden readonly solo cuando los registros viejos ya esten TODOS facturados.
		
		if not ((vals.get('invoice_date_charge')!=None) and (vals.get('invoice_date_charge')!=False) and (self.state == 'facturacion')):
			if (self.state in ('facturacion','cobrado') and self.antique_register != False):
				self.env.user.notify_info('No está permitido editar un registro antigüo ya facturado')
				return False
		"""	
		
		
		if vals.get('state') is None:
			state = 'carga'
			if self.check_fields_for_state(self.fields_to_check_carga,vals): 
				state = 'proceso_facturacion' 
			#if self.check_fields_for_state(self.fields_to_check_proceso_facturacion,vals): state = 'facturacion'
			#else:
			"""if (self.company_operator_code == 'pae'):
				if (vals.get('hesop')!=None or eval('self.hesop')!=False) and vals.get('hesop')!=False:
					state = 'facturacion'
			else:
				if (self.company_operator_code == 'ypf'):
					if (vals.get('habilita')!=None or eval('self.habilita')!=False) and vals.get('habilita')!=False:
						state = 'facturacion'
				else:
					if (vals.get('codigo')!=None or eval('self.codigo')!=False) and vals.get('codigo')!=False:
						state = 'facturacion'
					else:
						if not (self.company_operator_code in ('pae','ypf','sinopec')):
							state = 'facturacion'
			"""
			if self.check_fields_for_state(self.fields_to_check_facturacion,vals): 
				if (vals.get('valor_total_factura')!=None and vals.get('valor_total_factura')!=False and vals.get('valor_total_factura')>0) or (self.valor_total_factura!=False and self.valor_total_factura>0): 
					state = 'facturacion' 
				else:
					mensaje = 'El valor total de factura debe ser mayor que 0'
					self.message_post(body=mensaje)
					self.env.user.notify_info(mensaje)
			if self.check_fields_for_state(self.fields_to_check_cobrado,vals): 
				state = 'cobrado' 
				self.supervisor_id.operacionesHechas+=1
			vals['state'] = state

		""" comentado a pedido en reunion 10/09/2019
		else:
			if vals.get('state') == 'carga':
				for item in self.fields_to_check_proceso_facturacion + self.fields_to_check_facturacion + self.fields_to_check_cobrado:
					vals[item] = False
			if vals.get('state') == 'proceso_facturacion':
				for item in self.fields_to_check_facturacion + self.fields_to_check_cobrado:
					vals[item] = False
			if vals.get('state') == 'facturacion':
		
				vals['invoice_date_charge'] = False
		"""
		
		
		return super(certifications_certification_ceyf, self).write(vals)
		
	"""
	#Sirve para modificar la vista
	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(certifications_certification_ceyf, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
		context = self._context or {}

		if bool(view_type) & (view_type == 'form'):
			#res['arch'] = res['arch'].replace('<form string="Certificaciones">','<form string="Certificaciones" edit="false">',1)
			for field in res['fields']:
				res['fields'][field]['readonly'] = True
			#		res['fields'][field].update({'defaults': context.get('delivery_id')})
		return res
	"""

	@api.model
	def create(self, vals):
		
		#No es un dato calculado: Reunion 10/09/2019
		#superv = self.env['certifications.supervisor'].search([('id','=',vals['supervisor_id'])])
		#vals['parte'] = str(superv.numeroSupervisor) + "." + str(superv.operacionesHechas)
		
		item = super(certifications_certification_ceyf, self).create(vals)
		#check if state is completed
		if self.check_fields_for_state(self.fields_to_check_carga,vals): 
			item.state = 'proceso_facturacion'  

		return item 

	def suscribe_specific_partners(self,certif,partner_ids=[]):
		partner_ids = self.env['res.users'].search([('active','=',True)]).mapped('partner_id').ids
		super(certifications_certification_ceyf, self).suscribe_specific_partners(certif,partner_ids)




	def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
		if not orderby:
			return super(certifications_certification_ceyf, self).read_group(cr, uid, domain, fields, groupby, offset, limit, context, "fecha_realizacion desc", lazy)
		return super(certifications_certification_ceyf, self).read_group(cr, uid, domain, fields, groupby, offset, limit, context, orderby, lazy)
	
	
	
