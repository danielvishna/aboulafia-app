import frappe

def on_validate(doc, method=None):
        """
        בדיקת ייחודיות לכל אחד מהשדות: husband_taz / husband_passport / wife_taz / wife_passport
        אם ערך מופיע אצל לקוח אחר בכל אחד מארבעת השדות – נזרוק שגיאה.
        """
        if(doc.client_type == "לקוח פרטי"):
            checks = [
                ("תעודת הזהות של הבעל",     (doc.husband_taz or "").strip()),
                ("הדרכון של הבעל",          (doc.husband_passport or "").strip()),
                ("תעודת הזהות של האישה",    (doc.wife_taz or "").strip()),
                ("הדרכון של האישה",         (doc.wife_passport or "").strip()),
            ]

            for label, val in checks:
                if not val:
                    continue
                dup = frappe.db.sql(
                    """
                    SELECT name
                    FROM `tabPrivate Client`
                    WHERE name != %s
                    AND (
                            husband_taz     = %s OR
                            husband_passport= %s OR
                            wife_taz        = %s OR
                            wife_passport   = %s
                    )
                    LIMIT 1
                    """,
                    (doc.name or "", val, val, val, val),
                )
                if dup:
                    dup_name = dup[0][0]
                    frappe.throw(f"שגיאה: {label} '{val}' כבר קיים במערכת עבור לקוח אחר ({dup_name}).")

