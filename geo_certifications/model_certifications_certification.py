# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError

import logging
from datetime import date

_logger = logging.getLogger(__name__)

class certifications_certification(models.Model):
	_name = 'certifications.certification'
	_inherit = ['mail.thread','ir.needaction_mixin']
	
	_description = 'Certificaciones'

	def is_antique_register(self):
		return False

	@api.model
	def _get_last_exchange_date(self):
		try:
			if (not bool(self.cotizacion_to_date_charge)) or (bool(self.cotizacion_to_date_charge) and (self.cotizacion_to_date_charge > 0)): 
					if (not bool(self.is_antique_register())): 
						return self.env['exchange.cotizacion_dolar_bcra'].search([],limit=1).fecha
		except Exception:
			return
		return False
		
	@api.model
	def _get_last_exchange(self):
		try:
			return self.env['exchange.cotizacion_dolar_bcra'].search([],limit=1).venta
		except Exception:
			return


	@api.one
	def _is_administracion_read_only(self):
		rw = self.env.user.has_group('geo_certifications.group_name_certifications_ingenieria') or \
				self.env.user.has_group('geo_certifications.group_name_certifications_administrator') or \
					self.env.user.has_group('base.user_root')
				
		
		ro = self.env.user.has_group('geo_certifications.group_name_certifications_administracion') or \
				self.env.user.has_group('geo_certifications.group_name_solo_lectura')
		
		
		if rw: 
			self.is_administracion_read_only = False
			return
		
		self.is_administracion_read_only = ro
		
		
	
	contrato = fields.Many2one("certification.contract",domain = [('active','=','True')])
	
	#comunes
	#operadora = fields.Many2one('res.partner',oldname='operadora',domain = [('is_company','=','True')],string="Operadora")
	operadora_id = fields.Many2one('res.partner',oldname='operadora',domain = [('is_company','=','True')],required=True,string="Operadora")
								#groups='geo_certifications.group_name_certifications_administrator')
	is_administracion_read_only = fields.Boolean(compute="_is_administracion_read_only",readonly=True)
								
	company_operator_code = fields.Char(related='operadora_id.company_operator_code')
	pozo = fields.Char(required=True,string="Pozo",track_visibility='onchange')


	state = fields.Selection([("carga","Carga de Datos"),
							("proceso_facturacion","Proceso de Facturacion"),
							("facturacion","Facturado"),
							("cobrado","Cobrado")
							], string="Estado", required=True, readonly=True,default='carga') 

	dm = fields.Char(string="DM",track_visibility='onchange')
	habilita = fields.Char(string="Habilita")
	invoice_id = fields.Many2one('certification.invoice', string="Factura", ondelete='cascade')
	
	#related
	invoice_date = fields.Date(related="invoice_id.invoice_date",help="Campo requerido para pasar a facturado. Se debe completar tambien el nro de factura y el valor total")
	invoice_number = fields.Char(related='invoice_id.invoice_number',help="Campo requerido para pasar a facturado. Se debe completar tambien la fecha de factura y el valor total")
	valor_total_pesos_factura = fields.Monetary(related='invoice_id.valor_total_pesos',help="Se debe completar tambien el nro de factura y la fecha de factura")
	valor_total_factura = fields.Monetary(related='invoice_id.valor_total',help="Campo requerido para pasar a facturado. Se debe completar tambien el nro de factura y la fecha de factura")
	invoice_date_charge = fields.Date(related="invoice_id.invoice_date_charge")

	manual_exchange = fields.Boolean("Cotizacion manual",default=False)

	cotizacion_to_date_charge = fields.Monetary("Cotización  del dólar (1 U$S)",
											default=lambda self: self._get_last_exchange(),track_visibility='onchange'
											)
	cotizacion_to_date_charge_date = fields.Date("Fecha de Cotizacion",
											default=lambda self: self._get_last_exchange_date()
											)

	currency_id = fields.Many2one('res.currency', string='Account Currency',
    							help="Forces all moves for this account to have this account currency.")


	valor_productos = fields.Monetary(string="Valor de productos U$S",track_visibility='onchange')
	valor_servicios = fields.Monetary(string="Valor de servicios U$S",track_visibility='onchange')
	valor_servicios_pesos = fields.Monetary(string="Valor de servicios $",track_visibility='onchange')
	valor_total = fields.Monetary(readonly=True,store=True,compute='set_total_value', inverse='set_total_value',
								string="Valor Total")
	
	
	valor_total_factura_computed = fields.Monetary("Valor de Factura Total",store=True,
												compute='set_valor_total_factura_computed',
												help="Valor total de factura calculado con la cotizacion manual o de la fecha de factura")
	
	valor_total_list_view = fields.Monetary(readonly=True,compute='set_total_value_state',store=True,string="Valor [USD]")
	
	@api.depends('cotizacion_to_date_charge','invoice_id.valor_total','invoice_id.invoice_date','invoice_id.valor_total_pesos',
				'valor_total_factura','valor_total_pesos_factura','invoice_date')
	@api.one
	def set_valor_total_factura_computed(self):
		res = False
		if self.valor_total_pesos_factura > 0:
			if self.manual_exchange:
				# si se introdujo un valor de cotizacion manualmente se toma ese
				res = self.valor_total_factura + self.valor_total_pesos_factura / self.cotizacion_to_date_charge
			else:
				if bool(self.invoice_date):
					# si el valor es automatico para el valor total de la factura se toma 
					cotiz = self.env['exchange.cotizacion_dolar_bcra'].search([('fecha','<=',self.invoice_date)],limit=1)
					#if not bool(self.manual_exchange):
					#	if (self.cotizacion_to_date_charge_date != cotiz.fecha):
					#		self.cotizacion_to_date_charge_date = cotiz.fecha
					#		self.cotizacion_to_date_charge = cotiz.venta
						
					res = self.valor_total_factura + self.valor_total_pesos_factura / cotiz.venta
				else:
					self.env.user.notify_info('debe introducir una fecha de factura')
		else:
			res = self.valor_total_factura
		#self.write({'valor_total_factura_computed':res})
		self.valor_total_factura_computed = res
		return res
	
	@api.depends('valor_productos','valor_servicios','valor_servicios_pesos','state')
	@api.one
	def set_total_value(self):
		res = False
		if self.cotizacion_to_date_charge > 0:
			res = self.valor_productos + self.valor_servicios +  (self.valor_servicios_pesos / self.cotizacion_to_date_charge)
		else:
			res = self.valor_servicios + self.valor_productos
		if self.cotizacion_to_date_charge < 0:
			raise ValidationError("La cotizacion debe ser mayor que 0")

		#self.valor_total_factura = res
		if self.valor_total != res:
			self.valor_total = res
		return self.valor_total
		
	@api.depends('valor_total_factura_computed','valor_total','state')
	@api.one
	def set_total_value_state(self):
		res = self.valor_total
		res_f = self.valor_total_factura_computed
		state = self.state
		if state in ('facturacion','cobrado'):
			if 	(res_f > 0) & (res != res_f):
				self.valor_total_list_view = res_f
				return res_f
		self.valor_total_list_view = res
		return res
	
	""" si se habilita el boton para traer la ultima cotizacion, deberia funcionar con esta funciona
	@api.model
	def exchange_update(self):
		self._get_last_exchange()
		self._get_last_exchange_date()
	"""
	
	@api.one
	@api.constrains('valor_servicios_pesos')
	def validate_valor_servicios_pesos(self):
		if self.valor_servicios_pesos < 0:
			raise ValidationError("El Valor de servicios $ debe ser mayor que 0")
			return
		return
	
	@api.one
	@api.constrains('valor_servicios')
	def validate_valor_servicios(self):
		if self.valor_servicios < 0:
			raise ValidationError("El Valor de servicios U$S debe ser mayor que 0")
			return
		return
	
	@api.one
	@api.constrains('valor_productos')
	def validate_valor_productos(self):
		if self.valor_productos < 0:
			raise ValidationError("El Valor de productos U$S debe ser mayor que 0")
			return
		return
	
	@api.one
	@api.constrains('cotizacion_to_date_charge')
	def validate_cotizacion_to_date_charge(self):
		if self.cotizacion_to_date_charge < 0:
			raise ValidationError("La cotizacion debe ser mayor que 0")
			return
		return

	def name_get(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
	
		res = []
		for record in self.browse(cr, uid, ids, context=context):
			name = record.operadora_id.name
			pozo = ''
			invoice_number = ''
			if record.pozo:
				pozo = '('+record.pozo+')' or ''
			if record.invoice_number:
				invoice_number = '- Fact:'+ record.invoice_number or ''
			appeler = name + pozo + invoice_number
			
			res.append((record.id, appeler))
		
		return res
	

	def suscribe_specific_partners(self,certif,partner_ids=[]):
		#partner_ids = self.env['res.users'].search([('active','=',True)]).mapped('partner_id').ids
		certif.message_subscribe(partner_ids=partner_ids)

	
	
	@api.multi
	def write(self, vals):
		"""Patch:
		Esto deberia ser asi:
		self.env['exchange.cotizacion_dolar_bcra'].search(('venta','=',self.cotizacion_to_date_charge)],limit=1)
		pero odoo no ecuentra igual cuando el valor guardado es 54.886 y el buscado es 54.88
		"""
		#cotiz_register = self.env['exchange.cotizacion_dolar_bcra'].search(['&',('venta','>=',self.cotizacion_to_date_charge-0.01),('venta','<=',self.cotizacion_to_date_charge+0.01)],limit=1)
		#cotiz_register = self.env['exchange.cotizacion_dolar_bcra'].search(['&',('venta','>=',str(self.cotizacion_to_date_charge)+'0'),('venta','<=',str(self.cotizacion_to_date_charge)+'9')],limit=1)
		#self.env['exchange.cotizacion_dolar_bcra'].search([('venta','=',self.cotizacion_to_date_charge)],limit=1)
		#cotiz_register if bool(cotiz_register) else self.env['exchange.cotizacion_dolar_bcra'].search(['&',('venta','>=',self.cotizacion_to_date_charge-0.02),('venta','<=',self.cotizacion_to_date_charge+0.02)],limit=1)
		
		list_possible = [item for item in self.env['exchange.cotizacion_dolar_bcra'].search([],limit=250) if (item.venta >= (self.cotizacion_to_date_charge-0.1)) & (item.venta<=(self.cotizacion_to_date_charge+0.1))]
		if len(list_possible)>0:
			cotiz_register = list_possible[0] 
		else:
			cotiz_register = False
		if (self.cotizacion_to_date_charge == 0) and (vals.get('cotizacion_to_date_charge') is None):
			cotiz_register = self.env['exchange.cotizacion_dolar_bcra'].search([('fecha','<=',self.create_date)],limit=1)
			vals['cotizacion_to_date_charge_date'] = cotiz_register.fecha
			vals['cotizacion_to_date_charge'] = cotiz_register.venta
			
		if (not cotiz_register):
			#is manual value!
			if not bool(self.is_antique_register()):
				vals['manual_exchange'] = True
				if not bool(self.cotizacion_to_date_charge_date):
					vals['cotizacion_to_date_charge_date'] = self.create_date
					#date.today()
					self.message_post(body='La cotización ahora es un valor introducido manualmente:'+str(self.cotizacion_to_date_charge))
		else:
			if ((not bool(self.is_antique_register()))&(not bool(self.cotizacion_to_date_charge_date))&(vals.get('cotizacion_to_date_charge') is None)):
				vals['cotizacion_to_date_charge_date'] = cotiz_register.fecha
			
		res = super(certifications_certification, self).write(vals)
		
		return res
	
	@api.model
	def create(self, vals):

		certif = super(certifications_certification, self).create(vals)
		
		
		inv_vals = {'invoice_date':vals.get('invoice_date'),
					'invoice_date_charge':vals.get('invoice_date_charge'),
					'invoice_number':vals.get('invoice_number'),
					'valor_total':vals.get('valor_total'),
				}
		
		inv = self.env['certification.invoice'].create(inv_vals)
		
		certif.invoice_id = inv.id

		#suscribe all users 
		self.suscribe_specific_partners(certif)

		return certif
	
	
	def search_read(self, cr, uid, domain=None, fields=None, offset=0, limit=None, order=None, context=None):
		if context.get('search_default_message_needaction'):
			return super(certifications_certification, self).search_read(cr, uid, [('message_needaction', '=', True)], fields, offset, limit, order, context)
		return super(certifications_certification, self).search_read(cr, uid, domain, fields, offset, limit, order, context)
	
	
	@api.model
	def _needaction_domain_get(self):
		return [('message_needaction', '=', True)]
		#return [('journal_entry_ids', '=', False), ('account_id', '=', False)]

	def fields_get(self, cr, user, allfields=None, context=None, write_access=True, attributes=None):
		res = super(certifications_certification, self).fields_get( cr, user, allfields, context, write_access, attributes)
		"""
		my_special_keys = ['messa','write_uid','write_date','create_uid','create_date','id','__last_update','company_operator_code','currency_id']
		for k in res.keys():
			for i in my_special_keys:
				if i in k: 
					res.get(k)['exportable'] = False
					res.get(k)['searchable'] = False
					res.get(k)['selectable'] = False
		"""
		return res
		
		
	@api.multi
	def export_data_for_my_report(self, fields_to_export, raw_data=False):
		res = super(certifications_certification, self).export_data(fields_to_export,raw_data)
		return res
		
	@api.multi
	def export_data(self, fields_to_export, raw_data=False):
		res = super(certifications_certification, self).export_data(fields_to_export,raw_data)
		return res
		