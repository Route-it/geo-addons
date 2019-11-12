# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date, datetime
import pytz


import datetime
import logging

_logger = logging.getLogger(__name__)

class automatic_calculation_hours_by_month_for_plant(models.Model):

    _auto = False
    
    _name = "certifications.automatic_calculation_hours_by_month_for_plant"
     
    @api.model
    def process(self):

        logging.info("iniciando cron automatic_calculation_hours_by_month_for_plant")
        
        
        
        plants = self.env['certification.plant'].search([])
        
            
        for p in plants:
            if bool(p.type):
                p._set_hours_by_month()
        logging.info("Finalizo el cron de automatic_calculation_hours_by_month_for_plant")
        

        