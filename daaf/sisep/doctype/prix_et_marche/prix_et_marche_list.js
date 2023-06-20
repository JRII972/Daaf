frappe.listview_settings['Prix et Marche'] = {
    // add fields to fetch
    add_fields: ['statut', 'lieu'],
    // set default filters
    // filters: [
    //     ['public', '=', 1]
    // ],
    hide_name_column: true, // hide the last column which shows the `name`
    onload(listview) {
        listview.page.add_button(__("Collect GMS"), function() {
			frappe.call({
				method:'daaf.GMS.test.test',
				callback: function(r) {
					console.log(r)
				}
			});
		});

        listview.page.add_button(__("Import Mercuriale"), function() {
			frappe.call({
				method:'daaf.sisep.doctype.importation_donnee_mercuriale.importation_donnee_mercuriale.checkRunningJob',
				callback: function(r) {
					if( r.message ){
                        frappe.new_doc("Importation donnee Mercuriale");
                    }

				}
			});
            
		});

        frappe.realtime.on('gms_collecteur', (data) => {
            console.log(data)
            listview.refresh()
            frappe.show_alert({
                message:__('Hey, une collecte des GMS est prète'),
                indicator:'green'
            }, 5);
        })
    },
    before_render() {
        // triggers before every render of list records
    },

    // set this to true to apply indicator function on draft documents too
    // has_indicator_for_draft: false,

    // get_indicator(doc) {
    //     // customize indicator color
    //     if (doc.docstatus == 1) {
    //         return [__("Soumis "), "green", "public,=,Yes"];
    //     } else {
    //         return [__("Autre"), "darkgrey", "public,=,No"];
    //     }
    // },
    // primary_action() {
    //     // triggers when the primary action is clicked
    // },
    // get_form_link(doc) {
    //     // override the form route for this doc
    // },
    // add a custom button for each row
    // button: {
    //     show(doc) {
    //         return doc.reference_name;
    //     },
    //     get_label() {
    //         return 'View';
    //     },
    //     get_description(doc) {
    //         return __('View {0}', [`${doc.reference_type} ${doc.reference_name}`])
    //     },
    //     action(doc) {
    //         frappe.set_route('Form', doc.reference_type, doc.reference_name);
    //     }
    // },
    // // format how a field value is shown
    // formatters: {
    //     title(val) {
    //         return val.bold();
    //     },
    //     public(val) {
    //         return val ? 'Yes' : 'No';
    //     }
    // }
}

