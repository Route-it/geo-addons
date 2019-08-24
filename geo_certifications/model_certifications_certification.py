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

	
	contrato = fields.Char(string="Contrato")
	#comunes
	#operadora = fields.Many2one('res.partner',oldname='operadora',domain = [('is_company','=','True')],string="Operadora")
	operadora_id = fields.Many2one('res.partner',oldname='operadora',domain = [('is_company','=','True')],required=True,string="Operadora")
	company_operator_code = fields.Char(related='operadora_id.company_operator_code')
	pozo = fields.Char(string="Pozo")


	state = fields.Selection([("carga","Carga de Datos"),
							("proceso_facturacion","Proceso de Facturacion"),
							("facturacion","Facturacion"),
							("cobrado","Cobrado")
							], string="Estado", required=True, readonly=True,default='carga') 

	dm = fields.Char(string="DM")
	habilita = fields.Char(string="Habilita")
	invoice_id = fields.Many2one('certification.invoice', string="Factura")
	
	#related
	invoice_date = fields.Datetime(related="invoice_id.invoice_date")
	invoice_date_charge = fields.Datetime(related="invoice_id.invoice_date_charge")
	invoice_number = fields.Char(related='invoice_id.invoice_number')
	valor_total_factura = fields.Monetary(related='invoice_id.valor_total')

	cotizacion_to_date_charge = fields.Monetary("Cotización  del dólar (1 U$S)")

	currency_id = fields.Many2one('res.currency', string='Account Currency',
    							help="Forces all moves for this account to have this account currency.")


	valor_productos = fields.Monetary(required=True,string="Valor de productos U$S")
	valor_servicios = fields.Monetary(string="Valor de servicios U$S")
	valor_servicios_pesos = fields.Monetary(string="Valor de servicios $")
	valor_total = fields.Monetary(readonly=True,compute='setTotalValue',store=True,string="Valor total")
	
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

	@api.depends('valor_productos','valor_servicios','cotizacion_to_date_charge','valor_servicios_pesos','state')
	@api.one
	def setTotalValue(self):
		#Solo si es YPF el valor de productos esta en pesos
		self.valor_total = False
		if self.cotizacion_to_date_charge > 0:
			self.valor_total = self.valor_productos + self.valor_servicios +  (self.valor_servicios_pesos / self.cotizacion_to_date_charge)
		else:
			self.valor_total = self.valor_servicios + self.valor_productos
		if self.cotizacion_to_date_charge < 0:
			raise ValidationError("La cotizacion debe ser mayor que 0")

		self.valor_total_factura = self.valor_total

	def name_get(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
	
		res = []
		for record in self.browse(cr, uid, ids, context=context):
			name = record.operadora_id.name
			contract = ''
			invoice_number = ''
			if record.contrato:
				contract = '('+record.contrato+')' or ''
			if record.invoice_number:
				invoice_number = '- Fact:'+ record.invoice_number or ''
			appeler = name + contract +invoice_number
			
			res.append((record.id, appeler))
		
		return res
	

	def suscribe_specific_partners(self,certif,partner_ids=[]):
		#partner_ids = self.env['res.users'].search([('active','=',True)]).mapped('partner_id').ids
		certif.message_subscribe(partner_ids=partner_ids)

	
	
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

