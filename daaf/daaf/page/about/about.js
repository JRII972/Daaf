frappe.pages['about'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: _('About'),
		single_column: false
	});

	page.set_indicator('BETA', 'orange')

	let $btn = page.set_primary_action('New', () => create_new(), 'octicon octicon-plus')
	// add a normal menu item
	page.add_menu_item('Send Email', () => open_email_dialog())

	// add a standard menu item
	page.add_menu_item('Send Email 2', () => open_email_dialog(), true)
	page.add_action_item('Delete', () => delete_items())

	let fieldStatus = page.add_field({
		label: 'Status',
		fieldtype: 'Select',
		fieldname: 'status',
		options: [
			'Open',
			'Closed',
			'Cancelled'
		],
		change() {
			console.log(field.get_value());
		}
	});
	let fieldSTS = page.add_field({
		label: 'STS',
		fieldtype: 'Check',
		fieldname: 'check',
		change() {
			console.log(field.get_value());
		}
	});
}