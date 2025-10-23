// Global hide for Comments & Activity (with logs for verification)
(function () {
	function hideBits(frm) {
		if (!frm) return;
		try {
			// נסה להסתיר מיד
			frm.$wrapper
				.find(
					".form-comments, .timeline, .timeline-actions, .btn-new-email, .btn-new-event"
				)
				.hide();
			// נסה גם להסיר סקשנים עוטפים אם קיימים
			frm.$wrapper.find(".card-section").has(".form-comments").hide();
			frm.$wrapper.find(".card-section").has(".timeline").hide();

			// נסה שוב אחרי שה-DOM של הטופס מתייצב
			setTimeout(() => {
				frm.$wrapper
					.find(
						".form-comments, .timeline, .timeline-actions, .btn-new-email, .btn-new-event"
					)
					.hide();
				frm.$wrapper.find(".card-section").has(".form-comments").hide();
				frm.$wrapper.find(".card-section").has(".timeline").hide();
			}, 250);

			// לוג בדיקה
			console.log("[aboulafia] hideBits applied on", frm.doctype, frm.docname);
		} catch (e) {
			console.warn("[aboulafia] hideBits error:", e);
		}
	}

	frappe.ui.form.on("*", {
		onload_post_render: hideBits,
		refresh: hideBits,
		after_save: hideBits,
	});
})();
