// -*- coding: utf-8 -*-
// © 2012 Agile Business Group
// © 2012 Therp BV
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

odoo.define('web_export_view.Sidebar', function (require) {
"use strict";


var Model = require('web.DataModel');
var session = require('web.session');
var ListView = require('web.ListView');

var core = require('web.core');
var formats = require('web.formats');
var Sidebar = require('web.Sidebar');
var pyeval = require('web.pyeval');
var crash_manager = require('web.crash_manager');


var _t = core._t;


ListView.include({
	 render_pager: function() {
        var self = this;
        this._super.apply(this, arguments); // Sets this.$buttons
        this.$buttons.find("#button_export_excel").click(function(event){
        	self.geo_export_view("excel");
    	});
		
    	this.$buttons.find("#button_export_pdf").click(function(event){
        	self.geo_export_view("pdf");
    	});
    },
    geo_export_view: function(format) {
		var self = this
	    var export_type = format
	    var view = this.getParent()
	    
	    
	    /*aca vienen los grupos
	    self.grouped
	    self.groups.datagroup.group_by
	    */
	    
	    // Find Header Element
	    var header_eles = $(document).find('.oe_list_header_columns')
	    var header_name_list_xls = []
	    var header_name_list = []
	    $.each(header_eles,function(){
	        var $header_ele = $(this)
	        var header_td_elements = $header_ele.find('th')
	        $.each(header_td_elements,function(){
	            var $header_td = $(this)
	            var text = $header_td.text().trim() || ""
	            var data_id = $header_td.attr('data-id')
	            if (data_id != undefined)
	            	header_name_list_xls.push({'label': text.trim(), 'name': data_id})
	            if (text && !data_id){
	                var data_id = 'group_name'
	            }
	            header_name_list.push({'header_name': text.trim(), 'header_data_id': data_id})
	           // }
	        });
	    });
            
            //Find Data Element
        var data_eles = $(document).find('.oe_list_content > tbody > tr')
        var export_data = []//
        $.each(data_eles,function(){
            var data = []
            var $data_ele = $(this)
            var is_analysis = false
            if ($data_ele.text().trim()){
            //Find group name
                var group_th_eles = $data_ele.find('th')
                $.each(group_th_eles,function(){
                    var $group_th_ele = $(this)
                    var text = $group_th_ele.text().trim() || ""
                    var is_analysis = true
                    data.push({'data': text, 'bold': true})
                });
                var data_td_eles = $data_ele.find('td')
                $.each(data_td_eles,function(){
                    var $data_td_ele = $(this)
                    var text = $data_td_ele.text().trim() || ""
                    if ($data_td_ele && $data_td_ele[0].classList.contains('oe_number') && !$data_td_ele[0].classList.contains('oe_list_field_float_time')){
                        var text = text.replace('%', '')
//	                        text = instance.web.parse_value(text, { type:"float" })
                        //#787
                        var text = formats.parse_value(text, { type:"string" });
                        data.push({'data': text || "", 'number': true})
                    }
                    else{
                        data.push({'data': text})
                    }
                });
                export_data.push(data)
            }
        });
            
            //Find Footer Element
            
        var footer_eles = $(document).find('.oe_list_content > tfoot> tr')
        $.each(footer_eles,function(){
            var data = []
            var $footer_ele = $(this)
            var footer_td_eles = $footer_ele.find('td')
            $.each(footer_td_eles,function(){
                var $footer_td_ele = $(this)
                var text = $footer_td_ele.text().trim() || ""
                if ($footer_td_ele && $footer_td_ele[0].classList.contains('oe_number')){
                    //var text = instance.web.parse_value(text, { type:"float" })
		var text = formats.parse_value(text, { type:"float" });
                    data.push({'data': text || "", 'bold': true, 'number': true})
                }
                else{
                    data.push({'data': text, 'bold': true})
                }
            });
            export_data.push(data)
        });
        
        //var ids_to_export = $(document).find('.oe_list_content >tbody> tr').attr('data-id')
        var ids_to_export = data_eles.filter(function(i,elem) {	return $(elem).find('input:checked').is(":checked") }).map(function () {  return this.dataset.id;}).get()
        if (ids_to_export.length === 0) {
        	ids_to_export = []
        }
        //Export to excel
        
        function replacer(key, value) {
		  // Filtrando propiedades 

		  if ((key === "_proxies") || (key.startsWith("__"))|| (key.startsWith("action"))|| (key.startsWith("view"))|| (key === "group")
		  
		  ) {
		    return undefined;
		  }
		  return value;
		}
        
        var grouped = self.grouped
	    var group_by = self.groups.datagroup.group_by
        $.blockUI();
        if (export_type === 'excel'){
             this.session.get_file({
	            url: '/web/export/geo_xls_export',
	            data: {data: JSON.stringify({
	                model: this.dataset.model,
	                fields: header_name_list_xls, //exported_fields,
	                // ids: data_eles.map(function () {  return this.dataset.id;})
	                // filtro .filter(function(i,elem) {	return $(elem).find('input:checked').is(":checked") })
	                ids: ids_to_export,
					//ids: this.dataset.ids,
					grouped: self.grouped,
					group_by: self.groups.datagroup.group_by,
					children: self.groups.children,
					datagroup: self.groups.datagroup,
	                domain: pyeval.eval('domains',[this.dataset._model.domain()]),
	                context: pyeval.eval('contexts', [this.dataset._model.context()]),
	                import_compat: true,
	            },replacer)},
	            complete: $.unblockUI,//framework.unblockUI,
	            error: crash_manager.rpc_error.bind(crash_manager),
	        });
             /*this.session.get_file({
                 url: '/web/export/geo_xls_export',
                 data: {data: JSON.stringify({
                        model : view.model,
                        headers : header_name_list,
                        rows : export_data,
                 })},
                 complete: $.unblockUI

             });*/
         }
         else{
         	self = this
            new Model("res.users").get_func("read")(this.session.uid, ["company_id"]).then(function(res) {
                new Model("res.company").get_func("read")(res['company_id'][0], ["name"]).then(function(result) {
                    view.session.get_file({
                         url: '/web/export/geo_pdf_export',
                         data: {data: JSON.stringify({
                                uid: view.session.uid,
                                model : self.dataset.model,
                                headers : header_name_list,
                                rows : export_data,
                                company_name: result['name']
                         })},
                         complete: $.unblockUI,
		 	             error: crash_manager.rpc_error.bind(crash_manager),
                     });
                });
            });
		}
	}
});

Sidebar.include({
    init: function () {
        var self = this;
        this._super.apply(this, arguments);
        /*self.sections.push({
            name: 'export_current_view',
            label: _t('Export Current View')
        });
        self.items['export_current_view'] =  [];*/
        var view = self.getParent();
        if (view.fields_view && view.fields_view.type === "tree") {
            self.web_export_add_items();
        }
    },

    web_export_add_items: function () {
        var self = this;
		this.add_items('other', _.compact([{
            label: 'Excel',
            callback: self.on_sidebar_export_view_xls,
        },]));        
		/*this.add_items('other', _.compact([{
            label: 'PDF',
            callback: self.on_sidebar_export_view_pdf,
        },]));*/        
    },

    on_sidebar_export_view_xls: function () {
        // Select the first list of the current (form) view
        // or assume the main view is a list view and use that
        var self = this,
            view = this.getParent(),
            children = view.getChildren();

	    /*aca vienen los grupos
	    view.grouped
	    view.groups.datagroup.group_by
	    */

        if (children) {
            children.every(function (child) {
                if (child.field && child.field.type == 'one2many') {
                    view = child.viewmanager.views.list.controller;
                    return false; // break out of the loop
                }
                if (child.field && child.field.type == 'many2many') {
                    view = child.list_view;
                    return false; // break out of the loop
                }
                return true;
            });
        }
        var export_columns_keys = [];
        var export_columns_names = [];
        $.each(view.visible_columns, function () {
            if (this.tag == 'field') {
                // non-fields like `_group` or buttons
                export_columns_keys.push(this.id);
                export_columns_names.push(this.string);
            }
        });
        var rows = view.$el.find('tbody tr[data-id]');
        var export_rows = [];
        var ids = [];
        $.each(rows, function () {
            var $row = $(this);
            var export_row = [];
            var row_selector = '.o_list_record_selector input[type=checkbox],\
            .oe_list_record_selector input[type=checkbox]';
            var checked = $row.find(row_selector).is(':checked');
            var item_id = $row.filter(function(i,elem) {
										return $(elem).find('input:checked').is(":checked") 
								  }).map(function () {  
								  		return this.dataset.id;
								  	})
            			 	.get();
            if ($row.filter(function(i,elem) {	return $(elem).find('input:checked').is(":checked") }).map(function () {  return this.dataset.id;}).get().length > 0){
            	ids.push(item_id);
        	}
            if (children && checked === true) {
                $.each(export_columns_keys, function () {
                    var $cell = $row.find('td[data-field="' + this + '"]');
                    var text = $cell.text();
                    if ($cell.hasClass("oe_list_field_monetary")) {
                        // Remove all but digits, minus, dots and commas
                        text = text.replace(/[^\d\.,-]/g, "");
                        export_row.push(
                            formats.parse_value(text, {"type": "monetary"})
                        );
                    } else if ($cell.hasClass("oe_list_field_float")) {
                        export_row.push(
                            formats.parse_value(text, {'type': "float"})
                        );
                    } else if ($cell.hasClass("oe_list_field_boolean")) {
                        export_row.push(
                            $cell.is(':has(input:checked)')
                            ? _t("True") : _t("False")
                        );
                    } else if ($cell.hasClass("oe_list_field_date")) {
                        export_row.push(
                            formats.parse_value(text, {'type': "date"})
                        );
                        
                    } else if ($cell.hasClass("oe_list_field_integer")) {
                        var tmp, tmp2 = text;
                        do {
                            tmp = tmp2;
                            tmp2 = tmp.replace(
                                _t.database.parameters.thousands_sep,
                                ""
                            );
                        } while (tmp !== tmp2);

                        export_row.push(parseInt(tmp2));
                    } else {
                        export_row.push(text.trim());
                    }
                });
                export_rows.push(export_row);
            }
        });
        $.blockUI();
        view.session.get_file({
            url: '/web/export/geo_xls_export',
            data: {data: JSON.stringify({
                model: view.model,
                headers: export_columns_names,
                fields: export_columns_keys,
                ids: ids,
                rows: export_rows,
                domain: pyeval.eval('domains',[view.dataset._model.domain()]),
                context: pyeval.eval('contexts', [view.dataset._model.context()]),
                import_compat: true,
            })},
            complete: $.unblockUI,
            error: crash_manager.rpc_error.bind(crash_manager),
        });
    },

});
});
