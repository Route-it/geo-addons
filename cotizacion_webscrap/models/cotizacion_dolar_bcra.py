# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

import logging

from openerp import models, fields, api, _
from datetime import date, datetime
import datetime

_logger = logging.getLogger(__name__)

class cotizacion_dolar_bcra(models.Model):
    
    _name = "exchange.cotizacion_dolar_bcra"

    _description = 'Cotizacion del BCRA'

    _order = 'fecha desc'
    
    fecha = fields.Date("Fecha")
    compra = fields.Monetary("Compra")
    venta= fields.Monetary("Venta")
    
    
    currency_id = fields.Many2one('res.currency', string='Account Currency',
                                help="Forces all moves for this account to have this account currency.")
    

    last_month = fields.Boolean(compute='is_last_month',store=True)

    
    @api.depends('fecha')
    @api.one
    def is_last_month(self):

        today = datetime.datetime.today()            
        dd = datetime.datetime.strptime(self.fecha, '%Y-%m-%d')            
        _30dias  = today - datetime.timedelta(days=30)
        if (dd >= _30dias):
            self.last_month = True
        else:
            self.last_month = False
        
        return self.last_month
