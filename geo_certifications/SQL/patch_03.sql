
--Estos 2 registros no se tocan!
select * from certifications_certification_ceyf, certification_invoice
where 
certifications_certification_ceyf.invoice_id = certification_invoice.id
and certifications_certification_ceyf.id in(1794,1763)
--and certifications_certification_ceyf.fecha_realizacion = certification_invoice.invoice_date



--actualizando "todo lo que tiene confirmacion -> facturacion." son 1718 registros
update certifications_certification_ceyf 
set state = 'facturacion'
select * 
from certifications_certification, certification_invoice, certifications_certification_ceyf 
where
certifications_certification.id = certifications_certification_ceyf.id
and certifications_certification_ceyf.invoice_id = certification_invoice.id
and certifications_certification.confirmacion is not null
and certifications_certification_ceyf.antique_register is not null
--and certifications_certification_ceyf.id in(1794,1763)

--Ningún registro viejo puede estar en estado cobrado.
-- pasar todos los registros cobrados como "facturacion". Asumiste que todos los "cobrados estaban bien migrados"
update certifications_certification_ceyf set state = 'facturacion'
select * from certifications_certification_ceyf 
where state = 'cobrado'
and antique_register is not null

-- limpiar los valores de facturas.
update certification_invoice inv 
set 
	invoice_date = null , 
	invoice_date_charge = null
	from certifications_certification_ceyf ceyf
	where ceyf.antique_register is not null
	and ceyf.invoice_id = inv.id
	and ceyf.id not in(1794,1763)
	
select * from certifications_certification_ceyf, certification_invoice
where 
certifications_certification_ceyf.invoice_id = certification_invoice.id
and certifications_certification_ceyf.fecha_realizacion = certification_invoice.invoice_date
and certifications_certification_ceyf.id not in(1794,1763)
and certifications_certification_ceyf.dm = 'RORTYS0CENZG0002'

select * from certifications_certification, certifications_certification_ceyf, certification_invoice
where 
certifications_certification_ceyf.invoice_id = certification_invoice.id
AND certifications_certification.id = certifications_certification_ceyf.id
and Certifications_certification.PARTE = 'B9MMQO3KATA80007'



-- pasar a "proceso de facturacion" los registros antiguos no facturados (sin confirmacion)
-- Funciono: igual revisar y confirmar.
update certifications_certification_ceyf 
set state = 'proceso_facturacion'
--select * 
from certifications_certification, certification_invoice--,certifications_certification_ceyf
where
certifications_certification_ceyf.id = certifications_certification.id
and certifications_certification_ceyf.invoice_id = certification_invoice.id
and certifications_certification.confirmacion is null
and certifications_certification_ceyf.antique_register is not null
and certification_invoice.invoice_number is null
and certifications_certification_ceyf.id not in(1794,1763)

--no correr este update.
update certifications_certification_ceyf
set state = 'facturacion'
select * from 
certifications_certification ce inner join certifications_certification_ceyf ceyf 
	on ce.id = ceyf.id inner join
certification_invoice inv on ceyf.invoice_id = inv.id
where
ce.confirmacion is null
and ceyf.antique_register is not null
and inv.invoice_number is not null
	 
	 