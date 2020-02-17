
# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date

import logging

_logger = logging.getLogger(__name__)

class client(models.Model):
    
    _inherit = 'res.partner'
    
    vat = fields.Char("CUIT/CUIL", help = "identificador  único")
    #uso interno.
    company_operator_code = fields.Char("Codigo de operadora") 

    is_company_operator = fields.Boolean("Es una compania operadora de petroleo", default=False)

    #Se comenta por que igual esta la restriccion al agregar manualmente.
    _sql_constraints = [
            ('unique_vat', 'unique(vat)', 'El cuit/cuil registrado ya existe')
    ]
    
    @api.constrains('vat')
    @api.one
    def check_vat_ar(self):
        """
        Check VAT (CUIT) for Argentina
        """
        for record in self:
            if not record.vat: return
            vat = record.vat
            cstr = str(vat)
            salt = str(5432765432)
            n = 0
            sum = 0
    
            if not vat.isdigit:
                raise ValidationError("El campo CUIT/CUIL deben ser solo numeros.")
                return
    
            if (len(vat) != 11):
                raise ValidationError("El campo CUIT/CUIL debe ser de 11 digitos.")
                return
    
            while (n < 10):
                sum = sum + int(salt[n]) * int(cstr[n])
                n = n + 1
    
            op1 = sum % 11
            op2 = 11 - op1
    
            code_verifier = op2
    
            if (op2 == 11 or op2 == 10):
                if (op2 == 11):
                    code_verifier = 0
                else:
                    code_verifier = 9
    
            if (code_verifier == int(cstr[10])):
                return True
            else:
                raise ValidationError("El campo CUIT/CUIL "+ vat +" es invalido.")
                return

    
    