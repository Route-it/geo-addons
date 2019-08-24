
# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''
import logging
import urllib

from bs4 import BeautifulSoup
from requests import Session
from lxml import etree
from lxml.cssselect import CSSSelector
"""
from openerp import models, fields, api


_logger = logging.getLogger(__name__)


class cron_cotizacion_webscrap(models.Model):
    _name = "geopatagonia.cron_cotizacion_webscrap"

    _auto = False
    
        
    @api.model
    def get_state_from_cotizacion_webscrap(self):
    """
if __name__ == '__main__':
            
        
        try:
            s = Session()
            payload = {'moneda':'2','B1':'enviar'}

            url_cotizacion= "https://www.bcra.gob.ar/PublicacionesEstadisticas/Planilla_cierre_de_cotizaciones.asp"
            r = s.post(url=url_cotizacion,data=payload)
            soup = BeautifulSoup(r.content,"lxml")

            data = soup.select("div.contenido td")[4:7]
            
            for i in xrange(0,len(data),3):
                fecha = data[i].text
                i+=1
                compra = data[i].text
                i+=1
                venta = data[i].text
                print "d/m/y: "+fecha +" ; "+compra+" ; "+venta

        except Exception as e:
            raise Warning("Error: Intente nuevamente mas tarde\\n"+e.message)
        finally:
            print 'Done'



