
# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from mega import Mega
import requests
import sys
import click


"""
click.option('-db', prompt='Nombre de la base de datos:',default='base',help='Se obtiene al ingresar a odoo. Por defecto admin')
click.option('-pw', prompt='Master password:',default='admin',help='normalmente en openerp-server.conf. Por defecto admin')
click.option('-srv', prompt='Ip o nombre:',default='localhost',help='Servidor donde se encuentra odoo. Por defecto localhost')
click.option('-p', prompt='Puerto (ej:8069):',default='80',help='Puerto. Por defecto 80')
click.option('-d', prompt='Salida a (ej:/home/carlos/):',default='D:/',help='Directorio de salida (debe tener permisos de escritura). Por defecto D:/')
click.option('-f', default='zip',help='Formato (zip/dump):')

"""
@click.command()

@click.option('-db',default='base',help='Se obtiene al ingresar a odoo. Por defecto admin')
@click.option('-pw', default='admin',prompt='pass',hide_input=True,help='normalmente en openerp-server.conf. Por defecto admin')
@click.option('-srv',default='localhost',help='Servidor donde se encuentra odoo. Por defecto localhost')
@click.option('-p', default='80',help='Puerto. Por defecto 80')
@click.option('-d',default='D:/',help='Directorio de salida (debe tener permisos de escritura). Por defecto D:/')
@click.option('-f', default='zip',help='Formato (zip/dump):')
@click.option('-um',prompt='Usuario de mega:', help='Usuario de mega')
@click.option('-pm',prompt='Password de mega:', help='Password de mega')
def download_database(pw, db,srv,p,d,f,um,pm):
        try:
            #payload = {'master_pwd':'d54b1048','name':'geo_prod','backup_format':'zip'}
            payload = {'master_pwd':pw,'name':db,'backup_format':f}

            url= "http://"+srv+":"+p+"/web/database/backup"
            #url= "http://192.168.1.200/web/database/backup"

            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded', 'Accept-Encoding': 'gzip, deflate','DNT': '1'}

            
            r = requests.post(url=url,data=payload,allow_redirects=True, stream = True,headers=headers)

            filename = r.headers.get('Content-Disposition',"asd''acceso_denegado.txt").split("'")[2]
            #if r.ok & (r.headers['Content-Encoding']=='gzip'): 
            with open(d+"/"+filename,'wb') as f: 
                    f.write(r.content) 


            mega = Mega()

            m = mega.login(um, pm)

            file = m.upload(d+"/"+filename)

        except Exception as e:
            raise Warning("Error: Intente nuevamente mas tarde\\n"+e)
        finally:
            
            print ("Done")





if __name__ == '__main__':
    print ("the script has the name %s" % (sys.argv))
    download_database()


