// Copyright (c) 2023, SISEP - DAAF and contributors
// For license information, please see license.txt
function reset_validation(frm){
    frm.doc.prevent_validation = false 
    frm.doc.error_msg =''
    frm.refresh()
}

function prettyRow(frm){
    for (const row of frm.doc.relevé){
        document.querySelector('div[data-name="'+ row.name + '"]').style.backgroundColor = ''
        if (row.warning){ document.querySelector('div[data-name="'+ row.name + '"]').style.backgroundColor = 'var(--alert-bg-warning)' }
        if (row.prevent_validation){ document.querySelector('div[data-name="'+ row.name + '"]').style.backgroundColor = 'var(--alert-bg-danger)' }
    }
}

function setupIntro(frm){
    document.querySelector('[class*="form-message"]').innerHTML = '' 
    if (frm.doc.prevent_validation) {
        frm.set_intro('Vous ne pourez pas valider ce relevé, certaine valeur sont invalide ' + ((frm.doc.error_msg  === undefined || frm.doc.error_msg  === null) ? '' : '<br>' + frm.doc.error_msg) + '<br> Vous pouvez sauvegarder et revenir corriger plus tard', 'red');
        
        cur_page.page.querySelector("div.page-head.flex > div > div > div.flex.col.page-actions.justify-content-end > div.standard-actions.flex > button:nth-child(5)").classList.remove('btn-primary')
        cur_page.page.querySelector("div.page-head.flex > div > div > div.flex.col.page-actions.justify-content-end > div.standard-actions.flex > button:nth-child(5)").classList.remove('danger-primary')
        cur_page.page.querySelector("div.page-head.flex > div > div > div.flex.col.page-actions.justify-content-end > div.standard-actions.flex > button:nth-child(5)").classList.add('btn-danger')
        cur_page.page.querySelector("div.page-head.flex > div > div > div.flex.col.page-actions.justify-content-end > div.standard-actions.flex > button:nth-child(5)").classList.add('danger-action')
        
    } else {
        frm.set_intro('Vérifier bien les valeurs entré, elle ne seront pas modifiable après envoie', 'blue');
        cur_page.page.querySelector("div.page-head.flex > div > div > div.flex.col.page-actions.justify-content-end > div.standard-actions.flex > button:nth-child(5)").classList.add('btn-primary')
        cur_page.page.querySelector("div.page-head.flex > div > div > div.flex.col.page-actions.justify-content-end > div.standard-actions.flex > button:nth-child(5)").classList.add('danger-primary')
        cur_page.page.querySelector("div.page-head.flex > div > div > div.flex.col.page-actions.justify-content-end > div.standard-actions.flex > button:nth-child(5)").classList.remove('btn-danger')
        cur_page.page.querySelector("div.page-head.flex > div > div > div.flex.col.page-actions.justify-content-end > div.standard-actions.flex > button:nth-child(5)").classList.remove('danger-action')
    }
}

frappe.ui.form.on("Prix et Marche", {
    onload(frm){

    },
    onload_post_render(frm) {
        frm.fields_dict.date.datepicker.update({
            maxDate: new Date(frappe.datetime.get_today()),
            language: 'fr'
        });

        frm.set_query('lieu', () => {
            return {
                filters: {
                    is_group: false
                }
            }
        })
        
        if (!frm.doc.importation){
            frm.get_field('relevé').grid.toggle_reqd('prix_vente', true)
            frm.get_field('relevé').grid.toggle_reqd('poids_de_l_unité_de_vente', true)
            frm.get_field('relevé').grid.toggle_reqd('unité_de_vente', true)
            frm.get_field('relevé').grid.toggle_reqd('unité_de_vente', true)
        }

        prettyRow(frm)
    },
	refresh(frm) {
        setupIntro(frm)
        prettyRow(frm)
	},
    before_save(frm) {
        
        // frm.doc.error_msg = ''
        // frm.doc.prevent_validation = false

        // for (let i = 0; i < frm.doc.relevé.lenght; i++) {
        //     frm.doc.relevé[i]['date'] = frm.doc.date 
        //     frm.doc.relevé[i]['lieu'] = frm.doc.lieu
        //         // calc_price(frm, frm.doc.relevé[i])
        //         // if ( frm.doc.relevé[i].pass){
        //         //     continue
        //         // } else if (frm.doc.relevé[i].prevent_validation){
        //         //     if (!frm.doc.relevé[i].commentaire){
        //         //         frm.doc.prevent_validation = true
        //         //         break
        //         //     }
        //         // }
        //   }

        if (frm.doc.date > frappe.datetime.get_today()) {
            frappe.throw(__("Wo, vous revenez du future ! <br> Malheureusement, le voyage dans le temps n'est pas encore possible aujourd'hui <br> <b>Entre une date dans le passé ou aujourd'hui </b>"));
        }

        
        
        prettyRow(frm)
    },
    before_submit: function(frm) {
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

        frm.doc.error_msg = ''
        // frm.doc.prevent_validation = false

        for (let i = 0; i < frm.doc.relevé.lenght; i++) {
            frm.doc.relevé[i]['date'] = frm.doc.date 
                frm.doc.relevé[i]['lieu'] = frm.doc.lieu
                // calc_price(frm, frm.doc.relevé[i])
                if ( frm.doc.relevé[i].pass){
                    continue
                } else if (frm.doc.relevé[i].prevent_validation){
                    if (!frm.doc.relevé[i].commentaire){
                        frm.doc.prevent_validation = true
                        break
                    }
                }
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
    },
    date: function(frm){
        for (const _row of frm.doc.relevé){
            let row = frappe.get_doc(_row.doctype, _row.name);
            row.date = frm.doc.date
            calc_price(frm, row)
        }
    },
    lieu: function(frm){
        for (const _row of frm.doc.relevé){
            let row = frappe.get_doc(_row.doctype, _row.name);
            row.lieu = frm.doc.lieu
            calc_price(frm, row, silent=true)
        }
    },
    prevent_validation: function(frm){
        frm.enable_save();
        if(frm.doc.prevent_validation) {frm.disable_save();}
    }
});

function calc_price(frm, row, silent=false){
    if (row.prevent_calculation){
        priceVariation(frm, row)
        return
    }

    if (!row.produit) {
        return
    }
    if (!row.prix_vente) {
        return
    }
    if (!row.poids_de_l_unité_de_vente) {
        return
    }
    if (!row.unité_de_vente) {
        return
    }

    row.prevent_validation = false
    console.log(row)
    frappe.db.get_doc('Unite', row.unité_de_vente)
    .then(unite => {
        
        row.poids_de_référence = row.poids_de_l_unité_de_vente * unite.coef 
        row.prix_de_référence = row.prix_vente / row.poids_de_l_unité_de_vente * unite.coef 
        if (unite.unit_ref) {
            row.unité_de_référence = unite.unit_ref
        } else {
            row.unité_de_référence = row.unité_de_vente
        }

        // TODO: Prevnet missing date and location
        row.date = frm.doc.date 
        row.lieu = frm.doc.lieu
        frm.refresh();
        priceVariation(frm, row, silent)
    })
}

function priceVariation(frm, row, silent=false){
    if (row.prevent_check){
        priceVariation(frm, row)
        return
    }
    if (!frm.doc.date) {
        frappe.show_alert({
            message:__('Renseigner la date du relevé s\'il vous plait'),
            indicator:'orange'
        }, 15);
        return
    }
    if (!frm.doc.lieu) {
        frappe.show_alert({
            message:__('Renseigner le lieu du relevé s\'il vous plait'),
            indicator:'orange'
        }, 15);
        return
    }

    console.log(row.produit)
    frappe.call('daaf.sisep.doctype.prix_et_marche.prix_et_marche.PrixMarchePrixAvg', {
        'produit': row.produit,
        'date'   : frm.doc.date,
        'lieu'   : frm.doc.lieu,
    }).then(r => {
        ligne = 'NA'
        for (var i = 0; i < frm.doc.relevé.length; i++){
            if (frm.doc.relevé[i].name == row.name){
                ligne = i + 1   
                break
            }
        }
        
        document.querySelector('div[data-name="'+ row.name + '"]').style.backgroundColor = ''
        row.prevent_validation = false
        row.warning = false
        console.log(r)
        if (r.message.Error) {
            frappe.show_alert({
                message:__('Nous ne connaissons pas asser bien ce produit, verifier manuellment le prix'),
                indicator:'orange'
            }, 15);
        } else {
            console.log(r.message.avg + 2 * r.message.StdDev)
            console.log(r.message.avg - 2 * r.message.StdDev)
            console.log(r.message.avg + r.message.StdDev)
            console.log(r.message.avg - r.message.StdDev)
            console.log(row.prix_de_référence)
            if ( (row.prix_de_référence > (r.message.avg + 2 * r.message.StdDev) ) || (row.prix_de_référence < (r.message.avg - 2 * r.message.StdDev) ) ) {
                row.prevent_validation = true
                frm.doc.prevent_validation = true
                frm.doc.error_msg = __('<br> <hr> Le prix de référence de <b>' + row.produit + '<\b> atteint des valeurs abérente. <br> <b>Vérifier à la ligne ' + ligne +' le prix ET poids de l\'unité de vente.</b> <br> L\'Unité de vente peux aussi être incorrecte'+ 
                '<br> Nous avons observer des prix moyennement compris entre ' + frappe.format((r.message.avg - r.message.StdDev ), { fieldtype: 'Currency', options: 'currency' }, { inline: true })  + ' et ' + frappe.format((r.message.avg + r.message.StdDev), { fieldtype: 'Currency', options: 'currency' }, { inline: true }))
                frm.refresh()
                document.querySelector('div[data-name="'+ row.name + '"]').style.backgroundColor = 'var(--alert-bg-danger)'
                frappe.warn( __('Valeur du prix et/ou du poids invalide'),
                     __('Le prix de référence de ' + row.produit + ' atteint des valeurs abérente. <br> <hr> <b>Vérifier à la ligne ' + ligne +' le prix ET poids de l\'unité de vente.</b> <br> L\'Unité de vente peux aussi être incorrecte'+ 
                    '<br> Nous avons observer des prix moyennement compris entre ' + frappe.format((r.message.avg - r.message.StdDev ), { fieldtype: 'Currency', options: 'currency' }, { inline: true }) + ' et ' + frappe.format((r.message.avg + r.message.StdDev), { fieldtype: 'Currency', options: 'currency' }, { inline: true })),
                     () => {
                        frappe.prompt({
                            label: 'Commentaire',
                            fieldname: 'commentaire',
                            fieldtype: 'Small Text',
                            reqd: 1
                        }, (values) => {
                            console.log(values);
                            document.querySelector('div[data-name="'+ row.name + '"]').style.backgroundColor = 'var(--alert-bg-warning)'
                            row.warning = true
                            row.prevent_validation = false
                            row.commentaire = values.commentaire
                            reset_validation(frm)
                            setupIntro(frm)
                        })
                    },
                     "Commenter"
                );

                
    
            } else if (row.prix_de_référence < (r.message.avg - r.message.StdDev) ) {
                frappe.warn(__('Prix ou poids peut être incorrect ' + row.produit),
                     __('Le prix de référence de ' + row.produit + ' est inférieur à la variation standar moyenne. <br> <hr> <b>Vérifier à la ligne ' + ligne +' le prix ET poids de l\'unité de vente.</b> <br> L\'Unité de vente peux aussi être incorrecte' + '<br> Nous avons observer des prix moyennement compris entre ' + frappe.format((r.message.avg - r.message.StdDev ), { fieldtype: 'Currency', options: 'currency' }, { inline: true })  + ' et ' + frappe.format((r.message.avg + r.message.StdDev), { fieldtype: 'Currency', options: 'currency' }, { inline: true })),
                        () => {
                            // TODO: Scroll to field
                    },
                    'Vérifier',
                    false
                );
                row.warning = true
                document.querySelector('div[data-name="'+ row.name + '"]').style.backgroundColor = 'var(--alert-bg-warning)'
            } else if (row.prix_de_référence > (r.message.avg + r.message.StdDev) ) {
                frappe.warn(__('Prix ou poids peut être incorrect ' + row.produit),
                     __('Le prix de référence de ' + row.produit + ' est suppérieur à la variation standar moyenne. <br> <hr> <b>Vérifier à la ligne ' + ligne +' le prix ET poids de l\'unité de vente.</b> <br> L\'Unité de vente peux aussi être incorrecte' + 
                     '<br> Nous avons observer des prix moyennement compris entre ' + frappe.format((r.message.avg - r.message.StdDev ), { fieldtype: 'Currency', options: 'currency' }, { inline: true }) + ' et ' + frappe.format((r.message.avg + r.message.StdDev), { fieldtype: 'Currency', options: 'currency' }, { inline: true })),
                        () => {
                            // TODO: Scroll to field
                    },
                    'Vérifier',
                    false
                );
                row.warning = true
                document.querySelector('div[data-name="'+ row.name + '"]').style.backgroundColor = 'var(--alert-bg-warning)'
            } 
             
        }
    })
    
}

frappe.ui.form.on('Releve Mercuriale', {
    // cdt is Child DocType name i.e Releve Mercuriale
    // cdn is the row name for e.g bbfcb8da6a
    onload_post_render: function(frm, cdt, cdn){
        
    },
    before_save: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        ligne = 'NA'
        for (var i = 0; i < frm.doc.relevé.length; i++){
            if (frm.doc.relevé[i].name == row.name){
                ligne = i + 1   
                break
            }
        }


        if (row.doc.date > frappe.datetime.get_today()) {
            frappe.throw(__("Wo, vous revenez du future ! <br> Malheureusement, le voyage dans le temps n'est pas encore possible aujourd'hui <br> <b>Entre une date dans le passé ou aujourd'hui </b>"));
        }
        // calc_price(frm, row)
    },
    produit: function(frm, cdt, cdn){
        let row = frappe.get_doc(cdt, cdn);
        calc_price(frm, row)
    },
    prix_vente: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (row.prix_vente <= 0 ){
            frappe.msgprint({
                title: __('Notification'),
                indicator: 'red',
                message: __('le prix ne peux être négatif ou null')
            });
            row.prevent_validation = true
        } else {
            
            calc_price(frm, row)
        }

        
    },
    poids_de_l_unité_de_vente: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (row.poids_de_l_unité_de_vente <= 0 ){
            frappe.msgprint({
                title: __('Notification'),
                indicator: 'red',
                message: __('la poids_de_l_unité_de_vente ne peux être négatif ou null')
            });
        } else {
            calc_price(frm, row)
        }
    },
    unité_de_vente: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        calc_price(frm, row)
    },
    commentaire: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if( (row.commentaire != '') & (row.commentaire != null) & (row.commentaire != undefined) ){
            row.pass = true
            row.warning = true
            frm.refresh()
        }
    },
    lieu: function(frm, cdt, cdn){
        let row = frappe.get_doc(cdt, cdn);
        calc_price(frm, row)
    },
    date: function(frm, cdt, cdn){
        let row = frappe.get_doc(cdt, cdn);
        calc_price(frm, row)
    }
    
})



