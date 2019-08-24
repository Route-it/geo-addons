# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning

import logging

_logger = logging.getLogger(__name__)

	
class certification_invoice(models.Model):
	_name = 'certification.invoice'
	_order = 'id'
	
	invoice_date = fields.Datetime("Fecha de Factura")
	invoice_date_charge = fields.Datetime("Fecha de Cobro")
	invoice_number = fields.Char("Numero de Factura")
	currency_id = fields.Many2one('res.currency', string='Account Currency',
        help="Forces all moves for this account to have this account currency.")
	valor_total = fields.Monetary("Valor Total")



	@api.one
	@api.constrains('invoice_date_charge','invoice_date')
	def validate_dates(self):
		if bool(self.invoice_date) & bool(self.invoice_date_charge):
			if self.invoice_date >= self.invoice_date_charge:
				raise ValidationError("La fecha de factura debe ser anterior a la fecha de cobro")
			

	
	
	