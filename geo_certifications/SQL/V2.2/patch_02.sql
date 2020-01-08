/*

Parche  para corregir el estado como "facturacion" si es que tiene la fecha de factura. 

*/


select * from certifications_certification_ceyf ce inner join certification_invoice inv on ce.invoice_id = inv.id
where ce.state in ('carga','proceso_facturacion')
and ce.antique_register is not null
and inv.invoice_date is not null
--and operadora_id = 10


update certifications_certification_ceyf mio set state = 'facturacion'
from certifications_certification_ceyf ce inner join certification_invoice inv on ce.invoice_id = inv.id
where mio.state in ('carga','proceso_facturacion')
and mio.antique_register is not null
and inv.invoice_date is not null
and mio.id=ce.id