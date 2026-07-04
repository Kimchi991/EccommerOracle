import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

try:
    from reportlab.platypus import HRFlowable
except ImportError:
    from reportlab.platypus.flowables import HRFlowable

OUTPUT = "GymTrackPro_Blueprint_v2.pdf"

# Ensure output directory exists if path contains directories
dir_name = os.path.dirname(OUTPUT)
if dir_name:
    os.makedirs(dir_name, exist_ok=True)

# ── Palette ─────────────────────────────────────────────────────────────────
DARK_BG   = colors.HexColor("#0F1923")   # deep navy (header bg)
ACCENT    = colors.HexColor("#E63946")   # red accent
ACCENT2   = colors.HexColor("#457B9D")   # steel blue
LIGHT_BG  = colors.HexColor("#F1FAEE")   # off-white section bg
MID_GRAY  = colors.HexColor("#A8DADC")   # subtle teal
TEXT_DARK = colors.HexColor("#1D3557")
WHITE     = colors.white
ROW_ALT   = colors.HexColor("#EAF2FB")

# ── Doc ──────────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=18*mm, rightMargin=18*mm,
    topMargin=14*mm, bottomMargin=14*mm,
    title="GymTrack Pro - System Blueprint v2.0",
    author="Ghlen Del Rosario",
)

W, H = A4
CONTENT_W = W - 36*mm

styles = getSampleStyleSheet()

# ── Custom styles ────────────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)

sTitle = S("sTitle", fontSize=28, textColor=WHITE, fontName="Helvetica-Bold",
           spaceAfter=2, leading=32, alignment=TA_CENTER)
sSubtitle = S("sSubtitle", fontSize=11, textColor=MID_GRAY, fontName="Helvetica",
              spaceAfter=0, leading=14, alignment=TA_CENTER)
sSection = S("sSection", fontSize=13, textColor=ACCENT, fontName="Helvetica-Bold",
             spaceBefore=10, spaceAfter=4, leading=16)
sSubSection = S("sSubSection", fontSize=10.5, textColor=TEXT_DARK, fontName="Helvetica-Bold",
                spaceBefore=6, spaceAfter=3, leading=13)
sBody = S("sBody", fontSize=9, textColor=TEXT_DARK, fontName="Helvetica",
          spaceAfter=3, leading=13)
sBullet = S("sBullet", fontSize=9, textColor=TEXT_DARK, fontName="Helvetica",
            spaceAfter=2, leading=13, leftIndent=12, bulletIndent=0)
sCode = S("sCode", fontSize=8, textColor=colors.HexColor("#2B2D42"),
          fontName="Courier", spaceAfter=2, leading=11,
          leftIndent=8, backColor=colors.HexColor("#F0F4F8"))
sSmall = S("sSmall", fontSize=8, textColor=colors.HexColor("#555555"),
           fontName="Helvetica", spaceAfter=2, leading=11)
sNote = S("sNote", fontSize=8.5, textColor=colors.HexColor("#1A6B3C"),
          fontName="Helvetica-Oblique", spaceAfter=3, leading=12, leftIndent=8)
sPageNum = S("sPageNum", fontSize=8, textColor=colors.HexColor("#888888"),
             fontName="Helvetica", alignment=TA_RIGHT)
sCoverSmall = S("sCoverSmall", fontSize=8, textColor=MID_GRAY, fontName="Helvetica",
                spaceAfter=2, leading=11, alignment=TA_CENTER)

def section(title):
    return [
        Spacer(1, 4*mm),
        HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=3),
        Paragraph(title, sSection),
    ]

def subsection(title):
    return Paragraph(title, sSubSection)

def body(text):
    return Paragraph(text, sBody)

def bullet(text):
    return Paragraph(f"- {text}", sBullet)

def note(text):
    return Paragraph(f"<b>Note:</b> {text}", sNote)

def spacer(h=4):
    return Spacer(1, h*mm)

def code(text):
    return Paragraph(text.replace("\n", "<br/>").replace("  ", "&nbsp;&nbsp;"), sCode)

def hr(color=MID_GRAY, thick=0.5):
    return HRFlowable(width="100%", thickness=thick, color=color, spaceAfter=3, spaceBefore=3)

# ── Table helpers ────────────────────────────────────────────────────────────
HDR_STYLE = [
    ("BACKGROUND", (0,0), (-1,0), ACCENT),
    ("TEXTCOLOR",  (0,0), (-1,0), WHITE),
    ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",   (0,0), (-1,0), 8.5),
    ("ALIGN",      (0,0), (-1,0), "CENTER"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, ROW_ALT]),
    ("FONTNAME",   (0,1), (-1,-1), "Helvetica"),
    ("FONTSIZE",   (0,1), (-1,-1), 8),
    ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
    ("GRID",       (0,0), (-1,-1), 0.4, colors.HexColor("#CCCCCC")),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
]

def make_table(data, col_widths, extra_style=None):
    style = TableStyle(HDR_STYLE + (extra_style or []))
    return Table(data, colWidths=col_widths, style=style, repeatRows=1)

# ── Cover block ──────────────────────────────────────────────────────────────
def cover_block():
    cover_data = [[
        Paragraph("<br/><br/>", sTitle),
        Paragraph("GymTrack Pro", sTitle),
        Paragraph("System Blueprint v2.0", sSubtitle),
        Paragraph("<br/>", sSubtitle),
        Paragraph("Mobile Gym Management System", sSubtitle),
        Paragraph(".NET MAUI  ·  ASP.NET Core API  ·  MySQL  ·  Gemini AI", sCoverSmall),
        Paragraph("<br/>", sCoverSmall),
        Paragraph("Prepared by: Ghlen Del Rosario", sCoverSmall),
        Paragraph("<br/><br/>", sCoverSmall),
    ]]
    tbl = Table(cover_data, colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BG),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return tbl

# ── BUILD ────────────────────────────────────────────────────────────────────
story = []

# Cover
story.append(cover_block())
story.append(spacer(6))

# 1. Core Idea
story += section("01 · SYSTEM IDENTITY")
story.append(body(
    "<b>What it is:</b> A role-based gym management system - mobile-first (.NET MAUI) + REST API backend + "
    "MySQL database - with QR-powered attendance, Gemini AI assistant, and real-time analytics."
))
story.append(body(
    "<b>What it is NOT:</b> An e-commerce app, social platform, or offline-first app."
))
story.append(spacer(2))

# Tech stack pills as a compact table
story.append(subsection("Tech Stack"))
ts_data = [
    ["Layer", "Technology"],
    ["Mobile App", ".NET MAUI  ·  MVVM Toolkit  ·  CommunityToolkit.Maui"],
    ["Backend", "ASP.NET Core Web API  ·  Entity Framework Core  ·  JWT Auth"],
    ["Database", "MySQL (primary)"],
    ["Local Storage", "SecureStorage (JWT token only)"],
    ["AI Integration", "Gemini API (free tier)"],
    ["QR Generation", "QRCoder library (server-side PNG)"],
]
story.append(make_table(ts_data, [45*mm, CONTENT_W-45*mm]))
story.append(spacer(2))

# 2. User Roles
story += section("02 · USER ROLES & PERMISSIONS")
story.append(body("Two roles: <b>Admin (Gym Owner)</b> and <b>Receptionist (Front Desk Staff)</b>."))
story.append(spacer(2))

perm_data = [
    ["Feature / Action", "Admin", "Receptionist"],
    ["Login / Logout", "Yes", "Yes"],
    ["Full Dashboard (analytics)", "Yes", "No"],
    ["Basic Dashboard (today's stats)", "Yes", "Yes"],
    ["View Members", "Yes", "Yes"],
    ["Add Members", "Yes", "Yes"],
    ["Edit / Delete Members", "Yes", "No"],
    ["Manage Membership Plans", "Yes", "No"],
    ["View Plans", "Yes", "Yes"],
    ["Manage Subscriptions", "Yes", "No"],
    ["Record Payments", "Yes", "Yes"],
    ["View Full Payment History", "Yes", "No"],
    ["View Today's Payments", "Yes", "Yes"],
    ["Manual Check-in / Check-out", "Yes", "Yes"],
    ["QR Scan Check-in", "Yes", "Yes"],
    ["AI Assistant", "Yes", "No"],
    ["Reports Module", "Yes", "No"],
    ["Audit Log", "Yes", "No"],
    ["System Settings", "Yes", "No"],
]

# Set text colors dynamically: Green for "Yes", Red for "No"
perm_styles = [
    ("ALIGN", (1,0), (-1,-1), "CENTER"),
]
for r_idx, row in enumerate(perm_data[1:], start=1):
    for c_idx in [1, 2]:
        val = row[c_idx]
        if val == "Yes":
            perm_styles.append(("TEXTCOLOR", (c_idx, r_idx), (c_idx, r_idx), colors.HexColor("#198754")))
            perm_styles.append(("FONTNAME", (c_idx, r_idx), (c_idx, r_idx), "Helvetica-Bold"))
        elif val == "No":
            perm_styles.append(("TEXTCOLOR", (c_idx, r_idx), (c_idx, r_idx), colors.HexColor("#DC3545")))
            perm_styles.append(("FONTNAME", (c_idx, r_idx), (c_idx, r_idx), "Helvetica-Bold"))

story.append(make_table(perm_data,
    [CONTENT_W-52*mm, 26*mm, 26*mm],
    extra_style=perm_styles
))
story.append(spacer(2))

# 3. Subscription State Machine
story += section("03 · SUBSCRIPTION LIFECYCLE (State Machine)")
states = [
    ["State", "Trigger / Condition"],
    ["PENDING", "Subscription created, StartDate not yet reached"],
    ["ACTIVE", "StartDate reached"],
    ["EXPIRING SOON", "EndDate - Today <= 7 days - triggers local notification"],
    ["EXPIRED", "EndDate passed"],
    ["RENEWED (new row)", "New payment recorded -> new Subscription row created"],
]
story.append(make_table(states, [42*mm, CONTENT_W-42*mm]))
story.append(spacer(1))
story.append(note("Status is computed on-read by the API - no background cron job required for MVP."))
story.append(note("Renewal always creates a NEW Subscription row. Old record stays EXPIRED for history."))
story.append(note("New subscription StartDate = day after previous EndDate (if still active), else today."))
story.append(spacer(2))

# 4. Database Schema
story += section("04 · DATABASE SCHEMA (9 Tables)")

tables_info = [
    ("Users", [
        "UserID (PK)", "Username", "PasswordHash", "Role (Admin/Receptionist)",
        "FullName", "IsActive", "CreatedAt"
    ]),
    ("Members", [
        "MemberID (PK, UUID)", "FirstName", "LastName", "Gender", "Birthdate",
        "Phone (unique)", "Email (unique, nullable)", "Address",
        "EmergencyContactName", "EmergencyContactPhone", "ProfilePhotoUrl",
        "QRToken (unique UUID - not MemberID)", "Status (Active/Inactive)",
        "DateRegistered", "CreatedByUserID (FK -> Users)"
    ]),
    ("MembershipPlans", [
        "PlanID (PK)", "PlanName", "Price (decimal)", "DurationDays (int)",
        "Description", "IsActive (bool - soft delete)", "CreatedAt"
    ]),
    ("Subscriptions", [
        "SubscriptionID (PK)", "MemberID (FK)", "PlanID (FK)",
        "StartDate", "EndDate (auto = StartDate + DurationDays)",
        "Status (Pending/Active/ExpiringSoon/Expired) - computed on-read",
        "PaymentID (FK)", "CreatedByUserID (FK)", "CreatedAt"
    ]),
    ("Payments", [
        "PaymentID (PK)", "MemberID (FK)", "PlanID (FK)", "Amount (decimal)",
        "PaymentMethod (Cash/GCash/Maya/Bank)", "ReferenceNumber (nullable)",
        "DatePaid", "Notes (nullable)", "RecordedByUserID (FK)", "CreatedAt"
    ]),
    ("Attendance", [
        "AttendanceID (PK)", "MemberID (FK)", "CheckInTime (datetime)",
        "CheckOutTime (datetime, nullable)", "Mode (Manual/QR)",
        "RecordedByUserID (FK)", "Date (date - for fast daily queries)"
    ]),
    ("ProgressRecords (optional)", [
        "RecordID (PK)", "MemberID (FK)", "Weight", "Height", "BMI",
        "BodyFatPercent", "Notes", "RecordedAt"
    ]),
    ("AuditLogs", [
        "LogID (PK)", "UserID (FK)", "Action (e.g. MEMBER_CREATED)",
        "EntityType (Member/Payment/etc.)", "EntityID",
        "Details (JSON snapshot)", "Timestamp"
    ]),
    ("ChatLogs (optional)", [
        "LogID (PK)", "UserID (FK)", "Message", "Response",
        "Intent", "Timestamp"
    ]),
]

for tname, fields in tables_info:
    story.append(KeepTogether([
        subsection(f"  {tname}"),
        Paragraph("  " + "   ·   ".join(fields), sSmall),
        spacer(1),
    ]))

story.append(spacer(2))

# 5. API Routes
story += section("05 · REST API ENDPOINTS")

api_groups = [
    ("Auth", [
        ("POST", "/api/auth/login", "Returns JWT + role"),
        ("POST", "/api/auth/logout", "Invalidate token"),
        ("POST", "/api/auth/refresh", "Refresh JWT"),
    ]),
    ("Members", [
        ("GET",    "/api/members",              "Paginated, filterable list"),
        ("GET",    "/api/members/{id}",          "Member detail"),
        ("POST",   "/api/members",              "Create member + generate QRToken"),
        ("PUT",    "/api/members/{id}",          "Update member (Admin)"),
        ("DELETE", "/api/members/{id}",          "Soft delete (Admin)"),
        ("GET",    "/api/members/{id}/qr",       "Returns QR PNG image"),
        ("GET",    "/api/members/{id}/subscriptions", "Subscription history"),
        ("GET",    "/api/members/{id}/payments", "Payment history"),
        ("GET",    "/api/members/{id}/attendance","Attendance history"),
    ]),
    ("Plans", [
        ("GET",    "/api/plans",       "List active plans"),
        ("GET",    "/api/plans/{id}",  "Plan detail"),
        ("POST",   "/api/plans",       "Create plan (Admin)"),
        ("PUT",    "/api/plans/{id}",  "Update plan (Admin)"),
        ("DELETE", "/api/plans/{id}",  "Soft delete (Admin)"),
    ]),
    ("Subscriptions", [
        ("GET",  "/api/subscriptions",       "List, filterable by status"),
        ("GET",  "/api/subscriptions/{id}",  "Detail"),
        ("POST", "/api/subscriptions",       "Create - auto-creates linked payment (tx)"),
        ("PUT",  "/api/subscriptions/{id}",  "Update (Admin)"),
    ]),
    ("Payments", [
        ("GET",  "/api/payments",      "Filterable by date, method, member"),
        ("GET",  "/api/payments/{id}", "Detail"),
        ("POST", "/api/payments",      "Record payment"),
    ]),
    ("Attendance", [
        ("GET",  "/api/attendance",               "Filterable by date / member"),
        ("POST", "/api/attendance/checkin",        "Open attendance record"),
        ("POST", "/api/attendance/checkout",       "Close attendance record"),
        ("GET",  "/api/attendance/today",          "Today's list"),
    ]),
    ("QR System", [
        ("POST", "/api/qr/scan", "Body: { token } -> returns MemberProfile + ActiveSubscription + AttendanceStatus"),
    ]),
    ("AI Chat", [
        ("POST", "/api/chat/query", "Body: { message } -> returns Gemini-formatted response"),
    ]),
    ("Reports (Admin)", [
        ("GET", "/api/reports/revenue",    "Date range + method filter"),
        ("GET", "/api/reports/attendance", "Date range + member filter"),
        ("GET", "/api/reports/members",    "Status filter"),
        ("GET", "/api/reports/expiring",   "Days-until-expiry filter"),
    ]),
    ("Dashboard", [
        ("GET", "/api/dashboard/admin",       "Full analytics snapshot"),
        ("GET", "/api/dashboard/receptionist","Today's stats only"),
    ]),
    ("Audit (Admin)", [
        ("GET", "/api/audit", "Paginated log of all user actions"),
    ]),
]

for group_name, routes in api_groups:
    rows = [["Method", "Endpoint", "Notes"]] + [[m, e, n] for m, e, n in routes]
    col_w = [20*mm, 75*mm, CONTENT_W-95*mm]
    method_colors = [
        ("TEXTCOLOR", (0, i+1), (0, i+1),
         colors.HexColor("#0D6EFD") if routes[i][0]=="GET" else
         colors.HexColor("#198754") if routes[i][0]=="POST" else
         colors.HexColor("#FD7E14") if routes[i][0]=="PUT" else
         colors.HexColor("#DC3545"))
        for i in range(len(routes))
    ]
    story.append(KeepTogether([
        subsection(f"  {group_name}"),
        make_table(rows, col_w, extra_style=method_colors + [("FONTNAME", (0,1), (0,-1), "Courier-Bold"), ("FONTSIZE", (0,1), (0,-1), 8)]),
        spacer(2),
    ]))

story.append(spacer(2))

# 6. QR System Detail
story += section("06 · QR ATTENDANCE - DETAILED FLOW")
story.append(subsection("QR Token Rules"))
story.append(bullet("QRToken is a UUID v4 - separate from MemberID (security best practice)"))
story.append(bullet("Generated automatically on member creation by the API"))
story.append(bullet("Stored in Members table as a unique indexed column"))
story.append(bullet("Exposed via GET /api/members/{id}/qr as a server-rendered PNG image"))
story.append(bullet("Displayable in-app on Member Profile screen + printable via MAUI share sheet"))
story.append(spacer(2))

story.append(subsection("Scan -> Check-in Flow"))
flow_data = [
    ["Step", "Actor", "Action"],
    ["1", "Receptionist", "Opens QR Scanner screen in MAUI app"],
    ["2", "MAUI Camera", "Decodes QR -> extracts QRToken string"],
    ["3", "MAUI -> API", "POST /api/qr/scan  { token: 'uuid' }"],
    ["4", "API", "Looks up Member by QRToken"],
    ["5", "API -> MAUI", "Returns: MemberProfile + ActiveSubscription + AttendanceStatus"],
    ["6", "MAUI UI", "Displays Member Card (photo, name, plan, expiry status)"],
    ["7", "Receptionist", "Reviews card - taps Confirm Check-in button"],
    ["8", "MAUI -> API", "POST /api/attendance/checkin  { memberId, mode: 'QR' }"],
    ["9", "API", "Creates Attendance record, returns success"],
    ["10", "MAUI UI", "Shows success toast - ready for next scan"],
]
story.append(make_table(flow_data, [12*mm, 38*mm, CONTENT_W-50*mm]))
story.append(spacer(2))
story.append(note("Profile preview before confirmation prevents accidental check-ins - cleaner UX and stronger defense demo."))

story.append(spacer(2))

# 7. AI Assistant
story += section("07 · AI ASSISTANT - LOCKED QUERY VOCABULARY")
story.append(body(
    "Architecture: User message -> API intent matching -> pre-built DB query -> context string -> "
    "Gemini API prompt -> natural language response -> MAUI chat UI."
))
story.append(body(
    "Anything outside the 15 locked intents -> Gemini responds: \"I can only answer gym-related questions.\""
))
story.append(spacer(2))

ai_data = [
    ["#", "User Says...", "Maps To"],
    ["1",  "How many active members",        "COUNT active subscriptions"],
    ["2",  "Who expires this week",           "Members with EndDate <= 7 days"],
    ["3",  "Revenue this month",              "SUM payments for current month"],
    ["4",  "Revenue today",                   "SUM payments for today"],
    ["5",  "How many attended today",         "COUNT attendance for today"],
    ["6",  "Who checked in today",            "LIST attendance for today"],
    ["7",  "Member info [name]",              "GET member by name search"],
    ["8",  "When does [name] expire",         "GET subscription EndDate"],
    ["9",  "Is [name] active",                "GET member subscription status"],
    ["10", "How many members total",          "COUNT all members"],
    ["11", "New members this month",          "COUNT members registered this month"],
    ["12", "Most active members",             "TOP 5 by attendance count"],
    ["13", "Unpaid or expired members",       "LIST expired subscriptions"],
    ["14", "Payment history [name]",          "GET payments by member"],
    ["15", "Plans available",                 "LIST all active plans"],
]
story.append(make_table(ai_data, [10*mm, 72*mm, CONTENT_W-82*mm]))
story.append(spacer(2))

# 8. Reports
story += section("08 · REPORTS MODULE")
report_data = [
    ["Report", "Filters", "Output"],
    ["Revenue Report",         "Date range, payment method",  "Total + breakdown by method + daily chart"],
    ["Attendance Report",      "Date range, member",          "Count per day, peak hours"],
    ["Member Status Report",   "Status filter",               "List with plan + expiry date"],
    ["Most Active Members",    "Date range",                  "Top 10 by visit count"],
    ["Expiring Memberships",   "Days until expiry",           "Sorted list with contact info"],
]
story.append(make_table(report_data, [45*mm, 55*mm, CONTENT_W-100*mm]))
story.append(spacer(1))
story.append(note("All reports: table view + summary cards. Optional CSV export via MAUI share sheet."))
story.append(spacer(2))

# 9. Notifications
story += section("09 · LOCAL NOTIFICATIONS")
story.append(body("Implemented via CommunityToolkit.Maui. No external email/SMS service required."))
story.append(spacer(1))
notif_data = [
    ["Trigger Condition", "Notification Message", "When Fired"],
    ["EndDate - Today <= 7 days", "[Warning] {N} memberships expiring soon", "On every app launch"],
    ["EndDate - Today <= 1 day",  "[Alert] {MemberName} expires tomorrow", "On every app launch"],
]
story.append(make_table(notif_data, [58*mm, 72*mm, CONTENT_W-130*mm]))
story.append(spacer(2))

# 10. Screens
story += section("10 · SCREEN MAP")
screens = [
    ("Auth", ["Login Screen"]),
    ("Admin Navigation", [
        "Admin Dashboard (full analytics)",
        "Members List -> Member Detail -> Add/Edit Member",
        "Member Detail sub-screens: Subscription History, Payment History, Attendance History",
        "Member Detail: QR Code display + print/share",
        "Plans Management -> Add/Edit Plan",
        "Subscriptions List",
        "Reports Screen (5 report types)",
        "AI Assistant Chat Screen",
        "Audit Log Screen",
        "Settings Screen",
    ]),
    ("Receptionist Navigation", [
        "Receptionist Dashboard (today only)",
        "Members List (view + add only)",
        "Manual Check-in / Check-out Screen",
        "QR Scanner -> Member Card Preview -> Confirm Check-in",
        "Record Payment Screen",
    ]),
]
for group, items in screens:
    story.append(subsection(f"  {group}"))
    for item in items:
        story.append(bullet(item))
    story.append(spacer(1))

story.append(spacer(2))

# 11. Defense Checklist
story += section("11 · DEFENSE READINESS CHECKLIST")
check_data = [
    ["Area", "Status", "Evidence"],
    ["Real database design (9 tables)", "Done", "Section 04"],
    ["REST API (35+ endpoints)", "Done", "Section 05"],
    ["Mobile architecture (MVVM)", "Done", ".NET MAUI + MVVM Toolkit"],
    ["JWT Authentication", "Done", "Section 01 / Auth endpoints"],
    ["Role-based access control", "Done", "Permission matrix - Section 02"],
    ["CRUD completeness", "Done", "All modules covered"],
    ["Subscription lifecycle logic", "Done", "State machine - Section 03"],
    ["QR automation (scan + profile)", "Done", "Section 06"],
    ["AI integration (Gemini)", "Done", "15 locked intents - Section 07"],
    ["Reports module", "Done", "Section 08"],
    ["Local notifications", "Done", "Section 09"],
    ["Audit/activity log", "Done", "AuditLogs table - Section 04"],
    ["Offline mode", "Removed", "Intentional - avoids sync complexity"],
]
story.append(make_table(check_data, [72*mm, 28*mm, CONTENT_W-100*mm],
    extra_style=[
        ("TEXTCOLOR", (1,1), (1,12), colors.HexColor("#198754")),
        ("TEXTCOLOR", (1,13), (1,13), colors.HexColor("#DC3545")),
        ("FONTNAME", (1,1), (1,-1), "Helvetica-Bold"),
    ]
))

story.append(spacer(4))
story.append(hr(ACCENT, 1))
story.append(Paragraph(
    "GymTrack Pro - System Blueprint v2.0  ·  Ghlen Del Rosario  ·  Mapua Malayan Colleges Laguna",
    sSmall
))

# ── Build ─────────────────────────────────────────────────────────────────────
doc.build(story)
print("Done:", OUTPUT)
