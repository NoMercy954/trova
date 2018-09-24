from odoo import api, _, tools, fields, models, exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime, date, time
from . import amount_to_text
from dateutil.relativedelta import relativedelta


class TrovaVivienda(models.Model):
	"""docstring for ClassName"""

	_name = 'trova.vivienda'
	_description='Formulario de Viviendas'


	def _folio_default(self):
		cr = self.env.cr
		cr.execute('select "id" from "trova_vivienda" order by "id" desc limit 1')
		id_returned = cr.fetchone()
		if id_returned == None:
			id_returned = (0,)
		text=''
		if((max(id_returned)+1)<100):
			text='00'+str(max(id_returned)+1)
		else:
			text=str(max(id_returned)+1)
		return text
			

	name = fields.Char(string='Folio Real' , size=150, required=True)
	folio = fields.Char(string='Folio', required=True, help='Este es el Folio', default=_folio_default)
	paquete = fields.Many2one('trova.vivienda.paquete',string='Paquete' , size=150, help='Este es el Paquete')
	subasta = fields.Many2one('trova.vivienda.suba', string='Subasta' , size=150, help='Esta es la Subasta')
	desarrollo = fields.Many2one('trova.vivienda.desa', string='Desarrollo' , size=150, help='Este es el desarrollo')
	estado =  fields.Many2one('res.country.state',domain="[('country_id.code','=','MX')]", string="Estado")
	municipio = fields.Many2one('trova.vivienda.muni', string='Municipio' , size=150, help='El municipio')
	entre = fields.Char(string='Entre', size=100, help='Entre que calles')
	tipo_venta = fields.Many2one('trova.vivienda.tipo_venta', string='Tipo de Venta', help='Cual es el tipo de Venta')
	recamaras = fields.Integer('Numero de Recamaras',size=150, required=True, help='Este es el No. de Recamaras')
	fotos = fields.Boolean('Fotos', help='Fotos')
	clg = fields.Boolean('CLG',  help='CLG')
	aca = fields.Boolean('Avaluo Comercial anterior', help='Avaluo Comercial anterior')
	piso = fields.Boolean(string='Piso',  help='Piso')
	proteccion = fields.Boolean('Protecciones',  help='Protecciones')
	avalcat = fields.Boolean('Avaluo Catastral',  help='Avaluo Catastral')
	logo_viv = fields.Binary(string='Logo de encabezado')
	etapas = fields.Selection([('Disponible','Disponible'),
							   ('Invadida','Invadida'),
							   ('Poravaluo','Por avalúo'),
							   ('Porfirma','Por firmar'),
							   ('Firmada','Firmada'),
							   ('Cancelada','Cancelada')], help='Status',index=True, default='Disponible')
	precioventa = fields.Float('Precio de Venta' , required=True, help='Este sera el precio con el que se vendera la vivienda',  obj="res.currency")
	preciocompra = fields.Float('Precio de Compra' , required=True, help='Este sera el precio con el que se comprara la vivienda',  obj="res.currency")
	amount_to_text = fields.Char(compute='_get_amount_to_text', string='Monto en Texto', readonly=True,
                                 help='Amount of the invoice in letter', store=True)
	calle = fields.Char(string='Calle')
	calle2 = fields.Char(string='Colonia')
	estado =  fields.Many2one('res.country.state',domain="[('country_id.code','=','MX')]", string="Estado")
	municipio = fields.Many2one('trova.vivienda.muni', string='Municipio')
	cp = fields.Char(string='CP', size=5)
	noext = fields.Char(string='# Exterior')
	noint = fields.Char(string='# Interior')
	mz_lote = fields.Char(string ='Mza y Lote')
	tipo_casa = fields.Char(string='Tipo de Casa')
	m_sup = fields.Char(string='Metros Sup')
	m_const = fields.Char(string='Metros Const')
	sofol = fields.Char(string='SOFOL')
	denominacion = fields.Char(string='Denominacion')

	@api.one
	@api.depends('precioventa')
	def _get_amount_to_text(self):
		self.amount_to_text = amount_to_text.get_amount_to_text(self, self.precioventa, 'MXN')

	
	@api.onchange('desarrollo')
	def onchange_clien(self):
		if self.desarrollo:
			self.estado = self.desarrollo.estado
			self.municipio = self.desarrollo.municipio


class TrovaVivTitu(models.Model):
	
	_name = 'trova.vivienda.titu'
	_description = 'Pantalla de Titulacion'


	def _name_default(self):
		cr = self.env.cr
		cr.execute('select "id" from "trova_vivienda_titu" order by "id" desc limit 1')
		id_returned = cr.fetchone()
		if id_returned == None:
			id_returned = (0,)
		text=''
		if((max(id_returned)+1)<100):
			text='00'+str(max(id_returned)+1)
		else:
			text=str(max(id_returned)+1)
		return "Titulacion{}".format(text)


	name = fields.Char('Nombre' , size=150, required=True, default=_name_default)
	folio = fields.Many2one('trova.vivienda', string='Folio Real', required=True, help='Este es el Folio Real de la vivienda')
	etapas = fields.Selection(related='folio.etapas', help='Status',index=True,default='Disponible')
	confirmventa = fields.Char(string='Confirmacion de venta')
	presupuesto = fields.Many2one('sale.order', string='Presupuestos')
	asesor = fields.Many2one('res.users',string='Asesor', help='Lista de Asesores')
	tipocredito = fields.Selection([('tradicional','Tradicional'),('contado','Contado')], string='Confirmacion de venta Tipo de Credito')
	observaciones = fields.Selection([('habilitada','Habilitada'),('semihabilitada','Semihabilitada'),('sinhabilitar','Sin Habilitar')],string='Observaciones Vivienda', help='Observaciones')
	comentariostit = fields.Text(string='Comentarios Titulacion', help='Comentarios sobre la Titulacion')
	cliente = fields.Many2one('res.partner',string='Nombre del Cliente')
	nss = fields.Char(string='NSS', help='Ingresa el NSS', size=11)
	telefono = fields.Char(string='Telefono', help='Telefono Fijo')
	notaria = fields.Many2one('trova.notarias',string='Notaria', help='Notaria')
	numcredifona = fields.Integer(string='No. Credito Infonavit', help='Es el numero de credito Infonavit')
	fechacierre = fields.Date(string='Fecha Cierre')
	fechacaducacion = fields.Date(string='Fecha de Caducacion')
	medio_enterado = fields.Char(string='Medio de Enterado', help='Ingresa aqui el medio o la forma por el cual te enteraste del')
	pendientes = fields.Text(string='Faltantes de la Vivienda')
	fecha_concluido = fields.Date(string='Conclucion de Faltantes')
	evaluacion = fields.Many2one('trova_vivienda_eva', string='Evaluacion')
	
	tipo_pago = fields.Char(string='Tipo de Pago')
	num_pago = fields.Char(string='# de Pago')
	num_cuenta = fields.Char(string='# de Cuenta Bancaria')
	nombre_banco = fields.Char(string='Nombre Banco')
	monto_pago = fields.Integer(string='Monto a Pagar')
	precio_mejoras = fields.Integer(string='Precio de mejoras')
	fecha_pago_mejoras = fields.Date(string='Fecha de Pago de mejoras')
	total_pagar = fields.Float(string='Total a Pagar', readonly=True, compute="_total_vivienda")
	precio_vivienda = fields.Integer(string='Precio Vivienda')
	enganche_vivienda = fields.Integer(string='Enganche')
	apartado_vivienda = fields.Integer(string='Apartado')

	@api.depends('precio_mejoras','precio_vivienda')
	def _total_vivienda(self):
	    self.total_pagar = (int(self.precio_vivienda))+(int(self.precio_mejoras))

	
	@api.onchange('presupuesto')
	def onchange_pres(self):
		if self.presupuesto:			
			self.asesor = self.presupuesto.user_id.id
			self.cliente = self.presupuesto.partner_id.id
			self.folio = self.presupuesto.vivienda.id
			self.etapas = self.presupuesto.vivienda.etapas
			self.fechacaducacion = self.presupuesto.validity_date
			if(self.presupuesto.confirmation_date):
				self.confirmventa = str(self.presupuesto.confirmation_date)
			else:
				self.confirmventa='Pendiente'

	@api.onchange('cliente')
	def onchange_clien(self):
		if self.cliente:
			self.nss = self.cliente.nss
			self.telefono = self.cliente.phone
	@api.onchange('folio')
	def onchange_vivienda(self):
		if self.folio:
			self.precio_vivienda = self.folio.precioventa

class TrovaVivDesarollo(models.Model):
	_name = 'trova.vivienda.desa'
	_description = 'Pantalla de Desarrollo'

	name = fields.Char('Nombre' , size=150, required=True)
	estado =  fields.Many2one('res.country.state',domain="[('country_id.code','=','MX')]", string="Estado", required=True)
	municipio = fields.Many2one('trova.vivienda.muni',string='Municipio' , size=150, required=True, help='El municipio')
	
class TrovaVivSaneamiento(models.Model):
	_name = 'trova.vivienda.sanea'
	_description = 'Pantalla de Saneamiento'


	def _name_default(self):
		cr = self.env.cr
		cr.execute('select "id" from "trova_vivienda_sanea" order by "id" desc limit 1')
		id_returned = cr.fetchone()
		if id_returned == None:
			id_returned = (0,)
		text=''
		if((max(id_returned)+1)<100):
			text='00'+str(max(id_returned)+1)
		else:
			text=str(max(id_returned)+1)
		return "Saneamiento{}".format(text)


	name = fields.Char(string='Nombre', size=150, required=True, default=_name_default)
	folioreal = fields.Many2one('trova.vivienda', string='Folio Real', required=True, help='Este es el Folio Real de la Vivienda')
	cuentapredial = fields.Char(string='Cuenta de predial', size=150, )
	mpp = fields.Integer(string='Monto Pagado Predial', size=10, help='Monto pagado del Predial')
	mpcp = fields.Integer(string='Monto Pagado CNA Predial', size=10, help='Monto pagado del CNA Predial')
	fechapp = fields.Date(string='Fecha Pago Predial', help='Fecha en la que se realizo el pago del Predial')
	mpcfe = fields.Integer(string='Monto Pagado CFE', help='Monto total pagado CFE')
	fechapcfe = fields.Date(string='Fecha de Pago CFE', size=150, help='Fecha en la que se realizo el pago del Predial')
	estado =  fields.Many2one('res.country.state',domain="[('country_id.code','=','MX')]", string="Estado", required=True)
	cuentagua = fields.Char(string='Cuenta Agua', size=125, help='Numero de cuenta del Agua')
	mpa = fields.Integer(string='Monto Pagado del Agua', size=10, help='Monto pagado del Agua')
	mpca = fields.Integer(string='Monto Pagado CNA Agua', size=10, help='Monto pagado del CNA Agua')
	fechapa = fields.Date(string='Fecha Pago Agua', help='Fecha en la que se realizo el pago del Agua')
	certioyp = fields.Char(string='Certificado no adeudo Obras y Pavimento', size=150, help='Certificado no adeudo Obras y Pavimento')
	certinof = fields.Char(string='Certificado alineamiento No. Oficial', size=150, help='Certificado alineamiento No. Oficial')
	certinadeu = fields.Char(string='Certificado No adeudo Tesorería', size=150, help='Certificado No adeudo Tesorería')
	no_oficial = fields.Char(string='No. Oficial', size=150, help='No. Oficial')
	certihipo = fields.Char(string='Certificado Hipotecario	', size=150, help='Certificado Hipotecario	')
	certifiscal = fields.Char(string='Certificado Fiscal', size=150, help='Certificado Fiscal')
	juntaurba = fields.Char(string='Junta Urbanización', size=150, help='Junta Urbanización')
	cartografico = fields.Char(string='Cartográfico	', size=150, help='Ubicacion Cartográfica')
	mpcarto = fields.Integer(string='Monto de pagado', help='Monto pagado por cartografico')
	fechacarto = fields.Date(string='Fecha Pago cartografico')
	mpnumofici = fields.Integer(string='Monto pagado por No. Oficial')
	fechanumofi = fields.Date(string='Fecha Pago No. Oficial')	
	secretfinan = fields.Char(string='Secretaria de Finanzas')
	mpsecrefin = fields.Integer(string='Monto a pagar Finanzas')
	fechasecfin = fields.Date(string='Fecha de pago Finanzas')
	secretplanea = fields.Char(string='Secretaria de Planeacion')
	mpsecreplan = fields.Integer(string='Monto a pagar Planeacin')
	fechasecplan = fields.Date(string='Fecha de pago Planeacion')
	mpurba = fields.Integer(string='Monto a pagar Junta')
	fechaurba = fields.Date(string='Fecha de pago Junta')


	@api.onchange('folioreal')
	def onchange_folio(self):
		if self.folioreal:
			self.estado = self.folioreal.estado

class TrovaVivPaq(models.Model):
	_name = 'trova.vivienda.paquete'
	_description = 'Ventana de paquetes'

	name = fields.Char('Nombre' , size=150, required=True)
	estado =  fields.Many2one('res.country.state',domain="[('country_id.code','=','MX')]", string="Estado", required=True)
	corretaje = fields.Boolean(string='Corretaje')
	subastaprop = fields.Boolean(string='Subasta Propia')
	compradir = fields.Boolean(string='Compras Directas')
	prestaserv = fields.Boolean(string='Prestacion de Servicios')

class TrovaVivMuni(models.Model):
	_name = 'trova.vivienda.muni'
	_description = 'Pantalla de Municipio'

	name = fields.Char('Nombre' , size=150, required=True)

class TrovaVivSubasta(models.Model):
	"""docstring for TrovaTitu"""
	_name = 'trova.vivienda.suba'
	_description = 'Pantalla de subasta'

	name = fields.Char('Nombre' , size=150, required=True)

class TrovaVivTipoVenta(models.Model):
	"""docstring for TrovaTitu"""
	_name = 'trova.vivienda.tipo_venta'
	_description = 'Pantalla de Tipo de Venta'

	name = fields.Char('Nombre' , size=150, required=True)

class TrovaEvaluacion(models.Model):

	_name = 'trova.vivienda.eva'
	_description = 'Lista para Evaluacion de vivienda'


	def _name_default(self):
		cr = self.env.cr
		cr.execute('select "id" from "trova_vivienda_eva" order by "id" desc limit 1')
		id_returned = cr.fetchone()
		if id_returned == None:
			id_returned = (0,)
		text=''
		if((max(id_returned)+1)<100):
			text='00'+str(max(id_returned)+1)
		else:
			text=str(max(id_returned)+1)
		return "Evaluacion {}".format(text)	


		

	name = fields.Char(string="Evaluacion", default=_name_default)
	folio_vivienda = fields.Many2one('trova.vivienda',string='Folio Vivienda')
	cliente = fields.Many2one('res.partner',string='Cliente')
	limpieza_gen = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Limpieza general de interiores')
	resanes_danos = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')],string='Resanes de Albañilería daños menores')
	limpeza_patio = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Limpieza de patio trasero y frontal')
	det_pitura_int = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Detalle de pintura interior')
	det_pitura_ext = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Detalle de pintura exterior')
	pint_int = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Pintura de interior')
	pint_ext = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Pintura de exterior')
	pint_techo = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='pintura techo')
	cambio_vidrio = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Cambio de vidrios')
	cambio_perfil = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Cambio de perfiles')
	Cambio_chapa = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Cambio de chapa principal')
	rep_puerta = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Reparación o resane de puertas de media vida')
	puerta_int = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Puertas interiores')
	puerta_ext = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Puertas exterior')
	pint_puerta = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='pintura de puertas de media vida')
	det_piso = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Arreglo de detalles en pisos')
	instalacion_piso = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Instalación de piso (Cuando requiera)')
	acces_sanitario = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Accesorios Sanitarios')
	items_sanitario = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Minerales, Llaves del baño y regaderas')
	muebe_sanitario = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Muebles Sanitarios')
	llave_tarja = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Instalación de llave de tarja')
	inst_tarja = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Instalación y reemplazo de tarja de lavado')
	inst_electrica = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Revisión de instalaciones eléctricas y suministro de energía')
	compl_items_elect = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Complementación de placas, focos contactos y apagadores')
	cableado_gen = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Cableado general de luz')
	check_sis_hidraulico = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Revision de sistema hidráulico suminstros y desagüe')
	sumnin_hidraulicos = fields.Selection([('e','Excelente'),
							   ('b','Bueno'),
							   ('m','Malo')], string='Suministro e instalación de materiales para instalaciones hidraulicas')

		

class TrovaVivSale(models.Model):
	"""docstring for TrovaTitu"""
	_inherit = 'sale.order'

	vivienda = fields.Many2one('trova.vivienda', string="Folio Real Vivienda")
	etapas = fields.Selection([('Disponible','Disponible'),
							   ('Invadida','Invadida'),
							   ('Poravaluo','Por avalúo'),
							   ('Porfirma','Por firmar'),
							   ('Firmada','Firmada'),
							   ('Cancelada','Cancelada')], help='Status',index=True, default='Disponible')

	@api.onchange('vivienda')
	def onchange_vivienda(self):
		if self.vivienda:
			self.etapas = self.vivienda.etapas

class TrovaVivClientes(models.Model):
	_inherit = 'res.partner'

	fechanac=fields.Date(string='Fecha de Nacimiento')
	curp = fields.Char(string='CURP', size=18, help='Ingresa tu CURP')
	esque_credito = fields.Char(string='Esquema de Credito', size=100, help='Escribe tu Esquema de Credito')
	nss = fields.Char(string='NSS', help='Ingresa el Numero de Seguro Social',size=11)
	estado_civil = fields.Selection([('soltero/a','Soltero/a'),
							   ('casado/a','Casado/a'),
							   ('divorciado/a','Divorciado/a'),
							   ('viudo/a','Viuda/a')], help='Estado civil')
	empresa = fields.Char(string='Empresa', size=100, help='Nombre de la empresa')
	numext = fields.Char(string='No Ext', size=100, help='Insgresa el numero exterior')
	entre = fields.Char(string='Entre', size=100, help='Entre que calles')
	municipio = fields.Many2one('trova.vivienda.muni', string='Municipio')
	cp = fields.Char(string='CP',size=10, help='Ingresa el Codigo Postal de tu zona')
	areaodep = fields.Char(string='Area o Departamento', size=100)
	extension = fields.Char(string='Extension', size=20)
	calle = fields.Char(string='Calle', size=100)
	numint = fields.Char(string='No Interior', size=23)
	colonia = fields.Char(string='Colonia', size=100)
	estado =  fields.Many2one('res.country.state',domain="[('country_id.code','=','MX')]", string="Estado", required=True)
	nrp = fields.Char(string='NRP')
	tel = fields.Char(string='Telefono')
	nombcompleto1 = fields.Char(string='Nombre Completo', size=100)
	tel_lada1 = fields.Char(string='Tel (lada)', help='Ingresa tu numero telefonico empezando con tu lada')
	refer1 = fields.Boolean(string='Referencia correcta 1')
	nombcompleto2 = fields.Char(string='Nombre Completo', size=100)
	tel_lada2 = fields.Char(string='Tel (lada)', help='Ingresa tu numero telefonico empezando con tu lada')
	refer2 = fields.Boolean(string='Referencia correcta 2')
	tipocredito = fields.Selection([('tradicional','Tradicional'),('contado','Contado')], string='Confirmacion de venta Tipo de Credito')
	credito_conyu = fields.Boolean(string='Credito Conyugal')

	regimen_matrimonial = fields.Char(string="Regimen Matrimonial")
	name_cony = fields.Char(string='Nombre')
	empr_cony = fields.Char(string='Empresa de la Conyuge')
	rfc_cony = fields.Char(string="RFC")
	nss_cony = fields.Char(string='NSS', size=11)
	regimen = fields.Char(string='Regimen')
	antigue_cony = fields.Char(string='Antiguedad')
	dept_cony = fields.Char(string='Departamento')
	calle_cony = fields.Char(string='Calle')
	noext_cony = fields.Char(string='# Exterior')
	noint_cony = fields.Char(string ='# Interior')
	tel_casa_cony = fields.Integer(string='Telefono Casa')
	tel_trabajo_cony = fields.Integer(string='Telefono Trabajo')
	cel_cony = fields.Integer(string='Telefono Celular')

	name_benef1 = fields.Char(string='Nombre beneficiario 1')
	name_benef2 = fields.Char(string='Nombre beneficiario 2')
	porcent_benf1 = fields.Integer(string='Porcentaje1') 
	porcent_benf2 = fields.Integer(string='Porcentaje2')
	prentesco1 = fields.Char(string='Parentesco 1')
	prentesco2 = fields.Char(string='Parentesco 2')
	edad = fields.Integer(string='Edad', compute='_compute_age')
	lugar_nacimiento =fields.Char(string='Lugar de Nacimiento')

	@api.multi
	@api.depends('fechanac')
	def _compute_age(self):
	    for record in self:
	        if record.fechanac and record.fechanac <= fields.Date.today():
	            record.edad = relativedelta(
	                fields.Date.from_string(fields.Date.today()),
	                fields.Date.from_string(record.fechanac)).years 
	        else: 
	            record.edad = 0	

class TrovaNotarias(models.Model):

	_name = 'trova.notarias'
	_description = 'Creacion de Notarias'


	name = fields.Char(string='Notario')
	num_notaria = fields.Integer(string='Numero de Notaria')
	notaria = fields.Char(string='Notaria',compute='merge_func')
	calle = fields.Char(string='Calle')
	calle2 = fields.Char(string='Colonia')
	estado =  fields.Many2one('res.country.state',domain="[('country_id.code','=','MX')]", string="Estado")
	municipio = fields.Many2one('trova.vivienda.muni', string='Municipio')
	cp = fields.Char(string='CP', size=5)
	tel = fields.Char(string='Tel (lada)', help='Ingresa tu numero telefonico empezando con tu lada')
 
	@api.depends('estado','municipio')
	def merge_func(self):
	    self.notaria = (str(self.estado.name) or '')+','+(str(self.municipio.name) or '')