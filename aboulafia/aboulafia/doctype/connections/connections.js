frappe.ui.form.on("Connections", {
	refresh(frm) {
		// your code here
	},
	connection(frm) {
		console.log(frm.doc.connection);
		const val_to_doctype = {
			"קשר משפחתי": ["Families", "Private Client"],
			"קבוצת חברות": ["Company Client", "Company Client"],
			"בעלי מניות": ["Private Client", "Company Client"],
			נאמנויות: ["Private Client", "Private Client"],
			"לקוח מפנה": ["Private Client", "Private Client"],
		};
		frm.set_value("entity_type_a", val_to_doctype[frm.doc.connection][0]);
		frm.set_value("entity_type_b", val_to_doctype[frm.doc.connection][1]);
		frm.set_value("entity_a", "");
		frm.set_value("entity_b", "");
	},
});
