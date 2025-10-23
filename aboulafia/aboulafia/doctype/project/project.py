import frappe

def on_validate(doc, method=None):
    # --- חוק 1: בדיקת ייחודיות של לקוח + שנת פרויקט ---
    if not doc.customer or doc.project_description != "":
        return  # אם אין לקוח, לא נבצע את הבדיקה
    
    duplicate_project = frappe.db.exists("Project", {
        "customer": doc.customer,
        "project_year": doc.project_year,
        "project_type": doc.project_type,
        "name": ["!=", doc.name]  
    })

    if duplicate_project:
        frappe.throw(
            f"כבר קיים פרויקט עבור הלקוח <b>{doc.customer}</b> לשנת <b>{doc.project_year}</b>.\
                אם תרצה לצור עוד מאותו סוג לשנת {doc.project_year}</b>, יש למלא שדה תיאור לפרויקט.",
            title="כפילות פרויקט"
        )

    # --- חוק 2: בדיקה שדה תיאור חובה אם זה "עוד פרויקט" (כלומר, לא הראשון) ---
    # נבדוק אם קיימים פרויקטים אחרים לאותו לקוח
    other_projects_exist = frappe.db.exists("Project", {
        "customer": doc.customer,
        "name": ["!=", doc.name] # שוב, לא כולל את המסמך הנוכחי
    })

    # אם קיימים פרויקטים אחרים, והתיאור במסמך הנוכחי ריק -> חסום
    if other_projects_exist and not doc.description:
        frappe.throw(
            f"מאחר שללקוח <b>{doc.customer}</b> יש פרויקטים קיימים, חובה למלא את שדה התיאור.",
            title="תיאור נדרש"
        )