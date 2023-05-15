// Copyright (c) 2023, SISEP - DAAF and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Prix et Marche", {
// 	refresh(frm) {

// 	},
// });

function calc_price(row){
    console.log(row.unité)
    frappe.db.get_doc('Unite', row.unité)
    .then(unite => {
        console.log(unite)
        row.quantite_ref = row.quantité * unite.coef
        row.prix_ref = row.prix_vente * unite.coef

        if (unite.unit_ref) {
            row.unite_ref = unite.unit_ref
        } else {
            row.unite_ref = row.unité
        }

        frm.refresh();
    })
}

frappe.ui.form.on('Releve Mercuriale', {
    // cdt is Child DocType name i.e Releve Mercuriale
    // cdn is the row name for e.g bbfcb8da6a
    prix_vente(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (row.prix_vente <= 0 ){
            frappe.msgprint({
                title: __('Notification'),
                indicator: 'red',
                message: __('le prix ne peux être négatif ou null')
            });
        } else {
            if (row.quantité > 0){
                
                if ( row.unité ){
                    calc_price(row)
                }
            }
        }
    },
    Quantite_ref(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (row.quantité <= 0 ){
            frappe.msgprint({
                title: __('Notification'),
                indicator: 'red',
                message: __('la quantité ne peux être négatif ou null')
            });
        } else {
            if (row.prix_vente > 0){
                
                if ( row.unité ){
                    calc_price(row)
                }
            }
        }
    },
    Quantite_ref(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (row.quantité <= & row.prix_vente > 0){
                
                if ( row.unité ){
                    calc_price(row)
                } else {
                    frappe.msgprint({
                        title: __('Notification'),
                        indicator: 'red',
                        message: __('Unité obligatoire')
                    });
                }
            }
        }
    }
})