// aboulafia/public/js/custom_ui.js
// Hide Comments & Activity timeline across all Desk forms (Frappe v15+)

(function () {
  // Optional: allowlist של דוקטייפים שבהם כן תרצה לראות Comments/Activity
  // השאר ריק כדי להסתיר לכולם. אפשר להכניס שמות למשל: ["ToDo", "Issue"]
  const ALLOWLIST = new Set([]);

  function hideBits(frm) {
    try {
      if (!frm || !frm.doctype || ALLOWLIST.has(frm.doctype)) return;

      // --- Hide Comments block ---
      // מכסה גם רינדור מאוחר ושינויים דינמיים
      frm.$wrapper.find('.form-comments').hide();

      // --- Hide Activity (Timeline) ---
      // API פנימי של הטיימליין
      if (frm.timeline && frm.timeline.$wrapper) {
        frm.timeline.$wrapper.hide();
      }
      // גיבוי: כיתה כללית
      frm.$wrapper.find('.timeline').hide();

      // Hide timeline action buttons (New Email / New Event וכד')
      frm.$wrapper.find('.timeline-actions, .btn-new-email, .btn-new-event').hide();

      // לפעמים הכותרות נבנות מאוחר — נסה שוב קצר אחרי
      setTimeout(() => {
        frm.$wrapper.find('.form-comments, .timeline, .timeline-actions, .btn-new-email, .btn-new-event').hide();
        if (frm.timeline && frm.timeline.$wrapper) {
          frm.timeline.$wrapper.hide();
        }
      }, 200);
    } catch (e) {
      // אל תעצור את ה-UI אם משהו השתבש
      console.warn('[aboulafia] hideBits error:', e);
    }
  }

  // מפעילים לכל הדוקטייפים (Desk only)
  frappe.ui.form.on('*', {
    refresh: hideBits,
    onload_post_render: hideBits,
    after_save: hideBits
  });
})();
