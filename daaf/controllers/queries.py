
import frappe
from frappe.query_builder import DocType
from frappe.utils import getdate


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def pprod_contact_query(doctype, txt, searchfield, start, page_len, filters):
    print(doctype, txt, searchfield, start, page_len, filters)
    Affectation = DocType("Affectation Prix et production") 
    Affectation_sub = DocType("Affectation PPROD contact") 
    Etablissements = DocType("Etablissements") 


    
    result = (
        frappe.qb.from_(Affectation) \
            .inner_join(Affectation_sub).on(Affectation.name == Affectation_sub.parent)\
            .inner_join(Etablissements).on(Etablissements.name == Affectation_sub.Etablissements)\
            .select(Etablissements.name, Etablissements.status) \
            .where(
                (Affectation.début_de_laffectation <= getdate()) &
                (
                    (Affectation.date_fin_affectation >= getdate()) |
                    (Affectation.date_fin_affectation == 0)
                ) & 
                (Affectation.enquêteur == 'Administrator') &
                (
                    Etablissements.name.like('%' + txt + '%')
                )
            ) \
            .offset(start).limit(page_len)
    ).run(as_list = True)
    print(result)
    return result