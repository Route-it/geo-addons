
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

class company_operator(models.Model):
    
    _inherit = 'res.partner'
    _order = 'id asc'
    
    @api.model
    def default_get(self, fields):
        context = self._context or {}
        res = super(company_operator, self).default_get(fields)

        if ('supplier' in fields) & (bool(context.get("supplier")) == True):
            res.update({'supplier': True})
            res.update({'customer': False})
        if ('customer' in fields) & (bool(context.get("customer")) == True):
            res.update({'supplier': False})
            res.update({'customer': True})
        if ('employee' in fields) & (bool(context.get("employee")) == True):
            res.update({'employee': True})
        if ('is_company_operator' in fields) & (bool(context.get("default_is_company_operator")) == True):
            res.update({'is_company_operator': True})
            res.update({'customer': True})

        if ('is_company' in fields) & (bool(context.get("default_is_company")) == True):
            res.update({'is_company': True})
            res.update({'company_type': 'company'})


        
        return res

    
    