app_name = "aboulafia"
app_title = "Aboulafia"
app_publisher = "dani"
app_description = "hhh"
app_email = "daniel.vishna@gmail.com"
app_license = "mit"

# Apps
# ------------------
doc_events = {
    "Regular Updates": {
        "validate": "aboulafia.aboulafia.doctype.regular_updates.regular_updates.on_validate",
        "after_insert": "aboulafia.aboulafia.doctype.regular_updates.regular_updates.after_insert",
        "on_update": "aboulafia.aboulafia.doctype.regular_updates.regular_updates.on_update",
    },
    "Private Client": {
        "validate": "aboulafia.aboulafia.doctype.connections.private_client.on_validate",
    },
    "Client Projects": {
        "on_submit": "aboulafia.api.trigger_client_department_update",
        "on_update": "aboulafia.api.trigger_client_department_update",
        "on_trash": "aboulafia.api.trigger_client_department_update"
    },
    "Customer": {
        "validate": "aboulafia.aboulafia.doctype.customer.customer.on_validate",
    },
}

# app_include_js = "public/js/_ping.js"

# doctype_js = {
#     "Private Client": "public/js/private_client.js"
# }

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "aboulafia",
# 		"logo": "/assets/aboulafia/logo.png",
# 		"title": "Aboulafia",
# 		"route": "/aboulafia",
# 		"has_permission": "aboulafia.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/aboulafia/aboulafia/css/aboulafia.css"
# app_include_js = "/assets/aboulafia/js/aboulafia.js"

# include js, css files in header of web template
# web_include_css = "/assets/aboulafia/css/aboulafia.css"
# web_include_js = "/assets/aboulafia/js/aboulafia.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "aboulafia/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "aboulafia/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "aboulafia.utils.jinja_methods",
# 	"filters": "aboulafia.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "aboulafia.install.before_install"
# after_install = "aboulafia.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "aboulafia.uninstall.before_uninstall"
# after_uninstall = "aboulafia.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "aboulafia.utils.before_app_install"
# after_app_install = "aboulafia.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "aboulafia.utils.before_app_uninstall"
# after_app_uninstall = "aboulafia.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "aboulafia.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"aboulafia.tasks.all"
# 	],
# 	"daily": [
# 		"aboulafia.tasks.daily"
# 	],
# 	"hourly": [
# 		"aboulafia.tasks.hourly"
# 	],
# 	"weekly": [
# 		"aboulafia.tasks.weekly"
# 	],
# 	"monthly": [
# 		"aboulafia.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "aboulafia.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "aboulafia.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "aboulafia.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["aboulafia.utils.before_request"]
# after_request = ["aboulafia.utils.after_request"]

# Job Events
# ----------
# before_job = ["aboulafia.utils.before_job"]
# after_job = ["aboulafia.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"aboulafia.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

