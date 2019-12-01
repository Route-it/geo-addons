# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError

import logging
import datetime
from dateutil.relativedelta import relativedelta
import locale

_logger = logging.getLogger(__name__)

class certifications_certification_coiled_tubing(models.Model):
	_name= 'certifications.certification_coiled_tubing'
	_inherit = 'certifications.certification'
	
	_description = 'Certificaciones Coiled Tubing'

	_order = 'fecha_inicio desc'
	
	
	OPERATIONS = [("servicio_ct","SERVICIO CT"),("tapon","Tapón"),("cementacion","Cementación"),("punzado","Punzado"),
				("trailer","Tráiler"),("linea_venteo","Linea Venteo"),
				("producto","Producto")]
	
	
	contrato = fields.Many2one(required=True)
	
	"""
	equipo = fields.Selection([('UCT1','UCT-1'),
								('UCT2','UCT-2'),
								('UCT3','UCT-3'),
								('UCT4','UCT-4'),
								('UCT5','UCT-5')],required=True,string="Equipo",track_visibility='onchange')
	"""
	equipo = fields.Many2one("certification.plant",required=True,track_visibility='onchange',string="Equipo")		

	
	fecha_inicio = fields.Date(required=True,string="Fecha de inicio")
	fecha_fin = fields.Date(required=True,string="Fecha de fin")
	operacion = fields.Selection(OPERATIONS,required=True,string="Operación")
	regional = fields.Selection([("chubut","Chubut"),("santa_cruz","Santa Cruz"),("neuquen","Neuquen")],required=True,string="Regional")

	observaciones = fields.Text(string="Observaciones",help="Destinado a clarificar detalles. No incluir eventos, valores, vencimientos, fechas, etc.")
		
	operating_hours = fields.Integer("Horas Operativas")

	time_losed_ids = fields.One2many(comodel_name="certifications.coiled_tubing_time_losed",inverse_name="certification_coiled_tubing_id",string ="Horas Perdidas", ondelete='cascade', domain=[('time_losed_quantity','!=',0)])
	
	
	@api.constrains('fecha_inicio','fecha_fin','operacion')
	def check_servicio_ct_in_month(self):
		if self.operacion == 'servicio_ct':
			f_inicio = datetime.datetime.strptime(self.fecha_inicio, '%Y-%m-%d')
			f_fin = datetime.datetime.strptime(self.fecha_fin, '%Y-%m-%d')
			if (f_inicio.year != f_fin.year) or  (f_inicio.month != f_fin.month):
				raise ValidationError('Las fecha de inicio y la fecha de fin deben estar en el mismo mes para operaciones "SERVICIO CT"')

				

	@api.constrains('operating_hours','time_losed_ids','equipo')
	def check_max_plant_work(self):
		if self.operacion == 'servicio_ct':
			f_inicio = datetime.datetime.strptime(self.fecha_inicio, '%Y-%m-%d')
			first_day_of_month = datetime.datetime(f_inicio.year, f_inicio.month, 1)
			last_date_of_month = datetime.datetime(f_inicio.year, f_inicio.month, 1) + relativedelta(months=1, days=-1)
			last_date_of_month = last_date_of_month.replace(minute=59, hour=23, second=59, microsecond=0)

			operaciones = self.env['certifications.certification_coiled_tubing'].search([
											('equipo','=',self.equipo.id),
											('operacion','=','servicio_ct'),
											('fecha_inicio','<=',last_date_of_month),
											('fecha_inicio','>=',first_day_of_month),
											])
			
			hours_by_month = self.equipo._get_hours_by_month_for_month(f_inicio)
			hours_losed = 0
			hours_operated = 0
			for op in operaciones:
				hours_operated = hours_operated + op.operating_hours 
				for tli in op.time_losed_ids:
					hours_losed = hours_losed + tli.time_losed_quantity
		
			real_oper_hours = hours_operated - hours_losed

			if hours_by_month<real_oper_hours:
				loc = locale.getlocale(locale.LC_TIME)
				try:
					locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
				except: pass	
		
				mes = f_inicio.strftime('%B').capitalize()
				
				try:
					locale.setlocale(locale.LC_TIME, loc[0]+'.'+loc[1])	
				except: pass	
				#locale.setlocale(locale.LC_TIME, self.env.context['lang']+'.UTF-8')					
				raise ValidationError('Las horas operativas de todos las operaciones, son '+str(real_oper_hours-hours_by_month)+' mayores a las permitidas por el equipo para el mes de '+mes)

	def check_fields_for_state(self,fields_to_check,vals):
		yes = True
		for it in fields_to_check:
			yes = (True if (vals.get(it)!=None or eval('self.'+it)!=False) and vals.get(it)!=False else False) and yes
			if not yes: break
		return yes

	fields_to_check_carga = ['operadora_id','contrato','equipo','pozo',
					'fecha_inicio','fecha_fin','operacion',
					'regional']
	fields_to_check_proceso_facturacion = ['dm','habilita']
	fields_to_check_facturacion = ['invoice_date','invoice_number','valor_total_factura_computed']
	fields_to_check_cobrado = ['invoice_date_charge']
	
	
	@api.onchange('operadora_id')
	@api.one
	def change_confirmation_with_company_operator(self):
		if self.operadora_id != False:
			if self.operadora_id.company_operator_code != 'ypf':
				self.dm = ''
				self.habilita = ''
			
	
	
	@api.multi
	def write(self, vals):
		#determine state
		
		res = super(certifications_certification_coiled_tubing, self).write(vals)
		
		if vals.get('state') is None:
		
			state = 'carga'
			if self.check_fields_for_state(self.fields_to_check_carga,vals): 
				if (vals.get('valor_total')!=None and vals.get('valor_total')!=False and vals.get('valor_total')>0) \
					or (self.valor_total!=False and self.valor_total>0): 
						state = 'proceso_facturacion' 
			
			#solo si es ypf
			#if self.company_operator_code == 'ypf':
			if self.check_fields_for_state(self.fields_to_check_facturacion,vals): 
				if (vals.get('valor_total_factura_computed')!=None and vals.get('valor_total_factura_computed')!=False and vals.get('valor_total_factura_computed')>0) or (self.valor_total_factura_computed!=False and self.valor_total_factura_computed>0):
					if self.check_fields_for_state(self.fields_to_check_proceso_facturacion,vals):
						state = 'facturacion'
					else:
						raise ValidationError("Debe completar DM y Habilita")
						return
				else:
					mensaje = 'El valor total de factura debe ser mayor que 0'
					self.message_post(body=mensaje)
					self.env.user.notify_info(mensaje)
			#else:
			#	state = 'facturacion'
			if self.check_fields_for_state(self.fields_to_check_cobrado,vals): state = 'cobrado' 
			self.state = state

		""" comentado a pedido en reunion 10/09/2019
		else:
			if vals.get('state') == 'carga':
				for item in self.fields_to_check_proceso_facturacion + self.fields_to_check_cobrado:
					vals[item] = False
			if vals.get('state') == 'proceso_facturacion':
				for item in self.fields_to_check_cobrado:
					vals[item] = False
		"""
		
		
		return res
		
	@api.model
	def create(self, vals):
		
		#create dummy invoice object and link with them
		id_inv = self.env['certification.invoice'].create([])
		vals['invoice_id'] = id_inv.id
		
		
		item = super(certifications_certification_coiled_tubing, self).create(vals)
		
		#check if state is completed
		#if self.check_fields_for_state(self.fields_to_check_carga,vals): 
		#	item.state = 'proceso_facturacion'  

		id_time_l = self.env['certifications.coiled_tubing_time_losed'].create({'certification_coiled_tubing_id': item.id,
																			'time_losed_quantity':0})
		
		
		return item  


	def suscribe_specific_partners(self,certif,partner_ids=[]):
		partner_ids = self.env['res.users'].search([('active','=',True)]).mapped('partner_id').ids
		super(certifications_certification_coiled_tubing, self).suscribe_specific_partners(certif,partner_ids)


	def name_get(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
	
		res = []
		for record in self.browse(cr, uid, ids, context=context):
			name = record.operadora_id.name
			pozo = ''
			equipo = ''
			invoice_number = ''
			if record.pozo:
				pozo = '(pzo:'+record.pozo+')' or ''
			if record.equipo:
				equipo = '('+record.equipo.name+')' or ''
			if record.invoice_number:
				invoice_number = '- Fact:'+ record.invoice_number or ''
			appeler = name + pozo + equipo + invoice_number
			
			res.append((record.id, appeler))

		return res

