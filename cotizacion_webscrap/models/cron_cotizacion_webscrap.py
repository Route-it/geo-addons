
# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''
import logging

from bs4 import BeautifulSoup
from requests import Session

import datetime

from openerp import models, fields, api


_logger = logging.getLogger(__name__)


class cron_cotizacion_webscrap(models.Model):
    _name = "exchange.cron_cotizacion_webscrap"

    _auto = False
        
    @api.model
    def get_last_exchange_bcra_webscrap(self):
    #if __name__ == '__main__':
        _logger.info("arrancando session")
        s = Session()
        
        ##
        ## Cotizacion al cierre del dia anterior o historica
        ##
                
        try:
            payload = {'moneda':'2','B1':'enviar'}

            url_cotizacion= "https://www.bcra.gob.ar/PublicacionesEstadisticas/Planilla_cierre_de_cotizaciones.asp"
            _logger.info("arrancando post")
            r = s.post(url=url_cotizacion,data=payload, verify=False)
            _logger.info("arrancando bs4")
            soup = BeautifulSoup(r.content,"lxml")
            model_cotizacion_dolar_bcra = self.env['exchange.cotizacion_dolar_bcra']
            count = len(model_cotizacion_dolar_bcra.search([]))
            todos = soup.select("div.contenido td")
            todos_len = (len(todos)-4)
            a_restar = todos_len%3
            todos_len = todos_len - a_restar - 2 
            _logger.info("arrancando seleccion de cuantos")
            if count == 0:
                #no hay ninguna cotizacion cargada
                data = soup.select("div.contenido td")[4:todos_len]
            else:
                #cargo la ultima cotizacion.
                data = soup.select("div.contenido td")[4:7]
            
            c_data = {}
            _logger.info("arrancando for")
            for i in xrange(0,len(data),3):
                fecha = data[i].text
                fecha_obj = datetime.datetime.strptime(fecha, '%d-%m-%Y')
                i+=1
                compra = data[i].text
                i+=1
                venta = data[i].text
                c_data['fecha'] = fecha_obj
                c_data['compra'] = float(compra.replace(",","."))
                c_data['venta'] = float(venta.replace(",","."))

                cotizacion = model_cotizacion_dolar_bcra.search([['fecha','=',fecha_obj]])
                if len(cotizacion)==0:
                    #solo si la cotizacion no existe, la creo
                    _logger.info("creando")
                    exchange_at_close_date = model_cotizacion_dolar_bcra.create(c_data)
                else:        
                    #si existe, la actualizo
                    _logger.info("actualizando")
                    cotizacion.write(c_data)
                #print "d/m/y: "+fecha +" ; "+compra+" ; "+venta

        except Exception as e:
            _logger.info("error %s",e.message)
            #raise Warning("Error: Intente nuevamente mas tarde\\n"+e.message)
            print "Error: Intente nuevamente mas tarde\\n"+e.message
        finally:
            _logger.info("done")
            print 'Done'
        """
        
        ##
        ## Cotizacion del dia
        ##
        
        
        try:
            payload = {'moneda':'2','B1':'enviar','fecha':'05/09/2019'}

            url_cotizacion= "https://www.bcra.gob.ar/PublicacionesEstadisticas/Tipo_de_cambio_minorista_2.asp"
            r = s.post(url=url_cotizacion,data=payload)
            soup = BeautifulSoup(r.content,"lxml")

            # 0 es planilla por hora
            # 1 horarios  11  13  15
            # 2 compra/venta
            # 3 valores
            data = soup.select("table#tablita td")[11:]
            for i in xrange(0,len(data),2):
                compra = data[i].text
                i+=1
                venta = data[i].text
                
                if (i+1)/2 == 1: print "11 am"
                if (i+1)/2 == 2: print "13 am"
                if (i+1)/2 == 3: print "15 am"
                try:
                    print str(float(compra.replace(",",".")))+" ; "+str(float(venta.replace(",",".")))
                except Exception as e:
                    pass

            
        except Exception as e:
            raise Warning("Error: Intente nuevamente mas tarde\\n"+e.message)
        finally:
            print 'Done'
        """