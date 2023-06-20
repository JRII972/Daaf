// Copyright (c) 2023, SISEP - DAAF and contributors
// For license information, please see license.txt

frappe.ui.form.on("Importation donnee Mercuriale", {
	on_submit(frm) {
                frappe.set_route('List', 'Prix et Marche', 'List')
                cur_list.refresh()
                frappe.show_progress('Loading..', 70, 100, 'Please wait');
	},
        // on_save(frm) {
        // frappe.set_route('List', 'Prix et Marche', 'List')
        // },
});
