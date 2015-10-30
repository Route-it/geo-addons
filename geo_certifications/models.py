# -*- coding: utf-8 -*-

from openerp import models, fields, api

class GeoCertification(models.Model):
	_name = 'certifications.certification'
	
	parte = fields.Char()
	pozo = fields.Char()
	operadora = fields.Many2one('res.partner',domain = [('is_company','=','True')])
	yacimiento = fields.Selection([('chubut','Chubut'),('santa cruz','Santa Cruz')])
	supervisor = fields.Many2one('certifications.supervisor')
	
class GeoCertificationSupervisor(models.Model):
	_name = "certifications.supervisor"
	
	nombre = fields.Char()
	apellido = fields.Char()
	operacionesHechas = fields.Integer()
	nivelOperacion = fields.Selection([('1','1'),('2','2'),('3','3')])
	