# -*- coding: utf-8 -*-

from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)




class certifications_coiled_tubing_time_losed(models.Model):
	_name = "certifications.coiled_tubing_time_losed"

	
	time_losed_quantity = fields.Integer("Horas Perdidas", required=True)
	reason = fields.Selection(string="Motivo de NPT",[
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
						])

	
	comments = fields.Text("Comentarios")
	monetary_losed = fields.Monetary("Perdida (USD)")

	certification_coiled_tubing_id = fields.Many2one("certifications.certification_coiled_tubing","Certificación")
	
	
	currency_id = fields.Many2one('res.currency', string='Account Currency',
    							help="Forces all moves for this account to have this account currency.")
	
	def name_get(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
	
		res = []
		for record in self.browse(cr, uid, ids, context=context):
			name = record.reason + ' > ' + str(record.time_losed_quantity) +'hs'
			res.append((record.id, name))
		
		return res
	
	
