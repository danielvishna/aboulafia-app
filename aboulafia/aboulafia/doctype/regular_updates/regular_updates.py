import frappe

def on_validate(doc, method=None):
    frappe.log_error("hooks.on_validate()", "Debug Notifications 11111")

def after_insert(doc, method=None):
    _send_notifications(doc, event_type="חדש")

def on_update(doc, method=None):
    if getattr(doc.flags, "in_insert", False):
        return  # אם זה מגיע מאותה שמירה ראשונה
    before = doc.get_doc_before_save()
    if not before:
        return
    watched = ["subject", "title", "years", "customer_updated", "involved_departments_display"]
    changed = any(doc.get(f) != before.get(f) for f in watched)
    if not changed:
        return
    _send_notifications(doc, event_type="עודכן")

def _send_notifications(doc, event_type="חדש"):
    frappe.log_error(f"Attempting to send notifications for {doc.name}", "Debug Notifications")
    if not getattr(doc, "relevant_employees", None):
        frappe.log_error("No relevant employees found. Exiting.", "Debug Notifications")
        return
    subject = f"עדכון שוטף {event_type} עבור לקוח '{doc.client}': {doc.subject}"
    for row in doc.relevant_employees:
        if row.user:
            frappe.get_doc({
                "doctype": "Notification Log",
                "type": "Alert",
                "document_type": doc.doctype,
                "document_name": doc.name,
                "subject": subject,
                "read": 0,
                "for_user": row.user,
                "from_user": "Administrator",
            }).insert(ignore_permissions=True)