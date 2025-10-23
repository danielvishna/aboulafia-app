// Hide Comments & Activity globally with a MutationObserver (Frappe v15+)
(function () {
	const SELECTORS =
		".form-comments, .timeline, .timeline-actions, .btn-new-email, .btn-new-event";
	const WRAPPER_SELECTORS = [
		// הסתרת סקשן עוטף אם קיים
		".card-section:has(.form-comments)",
		".card-section:has(.timeline)",
	];

	function applyHide(root) {
		try {
			(root || document).querySelectorAll(SELECTORS).forEach((el) => {
				el.style.setProperty("display", "none", "important");
			});
			WRAPPER_SELECTORS.forEach((sel) => {
				(root || document).querySelectorAll(sel).forEach((el) => {
					el.style.setProperty("display", "none", "important");
				});
			});
		} catch (e) {
			console.warn("[aboulafia] applyHide error:", e);
		}
	}

	function startObserver(frm) {
		// הפעלה חד-פעמית לכל טופס
		const root = frm && frm.$wrapper ? frm.$wrapper[0] : document.body;
		applyHide(root);

		// תצפית על שינויים ב-DOM של הטופס – כל מה שנוסף יוסתר מייד
		const mo = new MutationObserver((muts) => {
			for (const m of muts) {
				if (m.addedNodes && m.addedNodes.length) {
					m.addedNodes.forEach((n) => {
						if (n.nodeType === 1) applyHide(n);
					});
				}
			}
		});
		mo.observe(root, { childList: true, subtree: true });
		// שמור reference על ה־frm כדי לא לפתוח כפילויות
		frm && (frm.__aboulafia_mo = mo);

		console.log("[aboulafia] observer active on", frm?.doctype, frm?.docname);
	}

	// הפעלה על כל הדוקטייפים
	frappe.ui.form.on("*", {
		onload_post_render(frm) {
			if (!frm.__aboulafia_mo) startObserver(frm);
		},
		refresh(frm) {
			applyHide(frm && frm.$wrapper ? frm.$wrapper[0] : document.body);
		},
	});

	// כיסוי ראשון גם לפני פתיחת טופס (למקרה של רכיבי Desk אחרים)
	if (document.readyState !== "loading") applyHide(document);
	else document.addEventListener("DOMContentLoaded", () => applyHide(document));
})();
