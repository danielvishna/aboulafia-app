// ====================================================================
// Main Event Handlers for "Private Client" DocType
// ====================================================================
frappe.ui.form.on("Private Client", {
	/**
	 * The 'refresh' event is the main trigger for loading data and setting UI states.
	 * It runs when the form is first loaded and after every save.
	 */
	refresh: function (frm) {
		frm.add_custom_button(
			__("New Client Project"),
			function () {
				// This function is called when the button is clicked.
				// It opens a new document of type 'Client Projects'.
				frappe.new_doc("Client Projects", {
					// This object pre-fills fields in the new document.
					client_type: frm.doctype, // Sets client_type to "Private Client"
					client_link: frm.doc.name, // Sets client_link to the current client's name
				});
			},
			__("Create")
		);
		// Load the read-only regular updates table
		// load_regular_updates(frm);

		// Apply custom styling to form sections
		apply_custom_styles(frm);
		// הסתר/הצג את השדות הרלוונטיים לפי מצב הצ'קבוקס
		toggle_contact_date_fields(frm);

		// אם אנחנו במצב אוטומטי, טען את התאריך לתוך שדה ה-HTML
		if (!frm.doc.override_last_contact_date) {
			update_last_contact_date_display(frm);
		} else {
			// אם במצב ידני, עדכן צבע מיד בטעינה
			apply_contact_date_coloring(frm);
		}

		// Logic for new vs. existing documents
		if (frm.is_new()) {
			frm.set_df_property("enable_editing_check_personal_information", "hidden", 1);
			frm.set_value("enable_editing_check_personal_information", 1);
			frm.set_df_property("customer_id", "read_only", 0);
		} else {
			load_regular_updates_html(frm);
			frm.set_df_property("enable_editing_check_personal_information", "hidden", 0);
			toggle_identity_fields(frm, "husband");
			if (frm.doc.marital_status == "נשוי") {
				toggle_identity_fields(frm, "wife");
			}
		}

		// Apply coloring logic to another table
		dateColoring(frm);
	},

	/**
	 * Toggles required state for parent client / connection group based on 'is_group' checkbox.
	 */
	is_group: function (frm) {
		const is_not_group = cint(frm.doc.is_group) === 0;
		frm.set_df_property("parent_private_client", "reqd", is_not_group);
		frm.set_df_property("connection_group", "reqd", !is_not_group);
		frm.set_df_property("connection_group", "read_only", is_not_group);
	},

	/**
	 * Custom validation logic that runs before the document is saved.
	 */
	validate: function (frm) {
		// Validate dates
		if (frm.doc.birth_date && frm.doc.immigration_date_husband) {
			if (new Date(frm.doc.birth_date) > new Date(frm.doc.immigration_date_husband)) {
				frappe.msgprint("Birth date must be earlier than immigration date.");
				frappe.validated = false;
			}
		}

		// Validate husband's and wife's ID/Passport based on nationality
		validate_identity_documents(frm);

		// Show a final confirmation dialog before saving
		handle_save_confirmation(frm);
	},
	// Add this to your main 'frappe.ui.form.on' block
	before_save: function (frm) {
		// Clear identity fields for the husband based on nationality
		clear_identity_fields(frm, "husband");

		if (frm.doc.marital_status !== "נשוי") {
			// If not married, clear all wife-related details
			clear_wife_details(frm);
		} else {
			// If married, clear identity fields for the wife based on nationality
			clear_identity_fields(frm, "wife");
		}
	},
	override_last_contact_date: function (frm) {
		toggle_contact_date_fields(frm);
		if (!frm.doc.override_last_contact_date) {
			update_last_contact_date_display(frm);
		}
		apply_contact_date_coloring(frm);
	},
	contact_frequency: function (frm) {
		apply_contact_date_coloring(frm);
	},
	last_contact_date: function (frm) {
		apply_contact_date_coloring(frm);
	},

	// Triggers for showing/hiding identity fields based on nationality selection
	nationalities_husband: (frm) => toggle_identity_fields(frm, "husband"),
	nationalities_wife: (frm) => toggle_identity_fields(frm, "wife"),
});

function load_regular_updates_html(frm) {
	// קריאה לפונקציית ה-Python שיצרנו בצד השרת
	frappe.call({
		method: "aboulafia.api.get_regular_updates",
		args: {
			client_name: frm.doc.name,
		},
		callback: function (r) {
			if (r.message && r.message.length > 0) {
				let updates = r.message;

				// התחל לבנות את ה-HTML של הטבלה
				let html = `
                    <div class="table-responsive">
                        <table class="table table-bordered table-striped">
                            <thead>
                                <tr>
                                    <th>נושא</th>
                                    <th>כותרת</th>
                                    <th>שנים</th>
                                    <th>תאריך עדכון</th>
                                    <th>משתמש מעדכן</th>
                                    <th>מחלקות מעורבות</th>
                                </tr>
                            </thead>
                            <tbody>
                `;

				// עבור על כל עדכון והוסף שורה לטבלה
				updates.forEach((item) => {
					// יצירת קישור דינמי לרשומת העדכון
					const url = `/app/regular-updates/${encodeURIComponent(item.name)}`;

					html += `
                        <tr>
                            <td><a href="${url}">${item.subject || ""}</a></td>
                            <td>${item.title || ""}</td>
                            <td>${item.years || ""}</td>
                            <td>${frappe.datetime.str_to_user(item.date_update) || ""}</td>
                            <td>${item.making_note_user || ""}</td>
                            <td>${item.involved_departments_display || ""}</td>
                        </tr>
                    `;
				});

				html += `
                            </tbody>
                        </table>
                    </div>
                `;

				// הצב את ה-HTML שיצרנו בתוך שדה ה-HTML שהוספנו ל-DocType
				frm.fields_dict.regular_updates_html.html(html);
			} else {
				// אם אין עדכונים, הצג הודעה מתאימה
				frm.fields_dict.regular_updates_html.html("<p>אין עדכונים שוטפים להצגה.</p>");
			}
		},
	});
}

// פונקציית עזר שמציגה ומסתירה את השדות הנכונים
function toggle_contact_date_fields(frm) {
	let is_manual = frm.doc.override_last_contact_date;
	frm.toggle_display("last_contact_date", is_manual);
	frm.toggle_display("last_system_date_display", !is_manual);
}

/// פונקציית העזר המעודכנת שמעדכנת את שדה ה-HTML
function update_last_contact_date_display(frm) {
	if (frm.is_new()) return;

	frappe.call({
		method: "aboulafia.api.get_latest_update_date",
		args: {
			client_name: frm.doc.name,
		},
		callback: function (r) {
			// שמור את התאריך הגולמי שחזר מהשרת במשתנה זמני בטופס
			// כדי שנוכל להשתמש בו בפונקציית הצביעה
			frm.latest_system_date_raw = r.message || null;

			const display_field = frm.fields_dict.last_system_date_display;
			if (r.message) {
				let formatted_date = frappe.datetime.str_to_user(r.message);
				display_field.html(
					`<span class="text-muted">שיחה אחרונה מהמערכת:</span><h5 style="margin-top: 5px; font-weight: bold;">${formatted_date}</h5>`
				);
			} else {
				display_field.html(`<p class="text-muted">אין שיחות מתועדות</p>`);
			}

			// לאחר עדכון התצוגה, קרא לפונקציית הצביעה
			apply_contact_date_coloring(frm);
		},
	});
}
function apply_contact_date_coloring(frm) {
	const frequency = frm.doc.contact_frequency;

	// קבע מהו תאריך השיחה האחרון הרלוונטי
	const last_contact = frm.doc.override_last_contact_date
		? frm.doc.last_contact_date
		: frm.latest_system_date_raw;

	// מצא את האלמנטים של השדות שברצוננו לצבוע
	const manual_field_wrapper = frm.get_field("last_contact_date").$wrapper;
	const html_field_wrapper = frm.get_field("last_system_date_display").$wrapper;

	// אם אין תדירות או אין תאריך - נקה את הצבע וחזור
	if (!frequency || !last_contact) {
		manual_field_wrapper.css("background-color", "");
		html_field_wrapper.css("background-color", "");
		return;
	}

	const today = frappe.datetime.now_date();
	let due_date;

	// חשב את תאריך היעד לפי התדירות
	switch (frequency) {
		case "חודש":
			due_date = frappe.datetime.add_months(last_contact, 1);
			break;
		case "רבעון":
			due_date = frappe.datetime.add_months(last_contact, 3);
			break;
		case "שנתי":
			due_date = frappe.datetime.add_months(last_contact, 12);
			break;
		default:
			return; // אם אין תדירות מוכרת, צא
	}

	// ברירת מחדל - צבע ירוק (הכל בסדר)
	let color = "#d4edda"; // light green
	// console.log(frappe.datetime.get_diff(today, due_date));
	// אם עברנו את תאריך היעד - שנה לצבע אדום (נדרשת פעולה)
	if (frappe.datetime.get_diff(today, due_date) > 0) {
		color = "#f8d7da"; // light pink/red
	}

	// החל את הצבע על שני השדות
	manual_field_wrapper.css("background-color", color);
	html_field_wrapper.css("background-color", color);
}

/**
 * Applies custom CSS colors and styles to various form sections.
 */
function apply_custom_styles(frm) {
	try {
		frm.fields_dict.section_break_h7p9?.head?.css("background-color", "cadetblue");
		frm.fields_dict.section_break_h7p9?.body?.css("background-color", "antiquewhite");

		[
			"general_information_section",
			"section_break_rpca",
			"open_projects_section",
			"regular_updates",
			"duties_section",
			"contacts_section",
			"israeli_tax_section",
		].forEach((f) => frm.fields_dict[f]?.collapse_link?.css("background-color", "coral"));

		["duties_audit", "debts_israeli", "debts_us", "duties_relocation"].forEach((fn) => {
			const el = document.querySelector(`[data-fieldname='${fn}']`);
			if (el) el.style.direction = "ltr";
		});
	} catch (e) {
		console.warn("Could not apply all custom styles.", e);
	}
}

/**
 * Handles the logic for the final "Are you sure?" confirmation dialog before saving.
 */
function handle_save_confirmation(frm) {
	// This logic prevents the confirmation from showing again when we programmatically call frm.save()
	if (frm.is_dirty()) {
		// Only show confirm if there are changes
		if (frm.__skip_next_confirm) {
			delete frm.__skip_next_confirm;
			return;
		}
		if (frm.__confirm_open) {
			frappe.validated = false;
			return;
		}

		frm.__confirm_open = true;
		frappe.validated = false; // Stop this save attempt

		frappe.confirm(
			"האם לשמור את השינויים?",
			() => {
				// "Yes" callback
				frm.__confirm_open = false;
				frm.__skip_next_confirm = true;
				frm.set_value("enable_editing_check_personal_information", 0);
				frm.save();
			},
			() => {
				// "No" callback
				frm.__confirm_open = false;
				frappe.show_alert("השמירה בוטלה", 3);
			}
		);
	}
}

/**
 * Validates the ID and passport fields for both husband and wife.
 */
function validate_identity_documents(frm) {
	const genericPassport = /^[A-Za-z0-9]{6,9}$/;

	// Husband Validation
	if (isIsraeli(frm.doc.nationalities_husband)) {
		const id = (frm.doc.husband_taz || "").trim();
		if (!id || !isIsraeliIDValid(id)) {
			frappe.msgprint('מספר הת"ז של הבעל לא תקין');
			frappe.validated = false;
		}
	} else {
		const passp = (frm.doc.husband_passport || "").trim();
		if (!passp || !genericPassport.test(passp)) {
			frappe.msgprint("מספר הדרכון של הבעל לא תקין");
			frappe.validated = false;
		}
	}

	// Wife Validation (only if married)
	if (frm.doc.marital_status == "נשוי") {
		if (isIsraeli(frm.doc.nationalities_wife)) {
			const id = (frm.doc.wife_taz || "").trim();
			if (!id || !isIsraeliIDValid(id)) {
				frappe.msgprint('מספר הת"ז של האישה לא תקין');
				frappe.validated = false;
			}
		} else {
			const passp = (frm.doc.wife_passport || "").trim();
			if (!passp || !genericPassport.test(passp)) {
				frappe.msgprint("מספר הדרכון של האישה לא תקין");
				frappe.validated = false;
			}
		}
	}
}

// ====================================================================
// Helper & Utility Functions
// ====================================================================

/**
 * Checks if 'ישראלית' is present in a nationalities child table.
 */
function isIsraeli(nationalities) {
	if (!Array.isArray(nationalities)) return false;
	return nationalities.some((r) => r.link_myur === "ישראלית");
}

/**
 * Toggles the visibility and required status of ID/Passport fields.
 * @param {object} frm The form object.
 * @param {string} person 'husband' or 'wife'.
 */
function toggle_identity_fields(frm, person) {
	const il = isIsraeli(frm.doc[`nationalities_${person}`]);
	frm.set_df_property(`${person}_taz`, "reqd", il);
	frm.set_df_property(`${person}_taz`, "hidden", !il);
	frm.set_df_property(`${person}_passport`, "reqd", !il);
	frm.set_df_property(`${person}_passport`, "hidden", il);
}

/**
 * A reusable function to clear either the passport or the ID field
 * based on whether the person has Israeli nationality.
 * @param {object} frm The form object.
 * @param {string} prefix The person prefix ('husband' or 'wife').
 */
function clear_identity_fields(frm, prefix) {
	const is_israeli = isIsraeli(frm.doc[`nationalities_${prefix}`]);

	if (is_israeli) {
		// If Israeli, the passport is not relevant, so we clear it if it has a value.
		if (frm.doc[`${prefix}_passport`]) {
			frm.set_value(`${prefix}_passport`, "");
		}
	} else {
		// If not Israeli, the Israeli ID is not relevant, so we clear it if it has a value.
		if (frm.doc[`${prefix}_taz`]) {
			frm.set_value(`${prefix}_taz`, "");
		}
	}
}

/**
 * A dedicated function to clear all fields related to the wife
 * when marital status is not 'Married'.
 * @param {object} frm The form object.
 */
function clear_wife_details(frm) {
	frm.set_value("nationalities_wife", []);
	frm.set_value("wife_passport", "");
	frm.set_value("wife_taz", "");
	frm.set_value("immigration_date_wife", null);
	frm.set_value("immigration_type_wife", "");
	frm.set_df_property("wife_taz", "reqd", 0);
	frm.set_df_property("wife_passport", "reqd", 0);
}

/**
 * Colors rows in the 'table_open_projects' based on dates.
 */
function dateColoring(frm) {
	try {
		if (!frm.doc.table_open_projects || !frm.fields_dict.table_open_projects) return;

		let rows = frm.fields_dict.table_open_projects.grid.grid_rows;
		let today = new Date();
		today.setHours(0, 0, 0, 0);
		let date_one_week = addDays(new Date(), 7);

		rows.forEach((row) => {
			if (row.doc.regular_update) {
				let cell = row.get_field("regular_update").$wrapper;
				let row_date = new Date(row.doc.regular_update);
				row_date.setHours(0, 0, 0, 0);

				// Reset color first
				cell.css("background-color", "");

				if (row_date.getTime() === today.getTime()) {
					cell.css("background-color", "green");
				} else if (row_date < today) {
					cell.css("background-color", "Crimson");
				} else if (row_date < date_one_week) {
					cell.css("background-color", "yellow");
				}
			}
		});

		// This logic seems to be to find the latest date but was unused, I left it commented out
		// let last_update = frm.doc.last_manual_update_date;
		// let latest_date = frm.doc.last_manual_update_date ? new Date(frm.doc.last_manual_update_date) : null;
		// (frm.doc.table_open_projects || []).forEach(d => {
		//     if(d.regular_update && new Date(d.regular_update) > latest_date) {
		//         latest_date = new Date(d.regular_update);
		//         last_update = d.regular_update;
		//     }
		// });
		// frm.set_value('last_updated_date', last_update);
	} catch (e) {
		console.warn("Date coloring failed.", e);
	}
}

/**
 * Adds a specified number of days to a date.
 */
function addDays(date, days) {
	let result = new Date(date);
	result.setDate(result.getDate() + days);
	return result;
}

/**
 * Validates an Israeli ID number using the Luhn algorithm.
 */
function isIsraeliIDValid(id) {
	let id_number = String(id).trim();
	if (id_number.length !== 9 || isNaN(id_number)) return false;

	let sum = 0;
	for (let i = 0; i < 9; i++) {
		let digit = parseInt(id_number[i]);
		let step = digit * ((i % 2) + 1);
		sum += step > 9 ? step - 9 : step;
	}
	return sum % 10 === 0;
}
