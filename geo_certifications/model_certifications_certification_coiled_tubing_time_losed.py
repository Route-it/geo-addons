# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging
import locale
from datetime import datetime

_logger = logging.getLogger(__name__)




class certifications_coiled_tubing_time_losed(models.Model):
	_name = "certifications.coiled_tubing_time_losed"

	_order = 'equipo, fecha_inicio_related desc, pozo, time_losed_quantity'

	@api.depends('certification_coiled_tubing_id.fecha_inicio','certification_coiled_tubing_id.fecha_fin','certification_coiled_tubing_id.valor_total_list_view','certification_coiled_tubing_id.operating_hours','certification_coiled_tubing_id')
	@api.one
	def _get_month(self):
		if bool(self.certification_coiled_tubing_id.fecha_inicio):
			self.mes = datetime.strptime(self.certification_coiled_tubing_id.fecha_inicio, "%Y-%m-%d").strftime('%B').capitalize()
			if (self.time_losed_quantity != 0):
				self.fecha_inicio = False
				self.fecha_fin = False
				self.operating_hours = False
				self.valor_total_list_view = False
			else:			
				self.fecha_inicio = self.certification_coiled_tubing_id.fecha_inicio
				self.fecha_fin = self.certification_coiled_tubing_id.fecha_fin
				self.operating_hours = self.certification_coiled_tubing_id.operating_hours
				self.valor_total_list_view = self.certification_coiled_tubing_id.valor_total_list_view
			
	
	time_losed_quantity = fields.Integer("Horas Perdidas", required=True,group_operator="sum")
	reason = fields.Selection([
						("falla_operativa","Falla Operativa"),
						("falta_habilitacion","Falta habilitación"),
						("rotura_equipo","Rotura de equipo / Mtto campo"),
						("fuerza_mayor","Fuerza mayor"),
						("problemas_geodata","Problemas Geodata"),
						("falta_personal","Falta de personal"),
						("accidente_personal","Accidente personal"),
						("exceso_horas","Exceso de horas de Mtto"),
						("exceso_dias","Exceso de días de IND"),
						("sindicato","Sindicato"),
						("problemas_bop","Problemas con BOP"),
						("exceso_frague","Exceso de fragüe"),
						("corte_pinchadura","Corte de caño/Pinchadura"),
						("otro","Otros")
						],string="Motivo de NPT")

	
	comments = fields.Text("Comentarios")
	monetary_losed = fields.Monetary("Perdida (USD)",group_operator="sum")

	certification_coiled_tubing_id = fields.Many2one("certifications.certification_coiled_tubing","Certificación")
	
	pozo = fields.Char(related="certification_coiled_tubing_id.pozo",store=True)
	equipo = fields.Many2one(related="certification_coiled_tubing_id.equipo",store=True)
	mes = fields.Char("Mes",
					#default=lambda self: self._get_month()
					compute="_get_month",store=True)
	
	fecha_inicio_related = fields.Date(related="certification_coiled_tubing_id.fecha_fin",store=True)


	
	fecha_inicio = fields.Date(string="Fecha Inicio", compute="_get_month",store=True)
	fecha_fin = fields.Date(string="Fecha Fin",  compute="_get_month",store=True)
	
	valor_total_list_view = fields.Monetary(string="Valor [USD]", compute="_get_month",store=True)
	operating_hours = fields.Integer(string="Horas operativas", compute="_get_month",store=True)

	company_id = fields.Many2one('res.company', 'Company',default=lambda self:self.env.user.company_id, index=1)
	currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self:self.env.user.company_id.currency_id,required=True)	 

	#@api.model
	#def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
	#	return super(certifications_coiled_tubing_time_losed, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=False)

	def name_get(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
	
		res = []
		name = ''
		for record in self.browse(cr, uid, ids, context=context):
			if (record.reason):
				reason = [item[1] for item in record._fields.get('reason')._column_selection if record.reason in item]
				if len(reason)>0:
					name = reason[0] + ' (' + str(record.time_losed_quantity) +'hs)'
				else:
					name = 'Sin Razon (' + str(record.time_losed_quantity) +'hs)'
				
			else:
				name = 'Operativas' + ' (' + str(record.operating_hours) +'hs)'
			res.append((record.id, name))
		
		return res
	
	
