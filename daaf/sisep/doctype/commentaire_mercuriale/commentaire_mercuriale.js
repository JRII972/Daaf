// Copyright (c) 2023, SISEP - DAAF and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Commentaire Mercuriale", {
// 	refresh(frm) {

// 	},
// });

function loadMercuriale(frm) {
    
    frm.doc.mercuriale.forEach(
        function(row, i) {
            frm.doc.mercuriale.splice(frm.doc.mercuriale, row.idx)
        }
    )

    frappe.call('daaf.sisep.doctype.ligne_commentaire_mercuriale.ligne_commentaire_mercuriale.MercurialeTbl', {
        'date'   : frm.doc.date,
        'lieu'   : frm.doc.lieu,
    }).then(r => {
        console.log(r.message)
        
        r.message.data.forEach(row => {
            let child = frm.add_child('mercuriale', {
                produit: row[0],
                nombre: row[1],
                prix_moyen: row[2],
                quantité_sur_létale: row[3],
                prix_minimum: row[4],
                prix_maximum: row[5],
                prix_moyen_précédent: row[6],
                variation: row[7],
            });
        });
        frm.refresh()
        frm.save();
    })
}

frappe.ui.form.on("Commentaire Mercuriale", {
    before_load(frm) {
        
    },
    onload_post_render(frm) {
        frm.fields_dict.date.datepicker.update({
            maxDate: new Date(frappe.datetime.get_today()),
            language: 'fr',
            // dateFormat: "mm-yyyy",
            // minView: 'months'
            
        });

        frm.add_custom_button('Charger la mercuriale', () => {
            loadMercuriale(frm)
        })
    },
	refresh(frm) {
        frm.add_custom_button('Charger la mercuriale', () => {
            loadMercuriale(frm)
        })
	},
    before_save(frm) {
       
    },
    validate: function(frm) {
        
    },
    date: function(frm){
        loadMercuriale(frm)
    }
});
