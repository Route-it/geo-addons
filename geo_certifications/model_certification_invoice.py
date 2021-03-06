# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning
from datetime import datetime

import logging


_logger = logging.getLogger(__name__)

	
class certification_invoice(models.Model):
	_name = 'certification.invoice'
	_order = 'id'
	
	invoice_date = fields.Date("Fecha de Factura",track_visibility='onchange')
	invoice_date_charge = fields.Date("Fecha de Cobro")
	invoice_number = fields.Char("Numero de Factura")
	currency_id = fields.Many2one('res.currency', string='Account Currency',
        help="Forces all moves for this account to have this account currency.")
	valor_total_pesos = fields.Monetary("Valor Pesos",track_visibility='onchange')
	valor_total = fields.Monetary("Valor U$S",track_visibility='onchange')



	@api.one
	@api.constrains('valor_total_pesos')
	def _check_valor_total_pesos(self):
		if self.valor_total_pesos < 0:
			raise ValidationError("El valor total en pesos debe ser mayor que 0")
			return
		return
	
	
	@api.one
	@api.constrains('valor_total')
	def _check_valor_total(self):
		if self.valor_total < 0:
			raise ValidationError("El valor total debe ser mayor que 0")
			return
		return

	@api.one
	@api.constrains('invoice_date_charge','invoice_date')
	def validate_dates(self):
		if bool(self.invoice_date) & bool(self.invoice_date_charge):
			invoice_date_date = self.invoice_date
			invoice_date_charge_date = self.invoice_date_charge
			try:
				invoice_date_date = datetime.strptime(self.invoice_date, '%Y-%m-%d') 
				invoice_date_charge_date = datetime.strptime(self.invoice_date_charge, '%Y-%m-%d') 
				invoice_date_charge_date.replace(hour=0, minute=0, second=0, microsecond=0)
				invoice_date_date.replace(hour=0, minute=0, second=0, microsecond=0)
			except Exception as e:
				_logger.warning('Ocurrio un problema al procesar las fechas de factura: invoice %i',self.id)	
			if invoice_date_date > invoice_date_charge_date:
				raise ValidationError("La fecha de factura debe ser anterior a la fecha de cobro")
			
	