import frappe
from frappe.utils.html_utils import escape_html

# סטטוסים שנחשבים "פתוח" (התאם לצורך)
OPEN_STATUSES = {
    "לא התחיל", "איסוף מסמכים", "בהכנה", "בדיקה", "הגשה",
    "החתמה", "בליניג", "סיום", "In Progress"
}

# דוקטייפים שנחשבים "לקוח" עבור פרויקט
CUSTOMER_DOCTYPES = ["Customer"]


# ----------------------------
# Regular Updates (ללא שינוי מהותי)
# ----------------------------
@frappe.whitelist()
def get_regular_updates(client_name):
    if not client_name:
        return []
    try:
        return frappe.get_list(
            "Regular Updates",
            filters={"client": client_name},
            fields=[
                "name", "subject", "title", "years", "making_note_user",
                "date_update", "relevant_employees", "customer_updated",
                "involved_departments_display",
            ],
            order_by="date_update desc",
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Error in get_regular_updates")
        return []


@frappe.whitelist()
def get_latest_update_date(client_name):
    if not client_name:
        return None
    return frappe.get_value(
        "Regular Updates",
        filters={"client": client_name},
        fieldname="date_update",
        order_by="date_update desc",
    )


# ----------------------------
# RELATED PROJECTS — לוגיקה פנימית (ללא whitelist)
# ----------------------------
def get_related_projects(base_doctype: str, base_name: str, depth: int = 3):
    """מחזיר self_open / self_closed / related_open כנתונים גולמיים (dict)."""
    MAX_DEPTH = 5
    try:
        depth = int(depth)
        if not (0 <= depth <= MAX_DEPTH):
            depth = MAX_DEPTH
    except (ValueError, TypeError):
        depth = 3

    # מי ה"לקוח הראשי" בהתאם למסך הנוכחי
    primary_customer = None
    if base_doctype == "Client Projects":
        customer_name = frappe.db.get_value("Client Projects", base_name, "client_link")
        if not customer_name:
            return {"self_open": [], "self_closed": [], "related_open": []}
        for dt in CUSTOMER_DOCTYPES:
            if frappe.db.exists(dt, customer_name):
                primary_customer = (dt, customer_name)
                break
    else:
        primary_customer = (base_doctype, base_name)

    if not primary_customer:
        return {"self_open": [], "self_closed": [], "related_open": []}

    # הרחבת קשרים עד עומק N
    # connection_rules = {
    #     d.name: {"is_symmetric": d.is_symmetric}
    #     for d in frappe.get_all("Connection Type", fields=["name", "is_symmetric"])
    # }
    related_entities = {primary_customer}
    frontier = {primary_customer}

    for _ in range(max(0, depth)):
        next_frontier = set()

        # A -> B
        for entity_type, entity_name in frontier:
            for conn in frappe.get_all(
                "Connections",
                filters={"entity_a": entity_name, "entity_type_a": entity_type},
                fields=["connection_type", "entity_type_b", "entity_b"],
            ):
                neighbor = (conn.entity_type_b, conn.entity_b)
                if neighbor not in related_entities:
                    related_entities.add(neighbor)
                    next_frontier.add(neighbor)

            # B -> A (אם סימטרי)
            for conn in frappe.get_all(
                "Connections",
                filters={"entity_b": entity_name, "entity_type_b": entity_type},
                fields=["connection_type", "entity_type_a", "entity_a"],
            ):
                # if connection_rules.get(conn.connection_type, {}).get("is_symmetric"):
                neighbor = (conn.entity_type_a, conn.entity_a)
                if neighbor not in related_entities:
                    related_entities.add(neighbor)
                    next_frontier.add(neighbor)

        if not next_frontier:
            break
        frontier = next_frontier

    primary_customer_name = primary_customer[1]
    related_customer_names = [
        name
        for doctype, name in related_entities
        if (doctype, name) != primary_customer and doctype in CUSTOMER_DOCTYPES
    ]

    # כל הפרויקטים של הלקוח הראשי
    self_projects = frappe.get_all(
        "Client Projects",
        filters={"client_link": primary_customer_name},
        fields=[
            "name", "project_year", "status_", "end_tax_year_project", "length",
            "assigned_user", "department", "client_link", "project_type",
        ],
    )

    self_open = [p for p in self_projects if p.status_ in OPEN_STATUSES]
    self_closed = [p for p in self_projects if p.status_ not in OPEN_STATUSES]

    # פרויקטים פתוחים של ישויות קשורות
    related_open = []
    if related_customer_names:
        related_open = frappe.get_all(
            "Client Projects",
            filters={
                "client_link": ["in", list(set(related_customer_names))],
                "status_": ["in", list(OPEN_STATUSES)],
            },
            fields=["name", "project_year", "status_", "assigned_user", "client_link", "project_type"],
        )

    return {"self_open": self_open, "self_closed": self_closed, "related_open": related_open}


# ----------------------------
# RELATED PROJECTS — API ציבורי שמחזיר HTML (whitelist)
# ----------------------------
@frappe.whitelist()
def get_related_projects_html(base_doctype, base_name, depth=2, exclude_self=False, current_name=None):
    """מחזיר HTML מלא לטבלאות פרויקטים קשורים (לשימוש מ-Client Script)."""
    results = get_related_projects(base_doctype, base_name, depth)

    self_open = results.get("self_open", []) or []
    self_closed = results.get("self_closed", []) or []
    related_open = results.get("related_open", []) or []

    # אם נמצאים על דף פרויקט – ניתן להסתיר את הפרויקט עצמו מהרשימות
    if exclude_self and current_name:
        self_open = [p for p in self_open if p.get("name") != current_name]
        self_closed = [p for p in self_closed if p.get("name") != current_name]

    def _safe(v):
        return escape_html(v or "")

    def build_table(title, projects):
        if not projects:
            return f"""
            <div class="frappe-card mb-3">
              <div class="card-body">
                <h5 class="card-title">{_safe(title)}</h5>
                <div class="text-muted">לא נמצאו פרויקטים.</div>
              </div>
            </div>
            """

        rows = []
        for p in projects:
            name = _safe(p.get("name"))
            display_name = _safe(p.get("project_type") or p.get("name"))
            client_link = _safe(p.get("client_link"))
            project_year = _safe(p.get("project_year"))
            status_ = _safe(p.get("status_"))
            assigned_user = _safe(p.get("assigned_user"))
            rows.append(f"""
                <tr>
                  <td><a href="/app/client-projects/{name}">{display_name}</a></td>
                  <td>{client_link}</td>
                  <td>{project_year}</td>
                  <td><span class="indicator blue">{status_}</span></td>
                  <td>{assigned_user}</td>
                </tr>
            """)

        return f"""
        <div class="frappe-card mb-3">
          <div class="card-body">
            <h5 class="card-title">{_safe(title)}</h5>
            <table class="table table-sm table-bordered">
              <thead class="table-light">
                <tr>
                  <th style="width:30%;">סוג פרויקט</th>
                  <th style="width:25%;">לקוח</th>
                  <th style="width:10%;">שנה</th>
                  <th style="width:15%;">סטטוס</th>
                  <th style="width:20%;">מטפל</th>
                </tr>
              </thead>
              <tbody>{''.join(rows)}</tbody>
            </table>
          </div>
        </div>
        """

    html = ""
    html += build_table("פרויקטים פתוחים", self_open)
    html += build_table("ארכיון פרויקטים (סגורים)", self_closed)
    html += build_table("פרויקטים קשורים (פתוחים)", related_open)
    return html


# @frappe.whitelist()
# def handle_regular_update_notification(doc, method):
#     """
#     This function is called from hooks.py for 'Regular Updates' doctype events.
#     It sends notifications to relevant employees.
#     """

#     # בדוק אם המסמך נשמר בפעם הראשונה (נוצר) או שהוא מתעדכן
#     # is_new() מחזיר True רק אחרי ההכנסה הראשונית (after_insert)
#     is_new_doc = doc.is_new()
    
#     # אם אין עובדים רלוונטיים, צא
#     if not doc.get("relevant_employees"):
#         return

#     # קבע את סוג האירוע עבור נושא ההתראה
#     event_type = "חדש" if is_new_doc else "עודכן"
#     subject = f"עדכון שוטף {event_type} עבור לקוח '{doc.client}': {doc.subject}"

#     notification_doc = {
#         "type": "Alert",
#         "document_type": doc.doctype,
#         "document_name": doc.name,
#         "subject": subject,
#     }

#     recipients = [row.user for row in doc.get("relevant_employees") if row.user]
    
#     # שלח התראה לכל אחד מהעובדים הרלוונטיים
#     for user in recipients:
#         notification_doc["for_user"] = user
#         frappe.utils.add_notification(notification_doc)
@frappe.whitelist()
def get_owned_companies(client_name):
    """
    מקבל שם של לקוח ומחזיר רשימה של חברות בבעלותו
    עם פרטים נוספים על כל חברה.
    """
    # 1. קודם כל, נמצא את כל סוגי הקשרים שמגדירים בעלות (לפי הצ'קבוקס שהגדרנו)
    ownership_connection_types = frappe.get_all(
        "Connection Type",
        filters={"requires_percentage": 1},
        pluck="name"
    )

    if not ownership_connection_types:
        return []

    # 2. נמצא את כל הקשרים שבהם הלקוח הוא "בעל המניות" (entity_a)
    #    וסוג הקשר הוא אחד מסוגי הבעלות שמצאנו
    connections = frappe.get_all(
        "Connections",
        filters={
            "entity_b": client_name,
            "connection_type": ["in", ownership_connection_types],
            },
        fields=["entity_a", "ownership_percent"] # entity_b היא החברה שבבעלותו
    )

    if not connections:
        return []

    # 3. נשלוף את שמות החברות כדי להביא עליהן פרטים נוספים
    company_names = [c.get("entity_a") for c in connections]

    # 4. נביא את הפרטים הנוספים על החברות (ח"פ ותאריך הקמה) מה-DocType שלהן
    #    !!! חשוב: החלף את 'tax_id' ו-'incorporation_date' בשמות השדות הנכונים אצלך!!!
    company_details = frappe.get_all(
        "Customer", # או כל DocType אחר שמייצג חברה
        filters={"name": ["in", company_names]},
        fields=["name", "ein", "company_establishment_date"]
    )
    
    # ניצור מילון כדי לגשת לפרטים בקלות
    company_details_map = {d.name: d for d in company_details}

    # 5. נבנה את רשימת התוצאות הסופית
    results = []
    for conn in connections:
        company_name = conn.get("entity_a")
        details = company_details_map.get(company_name)
        if details:
            results.append({
                "company_name": company_name,
                "ownership_percent": conn.get("ownership_percent"),
                "company_id": details.get("ein"),
                "incorporation_date": details.get("company_establishment_date")
            })

    return results

import frappe

import frappe

# ===================================================================
# ===== הקוד הסופי והנקי (בלי לוגים) =====
# ===================================================================
@frappe.whitelist()
def update_client_department_statuses(client_name):
    """
    (גרסה סופית)
    מחשב מחדש ומעדכן את טבלת הסטטוסים עבור לקוח ספציפי אחד.
    """
    try:
        client = frappe.get_doc("Customer", client_name)
    except frappe.DoesNotExistError:
        # אם הלקוח לא נמצא, אין טעם להמשיך
        return

    # 1. שלוף את כל הפרויקטים של הלקוח הספציפי הזה
    projects = frappe.get_all(
        "Client Projects",
        filters={"client_link": client_name},
        fields=["department", "status_"]
    )

    department_summary = {}
    if projects:
        # 2. עבד את הנתונים למבנה נוח
        for proj in projects:
            dept = proj.get("department")
            if not dept:
                continue
            
            if dept not in department_summary:
                department_summary[dept] = {"open": False, "closed": False}
                
            if proj.get("status_") in ["סיום", "בטל פרויקט"]:
                department_summary[dept]["closed"] = True
            else:
                department_summary[dept]["open"] = True

    # 3. בנה מחדש את טבלת הילדים
    client.department_statuses = []
    for dept, statuses in department_summary.items():
        client.append("department_statuses", {
            "department": dept,
            "has_open_projects": 1 if statuses["open"] else 0,
            "has_closed_projects": 1 if statuses["closed"] else 0
        })
        
    # 4. שמור את השינויים בלקוח
    client.save(ignore_permissions=True)
    frappe.db.commit()


def trigger_client_department_update(doc, method):
    """
    מופעלת על ידי ה-Hook. לוקחת את הלקוח מהפרויקט וקוראת לפונקציית העדכון.
    """
    client_name = doc.get("client_link")
    if not client_name:
        return
        
    frappe.enqueue(
        "aboulafia.api.update_client_department_statuses", 
        client_name=client_name
    )

# coding: utf-8
import frappe

@frappe.whitelist()
def get_shareholders(company_name):
    """
    מחזירה רשימה מאוחדת של כל בעלי המניות (לקוחות וחיצוניים) שמחזיקים בחברה הנתונה.
    """
    ownership_connection_types = frappe.get_all(
        "Connection Type",
        filters={"requires_percentage": 1},
        pluck="name"
    )

    if not ownership_connection_types:
        return []

    # שלב 1: אחזר קשרים
    connections = frappe.get_all(
        "Connections",
        filters={
            "entity_a": company_name,
            "connection_type": ["in", ownership_connection_types],
        },
        fields=["entity_b", "ownership_percent"]
    )

    if not connections:
        return []

    connection_map = {conn.get("entity_b"): conn for conn in connections}
    shareholder_names = list(connection_map.keys())

    # שלב 2: זהה את סוג ה-DocType עבור כל בעל מניות
    customer_matches = frappe.get_all("Customer", filters={"name": ["in", shareholder_names]}, pluck="name")
    external_matches = frappe.get_all("External Shareholder", filters={"name": ["in", shareholder_names]}, pluck="name")

    all_details_map = {}
    optional_fields = ["residency", "represents_personal_report", "represents_american_report", "nationalities_husband"]

    def get_multiselect_values(parent_doctype, doc_name, field_meta):
        """
        מאחזרת ערכים משדה Table MultiSelect ומחזירה אותם כמחרוזת מופרדת בפסיקים.
        """
        child_doctype = field_meta.options
        if not child_doctype:
            return ""

        # מצא את שם שדה ה-Link בטבלת הילדים
        child_meta = frappe.get_meta(child_doctype)
        link_fieldname = next((df.fieldname for df in child_meta.fields if df.fieldtype == "Link"), None)

        if not link_fieldname:
            return ""

        values = frappe.get_all(
            child_doctype,
            filters={'parent': doc_name, 'parenttype': parent_doctype},
            pluck=link_fieldname
        )
        return ", ".join(filter(None, values))


    # שלב 3: אחזר פרטים תוך טיפול ייעודי בשדות Table MultiSelect
    if customer_matches:
        customer_meta = frappe.get_meta("Customer")
        customer_query_fields = ["name", "customer_name as shareholder_name", "ein as shareholder_id"]
        
        for field in optional_fields:
            if customer_meta.has_field(field) and customer_meta.get_field(field).fieldtype != "Table MultiSelect":
                customer_query_fields.append(field)
                
        customer_details = frappe.get_all(
            "Customer",
            filters={"name": ["in", customer_matches]},
            fields=list(set(customer_query_fields))
        )
        
        for d in customer_details:
            d['doctype'] = 'Customer'
            for field in optional_fields:
                if customer_meta.has_field(field) and customer_meta.get_field(field).fieldtype == "Table MultiSelect":
                    d[field] = get_multiselect_values("Customer", d.name, customer_meta.get_field(field))
            all_details_map[d.name] = d

    if external_matches:
        external_meta = frappe.get_meta("External Shareholder")
        external_query_fields = ["name", "shareholder_name"]

        for field in optional_fields:
            if external_meta.has_field(field) and external_meta.get_field(field).fieldtype != "Table MultiSelect":
                external_query_fields.append(field)
        
        external_details = frappe.get_all(
            "External Shareholder",
            filters={"name": ["in", external_matches]},
            fields=list(set(external_query_fields))
        )

        for d in external_details:
            d['doctype'] = 'External Shareholder'
            d['shareholder_id'] = d.name
            for field in optional_fields:
                 if external_meta.has_field(field) and external_meta.get_field(field).fieldtype == "Table MultiSelect":
                    d[field] = get_multiselect_values("External Shareholder", d.name, external_meta.get_field(field))
            all_details_map[d.name] = d

    # שלב 4: הרכב את רשימת התוצאות הסופית
    results = []
    for shareholder_name, details in all_details_map.items():
        connection_info = connection_map.get(shareholder_name)
        if connection_info:
            details['ownership_percent'] = connection_info.get("ownership_percent")
            details['doc_name'] = shareholder_name
            results.append(details)

    return results

