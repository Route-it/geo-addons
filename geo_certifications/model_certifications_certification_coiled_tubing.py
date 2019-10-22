# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

class certifications_certification_coiled_tubing(models.Model):
	_name= 'certifications.certification_coiled_tubing'
	_inherit = 'certifications.certification'
	
	_description = 'Certificaciones Coiled Tubing'

	_order = 'fecha_inicio desc'
	
	
	OPERATIONS = [("servicio_ct","SERVICIO CT"),("tapon","Tapón"),("cementacion","Cementación"),("punzado","Punzado"),
				("trailer","Tráiler"),("linea_venteo","Linea Venteo"),
				("producto","Producto")]
	
	
	contrato = fields.Many2one(required=True)

	equipo = fields.Selection([('UCT1','UCT-1'),
								('UCT2','UCT-2'),
								('UCT3','UCT-3'),
								('UCT4','UCT-4'),
								('UCT5','UCT-5')],required=True,string="Equipo",track_visibility='onchange')
	
	fecha_inicio = fields.Date(required=True,string="Fecha de inicio")
	fecha_fin = fields.Date(required=True,string="Fecha de fin")
	operacion = fields.Selection(OPERATIONS,required=True,string="Operación")
	regional = fields.Selection([("chubut","Chubut"),("santa_cruz","Santa Cruz"),("neuquen","Neuquen")],required=True,string="Regional")

	observaciones = fields.Text(string="Observaciones",help="Destinado a clarificar detalles. No incluir eventos, valores, vencimientos, fechas, etc.")
		
	operating_hours = fields.Integer("Horas Operativas")
	
	time_losed_ids = fields.One2many("certifications.coiled_tubing_time_losed","certification_coiled_tubing_id",string ="Horas Perdidas", ondelete='cascade')
	
	

	def check_fields_for_state(self,fields_to_check,vals):
		yes = True
		for it in fields_to_check:
			yes = (True if (vals.get(it)!=None or eval('self.'+it)!=False) and vals.get(it)!=False else False) and yes
			if not yes: break
		return yes

	fields_to_check_carga = ['operadora_id','contrato','equipo','pozo',
					'fecha_inicio','fecha_fin','operacion',
					'regional']
	#fields_to_check_proceso_facturacion = ['dm','habilita']
	fields_to_check_proceso_facturacion = ['invoice_date','invoice_number','valor_total_factura_computed']
	fields_to_check_cobrado = ['invoice_date_charge']
	
	
	@api.onchange('operadora_id')
	@api.one
	def change_confirmation_with_company_operator(self):
		if self.operadora_id != False:
			if self.operadora_id.company_operator_code != 'ypf':
				self.dm = ''
				self.habilita = ''
			
	
	
	@api.multi
	def write(self, vals):
		#determine state
		
		res = super(certifications_certification_coiled_tubing, self).write(vals)
		
		if vals.get('state') is None:
		
			state = 'carga'
			if self.check_fields_for_state(self.fields_to_check_carga,vals): 
				if (vals.get('valor_total')!=None and vals.get('valor_total')!=False and vals.get('valor_total')>0) \
					or (self.valor_total!=False and self.valor_total>0): 
						state = 'proceso_facturacion' 
			
			#solo si es ypf
			#if self.company_operator_code == 'ypf':
			if self.check_fields_for_state(self.fields_to_check_proceso_facturacion,vals): 
				if (vals.get('valor_total_factura_computed')!=None and vals.get('valor_total_factura_computed')!=False and vals.get('valor_total_factura_computed')>0) or (self.valor_total_factura_computed!=False and self.valor_total_factura_computed>0): 
					state = 'facturacion' 
				else:
					mensaje = 'El valor total de factura debe ser mayor que 0'
					self.message_post(body=mensaje)
					self.env.user.notify_info(mensaje)
			#else:
			#	state = 'facturacion'
			if self.check_fields_for_state(self.fields_to_check_cobrado,vals): state = 'cobrado' 
			self.state = state

		""" comentado a pedido en reunion 10/09/2019
		else:
			if vals.get('state') == 'carga':
				for item in self.fields_to_check_proceso_facturacion + self.fields_to_check_cobrado:
					vals[item] = False
			if vals.get('state') == 'proceso_facturacion':
				for item in self.fields_to_check_cobrado:
					vals[item] = False
		"""
		
		
		return res
		
	@api.model
	def create(self, vals):
		
		#create dummy invoice object and link with them
		id_inv = self.env['certification.invoice'].create([])
		vals['invoice_id'] = id_inv.id
		
		
		item = super(certifications_certification_coiled_tubing, self).create(vals)
		
		#check if state is completed
		#if self.check_fields_for_state(self.fields_to_check_carga,vals): 
		#	item.state = 'proceso_facturacion'  

		
		return item  


	def suscribe_specific_partners(self,certif,partner_ids=[]):
		partner_ids = self.env['res.users'].search([('active','=',True)]).mapped('partner_id').ids
		super(certifications_certification_coiled_tubing, self).suscribe_specific_partners(certif,partner_ids)
