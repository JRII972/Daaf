// Copyright (c) 2023, SISEP - DAAF and contributors
// For license information, please see license.txt

frappe.ui.form.on("Releve prix et production", {
	onload_post_render(frm) {
        frm.set_query('producteur', () => {
            return {
                query: 'daaf.controllers.queries.pprod_contact_query'
            }
        })
	},
});
