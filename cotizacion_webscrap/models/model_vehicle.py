# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

import logging

from openerp import models, fields, api, _


_logger = logging.getLogger(__name__)

class geopatagonia_vehicle(models.Model):
    

    _inherit = ["geopatagonia.vehicle"]


    TRANSFURLONG_STATES  = [('En Playa','EN PLAYA'),
                            ('Deposito', 'EN DEPOSITO'),
                            ('A Enviar', 'A ENVIAR, EN CARGA'),
                            ('En Viaje', 'EN VIAJE'),
                            ('Entregada', 'UNIDAD ENTREGADA'),
                       ]


    cotizacion_webscrap_state = fields.Selection(TRANSFURLONG_STATES,string="Transfurlong")
        
        