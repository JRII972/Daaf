// Copyright (c) 2023, SISEP - DAAF and contributors
// For license information, please see license.txt
function reset_validation(frm){
    frm.doc.prevent_validation = false 
    frm.doc.error_msg =''
    frm.refresh()
}
function setupIntro(frm){
    document.querySelector('[class*="form-message"]').innerHTML = '' 
    if (frm.doc.prevent_validation) {
        frm.set_intro('Vous ne pourez pas valider ce relevé, certaine valeur sont invalide ' + ((frm.doc.error_msg  === undefined || frm.doc.error_msg  === null) ? '' : '<br>' + frm.doc.error_msg) + '<br> Vous pouvez sauvegarder et revenir corriger plus tard', 'red');
        
        if ( (document.querySelector('button[data-label="Valider"]') === undefined) || (document.querySelector('button[data-label="Valider"]') === null) ){
            document.querySelector('button[data-label="Valider"], button[data-label="sauvegarder"]').classList.add('btn-primary')
            document.querySelector('button[data-label="Valider"], button[data-label="sauvegarder"]').classList.add('danger-primary')
            document.querySelector('button[data-label="Valider"], button[data-label="sauvegarder"]').classList.remove('btn-danger')
            document.querySelector('button[data-label="Valider"], button[data-label="sauvegarder"]').classList.remove('danger-action')
        } else {
            document.querySelector('button[data-label="Valider"]').classList.remove('btn-primary')
            document.querySelector('button[data-label="Valider"]').classList.remove('danger-primary')
            document.querySelector('button[data-label="Valider"]').classList.add('btn-danger')
            document.querySelector('button[data-label="Valider"]').classList.add('danger-action')
        }
    } else {
        frm.set_intro('Vérifier bien les valeurs entré, elle ne seront pas modifiable après envoie', 'blue');
        document.querySelector('button[data-label="Valider"], button[data-label="sauvegarder"]').classList.add('btn-primary')
        document.querySelector('button[data-label="Valider"], button[data-label="sauvegarder"]').classList.add('danger-primary')
        document.querySelector('button[data-label="Valider"], button[data-label="sauvegarder"]').classList.remove('btn-danger')
        document.querySelector('button[data-label="Valider"], button[data-label="sauvegarder"]').classList.remove('danger-action')
    }
}

frappe.ui.form.on("Prix et Marche", {
    onload_post_render(frm) {
        frm.fields_dict.date.datepicker.update({
            maxDate: new Date(frappe.datetime.get_today())
        });

        frm.set_query('lieu', () => {
            return {
                filters: {
                    is_group: false
                }
            }
        })
    },
	refresh(frm) {
        setupIntro(frm)
        
	},
    before_save(frm) {
        frm.doc.error_msg = ''
        frm.doc.prevent_validation = false

        for (let i = 0; i < frm.doc.relevé.lenght; i++) {
            frm.doc.relevé[i]['date'] = frm.doc.date 
                frm.doc.relevé[i]['lieu'] = frm.doc.lieu
                // calc_price(frm, frm.doc.relevé[i])
                if ( frm.doc.relevé[i].pass){
                    continue
                } else if (frm.doc.relevé[i].prevent_validation){
                    frm.doc.prevent_validation = true
                    break
                }
          }

        if (frm.doc.date > frappe.datetime.get_today()) {
            frappe.throw(__("Wo, vous revenez du future ! <br> Malheureusement, le voyage dans le temps n'est pas encore possible aujourd'hui <br> <b>Entre une date dans le passé ou aujourd'hui </b>"));
        }
    },
    validate: function(frm) {
        if (frm.doc.date > frappe.datetime.get_today()) {
            frappe.throw(__("Wo, vous revenez du future ! <br> Malheureusement, le voyage dans le temps n'est pas encore possible aujourd'hui <br> <b> Entre une date dans le passé ou aujourd'hui </b>"));
        }

        if (frm.doc.prevent_validation){
            frappe.throw({
                title: __('Valeur du prix et/ou du poids invalide pour certain relevé'),
                message: frm.doc.error_msg
            });
            return false
        }

        frm.doc.relevé.forEach(
            function(value, i) {
                frm.doc.relevé[i]['date'] = frm.doc.date 
                frm.doc.relevé[i]['lieu'] = frm.doc.lieu
            }
        )
    },
    prevent_validation: function(frm){
        setupIntro(frm)
    }
});

function calc_price(frm, row){
    row.prevent_validation = false
    console.log(row)
    frappe.db.get_doc('Unite', row.unité_de_vente)
    .then(unite => {
        
        row.poids_de_référence = row.poids_de_l_unité_de_vente * unite.coef 
        row.prix_de_référence = row.prix_vente * unite.coef

        if (unite.unit_ref) {
            row.unité_de_référence = unite.unit_ref
        } else {
            row.unité_de_référence = row.unité_de_vente
        }

        // TODO: Prevnet missing date and location
        row.date = frm.doc.date 
        row.lieu = frm.doc.lieu
        priceVariation(frm, row)
        frm.refresh();
    })
}

function priceVariation(frm, row){
    console.log(row.produit)
    frappe.call('daaf.sisep.doctype.prix_et_marche.prix_et_marche.PrixMarchePrixAvg', {
        'produit': row.produit,
        'date'   : frm.doc.date,
        'lieu'   : frm.doc.lieu,
    }).then(r => {
        row.prevent_validation = false
        console.log(r)
        if (r.message.Error) {
            frappe.show_alert({
                message:__('Nous ne connaissons pas asser bien ce produit, verifier manuellment le prix'),
                indicator:'orange'
            }, 15);
        } else {
            if ( (row.prix_de_référence > (r.message.avg + 2 * r.message.StdDev) ) || (row.prix_de_référence < (r.message.avg - 2 * r.message.StdDev) ) ) {
                row.prevent_validation = true
                frm.doc.prevent_validation = true
                frm.doc.error_msg = __('<br> <hr> Le prix de référence de <b>' + row.produit + '<\b> atteint des valeurs abérente. <br> <b>Vérifier le prix ET poids de l\'unité de vente.</b> <br> L\'Unité de vente peux aussi être incorrecte'+ 
                'Nous avons observer des prix moyennement compris entre ' + (r.message.avg - r.message.StdDev)  + ' et ' + (r.message.avg + r.message.StdDev))
                frm.refresh()
                
                frappe.warn( __('Valeur du prix et/ou du poids invalide'),
                     __('Le prix de référence de ' + row.produit + ' atteint des valeurs abérente. <br> <hr> <b>Vérifier le prix ET poids de l\'unité de vente.</b> <br> L\'Unité de vente peux aussi être incorrecte'+ 
                    'Nous avons observer des prix moyennement compris entre ' + (r.message.avg - r.message.StdDev ) + ' et ' + (r.message.avg + r.message.StdDev)),
                     () => {
                        frappe.prompt({
                            label: 'Commentaire',
                            fieldname: 'commentaire',
                            fieldtype: 'Small Text',
                            reqd: 1
                        }, (values) => {
                            console.log(values);
                            row.commentaire = values.commentaire
                            reset_validation(frm)
                            setupIntro(frm)
                        })
                    },
                     "Commenter"
                );

                
    
            } else if (row.prix_de_référence < (r.message.avg - r.message.StdDev) ) {
                frappe.warn(__('Prix ou poids peut être incorrect ' + row.produit),
                     __('Le prix de référence de ' + row.produit + ' est inférieur à la variation standar moyenne. <br> <hr> <b>Vérifier le prix ET poids de l\'unité de vente.</b> <br> L\'Unité de vente peux aussi être incorrecte' + 'Nous avons observer des prix moyennement compris entre ' + (r.message.avg - r.message.StdDev)  + ' et ' + (r.message.avg + r.message.StdDev)),
                        () => {
                            // TODO: Scroll to field
                    },
                    'Vérifier',
                    false
                );
            } else if (row.prix_de_référence > (r.message.avg + r.message.StdDev) ) {
                frappe.warn(__('Prix ou poids peut être incorrect ' + row.produit),
                     __('Le prix de référence de ' + row.produit + ' est suppérieur à la variation standar moyenne. <br> <hr> <b>Vérifier le prix ET poids de l\'unité de vente.</b> <br> L\'Unité de vente peux aussi être incorrecte' + 
                     'Nous avons observer des prix moyennement compris entre ' + (r.message.avg - r.message.StdDev ) + ' et ' + (r.message.avg + r.message.StdDev)),
                        () => {
                            // TODO: Scroll to field
                    },
                    'Vérifier',
                    false
                );
            } 
             
        }
    })
    
}

frappe.ui.form.on('Releve Mercuriale', {
    // cdt is Child DocType name i.e Releve Mercuriale
    // cdn is the row name for e.g bbfcb8da6a
    before_save(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);

        if (row.poids_de_l_unité_de_vente)

        if (row.doc.date > frappe.datetime.get_today()) {
            frappe.throw(__("Wo, vous revenez du future ! <br> Malheureusement, le voyage dans le temps n'est pas encore possible aujourd'hui <br> <b>Entre une date dans le passé ou aujourd'hui </b>"));
        }
    },
    prix_vente(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (row.prix_vente <= 0 ){
            frappe.msgprint({
                title: __('Notification'),
                indicator: 'red',
                message: __('le prix ne peux être négatif ou null')
            });
            row.prevent_validation = true
        } else {
            if (row.poids_de_l_unité_de_vente > 0){
                
                if ( (row.unité_de_vente != '') && (row.unité_de_vente != undefined) && (row.unité_de_vente != null) ){
                    calc_price(frm, row)
                }
            }
        }

        
    },
    poids_de_l_unité_de_vente(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (row.poids_de_l_unité_de_vente <= 0 ){
            frappe.msgprint({
                title: __('Notification'),
                indicator: 'red',
                message: __('la poids_de_l_unité_de_vente ne peux être négatif ou null')
            });
        } else {
            if (row.prix_vente > 0){
                
                if ( (row.unité_de_vente != '') && (row.unité_de_vente != undefined) && (row.unité_de_vente != null)){
                    calc_price(frm, row)
                }
            }
        }
    },
    unité_de_vente(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if ( (row.poids_de_l_unité_de_vente > 0) & (row.prix_vente > 0) ){
                
            if ( (row.unité_de_vente != '') & (row.unité_de_vente != undefined) & (row.unité_de_vente != null)){
                calc_price(frm, row)
            } 
        }
    },
    commentaire(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if( (row.commentaire != '') & (row.commentaire != null) & (row.commentaire != undefined) ){
            row.pass = true
            frm.refresh()
        }
    }
    
})



