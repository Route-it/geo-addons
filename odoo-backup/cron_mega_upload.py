
# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from mega import Mega
import sys
import click


"""
click.option('-u', prompt='Nombre de usuario:',help='Se obtiene al ingresar a odoo. Por defecto admin')
click.option('-p', prompt='Password:',help='normalmente en openerp-server.conf. Por defecto admin')
click.option('-f', help='Nombre del archivo')

"""
@click.command()

@click.option('-u',prompt='usuario',help='Se obtiene al ingresar a odoo. Por defecto admin')
@click.option('-p',prompt='pass',hide_input=True,help='normalmente en openerp-server.conf. Por defecto admin')
@click.option('-f',help='archivo a subir')
def upload_file(u,p,f):
        try:
            mega = Mega()

            m = mega.login(u, p)

            file = m.upload(f)
            #folder = m.find('my_mega_folder')

            #file = m.upload('myfile.doc', folder[0])
            

            #files = mega.get_files()
            #print ("")
            
            """
            file = m.find('myfile.doc')
            m.download(file)
            m.download_url('https://mega.co.nz/#!utYjgSTQ!OM4U3V5v_W4N5edSo0wolg1D5H0fwSrLD3oLnLuS9pc')
            m.download(file, '/home/john-smith/Desktop')
            # specify optional download filename (download_url() supports this also)
            m.download(file, '/home/john-smith/Desktop', 'myfile.zip')
            """
        except Exception as e:
            raise Warning("Error: Intente nuevamente mas tarde\\n"+e)
        finally:
            print ("Done")





if __name__ == '__main__':
    print ("the script has the name %s" % (sys.argv))
    upload_file()


