INSERT INTO certification_contract(
	 create_uid, create_date, description, write_uid, write_date, active, name)
	VALUES ( 1, now(), 'Sin Contrato', 1, now(), false,'Sin Contrato');

select * from certifications_certification_ceyf
where operadora_id = 10
and antique_register is not null; --YPF

update certifications_certification_ceyf set contrato= (select max(id) from certification_contract)
where operadora_id = 10
and antique_register is not null; --YPF

update certifications_certification_ceyf set evento='Sin Evento' 
where (operadora_id = 10 --YPF
	   or operadora_id = 5) --PAE
	   and operacion='patagoniano'
and antique_register is not null; 

--(averiguar duplicado de operadora)
select * from res_partner where company_operator_code is not null

update res_partner set display_name = name
where id = 5


update certifications_certification_ceyf set operadora_id = 5 
where operadora_id = 92;

delete from res_partner where id = 92;

select count(*),operadora_id from certifications_certification_ceyf where antique_register is not null 
group by operadora_id 

select * from certifications_certification_ceyf where operadora_id = 92
