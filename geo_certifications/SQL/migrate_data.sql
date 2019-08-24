--agregamos las columnas a res_partner. Sin esto no arranca la app
ALTER TABLE public.res_partner
    ADD COLUMN company_operator_code character varying COLLATE pg_catalog."default",
    ADD COLUMN is_company_operator boolean;

-- update numero de supervisor para que pase la constraint
update certifications_supervisor set "numeroSupervisor" = 101 where id = 13;
update certifications_supervisor set "numeroSupervisor" = 102 where id = 4;
update certifications_supervisor set "numeroSupervisor" = 103 where id = 30;


--************** Actualizar la aplicacion.*****************


-- actualizando y limpiando tipos de confirmacion y confirmacion.
--check
select  distinct op.name,op.id,ce.tipo_confirmacion,ce.confirmacion from certifications_certification ce,res_partner op 
where tipo_confirmacion='habilita'
and ce.operadora_id=op.id
and op.id not in (10,57);
--update
update certifications_certification set tipo_confirmacion='factura'
where tipo_confirmacion='habilita'
and operadora_id not in (10,57);


--Migrando datos a ceyf
INSERT INTO certifications_certification_ceyf (id, operadora_id, supervisor_id,fecha_realizacion,bombeador,create_date,pozo,operacion,
											 state, equipo, fecha_cierre, write_date,write_uid,create_uid,blscemento,parte,yacimiento,
											  valor_productos,valor_servicios,valor_total)
SELECT id,operadora_id, supervisor,fecha_realizacion,bombeador,create_date,pozo,operacion,
											CASE WHEN state='aprobado' THEN 'cobrado'
											  	WHEN state='carga' THEN 'carga'
											    WHEN state='operadora' THEN 'proceso_facturacion'
											    WHEN state='validado' THEN 'facturacion'
											END
											 , equipo, fechacierre, write_date,write_uid,create_uid,blscemento,parte,yacimiento,
											 valorproductos,valorservicios,valortotal
FROM certifications_certification;

--migrando columnas de valores (son todos U$S)
update certifications_certification set valor_productos = valorproductos;
update certifications_certification set valor_servicios = valorservicios;
update certifications_certification set valor_total = valortotal;


--reinicializar la secuencia de ceyf
select setval('certifications_certification_ceyf_id_seq', (select max(id)+1 from certifications_certification), false);


--delete from certifications_certification_ceyf 
--delete from certification_invoice

--limpieza de partner
-- limpiar partners de operadoras
delete from res_partner where id in (27,90, 85, 87, 88, 89,79,26,71,56,74,68,69,72,70,73,81,86);

update res_partner set company_type = 'company' where id in (25,60);--termap

update res_partner set name = 'Pan American Energy (PAE)' where id = 5;


-- Migracion de "mano de obra" a "operadora".
update certifications_certification set
    operadora_id = 
		CASE 
			WHEN operadora_id = 57 THEN 10 --ypf
			WHEN operadora_id = 58 THEN 11 --sinopec
			WHEN operadora_id = 59 THEN 14 --tecpetrol
			WHEN operadora_id = 60 THEN 17 --capsa
			WHEN operadora_id = 61 THEN 17 --capsa (repetido)
			WHEN operadora_id = 62 THEN 5 --pae
			else operadora_id
		END;

update certifications_certification_ceyf set
    operadora_id = 
		CASE 
			WHEN operadora_id = 57 THEN 10 --ypf
			WHEN operadora_id = 58 THEN 11 --sinopec
			WHEN operadora_id = 59 THEN 14 --tecpetrol
			WHEN operadora_id = 60 THEN 17 --capsa
			WHEN operadora_id = 61 THEN 17 --capsa (repetido)
			WHEN operadora_id = 62 THEN 5 --pae
			else operadora_id
		END;


-- load who is company operator
update res_partner set is_company_operator = True where id in(5,6,10,14,17,11,25,53);
update res_partner set is_company_operator = False where id in(57,58,59,60,61,62);


-- load company_operator_code (quitar esto y colocarlo en res_partner para reconfigurar)
update res_partner set company_operator_code = 'pae' where id in( 5);
update res_partner set company_operator_code = 'ypf' where id in(10);
update res_partner set company_operator_code = 'sinopec' where id in(11);
update res_partner set company_operator_code = 'tecpetrol' where id in(14);
update res_partner set company_operator_code = 'capsa' where id in(17);
update res_partner set company_operator_code = 'enap' where id in(6);
update res_partner set company_operator_code = 'otros' where id in(25,53);--termap,internergy

--update res_partner set company_operator_code = null where id in(57,58,59,60,61,62);


-- desactivando supervisores solicitados en documento 15/08/2019.
update certifications_supervisor set activo = false
where id in (12,10,9,15,13,6);

--cambiando el lenguaje a español de españa para que se muestren bien todas las traducciones.
-- solicitado en documento 15/08/2019.
-- previo a esto se debe actualizar el proyecto con el cliente de transifex
update res_partner set lang = 'es_ES' where lang is not null;
-- cargar el nuevo idioma desde la aplicacion.


update certifications_certification_ceyf set antique_register = CURRENT_TIMESTAMP;

ALTER TABLE certification_invoice
    ADD COLUMN certifications_certification_id integer;

--Migrar factura
INSERT INTO certification_invoice(
	certifications_certification_id,create_uid, create_date, 
	invoice_date_charge, invoice_date, write_uid, currency_id, 
	write_date, invoice_number, valor_total)
	SELECT 
	ce.id, ce.create_uid, ce.create_date,ce.fechacierre,ce.fecha_realizacion,ce.write_uid,ce.currency_id,
	ce.write_date,
		case when
		ce.tipo_confirmacion='factura' then ce.confirmacion
		else ''
		end,
		valortotal
	from certifications_certification ce;

update certifications_certification set 
	invoice_id = certification_invoice.id
	from certification_invoice
	where certifications_certification.id=certification_invoice.certifications_certification_id;
	
update certifications_certification_ceyf set 
	invoice_id = certification_invoice.id
	from certification_invoice
	where certifications_certification_ceyf.id=certification_invoice.certifications_certification_id;


ALTER TABLE certification_invoice
    DROP COLUMN certifications_certification_id;

--migrar habilita
update certifications_certification_ceyf set 
	habilita = certifications_certification.confirmacion
	from certifications_certification
	where certifications_certification.tipo_confirmacion='habilita'
	and certifications_certification_ceyf.id = certifications_certification.id;

update certifications_certification set 
	habilita = confirmacion
	where tipo_confirmacion='habilita';

--migrar hesop
update certifications_certification_ceyf set 
	hesop = certifications_certification.confirmacion
	from certifications_certification
	where certifications_certification.tipo_confirmacion='hes'
	and certifications_certification_ceyf.id = certifications_certification.id;

--migrar facturas y habilita mal cargados.
select * from certifications_certification where tipo_confirmacion is null;

--> en confirmacion like 'FAC' or 'HAB' ->migrar split con ' ' 
SELECT SPLIT_PART(confirmacion,' ',2) as dato,SPLIT_PART(confirmacion,' ',1) as tipo FROM certifications_certification
 where tipo_confirmacion is null;

--migrando habilita mal cargado
update certifications_certification_ceyf set 
habilita = replace(replace(SPLIT_PART(certifications_certification.confirmacion,' ',2),'N',''),'ª','')
	from certifications_certification
	where certifications_certification.tipo_confirmacion is null
	and certifications_certification_ceyf.id = certifications_certification.id
	and SPLIT_PART(certifications_certification.confirmacion,' ',1) like upper('%HAB%');

--migrando nro factura mal cargado
update certification_invoice set 
	invoice_number = replace(replace(SPLIT_PART(certifications_certification.confirmacion,' ',2),'N',''),'ª','')
	from certifications_certification
	where certifications_certification.tipo_confirmacion is null
	and certifications_certification.invoice_id = certification_invoice.id
	and SPLIT_PART(certifications_certification.confirmacion,' ',1) like upper('%FAC%');


-- agregando grupo de seguridad para todos los usuarios.
insert into res_groups_users_rel 
select (select id from res_groups where name like '%Administrador de Certificaciones%'),id  from res_users where active = true and id != 1



--borrado de columnas viejas
ALTER TABLE certifications_certification DROP COLUMN parte;
ALTER TABLE certifications_certification DROP COLUMN operacion;
ALTER TABLE certifications_certification DROP COLUMN blscemento;
ALTER TABLE certifications_certification DROP COLUMN confirmacion;
ALTER TABLE certifications_certification DROP COLUMN bombeador;
ALTER TABLE certifications_certification DROP COLUMN equipo;
ALTER TABLE certifications_certification DROP COLUMN valorservicios;
ALTER TABLE certifications_certification DROP COLUMN supervisor;
ALTER TABLE certifications_certification DROP COLUMN valorproductos;
ALTER TABLE certifications_certification DROP COLUMN yacimiento;
ALTER TABLE certifications_certification DROP COLUMN fechacierre;
ALTER TABLE certifications_certification DROP COLUMN valortotal;
ALTER TABLE certifications_certification DROP COLUMN fecha_realizacion;
ALTER TABLE certifications_certification DROP COLUMN tipo_confirmacion;
ALTER TABLE certifications_certification DROP COLUMN valor_a_facturar;






