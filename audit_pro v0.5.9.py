"""
Pai Nayak & Associates - Audit Management Software
Custom file extension: .cafe (Company Audit File Encrypted)
Fully offline Windows desktop application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import base64
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import webbrowser
import zlib
import html
from datetime import datetime

# ── Constants ─────────────────────────────────────────────────────────────────
APP_NAME        = "Pai Nayak & Associates"
APP_VERSION     = "0.6.0"
FILE_EXT        = ".cafe"
FILE_EXT_DESC   = "Company Audit File Encrypted"
AUDIT_TYPES     = ["Statutory Audit", "Tax Audit"]
FINANCIAL_YEARS = [
    "FY 2024-25", "FY 2025-26", "FY 2026-27",
]

# ── Firm Logo (base64-encoded PNG) ───────────────────────────────────────────
FIRM_LOGO_B64 = "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7c3rxgZ9Vp3i+VVy8tnlw0lPFgx09O0sja4fpYz156rlogJD/KKnqYYm3SzwVc0LMRzsfse8g8eZkHeO2BjPqufebxVXR8YlbHFDC3bDBEMMjHoAuciA69BeWR0oo7hQx19OMBu55bJG3uGO5Dc/I+3Ur7eL/PX0MNuhp4aKhhcXCGHID3H9J3q7AAzx06LjogN24XCSsp6SF7dopovLGCTntn24AH0WS13epoKOspI2tkhq2Br2PLsAgg5GCOeO+R+AxzkQGegqXUddT1cbWudBK2RrXdCWnOD+C2YrrJHfjdzTwvkM7pzG7OzcST2OcAn1yueiA9zSPmmfLI4ue9xc4nuTySto3GY2YWtzI3RNm85ryPiacYIB9Dx+AWkiA3r7cpbvdZrjPHHHJMQXNjztGABxnPos8d+r22F9lc5r6UvDmg5yw5zxg/xyuUiA3rLcp7VW/aoGse7btLX5wRkHt7gLBQ1U9FWRVdM/ZNE8PY70I6LAiAkD9RU8srauWx0JrWvDg9uWxu5y4uZ3JPOcgD0XIudbUXGvmrap4dNM7c4gYH4LWRAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQH/2Q=="

def _load_firm_logo(width=460, height=82):
    """Return a tk.PhotoImage of the firm logo scaled to fit."""
    import tkinter as tk
    import base64, io
    try:
        from PIL import Image, ImageTk
        data = base64.b64decode(FIRM_LOGO_B64)
        img  = Image.open(io.BytesIO(data)).convert("RGBA")
        img  = img.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except ImportError:
        # Fallback — use tk's built-in PNG support (no resize)
        photo = tk.PhotoImage(data=FIRM_LOGO_B64)
        # tk.PhotoImage subsample to approximate sizing
        sx = max(1, photo.width()  // width)
        sy = max(1, photo.height() // height)
        s  = max(1, min(sx, sy))
        return photo.subsample(s, s)

# ── .cafe File Encryption ──────────────────────────────────────────────────────
# XOR cipher with a SHA-256 derived key + zlib compression + base64 encoding.
# Files written by v0.5.9+ start with _CAFE_MAGIC; older plain-JSON files are
# detected automatically and loaded without decryption (backwards compatible).

_CAFE_MAGIC  = b"PNAENC1:"
_CAFE_PHRASE = b"PaiNayakAndAssociates_CAFE_v1"

def _cafe_key():
    return hashlib.sha256(_CAFE_PHRASE).digest()   # 32-byte repeating key

def _cafe_encrypt(json_str: str) -> bytes:
    raw = zlib.compress(json_str.encode("utf-8"), level=6)
    key = _cafe_key()
    enc = bytes(b ^ key[i % 32] for i, b in enumerate(raw))
    return _CAFE_MAGIC + base64.b64encode(enc) + b"\n"

def _cafe_decrypt(raw: bytes) -> str:
    b64 = raw[len(_CAFE_MAGIC):].strip()
    enc = base64.b64decode(b64)
    key = _cafe_key()
    dec = bytes(b ^ key[i % 32] for i, b in enumerate(enc))
    return zlib.decompress(dec).decode("utf-8")

def _cafe_is_encrypted(filepath: str) -> bool:
    # Only treat .cafe files as encrypted
    if not filepath.lower().endswith(".cafe"):
        return False
    try:
        with open(filepath, "rb") as f:
            head = f.read(len(_CAFE_MAGIC) + 16).lstrip()
        return head.startswith(_CAFE_MAGIC)
    except Exception:
        return False

def _cafe_load(filepath: str) -> dict:
    # Only allow loading encrypted .cafe files
    if not filepath.lower().endswith(".cafe"):
        raise ValueError("Only .cafe files are supported.")
    with open(filepath, "rb") as f:
        raw = f.read().lstrip()
    if raw.startswith(_CAFE_MAGIC):
        return json.loads(_cafe_decrypt(raw))
    raise ValueError("File is not a valid encrypted .cafe file.")


def _cafe_save(filepath: str, data: dict) -> None:
    # Only allow saving as encrypted .cafe files
    if not filepath.lower().endswith(".cafe"):
        raise ValueError("Only .cafe files are supported.")
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    with open(filepath, "wb") as f:
        f.write(_cafe_encrypt(json_str))
    # Optionally, make file read-only (uneditable) at OS level
    try:
        os.chmod(filepath, 0o444)
    except Exception:
        pass

# ── Engagement Lock Passwords ────────────────────────────────────────────────
MASTER_PASSWORD = "PAINAYAK2000"
_PW_SALT = b"pna_caf_lock_v1"

def _hash_password(password: str, eng_id: str = "") -> str:
    h = hashlib.sha256()
    h.update(_PW_SALT)
    h.update(eng_id.encode("utf-8"))
    h.update(password.encode("utf-8"))
    return h.hexdigest()

def _verify_password(password: str, eng) -> bool:
    if password == MASTER_PASSWORD:
        return True
    stored = eng.get("lock_password_hash")
    if not stored:
        return True   # legacy: no password set, allow unlock
    return _hash_password(password, eng.get("id", "")) == stored


# ── Balance Sheet Line Items (Schedule III, India) ────────────────────────────
BS_LINE_ITEMS = [
    ("section", "EQUITY AND LIABILITIES"),
    ("section", "    Shareholders' Funds"),
    ("item",    "Share Capital"),
    ("item",    "Reserves and Surplus"),
    ("item",    "Money received against share warrants"),
    ("section", "    Share Application Money Pending Allotment"),
    ("item",    "Share application money pending allotment"),
    ("section", "    Non-current Liabilities"),
    ("item",    "Long-term Borrowings"),
    ("item",    "Deferred Tax Liabilities (Net)"),
    ("item",    "Other Long-term Liabilities"),
    ("item",    "Long-term Provisions"),
    ("section", "    Current Liabilities"),
    ("item",    "Short-term Borrowings"),
    ("item",    "Trade Payables"),
    ("item",    "Other Current Liabilities"),
    ("item",    "Short-term Provisions"),
    ("section", "TOTAL EQUITY AND LIABILITIES"),
    ("section", "ASSETS"),
    ("section", "    Non-current Assets"),
    ("item",    "Property, Plant and Equipment (Tangible)"),
    ("item",    "Intangible Assets"),
    ("item",    "Capital Work-in-Progress"),
    ("item",    "Intangible Assets Under Development"),
    ("item",    "Non-current Investments"),
    ("item",    "Deferred Tax Assets (Net)"),
    ("item",    "Long-term Loans and Advances"),
    ("item",    "Other Non-current Assets"),
    ("section", "    Current Assets"),
    ("item",    "Current Investments"),
    ("item",    "Inventories"),
    ("item",    "Trade Receivables"),
    ("item",    "Cash and Cash Equivalents"),
    ("item",    "Short-term Loans and Advances"),
    ("item",    "Other Current Assets"),
    ("section", "TOTAL ASSETS"),
]

# ── Profit & Loss Line Items (Schedule III, India) ────────────────────────────
PL_LINE_ITEMS = [
    ("section", "INCOME"),
    ("item",    "Revenue from Operations"),
    ("item",    "Other Income"),
    ("section", "TOTAL INCOME"),
    ("section", "EXPENSES"),
    ("item",    "Cost of Materials Consumed"),
    ("item",    "Purchases of Stock-in-Trade"),
    ("item",    "Changes in Inventories of FG, WIP & Stock-in-Trade"),
    ("item",    "Employee Benefits Expense"),
    ("item",    "Finance Costs"),
    ("item",    "Depreciation and Amortisation Expense"),
    ("item",    "Other Expenses"),
    ("section", "TOTAL EXPENSES"),
    ("section", "PROFIT BEFORE EXCEPTIONAL & EXTRAORDINARY ITEMS AND TAX"),
    ("item",    "Exceptional Items"),
    ("item",    "Extraordinary Items"),
    ("section", "PROFIT BEFORE TAX"),
    ("section", "TAX EXPENSE"),
    ("item",    "Current Tax"),
    ("item",    "Deferred Tax"),
    ("item",    "Earlier Year Tax Adjustments"),
    ("section", "PROFIT FOR THE YEAR"),
]

# Variance threshold (% change above which the row is flagged)
VARIANCE_THRESHOLD_PCT = 10.0

# ── Pre-Audit Documents ───────────────────────────────────────────────────────
PRE_AUDIT_DOCS_STAT = [
    ("letter_seeking_consent",    "Letter Seeking Auditors Consent"),
    ("auditors_consent_letter",   "Auditors Consent Letter"),
    ("auditors_appointment_letter","Auditors Appointment Letter"),
    ("auditors_appointment_res",  "Auditors Appointment Resolution"),
    ("acceptance_continuance",    "Acceptance & Continuance"),
    ("engagement_letter_general", "Engagement Letter — General"),
    ("engagement_letter_icofar",  "Engagement Letter — ICOFAR"),
    ("independence_confirmation", "Independence Confirmation"),
    ("audit_planning_checklist",  "Audit Planning Checklist"),
    ("minutes_team_planning",     "Minutes of Team Planning Meeting"),
    ("overall_strategy_memo",     "Overall Audit Strategy Memo"),
    ("risk_assessment",           "Risk Assessment"),
]

PRE_AUDIT_DOCS_TAX = [
    ("engagement_letter_tax",     "Engagement Letter — Tax Audit"),
    ("acceptance_continuance",    "Acceptance & Continuance"),
    ("independence_confirmation", "Independence Confirmation"),
    ("appointment_letter_tax",    "Tax Audit Appointment Letter"),
    ("board_resolution_tax",      "Board Resolution — Tax Audit"),
    ("prior_year_3cd",            "Previous Year Form 3CD"),
    ("client_kyc_docs",           "Client KYC / PAN / GST Documents"),
]


# ══════════════════════════════════════════════════════════════════════════════
# IFC Checklist — Internal Financial Controls
# Each section: (section_key, display_name, [(q_key, question_text), ...])
# ══════════════════════════════════════════════════════════════════════════════
IFC_CHECKLISTS = [
    ("assets", "Assets", [
        ("q_1",  "Are responsibilities for initiating, evaluating, and approving capital expenditures, leases, and maintenance or repair projects adequately segregated from those for project accounting, property records, and general ledger functions?"),
        ("q_2",  "Are responsibilities for initiating capital asset transactions adequately segregated from those for final approval, or committing government resources?"),
        ("q_3",  "Do authorization procedures and controls include proper methodology for identification of those individuals authorized to initiate capital asset transactions and clear definition of their authority?"),
        ("q_4",  "Are proper Procedures / Guidelines in place with respect to key considerations, such as prices to be paid, acceptable vendors and terms, asset quality standards, and the provision of funds for financing the expenditures?"),
        ("q_5",  "Are procedures in place for preparation, review and approval of a separate capital projects budget?"),
        ("q_6",  "Are proper procedures in place that require written executive approval for all significant capital asset projects or acquisitions?"),
        ("q_7",  "Are proper procedures in place for evaluating, approving and reviewing the decisions regarding suitable financing alternatives for funding the capital project?"),
        ("q_8",  "Are proper procedures in place for establishing and maintaining project cost records for capital expenditure and repair projects?"),
        ("q_9",  "Are proper procedures in place for review of the accounting distribution to ensure proper allocation of charges to capital asset and expenditure projects?"),
        ("q_10", "If construction work is performed by contractors, are proper procedures in place to provide for and maintain control over construction projects and progress billings?"),
        ("q_11", "Are proper procedures in place for authorizing, approving, and documenting sales or other dispositions of capital assets?"),
        ("q_12", "Is proper procedure in place for duly recording the capital asset in the Fixed Asset Register with proper identification and duly depreciating the same as per consistent accounting policy followed by the entity?"),
        ("q_13", "Is there a procedure in place for carrying fully depreciated assets in the accounting records as a means of providing accounting control?"),
        ("q_14", "Is proper procedure in place for periodic reconciliation of the detailed property/asset registers and records with the general ledger control accounts?"),
        ("q_15", "Are the accounting records adjusted promptly (both the asset and related allowance for depreciation) when items of plant and equipment are retired, sold, or transferred?"),
    ]),
    ("cash", "Cash & Bank", [
        ("q_1",  "Are responsibilities for collection and deposit preparation functions adequately segregated from those for recording cash receipts and general ledger entries?"),
        ("q_2",  "Are responsibilities for cash receipts functions adequately segregated from those for cash disbursements?"),
        ("q_3",  "Are responsibilities for disbursement preparation and disbursement approval functions adequately segregated from those for recording or entering cash disbursements information on the general ledger?"),
        ("q_4",  "Are responsibilities for preparing and approving bank account reconciliations adequately segregated from those for other cash receipt or disbursement functions?"),
        ("q_5",  "Do collections procedures provide for timely deposit of all receipts into the bank accounts?"),
        ("q_6",  "Are proper procedures in place for monitoring the collections in different locations?"),
        ("q_7",  "Are proper procedures in place for daily reconciliation of cash and bank balances?"),
        ("q_8",  "Are adequate security measures in the form of safe lockers, etc., provided at locations where there are significant cash collections?"),
        ("q_9",  "Is dual authorisation procedure in place for opening and handling safe lockers?"),
        ("q_10", "Are procedures in place for daily reporting of collections to the head office?"),
        ("q_11", "Do disbursement procedures include control over safe keeping of cheques / warrants?"),
        ("q_12", "Is a proper procedure in place for setting limits and giving authority for the cheque signer?"),
        ("q_13", "Is a proper review procedure in place to review whether limits and authority stipulated for cheque/warrant signer is duly informed to the bank and updated in the Bank software?"),
        ("q_14", "Are proper procedures in place for providing immediate notification to banks when warrant or check signers leave the unit or are otherwise no longer authorized to sign?"),
        ("q_15", "Are proper systems in place for prohibiting issue of bearer / name cheque without crossing 'Account Payee'?"),
        ("q_16", "Are proper procedures in place to prevent duplicate payments?"),
        ("q_17", "Do custody procedures provide for maintenance and control over unused / voided cheques / warrants?"),
        ("q_18", "Are proper systems in place for ensuring that collections and disbursements are recorded accurately and promptly in the correct fund or account?"),
        ("q_19", "Are proper procedures in place for authorizing and recording inter-bank and inter-fund transfers and providing for proper accounting for those transactions?"),
        ("q_20", "Are proper procedures in place for review and approval of all reconciliations and investigation of unusual reconciling items by an official not responsible for receipts and disbursements?"),
        ("q_21", "Are proper procedures in place for periodic investigation of checks outstanding for a considerable time?"),
    ]),
    ("employee_benefits", "Employee Benefits", [
        ("q_1",  "Are responsibilities for supervision and time-keeping functions adequately segregated from personnel, payroll processing, disbursement, and general ledger functions?"),
        ("q_2",  "Are responsibilities for the payroll processing function adequately segregated from the general ledger function?"),
        ("q_3",  "Are responsibilities for initiating payments under employee benefit plans adequately segregated from accounting and general ledger functions?"),
        ("q_4",  "Are there adequate procedures in place for properly authorizing, approving, and documenting all changes in employment (additions and terminations), salary and wage rates, and payroll deductions?"),
        ("q_5",  "Are there proper procedures in place for promptly reporting notices of additions, separations, and changes in salaries, wages, and deductions to the payroll processing function?"),
        ("q_6",  "Are there procedures in place for maintaining appropriate payroll records for accumulated employee benefits (vacation, pension data, sick leave, etc.)?"),
        ("q_7",  "Do supervision/time-keeping procedures include framework for review and approval by the employee's supervisor of hours worked, overtime hours, and other special benefits?"),
        ("q_8",  "Are there proper procedures in place for time keeping and attendance records?"),
        ("q_9",  "Are there proper procedures in place for authorizing, approving, and recording vacations, holidays, and sick leave and for approving and controlling compensatory time?"),
        ("q_10", "Do payroll processing procedures include proper control over payroll preparation and approvals?"),
        ("q_11", "Are proper systems in place for review and approval of completed payroll registers before disbursements are made?"),
        ("q_12", "Are proper systems in place for review of documents supporting employee benefit payments (such as accumulated vacation or sick leave) before disbursements are made?"),
        ("q_13", "Are there proper procedures in place for periodical review for reasonableness of comparisons (reconciliations) of gross pay for current to prior period payrolls by a knowledgeable person not otherwise involved in payroll processing?"),
        ("q_14", "Do payroll disbursement policies include a procedure for strong encouragement for all employees to receive payroll disbursement through direct deposit to their bank account?"),
        ("q_15", "If payment is made in cash, is there a proper procedure in place requiring signed receipts; and having someone independent of the payroll department compare the signed receipts, on a test basis, with signatures on file?"),
        ("q_16", "Are proper systems in place for returning unclaimed / returned wage payments to a custodian independent of the payroll department?"),
        ("q_17", "Are proper systems in place for making payments of unclaimed wages at a later date, only upon presentation of appropriate evidence of employment and with approval by an officer not responsible for payroll preparation or time reporting?"),
        ("q_18", "Is there an adequate procedure in place for proper recording or disclosure of accrued liabilities for unpaid employee compensation and benefit costs?"),
    ]),
    ("financial_reporting", "Financial Reporting", [
        ("q_1",  "Are responsibilities for the final review and approval of financial reports adequately segregated from those for the preparation of the reports?"),
        ("q_2",  "Are responsibilities for maintaining the general ledger adequately segregated from those for maintaining subsidiary ledgers?"),
        ("q_3",  "Are responsibilities for maintaining the general ledger adequately segregated from those for the custody of assets?"),
        ("q_4",  "Are responsibilities for principal accounting and for custody functions adequately segregated?"),
        ("q_5",  "Are the written accounting policy and procedural manuals distributed to appropriate personnel?"),
        ("q_6",  "Are proper procedures in place for updating the accounting policy and procedural manuals, as necessary?"),
        ("q_7",  "Are there proper systems in place for periodically evaluating the adequacy and effectiveness of the internal accounting controls related to the organization's transaction systems (procurement, revenues, receivables, etc.)?"),
        ("q_8",  "Are there adequate procedures and policies in place for closing the accounts for a reporting period, sufficient to ensure accounts are closed, adjusted, and reviewed on a timely basis?"),
        ("q_9",  "Are there proper procedures in place to ensure all accounting systems have included all transactions applicable to the reporting period?"),
        ("q_10", "Are proper systems in place for review and approval of provisions and other account balances based on estimates?"),
        ("q_11", "Is a proper system in place for having all journal entries reviewed, approved, and supported by adequate descriptions, narrations and/or documentation?"),
        ("q_12", "Are there proper procedures in place to ensure financial reports are supported by the underlying account records and/or other documentation?"),
        ("q_13", "Are there proper procedures in place for providing reasonable assurances that all data required to be included in legal, as well as public reports, are properly disclosed?"),
        ("q_14", "Are proper systems in place to ensure financial reports are prepared on a consistent basis?"),
        ("q_15", "Are proper procedures in place for review and approval of financial reports at appropriate levels of management before its release?"),
        ("q_16", "Are there proper procedures in place to ensure all requirements for filing of financial reports with the applicable regulatory agency / tax authority are duly met (ROC, SEBI, IT, etc.)?"),
    ]),
    ("investments", "Investments", [
        ("q_1",  "Are responsibilities for initiating, evaluating, and approving investment transactions adequately segregated from those for detail accounting, general ledger, and other related functions?"),
        ("q_2",  "Are responsibilities for initiating investment transactions adequately segregated from those for final approvals committing resources?"),
        ("q_3",  "Are responsibilities for monitoring investment market values and performance adequately segregated from those for investment acquisition?"),
        ("q_4",  "Are custodial responsibilities for securities or other investment documents evidencing ownership or other rights assigned to an official with no accounting duties?"),
        ("q_5",  "Are there adequate procedures in place to ensure only investments permitted by law are acquired?"),
        ("q_6",  "Are there properly established authority and responsibility frameworks in place for investment-opportunity evaluation and purchase?"),
        ("q_7",  "Are there proper systems in place for periodic evaluation of the performance of the investment portfolio by persons independent of investment portfolio management activities?"),
        ("q_8",  "Are there proper procedures in place governing the level and nature of approvals required to purchase or sell an investment?"),
        ("q_9",  "Do custody procedures include adequate physical safeguards over custody of negotiable/non-negotiable instruments and legal documents of ownership?"),
        ("q_10", "Are proper authorisation procedures in place to obtain release of securities from safekeeping?"),
        ("q_11", "Are proper procedures in place to ensure transactions arising from investments are properly processed, including income and amortization entries, wherever applicable?"),
        ("q_12", "Are proper systems in place for periodic comparison between income received and the amount specified by the terms of the security, or from publicly available investment information?"),
    ]),
    ("it_infrastructure", "IT Infrastructure", [
        ("q_1",  "Is the EDP department independent from the accounting and operating departments for which it processes data?"),
        ("q_2",  "Are duties within the data-processing function as adequately segregated as systems design, technical support and operations?"),
        ("q_3",  "Do EDP user controls include controls over preparation and approval of input transactions outside the EDP department and controls prohibiting the EDP department from initiating transactions?"),
        ("q_4",  "Are proper controls in place over entry of data in on-line systems to restrict access to terminals and to restrict data entry to authorized employees?"),
        ("q_5",  "Are there proper on-line systems controls in place to prevent documents from being keyed into the system more than once and to permit tracing from the computer output to data source and vice versa?"),
        ("q_6",  "Are proper controls in place over changes to master files, such as requiring preparation of specific forms indicating data to be changed, approval by a supervisor in the user department, and verifying against a printout of changes?"),
        ("q_7",  "Are proper procedures in place within the data processing function for providing proper control of data between the user and the EDP department?"),
        ("q_8",  "Are adequate automated controls over data entry in place — for example, to include adequate supervision, up-to-date instructions, key verification of important fields, and self-checking digits, etc.?"),
        ("q_9",  "Are proper procedures in place within the data processing control function concerning review and distribution of output?"),
        ("q_10", "Are adequate controls in place over changes to system software?"),
        ("q_11", "Are proper systems and controls over use and retention of tape and disk files, including provision for retention of adequate records to provide backup capabilities?"),
        ("q_12", "Is proper documentation or written manuals available regarding the procedures to be followed by computer operators?"),
        ("q_13", "Is there adequate documentation / framework available to provide for continuation of the organization, even if important data processing employees leave?"),
        ("q_14", "Are proper procedures in place to protect against a loss of important files, programs, or equipment?"),
        ("q_15", "Are proper procedures in place for carrying out adequate and sufficient testing and code review of new systems or modifications to existing application systems by competent personnel before the same is deployed?"),
    ]),
    ("purchases", "Purchases", [
        ("q_1",  "Are responsibilities for the requisitioning, purchasing, and receiving functions adequately segregated from those for the invoice processing, accounts payable, and general ledger functions?"),
        ("q_2",  "Are responsibilities for the purchasing function adequately segregated from those for the requisitioning and receiving functions?"),
        ("q_3",  "Are responsibilities for the invoice processing and accounts payable functions adequately segregated from those for the general ledger functions?"),
        ("q_4",  "Are responsibilities for the disbursement preparation and disbursement approval functions adequately segregated from those for recording cash disbursements and general ledger entries?"),
        ("q_5",  "Are responsibilities for the disbursement approval function adequately segregated from those for the disbursement preparation function?"),
        ("q_6",  "Is initiation of purchases of goods and services done by properly authorized requisitions bearing the approval of officials designated to authorize requisitions?"),
        ("q_7",  "Before commitment, is there a proper procedure in place for verification by the accounting and budget department to ensure that sufficient unobligated funds remain under the appropriation to meet the proposed expenditure?"),
        ("q_8",  "Do purchasing procedures and controls include proper framework for purchase order, contract issuance, and contract approvals?"),
        ("q_9",  "Is proper procedure in place for a periodic review of purchase prices through market inquiry by a responsible employee independent of the purchasing department?"),
        ("q_10", "Is proper procedure in place for rotation of purchase officer's area of responsibility within the organization?"),
        ("q_11", "Wherever competitive bidding procedures are followed, is there a proper framework for a tamper-proof bidding process?"),
        ("q_12", "Is periodic review of recurring purchases and documentation being carried out to check the justification for informal, rather than competitive, bids?"),
        ("q_13", "Are procedures in place for issuing purchase orders and contracts under numerical or some other suitable control?"),
        ("q_14", "Are proper procedures in place for obtaining an adequate number of price quotations before placing orders not subject to competitive bidding?"),
        ("q_15", "Is there a system of maintenance of price lists and other appropriate records of price quotations by the purchasing department?"),
        ("q_16", "Is there a proper system of maintenance of a record of suppliers who have not met quality or other performance standards by the purchasing department?"),
        ("q_17", "Do receiving procedures and controls include preparation of receiving reports / Goods Receipt Notes (GRNs) for all purchased goods?"),
        ("q_18", "Are proper procedures in place for taking steps to ensure goods received are accurately counted and examined, to ensure they meet quality standards?"),
        ("q_19", "Are proper procedures in place for numerically accounting for or otherwise controlling receiving reports, to ensure all receipts are reported to the accounting department?"),
        ("q_20", "Is a proper system in place for sending copies of receiving reports directly to purchasing, accounting, and (if appropriate) inventory record keeping?"),
        ("q_21", "Are adequate procedures in place to ensure goods for which payment is made have been received and they meet quality standards?"),
        ("q_22", "Does invoice processing include procedures and controls for reviewing the invoice quantities, prices, and terms to be compared with those on the purchase order and Goods Received Note?"),
        ("q_23", "Does the invoice processing procedure include proper method for verification of calculations, price/rate charges, rate of tax and other information mentioned in the invoice?"),
        ("q_24", "Does the invoice processing procedure include periodical verification of the contents of the invoice to see whether all applicable legal stipulations under the relevant indirect tax legislations regarding contents of the invoice are duly followed?"),
        ("q_25", "Is there a proper procedure in place for centralised receipt and processing of invoices from suppliers?"),
        ("q_26", "Are proper procedures in place for periodical reconciliation of Purchase Order / Goods Received Note / Purchase Invoice / Payment processing?"),
        ("q_27", "If an invoice is received from a supplier not previously dealt with, is a proper procedure in place for taking steps to ascertain the supplier actually exists?"),
        ("q_28", "Is there a proper procedure in place for controlling and monitoring the making of payments only on the basis of original invoices duly approved for payment?"),
        ("q_29", "Are proper procedures in place for referring differences in invoice and purchase order price, terms, shipping arrangements, or quantities to the purchasing department for review and approval?"),
        ("q_30", "Are proper procedures in place for recording and following up on partial deliveries by the accounting department?"),
        ("q_31", "Is proper procedure in place for promptly notifying the accounting and purchasing departments of returned purchases and correlating such purchases with vendor credit advices?"),
        ("q_32", "Do disbursements procedures include control over signing of warrants, drafts, and checks only after disbursement has had final approval?"),
        ("q_33", "Were invoices and supporting documents duly furnished to the signer prior to signing the warrant, sight-draft, or check?"),
        ("q_34", "Does the procedure for accounts payable record-keeping include regular comparison of statements from vendors with recorded amounts payable?"),
        ("q_35", "Is a proper procedure in place for review of ageing statement of trade payables and escalating old outstanding issues to the top management / CFO?"),
    ]),
    ("inventory", "Inventory", [
        ("q_1",  "Are responsibilities for physical custody of inventory (stores) adequately segregated from those for recording inventory transactions, accounts payable, and general ledger functions?"),
        ("q_2",  "Are responsibilities for the purchasing function adequately segregated from those for physical custody of inventory and inventory record-keeping?"),
        ("q_3",  "Are proper procedures in place for preparation and approval of Goods Receipt Notes (GRNs) for all inward inventory movements, with three-way matching of GRN, Purchase Order, and Supplier Invoice before goods are accepted into stores?"),
        ("q_4",  "Are goods issued from stores only against duly authorized Material Issue Slips / Store Requisitions approved by the appropriate authority, with no unauthorized withdrawals permitted?"),
        ("q_5",  "Is a periodic physical verification of inventory conducted in accordance with the Companies Act, 2013 and the applicable Rules, and are the results reconciled with book records, with differences duly investigated and approved adjustments recorded?"),
        ("q_6",  "Is the method of inventory valuation (FIFO / Weighted Average Cost) consistently applied in accordance with AS 2 / Ind AS 2 as applicable, and is inventory stated at the lower of cost and Net Realisable Value (NRV)?"),
        ("q_7",  "Are proper procedures in place for periodic assessment of NRV for all inventory categories, with write-downs to NRV recognised wherever cost exceeds NRV, duly approved by an appropriate authority?"),
        ("q_8",  "Are proper procedures in place for identification of slow-moving, non-moving, and obsolete inventory, with ageing reports reviewed by management and appropriate provisions created with proper authorisation?"),
        ("q_9",  "Are bin cards / stores ledgers maintained for all inventory items and periodically reconciled with the general ledger inventory control account, with unexplained differences escalated promptly?"),
        ("q_10", "Are proper cut-off procedures in place at each period-end to ensure goods received but not yet invoiced (GRN accruals) and goods despatched but not yet invoiced are accounted for in the correct accounting period?"),
        ("q_11", "Are proper procedures in place for accounting of process scrap, waste, and rejections, including authorisation for scrap write-offs and recording of recoveries / sale proceeds from disposal of scrap?"),
        ("q_12", "Is inventory held outside company premises — such as with job workers, at public warehouses, or with consignees — properly identified, tracked in separate records, and periodically confirmed by physical verification or third-party certificate?"),
        ("q_13", "Are inter-location / inter-unit stock transfers supported by authorised Transfer Notes and accounted for in both sending and receiving locations on the same date to prevent double-counting or omission?"),
        ("q_14", "Are inventory movement records periodically reconciled with GST returns (GSTR-1, GSTR-2B, and GSTR-3B) to ensure consistency between inventory transactions and Input Tax Credit claimed / reversed?"),
        ("q_15", "Are access rights to the inventory management system appropriately restricted by role, and are changes to inventory master data — such as item codes, unit of measure, and standard / landed costs — subject to formal authorisation and an audit trail?"),
    ]),
    ("revenue", "Revenue", [
        ("q_1",  "Are responsibilities for billing for goods and/or services adequately segregated from those for collection and accounting?"),
        ("q_2",  "Are responsibilities for maintaining detail accounts receivable records adequately segregated from those for collection and general ledger posting?"),
        ("q_3",  "Are tax assessment compliance responsibility and records held / maintained by individuals not engaged in any accounting or collection function?"),
        ("q_4",  "Are proper procedures in place for creating, maintaining and reviewing the database of customers?"),
        ("q_5",  "Are proper Verification and Validation procedures in place for recording the Tax Identification Number of the customer?"),
        ("q_6",  "Are proper procedures in place for thorough verification of calculation of rates, quantity, value, etc., in the sales invoices before the same is despatched to the customer?"),
        ("q_7",  "Are proper procedures in place for ascertaining the rate of tax and checking whether the tariff head applied is accurate?"),
        ("q_8",  "Are proper procedures in place for ensuring compliance with tax laws in respect of raising invoice in the prescribed format, timeliness of raising the invoice, etc.?"),
        ("q_9",  "Are proper procedures in place for printing the credit period and consequence of default in payment within the credit period, terms of cash discount if paid earlier, in the sales invoice?"),
        ("q_10", "Are proper procedures in place for generating the E-Way Bill / E-Invoice or such other procedure as may be required by the indirect tax legislation as applicable to the relevant time?"),
        ("q_11", "Are proper procedures including maker-checker-approver framework established and followed in the raising of invoice to customers?"),
        ("q_12", "Are proper procedures in place over billing and collection for miscellaneous revenue items, scrap sales, waste sales, etc.?"),
        ("q_13", "Are proper procedures in place for investigating and concluding the complaints / reports / disputes from customers regarding the contents in the sales invoice including invoice value, rate, quantity, etc.?"),
        ("q_14", "Do the collection procedures include strict control over cheques received?"),
        ("q_15", "Are proper controls in place for collection, timely deposit, and recording of collections in the accounting records at each collection location?"),
        ("q_16", "Are proper procedures in place for identifying and correctly recording direct deposit / NEFT / RTGS / IMPS collections from customers and duly accounting against the relevant invoice?"),
        ("q_17", "Are proper procedures in place for maintaining bill-to-bill set off of receipts against bills?"),
        ("q_18", "Are proper procedures in place for review of aging of receivables by supervisory personnel?"),
        ("q_19", "Are proper procedures in place for escalating the information about customer non-payment to people in the top management?"),
        ("q_20", "Are procedures in place for proper handling of subsequent purchase request from a delinquent customer who has unpaid old bills outstanding?"),
        ("q_21", "Are write-offs or other reductions of receivables formally approved by senior officials not involved in the collection function?"),
        ("q_22", "Are procedures provided for executing all possible legal remedies to collect written-off or uncollectible accounts, including tax-sale of property, liens, etc.?"),
        ("q_23", "Are proper procedures in place for obtaining and reconciling periodical confirmation statements from customers, say quarterly, half-yearly, etc.?"),
    ]),
    ("sa_210", "SA 210 — Terms of Engagement", [
        ("q_1",  "Is the applicable financial reporting framework correctly applied by the entity in preparation of the financial statements?"),
        ("q_2",  "Does the management acknowledge and understand its responsibility for the preparation of financial statements in accordance with the applicable financial reporting framework including its fair presentation?"),
        ("q_3",  "Does the management acknowledge and understand its responsibility for adequate internal control mechanism as is necessary for the preparation of financial statements that is free from material mis-statement?"),
        ("q_4",  "Has the management agreed to provide the auditor with access to all the information of which the management is aware and is relevant for the preparation of financial statements including all the records, documents, electronic records, etc.?"),
        ("q_5",  "Has the Management agreed to provide any other additional information that may be called for by the Auditor for the purpose of audit?"),
        ("q_6",  "Has the management agreed to provide unrestricted access to people in the entity from whom necessary audit evidence can be obtained?"),
    ]),
    ("sa_220", "SA 220 — Quality Control", [
        ("q_1",  "Has the engagement partner taken responsibility for the overall quality in this audit?"),
        ("q_2",  "Is there an indication of non-compliance with relevant ethical requirements by members of the engagement team? If yes, explain the details and steps to address the same in the Comments box."),
        ("q_3",  "Has the engagement partner reviewed all the relevant information from the firm and, where applicable, network firms, to identify and evaluate circumstances and relationships that create threats to independence?"),
        ("q_4",  "Has the Engagement Partner evaluated the information on identified breaches, if any, of the firm's independence policies and procedures to determine whether they create a threat to independence for the audit engagement?"),
        ("q_5",  "Where any threat to independence is noticed, whether appropriate action has been taken to eliminate such threats or reduce them to an acceptable level by applying necessary safeguards?"),
        ("q_6",  "Is the engagement partner satisfied that appropriate procedures regarding the acceptance and continuance of client relationships and audit engagements have been followed, and conclusions reached in this regard are appropriate?"),
        ("q_7",  "Is the engagement partner satisfied that the engagement team collectively have the appropriate competence and capabilities to perform the audit engagement in accordance with professional standards and regulatory and legal requirements?"),
        ("q_8",  "Has the engagement partner taken responsibility for the direction, supervision and performance of the audit engagement in compliance with professional standards and regulatory and legal requirements?"),
        ("q_9",  "Has the engagement partner taken responsibility for reviews being performed in accordance with the firm's review policies and procedures?"),
        ("q_10", "Has the engagement partner carried out a thorough review of the audit documentation and other evidences gathered and accordingly fully satisfied that sufficient appropriate audit evidence has been obtained to support the conclusions reached?"),
        ("q_11", "Whether the engagement partner has taken responsibility for (a) the engagement team undertaking appropriate consultation on difficult or contentious matters; (b) appropriate consultation during the course of the engagement; (c) the nature and scope of, and conclusions resulting from, such consultations; and (d) conclusions resulting from such consultations have been implemented?"),
        ("q_12", "For audits of financial statements of listed entities, whether the engagement partner has (a) determined the need to appoint an engagement quality control reviewer; (b) discussed significant matters with the engagement quality control reviewer; and (c) ensured that the report is not issued until the completion of the engagement quality control review?"),
        ("q_13", "Has the engagement quality control reviewer performed an objective evaluation of the significant judgments made by the engagement team, and the conclusions reached in formulating the auditor's report, including discussion of significant matters, review of financial statements, review of selected audit documentation, and evaluation of conclusions?"),
        ("q_14", "Where differences of opinion arise within the engagement team, with those consulted or between the engagement partner and the engagement quality control reviewer, has the engagement team followed the firm's policies and procedures for dealing with and resolving differences of opinion?"),
    ]),
    ("sa_230", "SA 230 — Audit Documentation", [
        ("q_1",  "Has the audit documentation been prepared on a timely basis?"),
        ("q_2",  "Is the audit documentation sufficient to enable an experienced auditor, having no previous connection with the audit, to understand (a) the nature, timing, and extent of the audit procedures performed; (b) the results of the audit procedures performed and the audit evidence obtained; and (c) significant matters arising during the audit, the conclusions reached, and significant professional judgments made?"),
        ("q_3",  "While documenting the nature, timing and extent of audit procedures performed, whether the following were recorded: (a) the identifying characteristics of the specific items or matters tested; (b) who performed the audit work and the date such work was completed; and (c) who reviewed the audit work performed and the date and extent of such review?"),
        ("q_4",  "Does the document include discussions of significant matters with management, those charged with governance, and others, including the nature of the significant matters discussed and when and with whom the discussions took place?"),
        ("q_5",  "Where it is identified that information is inconsistent with the auditor's final conclusion regarding a significant matter, is it documented as to how the inconsistency was addressed?"),
        ("q_6",  "Where it is considered necessary in exceptional circumstances to depart from a relevant requirement in a SA, does the audit document reflect how the alternative audit procedures performed achieved the aim of that requirement and the reasons for the departure?"),
        ("q_7",  "Where in exceptional circumstances new or additional audit procedures are performed or new conclusions are reached after the date of the audit report, whether the following were documented: (a) the circumstances encountered; (b) the new or additional audit procedures performed, audit evidence obtained, conclusions reached and their effect on the auditor's report; and (c) when and by whom the resulting changes to audit documentation were made and reviewed?"),
        ("q_8",  "Is it ensured that after the assembly of the final audit file has been completed, no deletion or discard of audit documentation of any nature has taken place before the end of its retention period?"),
        ("q_9",  "Where it is necessary to modify existing audit documentation or add new audit documentation after the assembly of the final audit file has been completed, whether the following were documented: (a) the specific reasons for making them; and (b) when and by whom they were made and reviewed?"),
    ]),
    ("sa_240", "SA 240 — Fraud Consideration", [
        ("q_1",  "Whether a review of documents in the course of audit indicate any record / document may not be authentic or that terms in a document have been modified but not disclosed to the auditor? If yes, elaborate the details and steps taken in the Comments."),
        ("q_2",  "Whether the responses received from the management or those charged with governance for the various inquiries and questionnaire during the course of audit were found to be inconsistent? If yes, elaborate the details in the Comments."),
        ("q_3",  "Whether a discussion took place between the engagement partner and his team with particular emphasis on how and where the entity's financial statements may be susceptible to material misstatement due to fraud, including how fraud might occur?"),
        ("q_4",  "Whether the procedure followed by the management to assess the risk of financial statement being materially misstated due to fraud is adequate and reasonable? If not, elaborate the details in the Comments."),
        ("q_5",  "Whether the Management's processes and procedures for identifying and responding to the risks of fraud in the entity, including any specific risks of fraud that management has identified or that have been brought to its attention, is adequate considering the nature and size of its business?"),
        ("q_6",  "Whether an inquiry was made with management, and others within the entity as appropriate (including internal auditors) to determine whether they have knowledge of any actual, suspected or alleged fraud or the risk of fraud, affecting the entity?"),
        ("q_7",  "Whether, during the course of audit, any risk of material misstatement due to fraud at the financial statement level, and at the assertion level for classes of transactions, account balances and disclosures, was identified? If yes, elaborate the details and steps taken to address the same in the Comments."),
        ("q_8",  "Where the answer to the previous question is YES, whether the further audit procedures whose nature, timing and extent are responsive to the assessed risks of material misstatement due to fraud at the assertion level, are designed and performed?"),
        ("q_9",  "Whether the inquiry with individuals involved in the financial accounting and reporting process revealed any inappropriate or unusual activity relating to the processing of journal entries and other adjustments? If yes, elaborate the details in the Comments."),
        ("q_10", "Whether a review of Journal Entries revealed any inconsistencies or inappropriateness in the financial reporting? If yes, elaborate the details in the Comments."),
        ("q_11", "Whether the accounting estimates are reviewed for biases and evaluated for the circumstances producing the bias, if any, and does this represent a risk of material misstatement due to fraud?"),
        ("q_12", "Is the evaluation of the judgments and decisions made by management in making the accounting estimates included in the financial statements, even if they are individually reasonable, considered for possible bias that may represent a risk of material misstatement due to fraud? If yes, elaborate in the Comments."),
        ("q_13", "Whether a retrospective review of management judgments and assumptions related to significant accounting estimates reflected in the financial statements of the prior year was performed to validate the reasonableness?"),
        ("q_14", "Where significant transactions that are outside the normal course of business for the entity appear to be unusual, whether the business rationale (or the lack thereof) of the transactions was evaluated for possibility of fraudulent financial reporting or to conceal misappropriation of assets?"),
        ("q_15", "Where a misstatement, material or not, is believed to be the result of fraud and that senior management is involved, whether a re-evaluation was done of the assessment of the risks of material misstatement due to fraud and its resulting impact on the nature, timing and extent of audit procedures?"),
        ("q_16", "Where it is not possible to conclude whether the financial statements are materially misstated as a result of fraud, were its implications for the audit opinion evaluated?"),
    ]),
    ("sa_250", "SA 250 — Laws & Regulations", [
        ("q_1",  "Whether an understanding of the entity and its environment in accordance with SA 315 includes: (a) The legal and regulatory framework applicable to the entity and the industry or sector in which the entity operates; and (b) How the entity is complying with that framework?"),
        ("q_2",  "Were sufficient appropriate audit evidences obtained regarding compliance with the provisions of those laws and regulations generally recognized to have a direct effect on the determination of material amounts and disclosures in the financial statements?"),
        ("q_3",  "Were the following audit procedures performed? (a) Inquiries of management and, where appropriate, those charged with governance, as to whether the entity is in compliance with such laws and regulations; and (b) Inspection of correspondence, if any, with the relevant licensing or regulatory authorities."),
        ("q_4",  "Has the engagement team remained alert to the possibility that other audit procedures applied may bring instances of non-compliance or suspected non-compliance with laws and regulations?"),
        ("q_5",  "Whether the management and, where appropriate, those charged with governance, were requested to provide written representations that all known instances of non-compliance or suspected non-compliance with laws and regulations whose effects should be considered when preparing financial statements have been disclosed to the auditor?"),
        ("q_6",  "Where the non-compliance is believed to be intentional and material, has it been communicated to those charged with governance as soon as practicable?"),
        ("q_7",  "Where the management or those charged with governance precludes the audit team from obtaining sufficient appropriate audit evidence to evaluate whether non-compliance that may be material to the financial statements has, or is likely to have, occurred — is there a qualified opinion or disclaimer of opinion on the financial statements on the basis of a limitation on the scope of the audit in accordance with SA 705, expressed?"),
    ]),
    ("sa_500", "SA 500 — Audit Evidence", [
        ("q_1",  "While determining the reliability of audit evidence were the following facts considered? (a) Audit evidence is influenced by its source and by its nature; (b) Audit evidence is dependent on the individual circumstances under which it is generated and obtained."),
        ("q_2",  "Are the designed and performed audit procedures appropriate in the circumstances for the purpose of obtaining sufficient appropriate audit evidence?"),
        ("q_3",  "Where information to be used as audit evidence has been prepared using the work of a management's expert, have the following been done: (a) Evaluate the competence, capabilities and objectivity of that expert; (b) Obtain an understanding of the work of that expert; and (c) Evaluate the appropriateness of that expert's work as audit evidence for the relevant assertion?"),
        ("q_4",  "Where the information produced by the entity is used does it provide: (a) Audit evidence about the accuracy and completeness of the information; and (b) The information is sufficiently precise and detailed?"),
        ("q_5",  "Where the evidence obtained from one source is inconsistent with the information obtained from another source, were additional procedures performed to resolve the inconsistency?"),
        ("q_6",  "Where the inventory is material to the financial statements, has sufficient appropriate audit evidence been obtained regarding the existence and condition of inventory by: (i) Evaluating management's instructions and procedures for recording and controlling the results of the entity's physical inventory counting; (ii) Observing the performance of management's count procedures; (iii) Inspecting the inventory; and (iv) Performing test counts?"),
        ("q_7",  "Where the physical inventory counting is conducted at a date other than the date of the financial statements, were audit procedures performed to obtain evidence about the changes in inventory between the count date and the date of the financial statements? Have they been properly recorded?"),
        ("q_8",  "Where the attendance at physical inventory counting is impracticable, have alternative audit procedures been performed to obtain sufficient appropriate audit evidence regarding the existence and condition of inventory? If that is also not possible, was a modified opinion issued in accordance with SA 705?"),
        ("q_9",  "When inventory under the custody and control of a third party is material to the financial statements, has sufficient appropriate audit evidence been obtained regarding the existence and condition of that inventory by performing one or both of the following: (a) Request confirmation from the third party as to the quantities and condition of inventory held on behalf of the entity; (b) Perform inspection or other audit procedures appropriate in the circumstances?"),
        ("q_10", "Whether the audit procedures performed to identify litigation and claims involving the entity which may give rise to a risk of material misstatement included the following: (a) Inquiry of the management and, where applicable, others within the entity, including in-house legal counsel; (b) Review of minutes of meetings of those charged with governance and correspondence between the entity and its external legal counsel; and (c) Review of legal expense accounts?"),
        ("q_11", "Where a risk of material misstatement is assessed regarding litigation or claims that have been identified, or when audit procedures performed indicate that other material litigation or claims may exist, was a direct communication with the entity's external legal counsel sought?"),
        ("q_12", "Where (a) management refuses to give permission to communicate or meet with the entity's external legal counsel, or the entity's external legal counsel refuses to respond appropriately to the letter of inquiry, or is prohibited from responding; and (b) it is not possible to obtain sufficient appropriate audit evidence by performing alternative audit procedures — has a modified opinion been issued in accordance with SA 705?"),
        ("q_13", "Does the written representation include a statement from the management and, where appropriate, those charged with governance that all known actual or possible litigation and claims whose effects should be considered when preparing the financial statements have been disclosed to the auditor and appropriately accounted for and disclosed in accordance with the applicable financial reporting framework?"),
        ("q_14", "Was sufficient appropriate audit evidence obtained regarding the presentation and disclosure of segment information in accordance with the applicable financial reporting framework by: (a) Obtaining an understanding of the methods used by management in determining segment information and evaluating whether such methods are likely to result in disclosure in accordance with the applicable financial reporting framework; and (b) Performing analytical procedures or other audit procedures appropriate in the circumstances?"),
    ]),
    ("sa_520", "SA 520 — Analytical Procedures", [
        ("q_1",  "Whether the technique of analytical review was planned to be used either alone or in combination with tests of details, as part of the substantive procedures in accordance with SA 330?"),
        ("q_2",  "Whether the suitability of particular substantive analytical procedures is determined, for the given assertions, taking into account the assessed risks of material misstatement and tests of details, if any, for these assertions?"),
        ("q_3",  "Were necessary audit procedures performed to understand the following: (a) Reliability of data; (b) Relevance of the information; (c) Source of information; (d) Comparability of the information; (e) Control over preparation?"),
        ("q_4",  "Was an expectation of recorded amounts or ratios developed?"),
        ("q_5",  "Is the expectation sufficiently precise to identify a misstatement that, individually or when aggregated with other misstatements, may cause the financial statements to be materially misstated?"),
        ("q_6",  "Were the analytical procedures performed near the end of the audit, to assist in forming an overall conclusion about the consistency of the financial statements with the auditor's understanding of the entity?"),
        ("q_7",  "Where the analytical procedures performed in accordance with this SA identify fluctuations or relationships that are inconsistent with other relevant information or that differ from expected values by a significant amount, was it investigated by: (a) Inquiring of management and obtaining appropriate audit evidence relevant to management's responses; and (b) Performing other audit procedures as necessary in the circumstances?"),
    ]),
    ("sa_540", "SA 540 — Accounting Estimates", [
        ("q_1",  "Has an understanding of the following been obtained in order to provide a basis for the identification and assessment of the risks of material misstatement for accounting estimates: (a) The requirements of the applicable financial reporting framework relevant to accounting estimates, including related disclosures; (b) How management identifies those transactions, events and conditions that may give rise to the need for accounting estimates to be recognized or disclosed in the financial statements; (c) Whether the management inquired about changes in circumstances that may give rise to new, or the need to revise existing, accounting estimates?"),
        ("q_2",  "Does a review of the process of making the accounting estimates by the management reveal that the management has assessed and appropriately handled the effect of estimation uncertainty?"),
        ("q_3",  "Whether a review of the outcome of accounting estimates included in the prior period financial statements or, where applicable, their subsequent re-estimation for the purpose of the current period was duly carried out?"),
        ("q_4",  "Did such a review take into account the nature of the accounting estimates?"),
        ("q_5",  "List down the items for which accounting estimates were generally adopted by the entity wherever applicable in the comments tab."),
        ("q_6",  "Call for and review the workings for making of the above estimates by the management."),
        ("q_7",  "Based on the review of workings and evidences used by the management for making the accounting estimates, was any potential risk of material misstatement of accounting estimates made in the current period financial statements noticed?"),
        ("q_8",  "While assessing the risk of material misstatements, was the degree of estimation uncertainty associated with an accounting estimate taken into consideration?"),
        ("q_9",  "Has management appropriately applied the requirements of the applicable financial reporting framework relevant to the accounting estimates?"),
        ("q_10", "Are the methods for making the accounting estimates appropriate and have been applied consistently, and are changes, if any, in accounting estimates or in the method for making such estimates from the prior period appropriate in the circumstances?"),
        ("q_11", "Are special skills or knowledge in relation to one or more aspects of the accounting estimates required in order to obtain sufficient appropriate audit evidence?"),
        ("q_12", "Whether sufficient appropriate audit evidence obtained about the disclosures in the financial statements related to accounting estimates are in accordance with the requirements of the applicable financial reporting framework?"),
        ("q_13", "Do the judgments and decisions made by the management in making the accounting estimates reveal any possibility for management bias?"),
        ("q_14", "Whether written representations obtained from management as to significant assumptions used by it in making accounting estimates are reasonable?"),
    ]),
    ("sa_550", "SA 550 — Related Parties", [
        ("q_1",  "Did the audit engagement team discussion include a specific consideration of the susceptibility of the financial statements to material misstatement due to fraud or error that could result from the entity's related party relationships and transactions?"),
        ("q_2",  "Were the following inquired of the management? (a) The identity of the entity's related parties, including changes from the prior period; (b) The nature of the relationships between the entity and these related parties; (c) Whether the entity entered into any transactions with these related parties during the period and, if so, the type and purpose of the transactions."),
        ("q_3",  "Were risk assessment procedures considered appropriate performed, to obtain an understanding of the controls, if any, that management has established to: (a) Identify, account for, and disclose related party relationships and transactions in accordance with the applicable financial reporting framework; (b) Authorize and approve significant transactions and arrangements with related parties; (c) Authorize and approve significant transactions and arrangements outside the normal course of business?"),
        ("q_4",  "Is the audit team alert to the fact that when inspecting records or documents, for arrangements or other information that may indicate the existence of related party relationships or transactions that management has not previously identified or disclosed to the auditor?"),
        ("q_5",  "Where a related party or significant related party transactions that management has not previously identified or disclosed: (a) Is it promptly communicated to the other members of the engagement team; (b) Is the management requested to identify all transactions with the newly identified related parties for further evaluation; (c) Is it inquired to find out why the entity's controls over related party relationships and transactions failed to enable the identification or disclosure; (d) Were appropriate substantive audit procedures performed relating to such newly identified related parties or significant related party transactions; (e) Whether the risk of other related parties or significant related party transactions may exist that management has not previously identified or disclosed is reconsidered; and (f) Where it is determined that the non-disclosure by management appears intentional (and therefore indicative of a risk of material misstatement due to fraud), were the implications for the audit evaluated?"),
        ("q_6",  "Where significant transactions outside the entity's normal course of business was identified when performing the audit procedures, was the management inquired about: (a) The nature of these transactions; and (b) Whether related parties could be involved?"),
        ("q_7",  "Were the significant related party transactions outside the entity's normal course of business identified? If so, how was the risk of material misstatement assessed?"),
        ("q_8",  "For identified significant related party transactions outside the entity's normal course of business, were the following done? (a) Inspect the underlying contracts or agreements, if any, and evaluate to ascertain: (i) The business rationale (or lack thereof) of the transactions suggests that they may have been entered into to engage in fraudulent financial reporting or to conceal misappropriation of assets; (ii) The terms of the transactions are consistent with management's explanations; and (iii) The transactions have been appropriately accounted for and disclosed in accordance with the applicable financial reporting framework; and (b) Obtain audit evidence that the transactions have been appropriately authorized and approved."),
        ("q_9",  "When the management has made an assertion in the financial statements to the effect that a related party transaction was conducted on terms equivalent to those prevailing in an arm's length transaction, whether sufficient appropriate audit evidence about the assertion was obtained?"),
        ("q_10", "While forming an opinion on the financial statements were the following evaluated? (a) The identified related party relationships and transactions have been appropriately accounted for and disclosed in accordance with the applicable financial reporting framework; and (b) The effects of the related party relationships and transactions which prevent the financial statements from achieving true and fair presentation (for fair presentation frameworks); or cause the financial statements to be misleading (for compliance frameworks)?"),
        ("q_11", "Whether written representations from management and where appropriate, those charged with governance were obtained including the following: (a) They have disclosed to the auditor the identity of the entity's related parties and all the related party relationships and transactions of which they are aware; and (b) They have appropriately accounted for and disclosed such relationships and transactions in accordance with the requirements of the framework?"),
        ("q_12", "Whether the names of the identified related parties and the nature of the related party relationships were documented?"),
    ]),
    ("sa_560", "SA 560 — Subsequent Events", [
        ("q_1",  "Review the procedures established by the management to ensure that subsequent events are identified."),
        ("q_2",  "Inquire with the management and, where appropriate, those charged with governance as to whether any subsequent events have occurred which might affect the financial statements."),
        ("q_3",  "Review the minutes of the meetings of the entity's owners, management and those charged with governance, that are held after the date of the financial statements and inquiring about matters discussed at any such meetings for which minutes are not yet available; verify whether any relevant subsequent event requires consideration."),
        ("q_4",  "Review the entity's latest subsequent interim financial statements, if any, to check any reference to a relevant subsequent event."),
        ("q_5",  "Have there been, as a result of the procedures performed above, any subsequent events identified that require adjustment of, or disclosure in, the financial statements?"),
        ("q_6",  "If yes, is each such event appropriately reflected in those financial statements?"),
        ("q_7",  "Has written representation been obtained from those charged with governance that all subsequent events have been disclosed adequately?"),
        ("q_8",  "Has any significant fact become known to the Auditor after the date of the Auditor's Report but before the date the Financial Statements are issued?"),
        ("q_9",  "If yes, were the following done: (a) Discuss the matter with management and, where appropriate, those charged with governance; (b) Determine whether the financial statements need amendment; and (c) Inquire how management intends to address the matter in the financial statements."),
        ("q_10", "Where the management amends the financial statements, were the audit procedures necessary in the circumstances on the amendment carried out?"),
        ("q_11", "When a new auditor's report on the amended financial statements is issued, has it been ensured that it is not dated earlier than the date of approval of the amended financial statements?"),
        ("q_12", "Has any significant fact become known to the auditor after the Financial Statements have been issued?"),
        ("q_13", "If yes, had it been known at the date of the audit report, would it have caused the amendment to the audit report?"),
        ("q_14", "If yes, were the following audit procedures done? (a) Discuss the matter with management and, where appropriate, those charged with governance; (b) Determine whether the financial statements need amendment; and (c) Inquire how management intends to address the matter in the financial statements."),
        ("q_15", "Where the management amends the financial statements were the following done? (a) Carry out the necessary audit procedures; (b) Review the steps taken by management to ensure that anyone in receipt of the previously issued financial statements together with the auditor's report thereon is informed of the situation; (c) Amend the auditor's report, or provide a new auditor's report as required."),
        ("q_16", "If management does not take the necessary steps to ensure that anyone in receipt of the previously issued financial statements is informed of the situation and does not amend the financial statements in circumstances where in the auditor's belief they need to be amended, was the management/all of those charged with governance involved in managing the entity notified?"),
        ("q_17", "If, despite such notification, management or those charged with governance do not take these necessary steps, was appropriate action taken to seek to prevent reliance on the auditor's report?"),
    ]),
    ("sa_580", "SA 580 — Written Representations", [
        ("q_1",  "Has the auditor requested detailed written representations from management with appropriate responsibilities for the financial statements and knowledge of the matters concerned?"),
        ("q_2",  "Has the Auditor requested the management to provide a written representation that it has fulfilled its responsibility for the preparation of the financial statements in accordance with the applicable financial reporting framework including, where relevant, their fair presentation, as set out in the terms of the audit engagement?"),
        ("q_3",  "Has the auditor requested management to provide a written representation that it has provided the auditor with all relevant information and access as agreed in the terms of the audit engagement?"),
        ("q_4",  "Has the auditor requested management to provide a written representation that all transactions have been duly recorded and are correctly reflected in the financial statements?"),
        ("q_5",  "Has management's responsibilities been described in the written representations required by this SA in the manner in which these responsibilities are described in the terms of the audit engagement?"),
        ("q_6",  "Has the auditor requested management to provide a written representation covering areas as mandated by other Standards on Auditing including SA 230, 240, 260, 501, 540, 550 and 570?"),
        ("q_7",  "Is the date of the written representation as near as practicable to, but in any case not later than, the date of the auditor's report on the financial statements?"),
        ("q_8",  "Does the written representations cover all financial statements and period(s) referred to in the auditor's report?"),
        ("q_9",  "Is the written representations in the form of a representation letter addressed to the auditor?"),
        ("q_10", "Does the auditor have concerns about the competence, integrity, ethical values or diligence of management, or about its commitment to or enforcement of these representations?"),
        ("q_11", "If yes, whether the auditor determined the effect of such concerns on the reliability of representations (oral or written) as well as the audit evidence in general?"),
        ("q_12", "Was it found that any of the written representations are inconsistent with other audit evidences gathered?"),
        ("q_13", "If yes, whether the auditor performed necessary further audit procedures to resolve these inconsistencies?"),
        ("q_14", "If any of the issues of inconsistency remain unresolved, has the auditor reconsidered the assessment of the competence, integrity, ethical values or diligence of management, and determined the effect that this may have on the reliability of representations (oral or written) and audit evidence in general?"),
        ("q_15", "If the auditor concludes that the written representations are not reliable, has the auditor taken appropriate actions, including determining the possible effect on the opinion in the auditor's report in accordance with SA 705, having regard to the requirement in paragraph 19 of this SA?"),
        ("q_16", "In case where the management does not provide one or more of the requested written representations, whether the auditor has: (a) Discussed the matter with management; (b) Re-evaluated the integrity of management and evaluated the effect that this may have on the reliability of representations (oral or written) and audit evidence in general; and (c) Taken appropriate actions, including determining the possible effect on the opinion in the auditor's report in accordance with SA 705?"),
        ("q_17", "Has the auditor issued an adverse or disclaimer opinion on the financial statements in accordance with SA 705 if: (a) The auditor concludes that there is sufficient doubt about the integrity of management such that the written representations required are not reliable; or (b) Management does not provide the written representations required?"),
    ]),
    ("sa_720", "SA 720 — Other Information", [
        ("q_1",  "Discuss with management in order to determine which document(s) comprises the Annual Report and the entity's planned manner and timing of issuance of such document(s) and the time at which the final version of such documents would be obtained."),
        ("q_2",  "Read the documents comprising the Annual Report to consider the following: (a) Material inconsistency between other information and financial statements; (b) Material inconsistency between other information and auditor's knowledge obtained in the audit."),
        ("q_3",  "Are there any indications that other information not related to financial statements or auditor's knowledge obtained in the audit appears to be materially misstated?"),
        ("q_4",  "In case of any material misstatement found in other information, was the management requested to correct other information?"),
        ("q_5",  "If in the above case, the management agrees for correction, was it determined that the correction was made?"),
        ("q_6",  "If in the above case, management refuses correction, was the matter communicated with those charged with governance and a request made to them for correction?"),
        ("q_7",  "When material inconsistencies are identified in other information obtained prior to the date of Auditor's report and the revision of audited financial statements is necessary and management refuses to make a revision, has the opinion been modified as per SA 705?"),
        ("q_8",  "When material inconsistencies are identified in other information obtained prior to the date of Auditor's report and the revision of other information is necessary and the management refuses to do so, has the same been communicated to those charged with governance and included in the Auditor's report as other matter paragraph describing material inconsistency in accordance with SA 706?"),
        ("q_9",  "When material inconsistencies are identified in other information obtained subsequent to the date of Auditor's report and the revision of audited financial statements is necessary, were the relevant requirements in SA 560 followed?"),
        ("q_10", "When material inconsistencies are identified in other information obtained subsequent to the date of Auditor's report and the revision of other information is necessary and the management refuses to do so, has the Auditor's concern been communicated to those charged with governance and any further appropriate action been taken?"),
        ("q_11", "If on reading the other information for the purpose of identifying material inconsistencies, it is concluded that there is a material misstatement of fact in the other information which management refuses to correct, has the Auditor's concern been communicated to those charged with governance and any further appropriate action been taken?"),
    ]),
]

IFC_RESPONSES = ["Yes", "No", "Partial"]

# ── Legal & Secretarial Requirements (Statutory Audit) ───────────────────────
LEGAL_SEC_ITEMS = [
    # ── Company Law Compliance ──────────────────────────────────────────────
    ("ls_group_company_law", "Company Law Compliance", "header"),

    ("ls_mca_filing_aoc4",   "AOC-4 (Financial Statements Filing)",     "item"),
    ("ls_mca_filing_mgt7",   "MGT-7 / MGT-7A (Annual Return)",          "item"),
    ("ls_mca_filing_adt1",   "ADT-1 (Auditor Appointment Filing)",       "item"),
    ("ls_mca_filing_dir12",  "DIR-12 (Director Changes, if any)",        "item"),
    ("ls_mca_filing_inc22a", "INC-22A / Active Status Compliance",       "item"),
    ("ls_mca_filing_dpt3",   "DPT-3 (Return of Deposits / Loans)",       "item"),
    ("ls_mca_filing_msme1",  "MSME-1 (Outstanding Payments to MSME)",    "item"),
    ("ls_mca_filing_llpin",  "LLP Annual Filing (if applicable)",        "item"),

    # ── Board & General Meetings ────────────────────────────────────────────
    ("ls_group_meetings", "Board & General Meetings", "header"),

    ("ls_board_meetings",    "Board Meetings held as required",           "item"),
    ("ls_agm_held",          "AGM held within due date",                  "item"),
    ("ls_agm_notice",        "AGM Notice & Agenda issued",                "item"),
    ("ls_egm_held",          "EGM held (if applicable)",                  "item"),
    ("ls_minutes_board",     "Minutes of Board Meetings maintained",      "item"),
    ("ls_minutes_agm",       "Minutes of General Meetings maintained",    "item"),
    ("ls_committee_minutes", "Committee Meeting Minutes (Audit / NRC / CSR)", "item"),

    # ── Directors & KMP ─────────────────────────────────────────────────────
    ("ls_group_directors", "Directors & Key Managerial Personnel", "header"),

    ("ls_din_kyc",           "Director DIN & KYC updated",                "item"),
    ("ls_dir8_disclosure",   "DIR-8 Disqualification Declaration",        "item"),
    ("ls_mbp1_disclosure",   "MBP-1 Interest Disclosure by Directors",    "item"),
    ("ls_kmp_appointment",   "KMP Appointment / Cessation filings",       "item"),
    ("ls_remuneration",      "Managerial Remuneration within limits",     "item"),
    ("ls_related_party",     "Related Party Transactions — Board approval", "item"),

    # ── Share Capital & Registers ───────────────────────────────────────────
    ("ls_group_registers", "Share Capital & Statutory Registers", "header"),

    ("ls_share_reg",         "Register of Members (MGT-1) maintained",   "item"),
    ("ls_share_transfer",    "Share Transfer procedures complied",        "item"),
    ("ls_demat_compliance",  "Dematerialisation compliance (if applicable)", "item"),
    ("ls_reg_charges",       "Register of Charges maintained & filed",    "item"),
    ("ls_reg_contracts",     "Register of Contracts / Related Parties",   "item"),
    ("ls_reg_directors",     "Register of Directors & KMP",               "item"),
    ("ls_reg_investments",   "Register of Investments / Loans",           "item"),

    # ── Secretarial & Governance ────────────────────────────────────────────
    ("ls_group_secretarial", "Secretarial & Governance", "header"),

    ("ls_sec_audit",         "Secretarial Audit (Form MR-3) — if applicable", "item"),
    ("ls_sec_standards",     "Secretarial Standards SS-1 & SS-2 followed", "item"),
    ("ls_csr_compliance",    "CSR Compliance (if Sec 135 applicable)",    "item"),
    ("ls_csr_report",        "CSR Report included in Board's Report",     "item"),
    ("ls_vigil_mechanism",   "Vigil Mechanism / Whistle-blower Policy",   "item"),
    ("ls_risk_mgmt",         "Risk Management Policy in place",           "item"),
    ("ls_ppe_policy",        "POSH Policy & ICC Committee (if applicable)", "item"),
    ("ls_board_report",      "Board's Report as per Sec 134 complied",    "item"),
    ("ls_auditor_report_dir","Directors' Response to Audit Observations", "item"),

    # ── SEBI & Listing (if listed) ──────────────────────────────────────────
    ("ls_group_sebi", "SEBI / Listing Obligations (if applicable)", "header"),

    ("ls_lodr_compliance",   "LODR Regulations compliance",               "item"),
    ("ls_corp_governance",   "Corporate Governance Report",               "item"),
    ("ls_quarterly_results", "Quarterly Results filing to exchanges",     "item"),
    ("ls_insider_trading",   "Insider Trading Code compliance",           "item"),
    ("ls_sast_compliance",   "SAST Regulations compliance",               "item"),

    # ── Other Filings ────────────────────────────────────────────────────────
    ("ls_group_other",       "Other Filings",                             "header"),
    ("ls_other_filings",     "Other Filings",                             "item"),
]

LS_STATUSES = ["Not Checked", "Compliant", "Non-Compliant", "N/A"]

# ── Form 3CD Clauses (Tax Audit) ──────────────────────────────────────────────
TAX_AUDIT_CLAUSES = [
    ("1",   "Name of the Assessee"),
    ("2",   "Address"),
    ("3",   "Permanent Account Number (PAN)"),
    ("4",   "Status"),
    ("5",   "Previous Year Ended"),
    ("6",   "Assessment Year"),
    ("7",   "Nature of Business / Profession"),
    ("8",   "Relevant clause of Section 44AB"),
    ("9",   "Whether books are prescribed u/s 44AA"),
    ("10",  "Nature of books of account maintained"),
    ("11",  "Whether books examined at head office or branches"),
    ("12",  "Details of partners / members / directors"),
    ("13",  "Method of Accounting"),
    ("14",  "Method of Accounting for Closing Stock"),
    ("15",  "Capital assets converted to stock-in-trade"),
    ("16",  "Amounts not credited to Profit & Loss Account"),
    ("17",  "Payments to Specified Persons u/s 40A(2)(b)"),
    ("18",  "Amounts deductible in any subsequent year"),
    ("19",  "Amounts not deductible u/s 40"),
    ("20",  "Amounts not deductible u/s 40A"),
    ("21",  "Deductions u/s 33AB / 33ABA / 35D / 35DD / 35E"),
    ("22",  "Amount of deduction u/s 35"),
    ("23",  "Amount deductible u/s 43B"),
    ("24",  "CENVAT Credit"),
    ("25",  "Shares of company in which public not substantially interested"),
    ("26",  "Details of amounts received / paid in cash — section 269SS / 269T"),
    ("27",  "Receipt of deemed dividend u/s 2(22)(e)"),
    ("28",  "Deemed profits chargeable u/s 41"),
    ("29",  "Deductions inadmissible u/s 30 to 37"),
    ("30",  "Particulars of TDS / TCS"),
    ("30A", "Transfer Pricing — Domestic Transactions u/s 92BA"),
    ("30B", "Secondary Adjustment u/s 92CE"),
    ("30C", "Limitation on Interest Deduction u/s 94B"),
    ("31",  "Payments / receipts in cash exceeding Rs. 2 lakh"),
    ("32",  "Brought forward losses / depreciation"),
    ("33",  "Chapter VI-A Deductions claimed"),
    ("34",  "TDS / TCS Compliance — defaults & interest"),
    ("35",  "Quantitative details of principal items"),
    ("36",  "Audit / accounting qualification under other laws"),
    ("36A", "Dividend declared / paid during the year"),
    ("37",  "Accounting Ratios"),
    ("38",  "Demands raised / Refunds issued during the year"),
    ("39",  "Details of deemed income u/s 59"),
    ("40",  "Details of CARO / auditors report"),
    ("41",  "Details of indirect tax refund / credit"),
    ("42",  "MSME dues — Section 43B(h)"),
    ("43",  "Country-by-Country Report (CbCR) — Section 286"),
    ("44",  "Break-up of expenditure — GST registered vs unregistered"),
]

# ── Notes to Accounts under AS (Statutory Audit) ──────────────────────────────
AS_NOTES = [
    ("1",  "Corporate Information"),
    ("2",  "Significant Accounting Policies"),
    ("3",  "Share Capital"),
    ("4",  "Reserves and Surplus"),
    ("5",  "Long-term Borrowings"),
    ("6",  "Deferred Tax Liabilities (Net)"),
    ("7",  "Other Long-term Liabilities"),
    ("8",  "Long-term Provisions"),
    ("9",  "Short-term Borrowings"),
    ("10", "Trade Payables"),
    ("11", "Other Current Liabilities"),
    ("12", "Short-term Provisions"),
    ("13", "Property, Plant & Equipment (Fixed Assets)"),
    ("14", "Non-current Investments"),
    ("15", "Deferred Tax Assets (Net)"),
    ("16", "Long-term Loans and Advances"),
    ("17", "Other Non-current Assets"),
    ("18", "Current Investments"),
    ("19", "Inventories"),
    ("20", "Trade Receivables"),
    ("21", "Cash and Bank Balances"),
    ("22", "Short-term Loans and Advances"),
    ("23", "Other Current Assets"),
    ("24", "Revenue from Operations"),
    ("25", "Other Income"),
    ("26", "Cost of Materials Consumed"),
    ("27", "Changes in Inventories of Finished Goods & WIP"),
    ("28", "Employee Benefits Expense"),
    ("29", "Finance Costs"),
    ("30", "Depreciation and Amortization Expense"),
    ("31", "Other Expenses"),
    ("32", "Earnings Per Share — AS 20"),
    ("33", "Related Party Disclosures — AS 18"),
    ("34", "Contingent Liabilities and Commitments"),
    ("35", "Segment Reporting — AS 17"),
    ("36", "Leases — AS 19"),
    ("37", "Employee Benefits (Gratuity / PF) — AS 15"),
    ("38", "Foreign Currency Transactions — AS 11"),
    ("39", "Borrowing Costs — AS 16"),
    ("40", "Taxes on Income — AS 22"),
]

# ── Notes to Accounts under Ind AS (Statutory Audit) ─────────────────────────
IND_AS_NOTES = [
    ("1",  "Corporate Information"),
    ("2",  "Basis of Preparation"),
    ("3",  "Significant Accounting Policies"),
    ("4",  "Critical Accounting Estimates and Judgements"),
    ("5",  "Property, Plant and Equipment — Ind AS 16"),
    ("6",  "Right-of-Use Assets — Ind AS 116"),
    ("7",  "Capital Work-in-Progress"),
    ("8",  "Goodwill and Other Intangible Assets — Ind AS 38"),
    ("9",  "Non-current Investments — Ind AS 109"),
    ("10", "Non-current Loans"),
    ("11", "Other Non-current Financial Assets"),
    ("12", "Deferred Tax Assets (Net) — Ind AS 12"),
    ("13", "Non-current Tax Assets"),
    ("14", "Other Non-current Assets"),
    ("15", "Inventories — Ind AS 2"),
    ("16", "Current Investments"),
    ("17", "Trade Receivables"),
    ("18", "Cash and Cash Equivalents — Ind AS 7"),
    ("19", "Bank Balances other than Cash & Cash Equivalents"),
    ("20", "Current Loans"),
    ("21", "Other Current Financial Assets"),
    ("22", "Current Tax Assets"),
    ("23", "Other Current Assets"),
    ("24", "Equity Share Capital"),
    ("25", "Other Equity"),
    ("26", "Non-current Borrowings"),
    ("27", "Lease Liabilities (Non-current) — Ind AS 116"),
    ("28", "Other Non-current Financial Liabilities"),
    ("29", "Non-current Provisions — Ind AS 37"),
    ("30", "Deferred Tax Liabilities (Net) — Ind AS 12"),
    ("31", "Other Non-current Liabilities"),
    ("32", "Current Borrowings"),
    ("33", "Trade Payables"),
    ("34", "Other Current Financial Liabilities"),
    ("35", "Lease Liabilities (Current) — Ind AS 116"),
    ("36", "Current Provisions"),
    ("37", "Current Tax Liabilities"),
    ("38", "Other Current Liabilities"),
    ("39", "Revenue from Operations — Ind AS 115"),
    ("40", "Other Income"),
    ("41", "Cost of Materials Consumed / Purchases of Stock-in-Trade"),
    ("42", "Changes in Inventories of Finished Goods & WIP"),
    ("43", "Employee Benefits Expense — Ind AS 19"),
    ("44", "Finance Costs"),
    ("45", "Depreciation and Amortization Expense"),
    ("46", "Other Expenses"),
    ("47", "Tax Expense — Ind AS 12"),
    ("48", "Earnings Per Share — Ind AS 33"),
    ("49", "Related Party Disclosures — Ind AS 24"),
    ("50", "Financial Instruments: Disclosures — Ind AS 107"),
    ("51", "Fair Value Measurements — Ind AS 113"),
    ("52", "Leases — Ind AS 116"),
    ("53", "Employee Benefits — Ind AS 19"),
    ("54", "Share-based Payments — Ind AS 102"),
    ("55", "Segment Reporting — Ind AS 108"),
    ("56", "Contingencies and Commitments — Ind AS 37"),
    ("57", "Events After the Reporting Period — Ind AS 10"),
]

# ── Color Palette ──────────────────────────────────────────────────────────────
C = {
    "bg":            "#0F1923",
    "panel":         "#162030",
    "sidebar":       "#111C28",
    "accent":        "#1DB8A8",
    "accent2":       "#F4A633",
    "text":          "#E8EDF2",
    "muted":         "#6B7E94",
    "border":        "#243447",
    "danger":        "#E05C5C",
    "success":       "#2ECC71",
    "btn_primary":   "#1DB8A8",
    "btn_hover":     "#17A396",
    "btn_secondary": "#243447",
    "input_bg":      "#1E2D3D",
    "input_border":  "#304560",
    "highlight":     "#1A3B52",
    "list_sel":      "#1E3A50",
    "chip_active":   "#172230",
    "chip_hover":    "#15202D",
    "status_ns":     "#6B7E94",
    "status_ip":     "#F4A633",
    "status_done":   "#2ECC71",
    "status_na":     "#4A5568",
    "lock_banner_bg":"#2A1A1E",
    "lock_banner_fg":"#FFC4CC",
}

FONT_TITLE   = ("Segoe UI", 22, "bold")
FONT_HEADING = ("Segoe UI", 13, "bold")
FONT_BODY    = ("Segoe UI", 10)
FONT_SMALL   = ("Segoe UI", 9)
FONT_MONO    = ("Consolas", 9)
FONT_LABEL   = ("Segoe UI", 10, "bold")



# ── Balance Sheet & P&L Templates (Schedule III aligned) ─────────────────────
# Each entry: (key, label, kind)  where kind is "header" | "item" | "total"
BALANCE_SHEET_TEMPLATE = [
    # EQUITY & LIABILITIES
    ("bs_h_eq",     "EQUITY AND LIABILITIES",                          "header"),
    ("bs_h_sf",     "Shareholders' Funds",                              "header"),
    ("bs_share_cap","Share Capital",                                    "item"),
    ("bs_reserves", "Reserves and Surplus",                             "item"),
    ("bs_warrants", "Money received against share warrants",            "item"),
    ("bs_sh_app",   "Share application money pending allotment",        "item"),
    ("bs_h_ncl",    "Non-Current Liabilities",                          "header"),
    ("bs_lt_borr",  "Long-term Borrowings",                             "item"),
    ("bs_dtl",      "Deferred Tax Liabilities (Net)",                   "item"),
    ("bs_ol_liab",  "Other Long-term Liabilities",                      "item"),
    ("bs_lt_prov",  "Long-term Provisions",                             "item"),
    ("bs_h_cl",     "Current Liabilities",                              "header"),
    ("bs_st_borr",  "Short-term Borrowings",                            "item"),
    ("bs_payables", "Trade Payables",                                   "item"),
    ("bs_oc_liab",  "Other Current Liabilities",                        "item"),
    ("bs_st_prov",  "Short-term Provisions",                            "item"),
    ("bs_t_eq",     "TOTAL EQUITY AND LIABILITIES",                     "total"),
    # ASSETS
    ("bs_h_assets", "ASSETS",                                           "header"),
    ("bs_h_nca",    "Non-Current Assets",                               "header"),
    ("bs_ppe",      "Property, Plant and Equipment",                    "item"),
    ("bs_cwip",     "Capital Work-in-Progress",                         "item"),
    ("bs_intang",   "Intangible Assets",                                "item"),
    ("bs_intang_dev","Intangible Assets under Development",             "item"),
    ("bs_nc_inv",   "Non-current Investments",                          "item"),
    ("bs_dta",      "Deferred Tax Assets (Net)",                        "item"),
    ("bs_lt_loans", "Long-term Loans and Advances",                     "item"),
    ("bs_onc_ass",  "Other Non-current Assets",                         "item"),
    ("bs_h_ca",     "Current Assets",                                   "header"),
    ("bs_cur_inv",  "Current Investments",                              "item"),
    ("bs_invent",   "Inventories",                                      "item"),
    ("bs_recv",     "Trade Receivables",                                "item"),
    ("bs_cash",     "Cash and Cash Equivalents",                        "item"),
    ("bs_st_loans", "Short-term Loans and Advances",                    "item"),
    ("bs_oc_ass",   "Other Current Assets",                             "item"),
    ("bs_t_ass",    "TOTAL ASSETS",                                     "total"),
]

PL_TEMPLATE = [
    ("pl_h_inc",    "INCOME",                                           "header"),
    ("pl_rev",      "Revenue from Operations",                          "item"),
    ("pl_oth_inc",  "Other Income",                                     "item"),
    ("pl_t_rev",    "Total Revenue",                                    "total"),
    ("pl_h_exp",    "EXPENSES",                                         "header"),
    ("pl_cogs",     "Cost of Materials Consumed",                       "item"),
    ("pl_purch",    "Purchases of Stock-in-Trade",                      "item"),
    ("pl_inv_chg",  "Changes in Inventories of FG, WIP & Stock-in-Trade","item"),
    ("pl_emp",      "Employee Benefits Expense",                        "item"),
    ("pl_fin",      "Finance Costs",                                    "item"),
    ("pl_dep",      "Depreciation and Amortisation Expense",            "item"),
    ("pl_oth_exp",  "Other Expenses",                                   "item"),
    ("pl_t_exp",    "Total Expenses",                                   "total"),
    ("pl_pbt_excep","Profit before Exceptional Items and Tax",          "total"),
    ("pl_excep",    "Exceptional Items",                                "item"),
    ("pl_pbt",      "Profit Before Tax",                                "total"),
    ("pl_h_tax",    "Tax Expense",                                      "header"),
    ("pl_cur_tax",  "Current Tax",                                      "item"),
    ("pl_def_tax",  "Deferred Tax",                                     "item"),
    ("pl_pat",      "Profit / (Loss) for the Period",                   "total"),
]

# ── Variance total computation map ───────────────────────────────────────────
# sign +1 = add, -1 = subtract.  Component keys may be items OR other totals.
VARIANCE_TOTALS = {
    "bs_t_eq":      [(+1, k) for k in
                     "bs_share_cap bs_reserves bs_warrants bs_sh_app "
                     "bs_lt_borr bs_dtl bs_ol_liab bs_lt_prov "
                     "bs_st_borr bs_payables bs_oc_liab bs_st_prov".split()],
    "bs_t_ass":     [(+1, k) for k in
                     "bs_ppe bs_cwip bs_intang bs_intang_dev "
                     "bs_nc_inv bs_dta bs_lt_loans bs_onc_ass "
                     "bs_cur_inv bs_invent bs_recv bs_cash bs_st_loans bs_oc_ass".split()],
    "pl_t_rev":     [(+1, "pl_rev"),      (+1, "pl_oth_inc")],
    "pl_t_exp":     [(+1, k) for k in
                     "pl_cogs pl_purch pl_inv_chg pl_emp pl_fin pl_dep pl_oth_exp".split()],
    "pl_pbt_excep": [(+1, "pl_t_rev"),    (-1, "pl_t_exp")],
    "pl_pbt":       [(+1, "pl_pbt_excep"),(-1, "pl_excep")],
    "pl_pat":       [(+1, "pl_pbt"),      (-1, "pl_cur_tax"), (-1, "pl_def_tax")],
}


# ══════════════════════════════════════════════════════════════════════════════
# Process Notes — separate dicts for AS, Ind AS, and Tax Audit
# Keys: plain note/clause number as a string, e.g. "1", "2", "30A"
# Language is past-tense ("register was obtained", not "obtain register")
# ══════════════════════════════════════════════════════════════════════════════

AS_PROCESS_NOTES = {
"1": """Objective: To verify that corporate information is accurate and complete.

Procedures performed:
1. The Certificate of Incorporation, Memorandum of Association, and Articles of Association were obtained and reviewed.
2. The registered office address was verified against MCA records.
3. The CIN, PAN, and nature of business activity were confirmed.
4. The entity's registration under the applicable provisions of the Companies Act, 2013 was verified.

Standard: AS 1 — Disclosure of Accounting Policies.""",

"2": """Objective: To verify that accounting policies adopted are appropriate, consistent with prior year, and adequately disclosed.

Procedures performed:
1. A list of accounting policies was obtained from management and evaluated against applicable Accounting Standards.
2. Each policy was assessed for compliance with the relevant AS.
3. Changes in policies from the prior year were identified; AS 5 disclosures were verified.
4. Revenue recognition, depreciation, and inventory valuation policies were assessed for appropriateness.
5. Significant estimates and judgements were confirmed as disclosed.

Standard: AS 1 — Disclosure of Accounting Policies; AS 5 — Net Profit or Loss.""",

"3": """Objective: To verify the accuracy and completeness of share capital disclosures.

Procedures performed:
1. The share capital balance was reconciled with the Register of Members.
2. Authorised, issued, subscribed, and paid-up capital figures were verified.
3. Changes during the year — fresh issue, buyback, or forfeiture — were identified and traced.
4. Rights, preferences, and restrictions on each class of shares were confirmed.
5. Shareholders holding more than 5% were verified as per the register.
6. Bonus and rights issues, if any, were traced to board and shareholder resolutions.

Standard: Schedule III, Companies Act 2013.""",

"4": """Objective: To verify that reserve and surplus balances are correctly stated and movements are properly supported.

Procedures performed:
1. A movement schedule for each reserve was obtained — capital reserve, general reserve, P&L, and securities premium.
2. Appropriations to reserves were verified against board resolutions.
3. Opening balances were agreed to the prior year audited financial statements.
4. Dividend declared was confirmed to be within distributable profits and approved by members.
5. Usage of securities premium was verified to be restricted as per Section 52 of the Companies Act, 2013.

Standard: AS 4 — Contingencies and Events Occurring After the Balance Sheet Date; Schedule III.""",

"5": """Objective: To verify the completeness and accuracy of long-term borrowings and compliance with loan terms.

Procedures performed:
1. Loan agreements were obtained and terms — rate, tenure, security, and covenants — were confirmed.
2. Balances were reconciled with lender confirmations and bank statements.
3. Security created was verified; ROC filings for charges (Form CHG-1) were inspected.
4. Classification between current and non-current portions was confirmed as correct.
5. Repayment schedules were checked and no defaults in repayment were noted.
6. Restrictive covenants and compliance certificates were inspected.

Standard: AS 16 — Borrowing Costs; Schedule III.""",

"6": """Objective: To verify the deferred tax liability computation and disclosure.

Procedures performed:
1. Deferred tax workings were obtained from management.
2. All temporary differences between the book and tax base of assets and liabilities were identified.
3. The tax rate applied was confirmed to be the enacted rate.
4. Movement in the DTL/DTA balance was agreed to the P&L tax charge.
5. The basis for recognition of any deferred tax asset was evaluated against future profitability projections.

Standard: AS 22 — Taxes on Income.""",

"7": """Objective: To verify that other long-term liabilities are complete and properly classified.

Procedures performed:
1. A detailed breakup of other long-term liabilities was obtained.
2. Each item was verified to be genuinely long-term in nature, i.e., due beyond 12 months from the reporting date.
3. Confirmations were obtained for significant balances.
4. Advances from customers were traced to underlying contract terms.

Standard: Schedule III, Companies Act 2013.""",

"8": """Objective: To verify that long-term provisions are adequately provided and properly estimated.

Procedures performed:
1. Actuarial valuation reports were obtained for employee benefit provisions — gratuity and leave encashment.
2. Actuarial assumptions — discount rate, salary growth, and attrition — were reviewed for reasonableness.
3. Provision for warranties was verified to be based on historical claims data.
4. Movement in provisions during the year was reviewed and confirmed.

Standard: AS 15 — Employee Benefits; AS 29 — Provisions, Contingent Liabilities and Contingent Assets.""",

"9": """Objective: To verify the completeness and accuracy of short-term borrowings.

Procedures performed:
1. Bank sanction letters were obtained and working capital limits were confirmed.
2. Balances were reconciled with bank statements and bank confirmation letters.
3. Security — hypothecation of stock and debtors — was verified to be noted appropriately.
4. Interest accrued was checked and rates were confirmed against sanction letters.
5. Drawing and repayment transactions were reviewed for any unusual items.

Standard: Schedule III.""",

"10": """Objective: To verify that trade payables are complete, properly aged, and correctly classified between MSME and non-MSME suppliers.

Procedures performed:
1. A creditor-wise ageing schedule was obtained and reviewed.
2. MSME suppliers were identified and dues outstanding beyond 45 days were verified for Section 43B(h) compliance.
3. Confirmation letters were sent to major suppliers, or alternative procedures were applied.
4. Debit balances in payables were identified and reclassified as applicable.
5. Cut-off procedures were applied — invoices received around year-end were verified to be accounted in the correct period.

Standard: MSMED Act 2006; Schedule III.""",

"11": """Objective: To verify that other current liabilities are complete and correctly classified.

Procedures performed:
1. A detailed breakup of other current liabilities was obtained and reviewed.
2. Statutory dues — TDS, GST, PF, and ESI — were confirmed to have been paid within due dates.
3. Advances from customers were reconciled with contracts and purchase orders.
4. The current maturity of long-term debt was confirmed to have been correctly extracted from the debt schedule.

Standard: Schedule III.""",

"12": """Objective: To verify that short-term provisions are adequately estimated and properly supported.

Procedures performed:
1. A breakup of short-term provisions was obtained.
2. The provision for tax was verified to have been computed correctly after considering advance tax and TDS credits.
3. The short-term portion of gratuity and leave encashment was confirmed to have been computed by the appointed actuary.
4. Provisions for pending expenses were checked and agreed to invoices received after year-end.

Standard: AS 29 — Provisions, Contingent Liabilities and Contingent Assets; AS 15 — Employee Benefits.""",

"13": """Objective: To verify the existence, ownership, valuation, and completeness of fixed assets.

Procedures performed:
1. The fixed assets register was obtained and opening balances were agreed to the prior year audited financial statements.
2. Additions were verified — purchase invoices, agreements, and board approvals were traced.
3. Disposals were verified — proceeds, gain/loss computation, and board approval were confirmed.
4. Physical verification of assets was attended or reviewed; discrepancies noted were investigated.
5. Depreciation was recomputed for a sample of assets and agreed to the stated policy.
6. Ownership was verified — title deeds, RC books, and registration documents were inspected.
7. Assets held for disposal were identified and carrying value was compared with NRV.

Standard: AS 6 — Depreciation Accounting; AS 10 — Property, Plant and Equipment.""",

"14": """Objective: To verify that non-current investments are properly valued and adequately disclosed.

Procedures performed:
1. The investment schedule with cost, market value, and carrying value was obtained.
2. Existence was verified — share certificates or demat account statements were obtained.
3. Quoted investments were confirmed to be valued at the lower of cost or fair value.
4. Unquoted investments were assessed for permanent diminution in value.
5. Income from investments — dividends and interest — was verified to have been properly recorded.

Standard: AS 13 — Accounting for Investments.""",

"15": """Objective: To verify that the deferred tax asset is recognised only to the extent it is virtually certain of realisation.

Procedures performed:
1. The deferred tax computation was obtained.
2. Management's assessment of future taxable profits was evaluated.
3. All temporary differences were confirmed to have been captured.
4. The movement in the DTA was agreed to the deferred tax charge in the P&L.

Standard: AS 22 — Taxes on Income.""",

"16": """Objective: To verify that long-term loans and advances are genuine, recoverable, and properly authorised.

Procedures performed:
1. A party-wise breakup of long-term loans and advances was obtained.
2. Advances to related parties were verified — board approvals and arm's length terms were confirmed.
3. Confirmation requests were sent for significant balances.
4. Recoverability was assessed and the adequacy of the provision for doubtful advances was evaluated.
5. Advances given out of borrowed funds were identified and related party implications were noted.

Standard: AS 18 — Related Party Disclosures.""",

"17": """Objective: To verify that other non-current assets are properly stated and recoverable.

Procedures performed:
1. A breakup of other non-current assets was obtained and each balance was verified to be genuinely non-current.
2. Prepaid expenses were reviewed and confirmed to relate to future periods beyond 12 months.
3. Capital advances were verified — the progress of underlying capital projects and their recoverability were assessed.

Standard: Schedule III.""",

"18": """Objective: To verify that current investments are properly valued at the lower of cost or fair value.

Procedures performed:
1. The investment schedule with acquisition cost and market value as at year-end was obtained.
2. The valuation basis — quoted price, or NAV for mutual funds — was confirmed.
3. Income accrued on investments was verified to have been properly recorded.

Standard: AS 13 — Accounting for Investments.""",

"19": """Objective: To verify that inventories are physically present, properly valued, and tested for NRV.

Procedures performed:
1. The physical inventory count was attended, or the count procedures were reviewed.
2. Book inventory was reconciled to the physical count; variances were investigated.
3. The valuation basis — FIFO or weighted average — was verified to have been consistently applied.
4. NRV for selected items was tested — cost was compared with selling price less costs to sell.
5. Slow-moving, obsolete, and damaged items were identified and the adequacy of provision was assessed.
6. Cut-off was checked — goods in transit and consignment stock treatment was verified.

Standard: AS 2 — Valuation of Inventories.""",

"20": """Objective: To verify that trade receivables are genuine, properly aged, and adequately provided for.

Procedures performed:
1. A debtor-wise ageing analysis was obtained.
2. External confirmations were sent to major debtors, or alternative procedures were applied.
3. Subsequent receipts were reviewed to assess recoverability.
4. The provision for doubtful debts was tested — management's basis and historical write-off experience were reviewed.
5. Outstanding debit note and credit note disputes were identified.
6. Debtors pledged as security were confirmed to be properly disclosed.

Standard: AS 1; Schedule III.""",

"21": """Objective: To verify that cash and bank balances are genuine and agree to bank confirmations.

Procedures performed:
1. Bank reconciliation statements (BRS) for all accounts as at year-end were obtained.
2. Bank confirmation letters were sent directly to the bankers.
3. The cash book balance was agreed to the physical cash count or confirmation from the branch.
4. All outstanding cheques and deposits in the BRS were traced to subsequent clearance.
5. Bank balances under lien or earmarked were confirmed to be properly disclosed.

Standard: Schedule III.""",

"22": """Objective: To verify that short-term loans and advances are genuine, authorised, and recoverable.

Procedures performed:
1. A party-wise breakup of short-term loans and advances was obtained and balances were aged.
2. Advances to employees were verified against HR records and recovery schedules.
3. Advances to suppliers were reviewed — receipt of goods or services was confirmed or goods in transit were identified.
4. Prepaid expenses were confirmed to relate to current year periods.

Standard: Schedule III.""",

"23": """Objective: To verify that other current assets are genuine and recoverable.

Procedures performed:
1. A breakup of other current assets was obtained.
2. Export incentives receivable were reviewed — eligibility and the basis of claim were confirmed.
3. GST and tax refund receivables were reconciled with filed returns.
4. Recoverability of each item was assessed.

Standard: Schedule III.""",

"24": """Objective: To verify that revenue from operations is complete, accurate, and recognised in the correct period.

Procedures performed:
1. Total revenue was agreed to the GST returns (GSTR-1) filed during the year.
2. Cut-off procedures were applied — dispatches and invoices around year-end were verified.
3. A sample of sales invoices was tested — delivery, pricing, and credit terms were confirmed.
4. Revenue by product and segment was analytically reviewed for unusual fluctuations.
5. Returns, discounts, and rebates were verified to have been properly recorded.

Standard: AS 9 — Revenue Recognition.""",

"25": """Objective: To verify that other income is complete and non-recurring items are separately disclosed.

Procedures performed:
1. A breakup of other income line items was obtained.
2. Dividend and interest income were verified to have been properly recorded and TDS deducted.
3. Profit on sale of assets was confirmed to agree to the fixed assets register.
4. Exchange gains and losses were verified to have been computed correctly.
5. Exceptional and non-recurring items were identified and confirmed to be separately disclosed.

Standard: AS 9 — Revenue Recognition; AS 11 — The Effects of Changes in Foreign Exchange Rates.""",

"26": """Objective: To verify that the cost of materials consumed is complete and accurately computed.

Procedures performed:
1. Purchases per books were reconciled with GSTR-2B and vendor ledgers.
2. The consumption calculation was reperformed: opening stock plus purchases less closing stock.
3. Results were agreed to the bill of materials (BOM) where applicable.
4. A sample of purchase invoices was tested — quantity, price, and receipt were verified.

Standard: AS 2 — Valuation of Inventories.""",

"27": """Objective: To verify that changes in inventories are correctly computed and agree to stock records.

Procedures performed:
1. Opening stocks were agreed to the prior year closing stocks.
2. Closing stocks were agreed to the physical verification report and stock ledgers.
3. The movement was verified to be in line with production and sales volumes.

Standard: AS 2 — Valuation of Inventories.""",

"28": """Objective: To verify that employee benefits expense is complete and properly accrued.

Procedures performed:
1. Salary expense was reconciled with payroll records and Form 24Q/Form 16.
2. PF, ESI, and professional tax deposits were verified to agree to challans filed.
3. The gratuity and leave encashment charge was agreed to the actuarial report.
4. ESOP expense, where applicable, was reviewed and confirmed.

Standard: AS 15 — Employee Benefits.""",

"29": """Objective: To verify that finance costs are properly recorded and agree to loan schedules.

Procedures performed:
1. Interest expense was agreed to lender statements and loan repayment schedules.
2. Processing fees and bank charges were verified to have been properly accounted.
3. Interest capitalised to capital work-in-progress was confirmed to relate to qualifying assets only.

Standard: AS 16 — Borrowing Costs.""",

"30": """Objective: To verify that depreciation is correctly computed and is consistent with the stated accounting policy.

Procedures performed:
1. Depreciation was recomputed for a sample of assets.
2. The useful life adopted was confirmed to be as per Schedule II, or supported by a technical assessment.
3. The residual value assumption was verified to be reasonable.
4. Depreciation on assets disposed of during the year was confirmed to be on a pro-rata basis.

Standard: AS 6 — Depreciation Accounting; Schedule II, Companies Act 2013.""",

"31": """Objective: To verify that other expenses are properly classified, authorised, and not fictitious.

Procedures performed:
1. The expense schedule was reviewed and analytical procedures were performed for unusual fluctuations.
2. Significant expense items were vouched — invoices, approvals, and business purpose were verified.
3. Expenses related to personal use of directors were confirmed to not have been charged to the company.
4. Repairs and maintenance were reviewed to confirm no capital expenditure was mis-classified.
5. CSR expenditure, where applicable, was confirmed to be properly disclosed.

Standard: Schedule III.""",

"32": """Objective: To verify that earnings per share is computed correctly using the weighted average method.

Procedures performed:
1. Profit after tax was agreed to the P&L statement.
2. The weighted average number of equity shares was computed and verified.
3. Diluted EPS was computed — dilutive instruments such as ESOPs and convertible bonds were considered.
4. Results were compared with the prior year and significant changes were investigated.

Standard: AS 20 — Earnings Per Share.""",

"33": """Objective: To verify that all related party transactions have been identified and adequately disclosed.

Procedures performed:
1. The list of related parties provided by management was obtained and completeness was confirmed against shareholding and directorship records.
2. A schedule of all transactions with related parties was obtained.
3. Transactions were verified to be at arm's length, or exceptions were confirmed as disclosed.
4. Board approvals for material related party transactions were confirmed.
5. Related party balances were cross-checked with confirmations.

Standard: AS 18 — Related Party Disclosures.""",

"34": """Objective: To verify that contingent liabilities are properly identified and disclosed, and that commitments are accurately stated.

Procedures performed:
1. A management representation letter on contingent liabilities was obtained.
2. Pending litigation was reviewed — legal opinions were obtained for significant matters.
3. Guarantees given were verified — counter-guarantee documents were inspected.
4. Capital commitments were confirmed to be based on contracts entered and outstanding.
5. Correspondence with regulators and tax authorities was reviewed.

Standard: AS 29 — Provisions, Contingent Liabilities and Contingent Assets.""",

"35": """Objective: To verify that segment information is complete and correctly presented.

Procedures performed:
1. Reportable segments were identified based on internal management reporting.
2. Segment revenue, results, assets, and liabilities were verified to reconcile to the financial statements.
3. Inter-segment eliminations were confirmed to have been properly made.

Standard: AS 17 — Segment Reporting.""",

"36": """Objective: To verify that lease disclosures are complete and consistent with lease agreements.

Procedures performed:
1. All lease agreements — operating and finance — were obtained.
2. Classification was verified — criteria for finance lease were assessed for correctness.
3. Minimum lease payment disclosures were agreed to lease schedules.
4. Operating lease expense was confirmed to be recognised on a straight-line basis.

Standard: AS 19 — Leases.""",

"37": """Objective: To verify that employee benefit obligations are properly measured and disclosed.

Procedures performed:
1. The actuarial valuation report was obtained from the appointed actuary.
2. Key actuarial assumptions — discount rate, mortality, attrition, and salary growth — were reviewed.
3. The defined benefit obligation and plan assets were agreed to the actuarial report.
4. The components of benefit expense — service cost, interest cost, and actuarial gains/losses — were verified.

Standard: AS 15 — Employee Benefits.""",

"38": """Objective: To verify that foreign currency transactions and year-end balances are properly translated.

Procedures performed:
1. A schedule of foreign currency transactions during the year was obtained.
2. Transactions were verified to have been recorded at the exchange rate on the date of transaction.
3. Year-end balances were re-translated at the closing rate and the resulting exchange difference was agreed.
4. Hedging instruments such as forward contracts were confirmed to have been properly accounted.

Standard: AS 11 — The Effects of Changes in Foreign Exchange Rates.""",

"39": """Objective: To verify that borrowing costs capitalised meet the criteria for qualifying assets.

Procedures performed:
1. Qualifying assets under construction were identified.
2. The amount of borrowing costs capitalised was verified based on the weighted average cost of borrowings.
3. Capitalisation was confirmed to have ceased when each asset was ready for its intended use.

Standard: AS 16 — Borrowing Costs.""",

"40": """Objective: To verify that current and deferred tax are correctly measured and adequately disclosed.

Procedures performed:
1. The current tax computation was verified and agreed to the tax return filed.
2. Advance tax and TDS credits were confirmed to have been properly set off.
3. The deferred tax workings were reviewed — all temporary differences were confirmed to have been captured.
4. The effective tax rate was confirmed to be reasonable and was reconciled to the statutory rate.

Standard: AS 22 — Taxes on Income.""",
}


IND_AS_PROCESS_NOTES = {
"1": """Objective: To verify that corporate information is accurate and complete.

Procedures performed:
1. The CIN, date of incorporation, registered office address, nature of business, and listing status were verified against MCA records and stock exchange filings.
2. Any changes in the above during the year were confirmed to have been properly updated in the disclosures.

Standard: Ind AS 1 — Presentation of Financial Statements.""",

"2": """Objective: To verify that the financial statements have been prepared in accordance with Ind AS.

Procedures performed:
1. The financial statements were confirmed to have been prepared under the Indian Accounting Standards (Ind AS) framework notified under the Companies Act, 2013.
2. The functional currency was verified to have been correctly identified as Indian Rupees.
3. The going concern assumption was evaluated — management's assessment was reviewed and found to be appropriate.

Standard: Ind AS 1 — Presentation of Financial Statements.""",

"3": """Objective: To verify that significant accounting policies are appropriate, Ind AS-compliant, and consistently applied.

Procedures performed:
1. The list of accounting policies was obtained from management and evaluated against applicable Ind AS standards.
2. Any changes in policy from the prior year were identified — retrospective application or transition adjustments were verified.
3. Revenue recognition, financial instruments, leases, and employee benefits policies were reviewed for compliance.
4. Significant estimates and judgements were confirmed to have been adequately disclosed.

Standard: Ind AS 1 — Presentation of Financial Statements; Ind AS 8 — Accounting Policies, Changes in Accounting Estimates and Errors.""",

"4": """Objective: To verify that critical accounting estimates and judgements are reasonable and adequately disclosed.

Procedures performed:
1. Areas requiring significant estimates were identified — expected credit losses, fair value of financial instruments, defined benefit obligations, useful lives of assets, and provisions.
2. Management's methodology and the data used for each estimate were assessed.
3. Sensitivity disclosures were reviewed for adequacy.
4. Estimates were compared with prior year and significant changes were investigated.

Standard: Ind AS 1; Ind AS 8.""",

"5": """Objective: To verify the existence, ownership, valuation, and completeness of property, plant and equipment.

Procedures performed:
1. The PPE schedule was obtained — opening balance, additions, disposals, depreciation, and closing balance were agreed to the ledger.
2. Additions were traced to purchase invoices and authorisation.
3. Componentisation was confirmed for significant assets where applicable.
4. Physical verification of assets was attended or reviewed; discrepancies were investigated.
5. Useful life and residual value assessments were verified.
6. The carrying amount of assets held for disposal was compared with NRV.

Standard: Ind AS 16 — Property, Plant and Equipment.""",

"6": """Objective: To verify that right-of-use assets and lease liabilities have been correctly recognised and measured.

Procedures performed:
1. All lease contracts were obtained and assessed for applicability of Ind AS 116.
2. The incremental borrowing rate used for discounting was reviewed for appropriateness.
3. The ROU asset and lease liability at commencement were recomputed for significant leases.
4. Depreciation of the ROU asset and interest on the lease liability were verified.
5. Short-term and low-value asset lease exemptions were confirmed to have been applied appropriately.
6. Lease modifications, if any, were verified to have been accounted for correctly.

Standard: Ind AS 116 — Leases.""",

"7": """Objective: To verify that capital work-in-progress represents genuine in-progress capital expenditure.

Procedures performed:
1. A project-wise CWIP schedule was obtained.
2. Supporting invoices and milestone completion certificates were verified.
3. Impaired or significantly delayed projects were identified and assessed.
4. Capitalisation during the year was verified to have been appropriately transferred to PPE.

Standard: Ind AS 16 — Property, Plant and Equipment.""",

"8": """Objective: To verify that goodwill and intangible assets are correctly recognised and tested for impairment.

Procedures performed:
1. The goodwill balance was agreed to acquisition documents and the purchase price allocation (PPA) report.
2. Management's annual impairment test was reviewed — CGU identification, recoverable amount, and discount rate assumptions were assessed.
3. Intangible assets were verified to meet the recognition criteria under Ind AS 38.
4. Amortisation was confirmed to be applied only to finite-life intangibles and not to indefinite-life assets.

Standard: Ind AS 36 — Impairment of Assets; Ind AS 38 — Intangible Assets.""",

"9": """Objective: To verify the classification and measurement of non-current financial investments.

Procedures performed:
1. The business model and cash flow characteristics were assessed for each investment to confirm FVTPL, FVOCI, or Amortised Cost classification.
2. Fair values were verified — Level 1 inputs (quoted prices), Level 2 inputs (observable), or Level 3 inputs (valuation models) were assessed.
3. Any irrevocable FVOCI elections for equity instruments were confirmed to have been made at inception.

Standard: Ind AS 109 — Financial Instruments.""",

"10": """Objective: To verify that non-current loans are genuine, properly measured, and adequately provided for.

Procedures performed:
1. A party-wise breakup was obtained and confirmation letters were sent.
2. Expected credit losses (ECL) were computed and the adequacy of the provision was assessed.
3. Loans to related parties were confirmed to be at arm's length and properly approved.
4. The amortised cost measurement was verified for significant loans.

Standard: Ind AS 109 — Financial Instruments; Ind AS 24 — Related Party Disclosures.""",

"11": """Objective: To verify that other non-current financial assets are properly recognised and measured.

Procedures performed:
1. A breakup was obtained — security deposits, derivative assets, and other items were reviewed.
2. Security deposits were verified to have been measured at amortised cost where material.
3. ECL was assessed on each item.
4. Derivative assets were confirmed to have been marked to market.

Standard: Ind AS 109 — Financial Instruments.""",

"12": """Objective: To verify that deferred tax assets are properly recognised and measured.

Procedures performed:
1. The deferred tax workings were obtained.
2. All deductible and taxable temporary differences were identified.
3. Recoverability of the DTA was assessed against future taxable profit projections.
4. Opening and closing DTA/DTL balances were agreed to the prior year and the movement schedule.

Standard: Ind AS 12 — Income Taxes.""",

"13": """Objective: To verify advance tax, TDS, and other non-current tax assets.

Procedures performed:
1. Advance tax payments were reconciled with challans.
2. TDS credits were confirmed per Form 26AS and the Annual Information Statement (AIS).
3. Netting against current tax liabilities was confirmed to be appropriate only where a legal right exists.

Standard: Ind AS 12 — Income Taxes.""",

"14": """Objective: To verify that other non-current assets are genuine and recoverable.

Procedures performed:
1. A breakup was obtained — capital advances and prepaid expenses beyond 12 months were reviewed.
2. Capital advances were verified to be supported by contracts and progress of the underlying project.
3. Recoverability of each item was assessed and the need for a provision was evaluated.

Standard: Schedule III.""",

"15": """Objective: To verify that inventories are correctly valued and tested for NRV.

Procedures performed:
1. The physical inventory count was attended or the count procedures were reviewed.
2. The valuation basis — FIFO or weighted average cost formula — was verified to have been consistently applied.
3. NRV was tested for finished goods and WIP — selling price less estimated costs to complete and sell was assessed.
4. Provisions for slow-moving and obsolete items were identified and assessed.

Standard: Ind AS 2 — Inventories.""",

"16": """Objective: To verify that current investments are correctly classified and measured at fair value.

Procedures performed:
1. Classification as FVTPL was confirmed for current financial investments.
2. Fair value was agreed to the NAV for mutual funds and the quoted price for equity instruments.
3. Income on investments was verified to have been correctly recorded.

Standard: Ind AS 109 — Financial Instruments.""",

"17": """Objective: To verify that trade receivables are genuine and adequately provided for using the ECL model.

Procedures performed:
1. A debtor-wise ageing schedule was obtained.
2. The simplified ECL approach was applied — historical loss rate data was obtained and assessed.
3. Confirmation letters were sent to major debtors.
4. Subsequent receipts after year-end were reviewed to assess recoverability.
5. Debtors pledged as security were confirmed to be disclosed.

Standard: Ind AS 109 — Financial Instruments.""",

"18": """Objective: To verify that cash and cash equivalents are genuine and agree to bank confirmations.

Procedures performed:
1. Bank reconciliation statements for all accounts as at year-end were obtained.
2. Bank confirmation letters were sent directly to the bankers.
3. Petty cash balance was verified.
4. All outstanding entries in the BRS were confirmed to have been cleared in the subsequent period.

Standard: Ind AS 7 — Statement of Cash Flows.""",

"19": """Objective: To verify that bank balances other than cash equivalents are properly classified and disclosed.

Procedures performed:
1. Fixed deposits and margin money were confirmed with bank statements and confirmation letters.
2. Classification between short-term and long-term was verified based on maturity.
3. Restrictions on use of balances, such as lien or earmarking, were confirmed to have been disclosed.

Standard: Ind AS 7 — Statement of Cash Flows.""",

"20": """Objective: To verify that current loans are genuine, recoverable, and adequately provided for.

Procedures performed:
1. A party-wise breakup was obtained and confirmations were sent.
2. The ECL model was applied to assess the provision requirement.
3. Loans to directors and related parties were confirmed to have board approval.

Standard: Ind AS 109 — Financial Instruments; Ind AS 24 — Related Party Disclosures.""",

"21": """Objective: To verify that other current financial assets are properly recognised and measured.

Procedures performed:
1. A breakup was obtained — derivative assets, interest accrued, and insurance claims were reviewed.
2. Fair value of derivative assets was verified — mark-to-market statements were obtained.
3. Insurance claims were confirmed to be based on accepted claims only.

Standard: Ind AS 109 — Financial Instruments.""",

"22": """Objective: To verify current tax assets — advance tax and TDS.

Procedures performed:
1. Advance tax payments were reconciled with the tax computation.
2. TDS credits were confirmed per Form 26AS and the AIS.
3. The appropriateness of netting against current tax liabilities was assessed.

Standard: Ind AS 12 — Income Taxes.""",

"23": """Objective: To verify that other current assets are genuine and properly stated.

Procedures performed:
1. A breakup was obtained — prepaid expenses, GST ITC, and export incentives were reviewed.
2. GST input tax credit was reconciled with GSTR-2B.
3. Export incentives were confirmed to be eligible and recognised on an accrual basis.

Standard: Schedule III.""",

"24": """Objective: To verify that equity share capital is correctly stated and changes are properly supported.

Procedures performed:
1. The share capital balance was agreed to the Register of Members.
2. Authorised, issued, subscribed, and paid-up capital were reconciled.
3. Changes during the year — fresh issue and buyback — were traced to board and shareholder resolutions.
4. Shareholders holding more than 5% were confirmed to have been disclosed.

Standard: Ind AS 32 — Financial Instruments: Presentation.""",

"25": """Objective: To verify that other equity components are correctly stated and movements are properly supported.

Procedures performed:
1. A movement schedule for each equity component was obtained — retained earnings, OCI reserves, and securities premium were reviewed.
2. OCI items — actuarial gains/losses and FVOCI changes — were confirmed to be net of deferred tax.
3. Transition adjustments under Ind AS 101 were confirmed to have been correctly carried over from the opening balance sheet.

Standard: Ind AS 1; Ind AS 101 — First-time Adoption of Indian Accounting Standards.""",

"26": """Objective: To verify that non-current borrowings are complete, correctly classified, and measured at amortised cost.

Procedures performed:
1. Loan agreements were obtained and the effective interest rate (EIR) and amortised cost were computed.
2. Balances were agreed to lender confirmations.
3. Security created was verified and ROC charge registration was confirmed.
4. Covenant compliance was reviewed and any waivers obtained were noted.

Standard: Ind AS 109 — Financial Instruments.""",

"27": """Objective: To verify that non-current lease liabilities are correctly measured.

Procedures performed:
1. A lease amortisation schedule was obtained showing the present value of future lease payments.
2. The incremental borrowing rate used for discounting was reviewed for appropriateness.
3. Lease modifications during the year were confirmed to have been accounted for correctly.

Standard: Ind AS 116 — Leases.""",

"28": """Objective: To verify that other non-current financial liabilities are properly recognised and measured.

Procedures performed:
1. A breakup was obtained — deferred payment liabilities, derivative liabilities, and security deposits received were reviewed.
2. Fair value of derivative liabilities was verified — mark-to-market statements were obtained.
3. Security deposits received were confirmed to have been measured at amortised cost.

Standard: Ind AS 109 — Financial Instruments.""",

"29": """Objective: To verify that non-current provisions are adequately estimated and properly measured.

Procedures performed:
1. Actuarial valuations were obtained for long-term employee benefit provisions.
2. Warranty and decommissioning provisions were assessed for reasonableness.
3. The discount rate applied to provisions was reviewed for appropriateness.

Standard: Ind AS 37 — Provisions, Contingent Liabilities and Contingent Assets; Ind AS 19 — Employee Benefits.""",

"30": """Objective: To verify that deferred tax liabilities are correctly measured.

Procedures performed:
1. The deferred tax workings were obtained and reviewed.
2. Taxable temporary differences — particularly accelerated depreciation for tax purposes — were verified.
3. The net DTL/DTA position was confirmed to be correct after offsetting where legally permitted.

Standard: Ind AS 12 — Income Taxes.""",

"31": """Objective: To verify that other non-current liabilities are genuine and correctly classified.

Procedures performed:
1. A breakup was obtained — advance from customers and deferred revenue were reviewed.
2. Each balance was confirmed to be genuinely non-current.
3. Deferred revenue was verified to relate to performance obligations not yet satisfied.

Standard: Ind AS 115 — Revenue from Contracts with Customers.""",

"32": """Objective: To verify that current borrowings are complete and correctly classified.

Procedures performed:
1. Bank overdraft and cash credit balances were confirmed with bank statements.
2. Current maturities of long-term debt were confirmed to have been properly transferred.
3. Covenant breaches, if any, that necessitate reclassification of long-term debt to current were assessed.

Standard: Ind AS 109 — Financial Instruments.""",

"33": """Objective: To verify that trade payables are complete, MSME classification is correct, and cut-off is accurate.

Procedures performed:
1. A creditor-wise ageing schedule was obtained.
2. MSME vendors were identified — Udyam Registration Numbers were verified.
3. Dues beyond 45 days to MSME suppliers were computed — disallowance under Section 43B(h) was assessed.
4. Confirmation letters were sent to major suppliers or alternative procedures were applied.
5. Cut-off was verified at year-end.

Standard: MSMED Act 2006; Ind AS 32 — Financial Instruments: Presentation.""",

"34": """Objective: To verify that other current financial liabilities are properly recognised and measured.

Procedures performed:
1. A breakup was obtained — capital creditors, employee dues, derivative liabilities, and interest accrued were reviewed.
2. Payroll payables were confirmed to agree to the payroll register.
3. Derivative liabilities were confirmed to have been marked to market.

Standard: Ind AS 109 — Financial Instruments.""",

"35": """Objective: To verify that the current portion of lease liabilities is correctly classified.

Procedures performed:
1. The lease amortisation schedule was obtained.
2. The current portion — due within 12 months — was confirmed to be correctly classified.
3. Lease payments made during the year were agreed to the amortisation schedule.

Standard: Ind AS 116 — Leases.""",

"36": """Objective: To verify that current provisions are adequately estimated.

Procedures performed:
1. The current portion of employee benefit provisions was obtained from the actuarial report.
2. Warranty provisions were confirmed to be based on historical claims data.
3. Provisions for pending litigation were reviewed and confirmed to be reasonable.

Standard: Ind AS 37 — Provisions, Contingent Liabilities and Contingent Assets.""",

"37": """Objective: To verify current tax liabilities.

Procedures performed:
1. The current year tax liability was computed and agreed to the provision in the books.
2. The advance tax set-off was confirmed to be correct.
3. Netting with deferred tax liabilities was confirmed to be appropriate only where legally permitted.

Standard: Ind AS 12 — Income Taxes.""",

"38": """Objective: To verify that other current liabilities are complete and correctly classified.

Procedures performed:
1. A breakup was obtained — statutory dues, advances from customers, and deferred revenue were reviewed.
2. Statutory dues — TDS, GST, PF, and ESI — were reconciled and confirmed to have been paid.
3. Deferred revenue was confirmed to relate to current period performance obligations.

Standard: Ind AS 115 — Revenue from Contracts with Customers.""",

"39": """Objective: To verify that revenue from contracts with customers is recognised at the correct amount and in the correct period.

Procedures performed:
1. Contracts with customers were identified and the five-step Ind AS 115 model was applied.
2. Performance obligations were determined and the transaction price was allocated.
3. Recognition timing — at a point in time or over time — was verified based on the transfer of control.
4. Revenue was reconciled with GST returns (GSTR-1) filed during the year.
5. Cut-off procedures were applied around year-end.

Standard: Ind AS 115 — Revenue from Contracts with Customers.""",

"40": """Objective: To verify that other income is complete and non-recurring items are separately disclosed.

Procedures performed:
1. A breakup of other income was obtained — dividend, interest, gains on investments, and exchange gains were reviewed.
2. Dividend income was verified to have been recognised on the ex-dividend date.
3. Interest income was confirmed to have been measured using the effective interest rate (EIR) method.
4. Exceptional items were identified and confirmed to not be recurring in nature.

Standard: Ind AS 109 — Financial Instruments; Ind AS 1.""",

"41": """Objective: To verify that cost of materials consumed and purchases of stock-in-trade are complete and accurate.

Procedures performed:
1. Purchases were reconciled with GSTR-2B.
2. The consumption calculation was reperformed: opening stock plus purchases less closing stock.
3. BOM reconciliation was performed for manufacturing entities.

Standard: Ind AS 2 — Inventories.""",

"42": """Objective: To verify that changes in inventories are correctly computed and agree to stock records.

Procedures performed:
1. Opening stocks were agreed to the prior year closing stocks.
2. Closing stocks were agreed to the physical verification report.
3. The movement was confirmed to be consistent with production volumes.

Standard: Ind AS 2 — Inventories.""",

"43": """Objective: To verify that employee benefits expense is complete and properly accrued.

Procedures performed:
1. Payroll expense was reconciled with Form 24Q and payroll registers.
2. PF, ESI, and professional tax contributions and deposits were verified.
3. The current service cost and net interest on the defined benefit obligation were agreed to the actuarial report.
4. OCI items — remeasurement gains/losses — were confirmed to have been correctly routed.

Standard: Ind AS 19 — Employee Benefits.""",

"44": """Objective: To verify that finance costs are properly recorded and agree to loan schedules.

Procedures performed:
1. Interest expense was agreed to lender statements and the EIR amortisation tables.
2. Interest on lease liabilities was verified per the Ind AS 116 amortisation schedule.
3. Borrowing costs capitalised were confirmed to meet the qualifying asset criteria.

Standard: Ind AS 23 — Borrowing Costs.""",

"45": """Objective: To verify that depreciation and amortisation have been correctly computed and disclosed.

Procedures performed:
1. Depreciation was recomputed for a sample of assets.
2. Useful life and residual value assumptions were reviewed for reasonableness.
3. ROU asset depreciation was confirmed to agree to the Ind AS 116 lease schedule.
4. Amortisation on intangible assets was verified to be based on finite useful life.

Standard: Ind AS 16 — Property, Plant and Equipment; Ind AS 38 — Intangible Assets; Ind AS 116 — Leases.""",

"46": """Objective: To verify that other expenses are properly classified, authorised, and supported.

Procedures performed:
1. Expenses were analytically reviewed by category and compared with the prior year.
2. Significant items were vouched — invoices, contracts, and approvals were verified.
3. No capital expenditure was confirmed to have been mis-classified as a revenue expense.
4. CSR spend was verified to be eligible and disclosed — amounts spent and shortfall, if any, were noted.

Standard: Ind AS 1 — Presentation of Financial Statements.""",

"47": """Objective: To verify that current and deferred tax expense is correctly measured and disclosed.

Procedures performed:
1. Current tax was agreed to the tax computation and return filed.
2. Deferred tax charge/credit was verified per the DTA/DTL movement schedule.
3. The effective tax rate was reconciled to the applicable statutory rate.

Standard: Ind AS 12 — Income Taxes.""",

"48": """Objective: To verify that basic and diluted EPS have been correctly computed.

Procedures performed:
1. Profit after tax was agreed to the statement of profit and loss.
2. The weighted average number of shares was computed and verified using the share register.
3. Dilutive instruments were identified and diluted EPS was recomputed.
4. Results were compared with the prior year and significant changes were investigated.

Standard: Ind AS 33 — Earnings Per Share.""",

"49": """Objective: To verify that all related party transactions are identified, disclosed, and on arm's length terms.

Procedures performed:
1. The related party list from management was obtained and completeness was confirmed against shareholding and directorship records.
2. All RPT schedules for the year were obtained and reviewed.
3. Transactions were assessed to be at arm's length, or exceptions were confirmed as disclosed.
4. Board approvals for material related party transactions were confirmed.
5. Related party balances were cross-checked with confirmations.

Standard: Ind AS 24 — Related Party Disclosures.""",

"50": """Objective: To verify that financial risk disclosures are complete and fair value measurements are appropriately classified.

Procedures performed:
1. The fair value hierarchy disclosure was reviewed — Level 1, 2, and 3 classification was confirmed for all financial instruments.
2. Significant unobservable inputs for Level 3 valuations were assessed for reasonableness.
3. Credit risk, liquidity risk, and market risk disclosures were reviewed for completeness.
4. Hedge accounting criteria were confirmed to have been met for all hedged items.

Standard: Ind AS 107 — Financial Instruments: Disclosures.""",

"51": """Objective: To verify that fair value measurements are consistent, supportable, and properly disclosed.

Procedures performed:
1. Level 1 inputs were confirmed to be unadjusted quoted prices from active markets.
2. Valuation techniques for Level 2 and Level 3 instruments were reviewed and assessed.
3. Sensitivity analysis for Level 3 instruments was confirmed to have been disclosed.

Standard: Ind AS 113 — Fair Value Measurement.""",

"52": """Objective: To verify that lease disclosures are complete and consistent with the lease contracts.

Procedures performed:
1. A complete lease schedule was obtained.
2. The maturity analysis of lease liabilities was verified.
3. Disclosures for ROU asset, depreciation, interest, and total cash outflow were confirmed to be accurate.
4. Variable lease payments were identified and confirmed to have been disclosed.

Standard: Ind AS 116 — Leases.""",

"53": """Objective: To verify that employee benefit disclosures are complete and consistent with the actuarial report.

Procedures performed:
1. All defined benefit disclosures were agreed to the actuarial valuation report.
2. Sensitivity analysis for actuarial assumptions was confirmed to have been disclosed.
3. Plan assets details and expected contributions for the next year were verified.

Standard: Ind AS 19 — Employee Benefits.""",

"54": """Objective: To verify that share-based payment disclosures are complete and the ESOP expense is correctly computed.

Procedures performed:
1. ESOP scheme documents and board approvals were obtained and reviewed.
2. The fair value of options on the grant date was agreed to the Black-Scholes or binomial model output.
3. Vesting conditions were reviewed and the ESOP expense recognised over the vesting period was verified.

Standard: Ind AS 102 — Share-based Payment.""",

"55": """Objective: To verify that segment information is complete and reconciles to the financial statements.

Procedures performed:
1. Operating segments were identified based on the Chief Operating Decision Maker's (CODM) reporting structure.
2. Segment revenue, profit, assets, and liabilities were confirmed to aggregate to the financial statement totals.
3. Inter-segment eliminations were confirmed to have been properly made.

Standard: Ind AS 108 — Operating Segments.""",

"56": """Objective: To verify that contingent liabilities and commitments are properly identified, quantified, and disclosed.

Procedures performed:
1. A management representation letter was obtained and legal counsel opinions were reviewed for significant litigation.
2. Tax contingencies were verified against tax computations and outstanding demand notices.
3. Capital commitments were confirmed to be based on contracts signed but not yet executed.
4. Each contingency was assessed to determine whether a provision should be recognised.

Standard: Ind AS 37 — Provisions, Contingent Liabilities and Contingent Assets.""",

"57": """Objective: To verify that events after the reporting period have been properly identified, assessed, and disclosed.

Procedures performed:
1. Management was enquired about significant events from the year-end to the date of the audit report.
2. Board meeting minutes and post year-end correspondence were reviewed.
3. Events were assessed and classified as adjusting (recognised in the financials) or non-adjusting (disclosed).

Standard: Ind AS 10 — Events after the Reporting Period.""",
}


TAX_PROCESS_NOTES = {
"1": """Objective: To verify the name of the assessee as per PAN records.

Procedures performed:
1. The name was confirmed against the PAN card and NSDL records.
2. The name was verified against the GST registration certificate.
3. Any discrepancy with the books of account was investigated.

Reference: Section 44AB, Income Tax Act 1961.""",

"2": """Objective: To verify the address of the assessee.

Procedures performed:
1. The address was confirmed against PAN records and the GST registration certificate.
2. The registered office address was verified against MCA records.
3. Multiple business locations, if any, were identified and noted.

Reference: Section 44AB.""",

"3": """Objective: To confirm the Permanent Account Number (PAN) of the assessee.

Procedures performed:
1. The PAN was verified against the PAN card copy and the NSDL portal.
2. The PAN was confirmed to have been quoted on all relevant statutory documents.

Reference: Section 139A.""",

"4": """Objective: To verify the status of the assessee.

Procedures performed:
1. The legal status was confirmed from constitutional documents — MOA, partnership deed, or LLP agreement as applicable.
2. The status was verified to match the ITR filed.

Reference: Section 44AB.""",

"5": """Objective: To verify the previous year end date.

Procedures performed:
1. The previous year end — generally 31 March — was confirmed as per the Income Tax Act.
2. Books of account were confirmed to be maintained up to this date.

Reference: Section 3, Income Tax Act 1961.""",

"6": """Objective: To confirm the assessment year.

Procedures performed:
1. The assessment year was confirmed to correspond to the previous year under audit.
2. The ITR was confirmed to have been or to be filed for the correct assessment year.

Reference: Section 2(9), Income Tax Act 1961.""",

"7": """Objective: To verify the nature of business or profession and the applicable section codes.

Procedures performed:
1. All business activities carried on by the assessee were identified.
2. Appropriate business codes from Schedule BP of the ITR were confirmed.
3. No undisclosed or unrelated business activity was noted.

Reference: Schedule BP, ITR.""",

"8": """Objective: To verify the applicable clause of Section 44AB under which the audit was triggered.

Procedures performed:
1. The reason triggering the audit — turnover exceeding the prescribed threshold or opting out of presumptive taxation — was determined.
2. Turnover or gross receipts were confirmed to exceed the applicable threshold.
3. The specific sub-clause of Section 44AB applicable was identified and noted.

Reference: Section 44AB, Income Tax Act 1961.""",

"9": """Objective: To verify whether books of account are required to be maintained under Section 44AA.

Procedures performed:
1. The nature of profession or business and the applicable sub-section of Section 44AA were determined.
2. Books were confirmed to be maintained as required and were inspected.

Reference: Section 44AA, Income Tax Act 1961.""",

"10": """Objective: To verify the nature of books of account maintained and the method of accounting.

Procedures performed:
1. Whether accounts are maintained manually or through computer software was confirmed.
2. The method of accounting — mercantile or cash basis — was confirmed.
3. All books maintained — cash book, ledger, stock register, etc. — were listed and verified.

Reference: Section 44AA; Section 145.""",

"11": """Objective: To verify whether books of account were examined at the head office, branches, or both.

Procedures performed:
1. All business locations were identified.
2. Whether branch books are consolidated at the head office and where the audit was conducted was confirmed.

Reference: Section 44AA.""",

"12": """Objective: To verify details of partners, members, or directors.

Procedures performed:
1. The list of partners, directors, or members with their profit-sharing ratios was obtained.
2. Verification was done against the partnership deed, MOA, or LLP agreement as applicable.
3. Changes in constitution during the year were confirmed with effective dates.

Reference: Schedule III, Form 3CD.""",

"13": """Objective: To verify the method of accounting and confirm consistency.

Procedures performed:
1. Whether the mercantile or cash basis is followed was confirmed.
2. Any change in method during the year was identified and assessed.
3. Where a change was made, the effect was quantified and AS 5 compliance was verified.

Reference: Section 145; AS 5.""",

"14": """Objective: To verify the method of accounting for closing stock and confirm consistency.

Procedures performed:
1. The basis — FIFO, weighted average, or specific identification — was confirmed.
2. Consistency with the prior year was verified.
3. Where a change was made, the effect was quantified and disclosed.

Reference: AS 2 — Valuation of Inventories.""",

"15": """Objective: To identify and disclose any capital assets converted to stock-in-trade during the year.

Procedures performed:
1. Management was enquired about any such conversions.
2. The date and fair market value at the time of conversion were verified.
3. Capital gains implications were confirmed to have been considered.

Reference: Section 45(2), Income Tax Act 1961.""",

"16": """Objective: To identify amounts that have not been credited to the Profit and Loss Account.

Procedures performed:
1. Capital reserve and capital redemption reserve movements were reviewed.
2. Any credits directly to the balance sheet that bypassed the P&L were identified.
3. Each such item was confirmed to be in accordance with applicable law.

Reference: Clause 16, Form 3CD.""",

"17": """Objective: To identify payments to specified persons under Section 40A(2)(b) that are excessive or unreasonable.

Procedures performed:
1. The list of related parties and associated persons was obtained.
2. All transactions with such persons during the year were reviewed.
3. Amounts paid were assessed against market rates and fair value.
4. Those exceeding fair market value were identified and disclosed with justification.

Reference: Section 40A(2)(b), Income Tax Act 1961.""",

"18": """Objective: To identify amounts allowable as a deduction in future years but claimed in the current year.

Procedures performed:
1. Deferred revenue expenditure treated as an asset was reviewed.
2. Claims under Sections 35D, 35DD, 35DDA, and 35E were verified.
3. Underlying documents were traced and the treatment was confirmed to be as per the Act.

Reference: Sections 35D, 35DD, 35DDA, 35E, Income Tax Act 1961.""",

"19": """Objective: To identify amounts not deductible under Section 40 due to TDS defaults.

Procedures performed:
1. Form 26Q and Form 27Q returns were reviewed and reconciled with expense ledgers.
2. Payments where TDS was not deducted or not deposited in time were identified.
3. Disallowance under Sections 40(a)(i) and 40(a)(ia) was computed.
4. Compliance with Section 40A(3) for cash payments exceeding ₹10,000 was verified.

Reference: Section 40, Income Tax Act 1961.""",

"20": """Objective: To identify amounts disallowed under Section 40A — excessive payments and cash payments.

Procedures performed:
1. All cash payments to a single person exceeding ₹10,000 in a day were identified.
2. Payments to related parties in excess of reasonable amounts were identified.
3. Disallowance under Sections 40A(3) and 40A(3A) was computed.

Reference: Section 40A, Income Tax Act 1961.""",

"21": """Objective: To identify deductions claimed under Sections 33AB, 33ABA, 35D, 35DD, and 35E.

Procedures performed:
1. Eligibility for each deduction claimed was verified.
2. Deposits in the approved scheme were confirmed for Sections 33AB and 33ABA.
3. Preliminary and expansion expenses were confirmed to qualify for amortisation under Section 35D.
4. Documentation and board approval were verified.

Reference: Sections 33AB, 33ABA, 35D, 35DD, 35E, Income Tax Act 1961.""",

"22": """Objective: To verify deductions under Section 35 for scientific research expenditure.

Procedures performed:
1. In-house R&D expenditure was verified to be eligible and certified by DSIR.
2. Contributions to approved research institutions were confirmed.
3. Compliance with Form 3CK and Form 3CL requirements was verified as applicable.

Reference: Section 35, Income Tax Act 1961.""",

"23": """Objective: To identify amounts deductible under Section 43B only on actual payment basis.

Procedures performed:
1. All expenses covered by Section 43B were identified — taxes, duties, PF, ESI, bonus, leave encashment, and interest.
2. Each was verified to have been paid before the due date of filing the return, or before year-end as applicable.
3. Disallowance was computed for amounts not paid within the stipulated time.
4. MSME payments under Section 43B(h) were verified to be within 45 days.

Reference: Section 43B, Income Tax Act 1961.""",

"24": """Objective: To verify input tax credit (ITC) availed under GST.

Procedures performed:
1. ITC availed was reconciled with GSTR-2B for the year.
2. ITC reversals — ineligible expenses, exempt supplies — were confirmed to have been effected.
3. The net ITC position was agreed to the electronic credit ledger.

Reference: Section 16, CGST Act 2017.""",

"25": """Objective: To identify shares held in companies where the public are not substantially interested.

Procedures performed:
1. Investments in closely held companies were identified.
2. Deemed dividend implications under Section 2(22)(e) were assessed.
3. Required details were confirmed to have been disclosed.

Reference: Section 2(22)(e), Income Tax Act 1961.""",

"26": """Objective: To verify compliance with Sections 269SS and 269T regarding loan and deposit transactions in cash.

Procedures performed:
1. All loans and deposits received and repaid during the year were reviewed.
2. Transactions above ₹20,000 made in cash were identified.
3. Violations were confirmed and reported with party details and amounts.

Reference: Sections 269SS and 269T, Income Tax Act 1961.""",

"27": """Objective: To identify deemed dividends under Section 2(22)(e).

Procedures performed:
1. Advances and loans by closely held companies to shareholders and concerns were identified.
2. Whether the conditions of Section 2(22)(e) are met was verified.
3. The deemed dividend amount and recipient were disclosed.

Reference: Section 2(22)(e), Income Tax Act 1961.""",

"28": """Objective: To identify deemed profits chargeable under Section 41 due to recovery of previously allowed losses or expenditure.

Procedures performed:
1. Liabilities written back during the year were reviewed.
2. Insurance and other claims received against earlier deductions were identified.
3. Taxability under Section 41 was assessed.

Reference: Section 41, Income Tax Act 1961.""",

"29": """Objective: To identify deductions inadmissible under Sections 30 to 37.

Procedures performed:
1. All expense heads were reviewed for personal, capital, or non-business expenditure.
2. Expenditure not wholly and exclusively for business purposes was identified.
3. Expenditure on political advertisements, club fees, and entertainment not qualifying as business expenditure was noted.

Reference: Sections 30 to 37, Income Tax Act 1961.""",

"30": """Objective: To verify TDS and TCS compliance — amounts deducted, deposited, and returns filed.

Procedures performed:
1. TDS deducted from vendor payments was reconciled with Form 26Q filings.
2. TDS deducted from salaries was reconciled with Form 24Q.
3. Deposits of TDS were confirmed to be within due dates and interest for late payment was identified.
4. TCS collected and deposited on applicable transactions was verified.
5. Defaults — short deduction, late deposit — were identified and reported.

Reference: Sections 194 to 196, 206C, Income Tax Act 1961.""",

"30A": """Objective: To verify compliance with domestic transfer pricing provisions under Section 92BA.

Procedures performed:
1. Specified domestic transactions were identified.
2. Arm's length price computations were reviewed.
3. Form 3CEB was confirmed to have been filed if the aggregate value of transactions exceeded ₹20 crore.

Reference: Section 92BA, Income Tax Act 1961.""",

"30B": """Objective: To verify secondary adjustment requirements under Section 92CE.

Procedures performed:
1. Whether a primary transfer pricing adjustment was made was identified.
2. Whether a secondary adjustment is required was determined and the computation was verified.
3. Repatriation of excess money within the prescribed time was confirmed.

Reference: Section 92CE, Income Tax Act 1961.""",

"30C": """Objective: To verify the limitation on interest deduction under Section 94B.

Procedures performed:
1. Interest payments to non-resident associated enterprises were identified.
2. Whether the entity is a company and whether interest exceeds ₹1 crore was confirmed.
3. The limitation — 30% of EBITDA — and the resulting disallowance were computed.

Reference: Section 94B, Income Tax Act 1961.""",

"31": """Objective: To identify cash receipts or payments exceeding ₹2 lakh in violation of Section 269ST.

Procedures performed:
1. All cash transactions exceeding ₹2 lakh in a single day with a single person were reviewed.
2. Whether any exemptions are applicable was confirmed.
3. Violations were reported with the applicable penalty implications.

Reference: Section 269ST, Income Tax Act 1961.""",

"32": """Objective: To verify brought forward losses and unabsorbed depreciation.

Procedures performed:
1. The computation of income for prior years showing losses and depreciation was obtained.
2. Disclosures were agreed to the prior year's Form 3CD.
3. Availability for set-off against current year income was confirmed under Sections 72, 73, and 74.
4. Whether conditions for carry forward were met — return filed on time — was verified.

Reference: Sections 72, 73, 74, Income Tax Act 1961.""",

"33": """Objective: To verify Chapter VI-A deductions claimed.

Procedures performed:
1. All deductions claimed — Sections 80C, 80G, 80IC, 80IAC, etc. — were identified.
2. Eligibility conditions for each deduction were verified.
3. Documentation was confirmed to be adequate — receipts, certificates, and donee registrations were inspected.
4. The deduction amount was computed and verified against the provisions of the Act.

Reference: Chapter VI-A, Income Tax Act 1961.""",

"34": """Objective: To verify TDS and TCS defaults — late deduction, short deduction, and late deposit.

Procedures performed:
1. TRACES portal data was obtained — defaults and interest computed by the system were reviewed.
2. An independent verification of TDS deductions and deposit dates was performed and reconciled.
3. Defaults were reported with interest under Sections 201(1A) and 220(2).
4. Form 15G and Form 15H submissions were checked — whether non-deduction is justified was confirmed.

Reference: Sections 201, 206AA, Income Tax Act 1961.""",

"35": """Objective: To verify quantitative details of principal items of goods traded or manufactured.

Procedures performed:
1. Item-wise production, purchase, sales, and closing stock quantities were obtained.
2. Reconciliation with the stock register, purchase register, and sales register was performed.
3. The gross profit ratio was computed and compared with prior years.

Reference: Clause 35, Form 3CD.""",

"36": """Objective: To verify qualifications or adverse remarks in audit reports issued under other laws.

Procedures performed:
1. Copies of all statutory audit reports — Companies Act, GST, customs — were obtained.
2. Qualifications, adverse opinions, and emphasis of matter paragraphs were identified.
3. The substance of each qualification was disclosed.

Reference: Clause 36, Form 3CD.""",

"36A": """Objective: To verify dividends declared or paid during the year.

Procedures performed:
1. Board and shareholder resolutions approving the dividend were confirmed.
2. Dividend distribution tax compliance was verified for prior years where applicable.
3. Dividend was confirmed to have been paid only from distributable profits.

Reference: Section 2(22), Income Tax Act 1961.""",

"37": """Objective: To compute and disclose key accounting ratios.

Procedures performed:
1. The gross profit ratio, net profit ratio, stock turnover ratio, and debtors turnover ratio were computed.
2. Results were compared with prior years and significant fluctuations were investigated.
3. Inputs — sales, purchases, stocks, and debtors — were reconciled to the financial statements.

Reference: Clause 37, Form 3CD.""",

"38": """Objective: To disclose demands raised and refunds received during the year by tax authorities.

Procedures performed:
1. Details of all outstanding demands — income tax, GST, customs, and excise — were obtained.
2. Refunds received were confirmed to have been correctly accounted.
3. Demands raised, appeals filed, and current status were disclosed.

Reference: Clause 38, Form 3CD.""",

"39": """Objective: To verify deemed income under Section 59.

Procedures performed:
1. Any trading liability received in earlier years that has since lapsed was identified.
2. Taxability under Section 59 was assessed and disclosed.

Reference: Section 59, Income Tax Act 1961.""",

"40": """Objective: To disclose relevant details from the CARO report and other statutory auditor reports.

Procedures performed:
1. The latest CARO report (for companies) was obtained.
2. Adverse remarks on fraud, statutory dues, and related party transactions were identified.
3. Relevant observations were summarised for Form 3CD disclosure.

Reference: Companies (Auditor's Report) Order, 2020.""",

"41": """Objective: To disclose indirect tax refunds or credits received during the year.

Procedures performed:
1. GST and customs duty refunds received and accounted were identified.
2. Credits availed in the electronic credit ledger were verified.
3. The treatment in the books of account was confirmed to be correct.

Reference: CGST Act 2017; Customs Act 1962.""",

"42": """Objective: To verify MSME dues outstanding beyond 45 days under Section 43B(h).

Procedures performed:
1. The list of MSME vendors with Udyam Registration Numbers was obtained.
2. Outstanding payables were reviewed and those due beyond 45 days were identified.
3. Disallowance under Section 43B(h) for amounts unpaid at year-end was computed.
4. Reconciliation with the MSME half-yearly return (Form MSME-1) filed with MCA was performed.

Reference: Section 43B(h), Income Tax Act 1961; MSMED Act 2006.""",

"43": """Objective: To verify Country-by-Country Report (CbCR) compliance under Section 286.

Procedures performed:
1. Whether the entity is a constituent entity of an international group was determined.
2. Whether consolidated group revenue exceeds ₹5,500 crore was verified.
3. Forms 3CEAB, 3CEAC, and 3CEAD were confirmed to have been filed within due dates.

Reference: Section 286, Income Tax Act 1961.""",

"44": """Objective: To provide a GST-aligned breakup of total expenditure classified by supplier registration status.

Procedures performed:
1. Vendor-wise GSTIN data was obtained from the accounts payable team.
2. Each vendor was classified as registered (regular), registered (composition), exempt, or unregistered.
3. Expenditure under each category was aggregated.
4. Total expenditure was reconciled to the P&L account.
5. Registered supplier totals were cross-checked with GSTR-2B data.

Reference: Clause 44, Form 3CD; CGST Act 2017.""",
}


def get_process_note(key, eng):
    """Look up the default process note for a given workpaper key and engagement.
    Uses the version stamp on the engagement so old engagements always get the
    right process notes even after regulations change."""
    is_tax = eng.get("audit_type") == "Tax Audit"
    if is_tax:
        num = key.replace("cl_", "")
        ver = eng.get("form3cd_version", _default_ver(FORM3CD_VERSION_BY_FY, eng.get("financial_year","")))
        return TAX_PROCESS_NOTES_VERSIONS.get(ver, TAX_PROCESS_NOTES).get(num, "")
    num = key.replace("note_", "")
    std = eng.get("accounting_standard") or "AS"
    if std == "Ind AS":
        ver = eng.get("notes_indas_version", _default_ver(INDAS_NOTES_VERSION_BY_FY, eng.get("financial_year","")))
        return INDAS_PROCESS_NOTES_VERSIONS.get(ver, IND_AS_PROCESS_NOTES).get(num, "")
    ver = eng.get("notes_as_version", _default_ver(AS_NOTES_VERSION_BY_FY, eng.get("financial_year","")))
    return AS_PROCESS_NOTES_VERSIONS.get(ver, AS_PROCESS_NOTES).get(num, "")



# ── CARO 2020 Checklist ───────────────────────────────────────────────────────
# Each entry: (key, label, kind)  kind = "header" | "item"
CARO_ITEMS = [
    # Clause i — PP&E
    ("caro_h1",  "Clause 3(i) — Property, Plant & Equipment", "header"),
    ("caro_1a",  "3(i)(a)(A) — Proper records maintained for PP&E showing full particulars including quantitative details and situation", "item"),
    ("caro_1aB", "3(i)(a)(B) — Proper records maintained for intangible assets showing full particulars", "item"),
    ("caro_1b",  "3(i)(b) — PP&E physically verified by management at reasonable intervals; material discrepancies dealt with in books of account", "item"),
    ("caro_1c",  "3(i)(c) — Title deeds of all immovable properties held in the name of the company", "item"),
    ("caro_1d",  "3(i)(d) — Revaluation of PP&E or intangible assets during the year; based on Registered Valuer; change of 10% or more reported", "item"),
    ("caro_1e",  "3(i)(e) — Any proceedings initiated or pending against the company for holding any benami property under the Benami Transactions (Prohibition) Act, 1988", "item"),
    ("caro_h2",  "Clause 3(ii) — Inventories", "header"),
    ("caro_2a",  "3(ii)(a) — Physical verification of inventory conducted at reasonable intervals; coverage and procedure appropriate; discrepancies of 10% or more in each class dealt with in books", "item"),
    ("caro_2b",  "3(ii)(b) — Working capital limits exceeding ₹5 crore sanctioned on basis of security of current assets; quarterly returns filed agree with books of account", "item"),
    ("caro_h3",  "Clause 3(iii) — Investments, Guarantees, Security, Loans & Advances in nature of Loans", "header"),
    ("caro_3a",  "3(iii) — Whether during the year the company made investments, provided guarantees or security, or granted loans or advances in the nature of loans to companies, firms, LLPs or other parties", "item"),
    ("caro_3aA", "3(iii)(a)(A) — Aggregate amount during the year and balance outstanding at balance sheet date for loans/advances/guarantees/security to subsidiaries, joint ventures and associates", "item"),
    ("caro_3aB", "3(iii)(a)(B) — Aggregate amount during the year and balance outstanding at balance sheet date for loans/advances/guarantees/security to parties other than subsidiaries, joint ventures and associates", "item"),
    ("caro_3b",  "3(iii)(b) — Terms and conditions of all loans/advances/guarantees/security not prejudicial to company's interest", "item"),
    ("caro_3c",  "3(iii)(c) — Schedule of repayment of principal and payment of interest stipulated; repayments or receipts are regular", "item"),
    ("caro_3d",  "3(iii)(d) — Amounts overdue for more than 90 days; reasonable steps taken by company for recovery of principal and interest", "item"),
    ("caro_3e",  "3(iii)(e) — Loans/advances fallen due, renewed or extended or fresh loans granted to settle overdues of existing loans; aggregate amount and percentage reported", "item"),
    ("caro_3f",  "3(iii)(f) — Loans/advances in nature of loans repayable on demand or without specifying terms or period of repayment; aggregate amount, percentage to total loans, and promoter/related party breakdown", "item"),
    ("caro_h4",  "Clause 3(iv) — Loans & Investments under Sections 185 & 186", "header"),
    ("caro_4a",  "3(iv) — Provisions of Sections 185 and 186 of Companies Act 2013 complied with for loans, investments, guarantees and security", "item"),
    ("caro_h5",  "Clause 3(v) — Deposits", "header"),
    ("caro_5a",  "3(v) — RBI directives and Sections 73 to 76 of Companies Act complied with for deposits accepted or amounts deemed to be deposits; orders of CLB/NCLT/RBI/Court complied with", "item"),
    ("caro_h6",  "Clause 3(vi) — Cost Records", "header"),
    ("caro_6a",  "3(vi) — Cost records prescribed under Section 148(1) maintained; accounts and records made and maintained properly", "item"),
    ("caro_h7",  "Clause 3(vii) — Statutory Dues", "header"),
    ("caro_7a",  "3(vii)(a) — Regular in depositing undisputed statutory dues (GST, PF, ESI, Income Tax, Customs, Excise, cess etc.); arrears outstanding more than 6 months from due date indicated", "item"),
    ("caro_7b",  "3(vii)(b) — Disputed statutory dues not deposited — amounts involved and forum where dispute is pending", "item"),
    ("caro_h8",  "Clause 3(viii) — Unrecorded Income / Transactions", "header"),
    ("caro_8a",  "3(viii) — Transactions not recorded in books of account surrendered or disclosed as income during the year in tax assessments; previously unrecorded income properly recorded in books", "item"),
    ("caro_h9",  "Clause 3(ix) — Loans, Borrowings & Fund Utilisation", "header"),
    ("caro_9a",  "3(ix)(a) — Default in repayment of loans or borrowings or in payment of interest to any lender; period and amount of default reported", "item"),
    ("caro_9b",  "3(ix)(b) — Company declared a wilful defaulter by any bank, financial institution or other lender", "item"),
    ("caro_9c",  "3(ix)(c) — Term loans applied for the purpose for which the loans were obtained; amount diverted and purpose reported if used otherwise", "item"),
    ("caro_9d",  "3(ix)(d) — Funds raised on short-term basis utilised for long-term purposes; nature and amount indicated", "item"),
    ("caro_9e",  "3(ix)(e) — Funds taken from any entity or person to meet obligations of subsidiaries, associates or joint ventures; details and amounts reported", "item"),
    ("caro_9f",  "3(ix)(f) — Loans raised during the year on pledge of securities held in subsidiaries, joint ventures or associate companies; default in repayment of such loans reported", "item"),
    ("caro_h10", "Clause 3(x) — Public Offers & Preferential Allotment", "header"),
    ("caro_10a", "3(x)(a) — Moneys raised by way of IPO or FPO (including debt instruments) applied for the purposes for which raised; delays or default and subsequent rectification reported", "item"),
    ("caro_10b", "3(x)(b) — Preferential allotment or private placement of shares or convertible debentures; Sections 42 and 62 of Companies Act 2013 complied with; funds raised used for stated purpose", "item"),
    ("caro_h11", "Clause 3(xi) — Fraud", "header"),
    ("caro_11a", "3(xi)(a) — Any fraud by the company or on the company noticed or reported during the year; nature and amount involved indicated", "item"),
    ("caro_11b", "3(xi)(b) — Report under Section 143(12) filed by auditors in Form ADT-4 as prescribed under rule 13 of Companies (Audit and Auditors) Rules, 2014 with the Central Government", "item"),
    ("caro_11c", "3(xi)(c) — Whistle-blower complaints received during the year considered by the statutory auditor", "item"),
    ("caro_h12", "Clause 3(xii) — Nidhi Company", "header"),
    ("caro_12a", "3(xii)(a) — Net Owned Funds to Deposits ratio of 1:20 maintained to meet out the liability", "item"),
    ("caro_12b", "3(xii)(b) — Ten per cent unencumbered term deposits as specified in Nidhi Rules 2014 maintained to meet out the liability", "item"),
    ("caro_12c", "3(xii)(c) — Default in payment of interest on deposits or repayment thereof for any period; details reported", "item"),
    ("caro_h13", "Clause 3(xiii) — Related Party Transactions", "header"),
    ("caro_13a", "3(xiii) — All transactions with related parties in compliance with Sections 177 and 188 of Companies Act; details disclosed in financial statements as required by applicable accounting standards", "item"),
    ("caro_h14", "Clause 3(xiv) — Internal Audit", "header"),
    ("caro_14a", "3(xiv)(a) — Internal audit system commensurate with the size and nature of the company's business", "item"),
    ("caro_14b", "3(xiv)(b) — Reports of the Internal Auditors for the period under audit considered by the statutory auditor", "item"),
    ("caro_h15", "Clause 3(xv) — Non-cash Transactions with Directors", "header"),
    ("caro_15a", "3(xv) — Non-cash transactions entered into with directors or persons connected with them; provisions of Section 192 of Companies Act complied with", "item"),
    ("caro_h16", "Clause 3(xvi) — RBI Registration / NBFC / CIC", "header"),
    ("caro_16a", "3(xvi)(a) — Company required to be registered under Section 45-IA of the RBI Act 1934; registration obtained", "item"),
    ("caro_16b", "3(xvi)(b) — Non-Banking Financial or Housing Finance activities conducted without a valid Certificate of Registration (CoR) from the RBI", "item"),
    ("caro_16c", "3(xvi)(c) — Company is a Core Investment Company (CIC) as defined in RBI regulations; continues to fulfil CIC criteria; exempted or unregistered CIC criteria fulfilled", "item"),
    ("caro_16d", "3(xvi)(d) — Group has more than one CIC as part of the Group; number of CICs in the Group indicated", "item"),
    ("caro_h17", "Clause 3(xvii) — Cash Losses", "header"),
    ("caro_17a", "3(xvii) — Cash losses incurred in the financial year and in the immediately preceding financial year; amount of cash losses stated", "item"),
    ("caro_h18", "Clause 3(xviii) — Resignation of Statutory Auditors", "header"),
    ("caro_18a", "3(xviii) — Resignation of statutory auditors during the year; issues, objections or concerns raised by the outgoing auditors taken into consideration", "item"),
    ("caro_h19", "Clause 3(xix) — Going Concern & Financial Ratios", "header"),
    ("caro_19a", "3(xix) — Based on financial ratios, ageing and expected dates of realisation of financial assets and payment of liabilities, and management plans, whether material uncertainty exists that company is capable of meeting liabilities within one year from the balance sheet date", "item"),
    ("caro_h20", "Clause 3(xx) — Corporate Social Responsibility (CSR)", "header"),
    ("caro_20a", "3(xx)(a) — Unspent CSR amount in respect of non-ongoing projects transferred to Fund specified in Schedule VII within six months of expiry of financial year; compliance with second proviso to Section 135(5)", "item"),
    ("caro_20b", "3(xx)(b) — Unspent CSR amount under ongoing projects transferred to special account as per Section 135(6) of Companies Act before 30th April of succeeding year", "item"),
    ("caro_h21", "Clause 3(xxi) — Qualifications in CARO Reports of Consolidated Entities", "header"),
    ("caro_21a", "3(xxi) — Qualifications or adverse remarks by respective auditors in CARO reports of companies included in consolidated financial statements; details of companies and paragraph numbers of CARO reports containing qualifications or adverse remarks", "item"),
]



# ── Financials Tab — Document Categories ──────────────────────────────────────
FINANCIALS_DOCS_STAT = [
    # Financial Statements
    ("fin_stat_bs",         "Balance Sheet",                                      "financials"),
    ("fin_stat_pl",         "Statement of Profit & Loss",                         "financials"),
    ("fin_stat_cf",         "Cash Flow Statement",                                "financials"),
    ("fin_stat_sce",        "Statement of Changes in Equity",                     "financials"),
    ("fin_stat_notes",      "Notes to Accounts",                                  "financials"),
    # Audit Reports
    ("fin_rep_main",        "Independent Auditor’s Report (Main)",                "reports"),
    ("fin_rep_caro",        "CARO 2020 Report",                                   "reports"),
    ("fin_rep_ifc",         "Report on Internal Financial Controls",              "reports"),
    ("fin_rep_tax",         "Tax Audit Report (Form 3CD / 3CB)",                  "reports"),
    ("fin_rep_mgt",         "Management Representation Letter",                   "reports"),
]

FINANCIALS_DOCS_TAX = [
    # Form 3CD & Audit Reports
    ("fin_tax_3cd",         "Form 3CD",                                           "reports"),
    ("fin_tax_3cb",         "Form 3CB / 3CA (Audit Report)",                      "reports"),
    ("fin_tax_3ceb",        "Form 3CEB (Transfer Pricing — if applicable)",         "reports"),
    ("fin_tax_mgtrep",      "Management Representation Letter",                   "reports"),
    # Financial Statements
    ("fin_fs_bs",           "Balance Sheet",                                      "financials"),
    ("fin_fs_pl",           "Profit & Loss Account",                              "financials"),
    ("fin_fs_notes",        "Notes / Schedules to Accounts",                      "financials"),
    ("fin_fs_tb",           "Trial Balance",                                      "financials"),
    # Tax Computations & Returns
    ("fin_tc_comp",         "Tax Computation Sheet",                              "tax"),
    ("fin_tc_itr",          "Income Tax Return (ITR)",                            "tax"),
    ("fin_tc_tds",          "TDS Returns (24Q, 26Q)",                             "tax"),
    ("fin_tc_gst",          "GST Returns (GSTR-1, 3B, 9, 9C)",                   "tax"),
    ("fin_tc_pf",           "PF / ESI Contribution Statements",                  "tax"),
    # Books & Supporting Records
    ("fin_bk_cash",         "Cash Book",                                          "records"),
    ("fin_bk_bank",         "Bank Statements & BRS",                              "records"),
    ("fin_bk_inv",          "Invoices & Vouchers (Sample)",                       "records"),
    ("fin_bk_depr",         "Depreciation Schedule",                              "records"),
    ("fin_bk_loan",         "Loan Accounts & Interest Workings",                  "records"),
    ("fin_bk_debtor",       "Debtors / Creditors Statements",                     "records"),
]

FINANCIALS_SECTION_LABELS = {
    "financials":  "📊  Financial Statements",
    "reports":     "📋  Audit Reports",
    "schedules":   "📂  Supporting Schedules",
    "tax":         "💰  Tax & Compliance",
    "secretarial": "📜  Board & Secretarial",
    "records":     "📁  Books & Records",
}


# ── Financials Tab — Additional Checklist Items ────────────────────────────────────
FIN_CHECKLIST_ITEMS = [
    ("fc_01", "Loans & advances made by the company on the basis of security — Whether loans/advances granted are adequately secured and the terms thereof are not prejudicial to the interest of the company or its members"),
    ("fc_02", "Transactions represented only by book entries — Whether transactions made by the company are represented merely by book entries, and whether such entries are supported by adequate documentation"),
    ("fc_03", "Sale of shares, debentures & other securities below purchase cost — Whether the company (other than an investment or banking company) has at any time during the year sold shares, debentures or other securities at a price below their purchase cost; if so, details disclosed"),
    ("fc_04", "Loans & advances disclosed as deposits — Whether any loans and advances made by the company have been shown as deposits in the books of account"),
    ("fc_05", "Personal expenses charged to revenue — Whether any personal expenses have been charged to revenue account of the company; if so, details thereof"),
    ("fc_06", "Receipt of share application money & allotment disclosure — Where shares have been allotted for cash, whether cash has actually been received and is properly disclosed in the balance sheet;"),
]

FIN_CL_STATUSES     = ["Not Checked", "Compliant", "Non-Compliant", "N/A"]
FIN_CL_STATUS_COLORS = {
    "Not Checked":   C["border"],
    "Compliant":     C["success"],
    "Non-Compliant": C["danger"],
    "N/A":           C["muted"],
}


# ── Schedule III Additional Disclosures Checklist ─────────────────────────────
SCH3_ITEMS = [
    ("s3h1",  "General Disclosures", "header"),
    ("s3_01", "Contingent Liability — Disclosed with nature, timing and financial effect per applicable standards", "item"),
    ("s3_02", "Other Commitments — Capital and other commitments not provided for in the accounts", "item"),
    ("s3_03", "Dividend proposed to be distributed — Amount per share and total proposed dividend disclosed", "item"),
    ("s3_04", "Arrears of fixed cumulative dividend on preference shares — Period and amount in arrears disclosed", "item"),
    ("s3_05", "Unutilized amounts in respect of issue of securities for specific purpose — Purpose, amount raised, utilised and balance disclosed", "item"),
    ("s3_06", "Borrowings from banks & financial institutions for specific purpose not so utilized — Purpose, original amount, utilised and balance disclosed", "item"),
    ("s3h2",  "Assets & Property", "header"),
    ("s3_07", "Director's statement on realisation of assets other than PPE & non-current investments — Statement that assets are realisable at the value stated in balance sheet", "item"),
    ("s3_08", "Title deeds of immovable property not held in the name of the company — Details of property, gross/net carrying value, reason and when acquired", "item"),
    ("s3_09", "Disclosure with regards to revaluation of PPE — Whether revalued during the year; if yes, basis of valuation and change in value disclosed", "item"),
    ("s3_10", "Ageing in relation to CWIP & intangible assets under development — Age-wise schedule in prescribed format disclosed", "item"),
    ("s3_11", "Disclosure with regard to overdue CWIP & intangible assets under development — Projects with cost overrun or completion beyond original plan disclosed", "item"),
    ("s3h3",  "Related Parties & Governance", "header"),
    ("s3_12", "Disclosure of loans given to promoter, director, KMP & related party — Amount, purpose, whether repaid and outstanding at year end", "item"),
    ("s3_13", "Disclosure with regards to benami property — Any proceedings pending under Benami Transactions (Prohibition) Act, 1988 disclosed", "item"),
    ("s3_14", "Disclosure with regards to wilful defaulter — Whether the company has been declared a wilful defaulter by any bank or financial institution", "item"),
    ("s3_15", "Relationship with struck off companies — Transactions with companies struck off under Section 248 of Companies Act 2013 disclosed", "item"),
    ("s3h4",  "Compliance & Regulatory", "header"),
    ("s3_16", "Registration & satisfaction of charge with ROC — Pending registration or satisfaction of charges disclosed with amount and details", "item"),
    ("s3_17", "Compliance with number of layers of company — Whether company has complied with Section 2(87) and Companies (Restriction on Number of Layers) Rules, 2017", "item"),
    ("s3_18", "Compliance with approved scheme of arrangement (Merger/demerger etc.) — Every element of scheme of arrangement given effect to in books", "item"),
    ("s3h5",  "Financial Ratios & Utilisation", "header"),
    ("s3_19", "11 number of ratios with explanation where change is more than 25% of PY — Current Ratio, Debt-Equity, Debt Service Coverage, Return on Equity, Inventory Turnover, Trade Receivables Turnover, Trade Payables Turnover, Net Capital Turnover, Net Profit Ratio, Return on Capital Employed, Return on Investment disclosed with explanations", "item"),
    ("s3_20", "Utilisation of borrowed funds & share premium — Where funds are borrowed and used for purposes other than the stated purpose; any round-tripping disclosed", "item"),
    ("s3_21", "Utilisation of funds advanced or investments — Where company has advanced funds or investments and the recipient has used funds for purposes other than stated", "item"),
    ("s3h6",  "Other Disclosures", "header"),
    ("s3_22", "Undisclosed income — Any income surrendered or disclosed as income during the year in tax assessments; whether previously unrecorded in books", "item"),
    ("s3_23", "CSR disclosure — Amount required to be spent, amount spent, amount unspent; details of ongoing and other projects as applicable", "item"),
    ("s3_24", "Crypto currency & virtual currency — Whether the company has traded or invested in crypto/virtual currency; if yes, profit/loss, amount held and deposits/advances disclosed", "item"),
]

SCH3_STATUSES     = ["Not Checked", "Compliant", "Non-Compliant", "N/A"]
SCH3_STATUS_COLORS = {
    "Not Checked":   C["border"],
    "Compliant":     C["success"],
    "Non-Compliant": C["danger"],
    "N/A":           C["muted"],
}


# ── ICAI Guidance Notes ────────────────────────────────────────────────────────
ICAI_GUIDANCE_NOTES = [
    {
        "section": "Key Guidance Notes",
        "icon": "📌",
        "items": [
            ("Guidance Note on Tax Audit under Section 44AB of the Income-tax Act, 1961 (Revised 2023)",
             "https://resource.cdn.icai.org/75812dtc61332.pdf"),
            ("Guidance Note on Report Under Section 92E of the Income-Tax Act, 1961 (Transfer Pricing) (Revised 2022)",
             "https://resource.cdn.icai.org/71914citax251022.pdf"),
            ("Guidance Note on the Companies (Auditor’s Report) Order, 2020 (Revised 2022 Edition)",
             "https://resource.cdn.icai.org/70956aasb56965.pdf"),
            ("Guidance Note on Audit of Internal Financial Controls Over Financial Reporting",
             "https://resource.cdn.icai.org/39249aasb28733.pdf"),
            ("Revised Guidance Note on Reporting on Fraud under Section 143(12) of the Companies Act, 2013",
             "https://resource.cdn.icai.org/41297aasb-gn-fraud-revised.pdf"),
        ],
    },
    {
        "section": "Audit Reports & Certificates",
        "icon": "📋",
        "items": [
            ("Guidance Note on Reports or Certificates for Special Purposes (Revised 2016)",
             "https://resource.cdn.icai.org/43452aasb-gn-rcsp.pdf"),
            ("Guidance Note on Reports in Company Prospectuses (Revised 2019)",
             "https://resource.cdn.icai.org/53704aasb43145a.pdf"),
            ("Guidance Note on Reporting under Section 143(3)(f) and (h) of the Companies Act, 2013",
             "https://resource.cdn.icai.org/37392aasb26881.pdf"),
            ("Guidance Note on Audit of Consolidated Financial Statements (Revised 2016)",
             "https://resource.cdn.icai.org/43577aasb-gncfs171016.pdf"),
            ("Certificate on Corporate Governance (Revised)",
             "https://resource.cdn.icai.org/57066aasb46101-14.pdf"),
        ],
    },
    {
        "section": "Audit of Balance Sheet Items",
        "icon": "📊",
        "items": [
            ("Audit of Property, Plant and Equipment",
             "https://resource.cdn.icai.org/57053aasb46101-1.pdf"),
            ("Audit of Cash and Bank Balances",
             "https://resource.cdn.icai.org/57055aasb46101-3.pdf"),
            ("Audit of Debtors, Loans and Advances",
             "https://resource.cdn.icai.org/57056aasb46101-4.pdf"),
            ("Audit of Inventories",
             "https://resource.cdn.icai.org/57058aasb46101-6.pdf"),
            ("Audit of Investments",
             "https://resource.cdn.icai.org/57059aasb46101-7.pdf"),
            ("Audit of Liabilities",
             "https://resource.cdn.icai.org/57060aasb46101-8.pdf"),
            ("Capital and Reserves",
             "https://resource.cdn.icai.org/57065aasb46101-13.pdf"),
        ],
    },
    {
        "section": "Audit of P&L Items",
        "icon": "💰",
        "items": [
            ("Audit of Revenue",
             "https://resource.cdn.icai.org/57063aasb46101-11.pdf"),
            ("Audit of Expenses",
             "https://resource.cdn.icai.org/57057aasb46101-5.pdf"),
            ("Audit of Payment of Dividend",
             "https://resource.cdn.icai.org/57062aasb46101-10.pdf"),
            ("Audit of Miscellaneous Expenditure (Revised)",
             "https://resource.cdn.icai.org/57061aasb46101-9.pdf"),
        ],
    },
    {
        "section": "Industry Specific",
        "icon": "🏦",
        "items": [
            ("Guidance Note on Audit of Banks (2025 Edition)",
             "https://www.icai.org/post/guidance-note-on-audit-of-banks-2025-edition"),
            ("Guidance Note on Audit of Banks (2024 Edition)",
             "https://www.icai.org/post/guidance-note-on-audit-of-banks-2024-edition"),
            ("Guidance Note on Audit of Banks (2023 Edition)",
             "https://www.icai.org/post/guidance-note-on-audit-of-banks-2023-edition"),
            ("Audit of Accounts of Non-Corporate Entities (Bank Borrowers)",
             "https://resource.cdn.icai.org/57054aasb46101-2.pdf"),
            ("Audit of Accounts of Members of Stock Exchanges (Revised)",
             "https://resource.cdn.icai.org/13647Link%2033.pdf"),
            ("Audit of Companies Carrying on General Insurance Business",
             "https://resource.cdn.icai.org/13648Link%2034.pdf"),
            ("Audit of Companies Carrying on Life Insurance Business",
             "https://resource.cdn.icai.org/13649Link%2035.pdf"),
        ],
    },
    {
        "section": "Technology & Other Aspects",
        "icon": "💻",
        "items": [
            ("Computer Assisted Audit Techniques (CAATs)",
             "https://resource.cdn.icai.org/57069aasb46101-17.pdf"),
            ("Certification of XBRL Financial Statements",
             "https://resource.cdn.icai.org/24637gnotes_xbrl.pdf"),
            ("Duty Cast on the Auditors under Section 45-MA of the Reserve Bank of India Act, 1934",
             "https://resource.cdn.icai.org/57070aasb46101-18.pdf"),
            ("Preparation of Financial Statements on Letterheads and Stationery of Auditors",
             "https://resource.cdn.icai.org/57072aasb46101-20.pdf"),
        ],
    },
]


# ── Other Resources (Statutory Audit) ──────────────────────────────────────────────────────
OTHER_RESOURCES_STAT = [
    {
        "section": "Indian Accounting Standards (Ind AS)",
        "icon": "\U0001f1ee\U0001f1f3",
        "source_url": "https://www.icai.org/post/indian-accounting-standards-indas",
        "items": [
            ("Release of Indian Accounting Standards (Ind AS): An Overview (Revised 2023)",
             "https://www.icai.org/post/indas-revised-2023", "WEB"),
            ("Compendium of Indian Accounting Standards and Ind AS Guidance Material",
             "https://www.icai.org/post/compendium-of-indian-accounting-standards-and-ind-as-guidance-material", "WEB"),
            ("Conceptual Framework Under Indian Accounting Standards (Ind AS)",
             "https://indasaccess.icai.org/download/2021/asb072021/590/590asb53118a.pdf", "PDF"),
            ("Framework for the Preparation and Presentation of Financial Statements (Ind AS)",
             "https://resource.cdn.icai.org/82617asb66726.pdf", "PDF"),
            ("Notified Ind AS in Hindi (compiled as on 28.02.23)",
             "https://www.icai.org/post/asb-indas-hindi-280223", "WEB"),
            ("Companies (Indian Accounting Standards) Rules notified by Central Government",
             "https://www.icai.org/post.html?post_id=12125", "WEB"),
            ("Educational Materials on Ind AS",
             "https://www.icai.org/post/8202", "WEB"),
            ("ITFG Clarification Bulletins (including Compendium)",
             "https://www.icai.org/post/12745", "WEB"),
            ("Quick Referencer on Indian Accounting Standards",
             "https://www.icai.org/post/16094", "WEB"),
            ("IFRIC Agenda Decisions (IFRS Foundation)",
             "https://www.ifrs.org/supporting-implementation/supporting-materials-by-ifrs-standards/#ifrs-standards", "WEB"),
        ],
    },
    {
        "section": "Accounting Standards (AS)",
        "icon": "\U0001f4d8",
        "source_url": "https://www.icai.org/post/accounting-standards-as",
        "items": [
            ("Accounting Standards as on April 1, 2025 — HTML Version",
             "https://indasaccess.icai.org/Volume-III-25-26/AS/volume-III.html", "WEB"),
            ("Accounting Standards as on April 1, 2025 — PDF Version",
             "https://www.icai.org/www.icai.org/post/accounting-standards-as-on-april2025", "PDF"),
            ("Amendments to AS 22 — Accounting for Taxes on Income (Non-company entities)",
             "https://www.icai.org/post/amendments-to-as22-nce", "WEB"),
            ("Accounting Standards as on February 1, 2022 — HTML Version",
             "https://www.icai.org/volume-III.html", "WEB"),
            ("Accounting Standards as on February 1, 2022 — PDF Version",
             "https://www.icai.org/www.icai.org/post/accounting-standards-as-on-1stfeb2022", "PDF"),
            ("Accounting Standards as on July 1, 2019",
             "https://resource.cdn.icai.org/56169asb45450.pdf", "PDF"),
            ("Accounting Standards as on July 1, 2017",
             "https://resource.cdn.icai.org/46901asb36689asb-compendium.pdf", "PDF"),
            ("Framework for the Preparation and Presentation of Financial Statements (AS)",
             "https://resource.cdn.icai.org/89089asb-aps2918-framework.pdf", "PDF"),
            ("Preface to the Statements of the Accounting Standards",
             "https://resource.cdn.icai.org/89088asb-aps2918-preface.pdf", "PDF"),
            ("Companies (Accounting Standards) Rules — Notified by the Central Government",
             "https://www.icai.org/post.html?post_id=3610", "WEB"),
            ("Companies (Accounting Standards) Rules, 2021 (MCA Notification)",
             "https://mca.gov.in/bin/dms/getdocument?mds=RKk43Bmg99ksfV0bUGr6XA%253D%253D&type=open", "WEB"),
        ],
    },
]

# ── Pre-Audit Document Templates (base64-encoded) ─────────────────────────────
PAD_TEMPLATES = {
    "letter_seeking_consent": (".docx", "UEsDBBQABgAIAAAAIQDfpNJsWgEAACAFAAATAAgCW0NvbnRlbnRfVHlwZXNdLnhtbCCiBAIooAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC0lMtuwjAQRfeV+g+Rt1Vi6KKqKgKLPpYtUukHGHsCVv2Sx7z+vhMCUVUBkQpsIiUz994zVsaD0dqabAkRtXcl6xc9loGTXmk3K9nX5C1/ZBkm4ZQw3kHJNoBsNLy9GUw2ATAjtcOSzVMKT5yjnIMVWPgAjiqVj1Ykeo0zHoT8FjPg973eA5feJXApT7UHGw5eoBILk7LXNX1uSCIYZNlz01hnlUyEYLQUiep86dSflHyXUJBy24NzHfCOGhg/mFBXjgfsdB90NFEryMYipndhqYuvfFRcebmwpCxO2xzg9FWlJbT62i1ELwGRztyaoq1Yod2e/ygHpo0BvDxF49sdDymR4BoAO+dOhBVMP69G8cu8E6Si3ImYGrg8RmvdCZFoA6F59s/m2NqciqTOcfQBaaPjP8ber2ytzmngADHp039dm0jWZ88H9W2gQB3I5tv7bfgDAAD//wMAUEsDBBQABgAIAAAAIQAekRq37wAAAE4CAAALAAgCX3JlbHMvLnJlbHMgogQCKKAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAArJLBasMwDEDvg/2D0b1R2sEYo04vY9DbGNkHCFtJTBPb2GrX/v082NgCXelhR8vS05PQenOcRnXglF3wGpZVDYq9Cdb5XsNb+7x4AJWFvKUxeNZw4gyb5vZm/cojSSnKg4tZFYrPGgaR+IiYzcAT5SpE9uWnC2kiKc/UYySzo55xVdf3mH4zoJkx1dZqSFt7B6o9Rb6GHbrOGX4KZj+xlzMtkI/C3rJdxFTqk7gyjWop9SwabDAvJZyRYqwKGvC80ep6o7+nxYmFLAmhCYkv+3xmXBJa/ueK5hk/Nu8hWbRf4W8bnF1B8wEAAP//AwBQSwMEFAAGAAgAAAAhAJGlt0qCBgAAoC0AABEAAAB3b3JkL2RvY3VtZW50LnhtbOxabXPaOBD+fjP3HzT+eNPEFubNTKGDA2QyN+1lQm7ar8IW2I1tuZIM4X79reQXSEhaQ9omZMIHbEnWo9Xus6uV7PcfbuMILSkXIUv6Bj61DEQTj/lhsugb/15PTroGEpIkPolYQvvGmgrjw+DPP96vej7zspgmEgFEInqr1OsbgZRpzzSFF9CYiNM49DgTbC5PPRabbD4PPWquGPfNhoUtfZdy5lEhYLwzkiyJMAo477Yems/JCjorwKbpBYRLervBwHuDtEzH7O4CNQ4Aghk28C6UvTdU21RS7QA1DwICqXaQWochPTC59mFIjV2kzmFI9i5S9zCkHTrFuwRnKU2gcc54TCQU+cKMCb/J0hMATokMZ2EUyjVgWu0ShoTJzQESQa8KIbb9vRE6Zsx8Gtl+icL6RsaTXtH/pOqvRO/l/YtL1YNG9YaF4RyT3spIyLIvr6O7vPuoCCxaayanEeiRJSII0yo6xIeiQWNQgiy/p4BlHJXPrVJc09UeC22j3AwbwDriF7aLo1zy7yNiq4Y1FUTVo44Id8csJYmBwZuBD1LNlnJxzeBTAjR2ANoerblYlBjdAsP0Nt6tcMKablXi5FZROOFGsbhmDLwvzBaA8KUf7IXSKPVqqr5EkoCIiugKke4nVKuCW8dbOkoXT3OEc86ydIMWPg3tYhMSVyo52QOrcKhtJxdPE2YakBQiZez1LhYJ42QWgUTgHggYjrQF1D8QRV30Lb3V9crWSMUYYwBZ1Yz5a3VNoa3ZSwknF0BKbLcbeIyxoWthTZKqtlP8oLYHGZx/1Tcsq2XZjYZVVV3yBypHdE6ySG616CEvub5M5ToCYXtLAuH+kwoH0Wc6M0zVyPNnxH9lO+6qBrNoMSsU/qAAWxB8whIp4CkivBCI4DJ2g4aJDL9lRAkaDBNxv1qL4LGIKXQ9vKV/ecN9oaAm8MsqL6KEK1zdvW+QTDJVnIcRtE7gl8OUM1n15GBEJFUVMq/Op7drHLBN155Y4zfj7GGcjZ5nXD8gB9fsjrJriPk4qN6V9ERKPPDClFNB+ZIaA1TDnE1sddxRVxnkzZy/zdcmIY/RJxLXcbi2NRkNrfGbw/1+Cw19H5xJ1DBSZ4TtYdNxjsVIj8yi5YzbEy3Ha6XaOYVUP9xmWVlzaER/JPj+HSY+GkoJmzHYz/XuxuJnFPzJnqHCFmJzdEm4TCiv4RytIYYAZrlvtPrV1tHZxbNTbJst02z2lXqyh6aU3sDGAZ2xRKhzVALuMY7CRXFohCIKvsIRbMgRSVMWJlIftxKhTmQlzJyvEcn8EG6Eop8MKNLHTskanaAruqhBRBsitOO4z0/Er15lY5gk5T+bnntHq7+qX52k0bKHbmfkPv8GbaPHGZPB8aUpP7TLNbDcZYT7ivKjkIMrPcD/MNFF8B0ZQJ1ys4+USnWNiWpWnkWikEAPENlXpY2PmZxuexxgTyuPG5YeB37I6bcMJPBRliiEKcgCKxvCtlPKc6blCalAQ0++Qw0L22jOWVwIm3hRpl69lI8/dUl8gWnjly8vb1I/JBngJhmJ0DmF9RyuJXcke8Bwb0Z70UY7rRG+2y0Luw27fczh+5GFaYTHQ7vVfFuYfh79Bp9hkiyLfL0AUCHRmmUqNqTgakKHhyVdq0pABi8DEiawadYJHt1K8KDHjJbrDqwisKKo6LKz1txdTNa1CO22zzqu0319hLbds3HbbTbeCP0rCE0iwR5hdcrZEhIllOUs9SiX4Tz0iKRbeZApEG7i72Y/is/gGJC4Me6LOmTudCctp9GyXx+ZO5OJ28buUc/sxZH5Mucr7KmBzzq/L3fX28G32F0LldERiVZUh2ogO2QVmrxCneoothYZn94l6E8RSnrP9DZEAXO6BHcABBnoFp96oU4PAVmVIQOLwA1krdDtjC2M26PXx/ZW03I6HXz27DM7VmZfByTRR0YQmd/VoJI1bLit7gsInEeq8If3GRPAuaP8OmLf0c5UcpYsCtW8/N1gkXfWfT1nu+MuxuOjYd0jwQpbNsaTo3l/9dJ8ZzC6uBqfXf9z9SBjBPXkZSVwTSWq87X7ClxMlQgrEAA7ljZLAPftru3kEqaLj0SNI1naNxwrxwoXgVSvkXUJFjfJ4qoY0fmmLaAEFn0wey7EnDG5VVxkKoUAiSotKeUW8UI9o6t95p1z9dlPDzaC9DKUXqC+GSm9LNeEvs2//TE3n1YP/gcAAP//AwBQSwMEFAAGAAgAAAAhANZks1H0AAAAMQMAABwACAF3b3JkL19yZWxzL2RvY3VtZW50LnhtbC5yZWxzIKIEASigAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAArJLLasMwEEX3hf6DmH0tO31QQuRsSiHb1v0ARR4/qCwJzfThv69ISevQYLrwcq6Yc8+ANtvPwYp3jNR7p6DIchDojK971yp4qR6v7kEQa1dr6x0qGJFgW15ebJ7Qak5L1PWBRKI4UtAxh7WUZDocNGU+oEsvjY+D5jTGVgZtXnWLcpXndzJOGVCeMMWuVhB39TWIagz4H7Zvmt7ggzdvAzo+UyE/cP+MzOk4SlgdW2QFkzBLRJDnRVZLitAfi2Myp1AsqsCjxanAYZ6rv12yntMu/rYfxu+wmHO4WdKh8Y4rvbcTj5/oKCFPPnr5BQAA//8DAFBLAwQUAAYACAAAACEAlKlShtQGAADHIAAAFQAAAHdvcmQvdGhlbWUvdGhlbWUxLnhtbOxZW4sbNxR+L/Q/iHl3PDP2+BLiLb42TXaTkN2k9FFryzOKNaNBkndjQqCkT30pFNrShwb61odSGmihpS/9MQsJvfyISpqxZ2RrmtumhLJrWI+k7xx9Oufo6Fhz5b37MQEniHFMk57jXXIdgJIpneEk7Dl3jia1jgO4gMkMEpqgnrNC3Hlv7913rsDLIkIxAlI+4Zdhz4mESC/X63wquyG/RFOUyLE5ZTEUssnC+ozBU6k3JnXfdVv1GOLEAQmMpdqb8zmeInCkVDp7a+VjIv8lgquOKWGHSjUyJDR2tvDUF1/xIWHgBJKeI+eZ0dMjdF84gEAu5EDPcfWfU9+7Ut8IEVEhW5Kb6L9cLheYLXwtx8LjjaA79jtNb6NfA4jYxY076rPRpwFwOpUrzbiUsV7Qcjt+ji2BskeL7m7ba5j4kv7Grv5ua+A3DbwGZY/N3TVOuuNRYOA1KHsMdvB91x90GwZeg7LH1g6+Oe63/bGB16CI4GSxi261O51Wjt5A5pRctcK7rZbbHuXwAlUvRVcmn4iqWIvhPcomEqCdCwVOgFilaA6nEtdPBeVghHlK4MoBKUwol92u73ky8Jquv/loi8PLCJaks64p3+lSfACfMpyKnnNNanVKkKe//nr26OezR7+cffLJ2aMfwT4OI2GRuwqTsCz313ef//34Y/DnT9/+9cWXdjwv45/98Omz337/N/XCoPXVk2c/P3n69Wd/fP+FBd5n8LgMP8Ix4uAGOgW3aSwXaJkAHbOXkziKIC5L9JOQwwQqGQt6LCIDfWMFCbTgBsi0410m04UN+P7ynkH4MGJLgS3A61FsAA8oJQPKrGu6ruYqW2GZhPbJ2bKMuw3hiW3u4ZaXx8tUxj22qRxGyKB5i0iXwxAlSAA1RhcIWcQ+wtiw6wGeMsrpXICPMBhAbDXJET42oqkQuopj6ZeVjaD0t2Gbg7tgQIlN/QidmEi5NyCxqUTEMOP7cClgbGUMY1JG7kMR2UgertjUMDgX0tMhIhSMZ4hzm8xNtjLoXocyb1ndfkBWsYlkAi9syH1IaRk5oothBOPUyhknURn7AV/IEIXgFhVWEtTcIaot/QCTSnffxchw9/P39h2ZhuwBokaWzLYlEDX344rMIbIp77PYSLF9hq3RMViGRmjvI0TgKZwhBO58YMPT1LB5QfpaJLPKVWSzzTVoxqpqJ4jLWkkVNxbHYm6E7CEKaQWfg9VW4lnBJIasSvONhRky42MmN6MtXsl0YaRSzNSmtZO4yWNjfZVab0XQCCvV5vZ4XTHDfy+yx6TMvVeQQS8tIxP7C9vmCBJjgiJgjiAG+7Z0K0UM9xciajtpsaVVbm5u2sIN9a2iJ8bJcyqg/67ykfXF028eW7DnU+3Yga9T51Slku3qpgq3XdMMKZvht7+kGcFlcgvJU8QCvahoLiqa/31FU7WfL+qYizrmoo6xi7yBOqYoXfQF0PqaR2uJK+985piQQ7EiaJ/roofLvT+byE7d0EKbK6Y0ko/5dAYuZFA/A0bFh1hEhxFM5TSeniHkueqQg5RyWTjpbqtuNUCW8QGd5Td4qsLSt5pSAIqi3w02/bJIE1lvq11cgW7U61aor1nXBJTsy5AoTWaSaFhItNedzyGhV3YuLLoWFh2lvpKF/sq9Ig8nANWFeNDMGMlwkyE9U37K5NfePXdPVxnTXLZvWV5XcT0fTxskSuFmkiiFYSQPj+3uc/Z1t3CpQU+ZYpdGu/MmfK2SyFZuIInZAqdyzzUCqWYK054zlz+Y5GOcSn1cZSpIwqTnTEVu6FfJLCnjYgR5lMH0ULb+GAvEAMGxjPWyG0hScPP8tlrjW0qu6759ltNfZSej+RxNRUVP0ZRjmRLr6GuCVYMuJenDaHYKjsmS3YbSUEHbUwacYS421pxhVgruwopb6Srfisa7n2KLQpJGMD9Rysk8g+vnDZ3SOjTT7VWZ7Xwxx6Fy0mufus8XUgOlpFlxgKhT054/3twhX2JV5H2DVZa6t3Ndd53rqk6J1z8QStSKyQxqirGFWtFrUjvHgqA03SY0q86I8z4NtqNWHRDrulK3dl5r0+N7MvJHslpdEsE1VfmrhcHh+oVklgl07zq73BdgyXDPeeAG/ebQD4Y1txOMa81G0611gn6j1g+ChjcOPHc08B9Ko4go9oJs7on8sU9W+Vt73b/z5j5el9qXpjSuU10H17WwfnPv+dVv7gGWlnngj72m3/eHteHIa9Wa/qhV67Qb/drQb438vkxCrUn/oQNONNgbjEaTSeDXWkOJa7r9oNYfNIa1Vmc88CfeuDlyJThPhvfz9JHbYm3QvX8AAAD//wMAUEsDBBQABgAIAAAAIQAO2J68FgQAAMUKAAARAAAAd29yZC9zZXR0aW5ncy54bWykVttu2zgQfV9g/8HQ8zq6RFIToU7hJE3j3WS3iBPkmRIpiwgvAkn5sov+e4eUaDlNUSTZF5uaM3NmOBwe6eOnLWeTNVGaSjEL4qMomBBRSUzFahY83F9NT4KJNkhgxKQgs2BHdPDp7PffPm4KTYwBNz0BCqELXs2Cxpi2CENdNYQjfSRbIgCspeLIwKNahRypp66dVpK3yNCSMmp2YRJFeTDQyFnQKVEMFFNOKyW1rI0NKWRd04oMfz5CvSZvH3Ipq44TYVzGUBEGNUihG9pqz8bfywZg40nWv9rEmjPvt4mjV2x3IxXeR7ymPBvQKlkRreGAOPMFUjEmTl8Q7XMfQe5hi44KwuPIrQ4rz95GkLwgyCuyfRvHycARQuQhD8Vv48n3PHRsbJy/r5gDAo0Nbt7Ekvi+hjYWGdQgvZ8iy0jeVlS2p9vxsUeavWZqeuiGlgqp/k4OI8OrYrESUqGSQTkwOhM4/Ymrzv5CE+2fW5Kts9s+BGegEf9KySeboiWqgosCAhNFQWgBTGrUMXOPyqWRLbisERT5IRlgIb92ojKdu59/ESVgjh1QNUihyhC1bFEFxgspjJLME2D5tzQXIC4KZr+n6qXG5bTgUqD2Xn5RFC/EBWGsr8YijwoQsjWP1DQu+wg9aPIZaTPXFIlzRdDTXceIdvhKyc28M7KmvX+fbtlrI5QlEIemPdO7W4lBvDZFp+jrT9cGuC3G2eG+fkyEaV0TBb2myJBb6DCF+u7tyV0ThEHn/0fiX+XtNHkEZxjB43s4oKdzaYzk17u2IcId4vvzupEIDw8S3lZY+8WdlGbvGmXRceKHyKI/Q8I9Ay+san9VfnUF0zThfcQF4qWiaHJrdT20HqV6OqfC4yWBy0MOkWVXenA67QHNEWNX0BAPuAJ4galuL0nt1uwWqdXIO3ion1rh2vy557JXiqgvSnZtj25gghcCk3ETcZoOkVSYG8q9XXfl0kcJuO4HUCfwP2vl+jS2Z1MYOC5i+3OD3LE7XyKmD8thLJha2iMlt6ht+8koV/EsYHTVmNgepoEnDK9/91CukgFLHJb0mHtAld0ZeA+L0ZZ424Hfsbcdj7bU29LRlnlbNtpyb8utrdmBTjEqnmBI/dLaa8mY3BB8PeIvTIOqWbFYiIp1mMA0YFnphVgaUFgH6wa15LJXPpg+2RsGKdSTdQHqA03F1MBHV0sxR1srmUlu2QdvhnayM898LWad2+cM9nUy3NrwWbC7AT/UYhW5ojCtyx0vRz096vfFqIYb34L0Gqk89ofD4hR2XS3sKyDt7fn883GaZ71cxJmTbONEAcbijtTnSBM8YD4060P/S9IsTU9OT6bzeJ5P09M8ns4vo3gaXZycplGWXs7zD9+GO+y/P8++AwAA//8DAFBLAwQUAAYACAAAACEAbcBEwu8LAAC1dQAADwAAAHdvcmQvc3R5bGVzLnhtbMSdXXPbuhGG7zvT/8DRVXuRyN9OPMc54zhO42mc+ER2cw2RkIWaJFSCjO3z6wuCkARpCYoLbt2bxJK4DwG8eJdYkqJ++/05S6NfvFBC5uej/bd7o4jnsUxE/nA+ur/7/ObdKFIlyxOWypyfj164Gv3+4a9/+e3pTJUvKVeRBuTqLIvPR/OyXJyNxyqe84ypt3LBc/3hTBYZK/XL4mGcseKxWryJZbZgpZiKVJQv44O9vZORxRR9KHI2EzH/JOMq43lp4scFTzVR5mouFmpJe+pDe5JFsihkzJXSnc7Shpcxka8w+0cAlIm4kErOyre6M7ZFBqXD9/fMX1m6BhzjAAcAcBLzZxzjnWWMdaTLEQmOc7LiiMThhDXGAaikTOYoysFyXMd1LCvZnKm5S+S4Rh2vcC9ZPUZZfHb9kMuCTVNN0qpHWrjIgOt/df/r/8yf/Nm8X3dh9EF7IZHxJz5jVVqq+mVxW9iX9pX577PMSxU9nTEVC3E+uhOZts83/hT9kBnTs+3pjDNVXijBWj+cX+SqPSxW8O1xvcuU5Q/6818sPR/x/M39ZHMnq7emItFkVryZXNSBY9vm5n+nJ4vVq2arrW5rC2pDTpq8oD/ls68yfuTJpNQfnI/26l3pN++vbwshC+3989H79/bNCc/EF5EkPHc2zOci4T/nPL9XPFm//8dn41/7RiyrXP99eHpipEhVcvUc80WdDfSnOcv0rr/VAWm9dSXWOzfh/1nC9u2YtcXPOatTYrS/jTDNRyEO6gjl9LadWW313WyF2tHha+3o6LV2dPxaOzp5rR2dvtaO3r3Wjgzmf7kjkSc6+5rt4W4AdRfH40Y0x2M2NMfjJTTHYxU0x+MENMcz0dEczzxGczzTFMEpZeybhc5kP/TM9m7u7mNEGHf3ISGMu/sIEMbdnfDDuLvzexh3dzoP4+7O3mHc3ckaz22WWtG1tlleDnbZTMoylyWPSv48nMZyzTJ1Ig2vPujxgqSTBJgms9kD8WBazMzr3TPEmDT8eF7W5VYkZ9FMPFQFV4MbzvNfPNWFfsSSRPMIgQUvq8IzIiFzuuAzXvA85pQTmw6aipxHeZVNCebmgj2QsXieEA/fkkiSFFYTmlXlvDaJIJjUGYsLObxpkpHlh69CDR+rGhJ9rNKUE7G+0UwxwxpeGxjM8NLAYIZXBgYzvDBwNKMaIksjGilLIxowSyMat2Z+Uo2bpRGNm6URjZulDR+3O1GmJsW7q479/ufuLlNZn9kf3I6JeMiZXgAMP9zYc6bRLSvYQ8EW86g+NdyOdfuM3c9HmbxEdxTHtBWJal1vpsil7rXIq+EDukGjMteKR2SvFY/IYCvecIvd6GVyvUD7QlPPTKpp2WpaQ+pl2glLq2ZBO9xtrBw+w9YG+CwKRWaDdizBDP5WL2drOSky37qVwxu2Zg231XZWIm2eRRK0MpXxI00a/vKy4IUuyx4Hkz7LNJVPPKEjTspCNnPNtfyBkaSX5a+yxZwpYWqlDUT/Q/3ynoDohi0Gd+g2ZSKn0e3qTcZEGtGtIL7c3XyN7uSiLjPrgaEBfpRlKTMypj0T+LeffPp3mgZe6CI4fyHq7QXR6SEDuxQEB5mGJBMikl5milyQHEMN75/8ZSpZkdDQbgve3IZTciLihGWLZtFB4C2dF590/iFYDRnev1gh6vNCVKa6I4E5pw1VNf03j4enum8yIjkz9L0qzflHs9Q10XS44cuEDdzwJYJRUx8e6vlL0NkN3PDObuCoOnuZMqWE9xJqMI+qu0sedX+HF3+WJ1NZzKqUbgCXQLIRXALJhlCmVZYryh4bHmGHDY+6v4RTxvAITskZ3j8KkZCJYWBUShgYlQwGRqWBgZEKMPwOHQc2/DYdBzb8Xp0GRrQEcGBU84z08E90lceBUc0zA6OaZwZGNc8MjGqeHX6K+GymF8F0hxgHSTXnHCTdgSYvebaQBSteiJBXKX9gBCdIG9ptIWf19zNk3tzETYCsz1GnhIvtBkcl8k8+JWtazaJsF8EZUZamUhKdW1sfcEzk5r1ru8Lu5jwbXkbfpizmc5kmvPD0yR+r6+XJgsX2ND243NfrtOdX8TAvo8l8dbbfxZzs7YxcFuwbYbt32DbmJwcdYTc8EVW2bCj8MsXJYf9gM6M3go92B69XEhuRxz0j4T5PdkeuV8kbkac9I+E+3/WMND7diOzywydWPLZOhNOu+bOq8TyT77RrFq2CW3fbNZFWkW1T8LRrFm1YJbqI4/pqAVSnn2f88f3M44/HuMhPwdjJT+ntKz+iy2A/+C9RH9kxSdPsb3X3BMj7ZhHdK3P+UcnmvP3GBaf+X+q61gunXPGolXPY/8LVRpbxj2PvdONH9M47fkTvBORH9MpE3nBUSvJTeucmP6J3kvIj0NkKHhFw2QrG47IVjA/JVpASkq0GrAL8iN7LAT8CbVSIQBt1wErBj0AZFYQHGRVS0EaFCLRRIQJtVLgAwxkVxuOMCuNDjAopIUaFFLRRIQJtVIhAGxUi0EaFCLRRA9f23vAgo0IK2qgQgTYqRKCNataLA4wK43FGhfEhRoWUEKNCCtqoEIE2KkSgjQoRaKNCBNqoEIEyKggPMiqkoI0KEWijQgTaqM1XDcONCuNxRoXxIUaFlBCjQgraqBCBNipEoI0KEWijQgTaqBCBMioIDzIqpKCNChFoo0IE2qjmYuEAo8J4nFFhfIhRISXEqJCCNipEoI0KEWijQgTaqBCBNipEoIwKwoOMCiloo0IE2qgQ0TU/7SVK3232+/iznt479vtfurKN+uF+ldtFHfZHLVvlZ/X/LsJHKR+j1i8eHpp6ox9ETFMhzSlqz2V1l2tuiUBd+Px+2f0NH5c+8KFL9rsQ5popgB/1jQTnVI66prwbCYq8o66Z7kaCVedRV/Z1I8Fh8Kgr6RpfLm9K0YcjENyVZpzgfU94V7Z2wuEQd+VoJxCOcFdmdgLhAHflYyfwOKqT83b0cc9xOlndXwoIXdPRIZz6CV3TEmq1TMfQGH1F8xP6qucn9JXRT0Dp6cXghfWj0Ar7UWFSQ5thpQ43qp+AlRoSgqQGmHCpISpYaogKkxomRqzUkICVOjw5+wlBUgNMuNQQFSw1RIVJDQ9lWKkhASs1JGClHnhA9mLCpYaoYKkhKkxquLjDSg0JWKkhASs1JARJDTDhUkNUsNQQFSY1qJLRUkMCVmpIwEoNCUFSA0y41BAVLDVEdUltzqJsSI1S2AnHLcKcQNwB2QnEJWcnMKBacqIDqyWHEFgtQa2WmuOqJVc0P6Gven5CXxn9BJSeXgxeWD8KrbAfFSY1rlpqkzrcqH4CVmpcteSVGlctdUqNq5Y6pcZVS36pcdVSm9S4aqlN6vDk7CcESY2rljqlxlVLnVLjqiW/1LhqqU1qXLXUJjWuWmqTeuAB2YsJlxpXLXVKjauW/FLjqqU2qXHVUpvUuGqpTWpcteSVGlctdUqNq5Y6pcZVS36pcdVSm9S4aqlNaly11CY1rlrySo2rljqlxlVLnVLjqqUbHSIIHgE1yVhRRnTPi/vC1Lxkwx9OeJ8XXMn0F08i2q5+RfVy/LTx81c12/xAnt6+1GNWPwHd+bpS0jwB1gLNhtfJ6meq6uC6JZH96S77tmmwvVxr/t7+YbHlL3uZb7WejzKRy+LKvtdEqz+XzAN7GVT9eVmHOu85v/5lGga7Es91X2L7bCxPV+wzbldf0jJPuN3umOdBuKZh6wm+3NpKttaj2W5Djab9nnaXtaE62mwM16lB40lfA9/bJLOrhbo907TRTv9xnSca8GR/jqxpafJsBdOfX/I0vWHN1nLh3zTls7L5dH/PPBJh6/Np83Q/b3xhDgNewHizMc3L7nnSPO/f3p/gnfJ1rmsZbnOzzNCR9rdtw45xpfTQGOduty9TMjfS74E2rj6y48v0Pr/XWQSYdtGIrZoveustpvWz7+p97RklmpcXVSntJrYVbKZNttrKvNraqOmj4ffs61ay+cmnvrnePLhxV9+G2OD/PC4beWw1LvZBptuDYt9uG47WXOcZnAN7rG7J49OGfalak/DyL/XhvwAAAP//AwBQSwMEFAAGAAgAAAAhAAKGbhtfAQAAnAMAABQAAAB3b3JkL3dlYlNldHRpbmdzLnhtbJzTX2vCMBAA8PfBvkPJu6bKlFGswhiOvYzBtg8Q06sNS3IlF63u0+/aqXP4YvfS/Ov9uEu42WLnbLKFQAZ9LkbDVCTgNRbGr3Px8b4c3IuEovKFsughF3sgsZjf3syarIHVG8TIf1LCiqfM6VxUMdaZlKQrcIqGWIPnwxKDU5GXYS2dCp+beqDR1SqalbEm7uU4TafiwIRrFCxLo+ER9caBj128DGBZRE+VqemoNddoDYaiDqiBiOtx9sdzyvgTM7q7gJzRAQnLOORiDhl1FIeP0m7m7C8w6QeML4Cphl0/4/5gSI48d0zRz5meHFOcOf9L5gygIhZVL2V8vFfZxqqoKkXVuQj9kpqcuL1r78jp7HntMaiVZYlfPeGHSzq4/XL97dBNYdfttyWIOTfEsXGSJtsqm4sNDRRpY4RsT7GOxpkvWGJ4CNgQhG5bWYvN68sTL+Sfnpp/AwAA//8DAFBLAwQUAAYACAAAACEAc/af3hoCAAA/CAAAEgAAAHdvcmQvZm9udFRhYmxlLnhtbNyUXW/aMBSG7yftP0S+L3HCRylqqNq1TLvZxdT9AOM4xGpsZz6GwL/fsRM+JoREkHZTpBDn9TlPzvsm8Pi0VVW0ERak0RlJBpREQnOTS73KyO/3xd2UROCYzllltMjITgB5mn/98tjMCqMdRNivYaZ4Rkrn6lkcAy+FYjAwtdC4WRirmMNLu4oVsx/r+o4bVTMnl7KSbhenlE5Ih7HXUExRSC5eDV8roV3oj62okGg0lLKGPa25htYYm9fWcAGAnlXV8hST+oBJRmcgJbk1YAo3QDPdRAGF7QkNK1UdAeN+gPQMMOFi248x7Rgxdp5yZN6PMzlwZH7CuW2YEwDkLi97UdJ9rrHvZY6VDMpToug31PiA2ymfkeKzHyttLFtWSMKnHuGDiwLYf6N/fwpLsQ26t0Dm3U8hamaaKex8l0pA9FM00S+jmA4FNdMGRII1G1ZlhHo3EzqkYzrCI8XViMS+kJfMgvCwtpC2csGUrHZ71QZu2Kil4+Ve3zAr/fTtFsgVbqxhSTPyRilN3xYL0ipJRr6hcj8dv3RK6u8VPg+dMjwo1Cs8cMJl0nJ44Bxq8J5xm8RZIi/GfETP2sk/a3YhjhHGkWIUPpLhf48jTJxO749xnFr9J469cjkO+tAzju8C/3jk5ST8C3F8MYafOInn2hmIXiXUFduFPK6yCY0E6GUzvWRzeIPN5Cabn8het4D5XwAAAP//AwBQSwMEFAAGAAgAAAAhAF5AXIZ7AQAA+QIAABEACAFkb2NQcm9wcy9jb3JlLnhtbCCiBAEooAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJySzW7CMBCE75X6DpHvwU6oUBWFoP6IU5EqlapVb8ZewCV2LHsh8PZ1Egil4tTbjvfb0XrsfLLXZbQD51VlxiQZMBKBEZVUZjUm7/NpfE8ij9xIXlYGxuQAnkyK25tc2ExUDl5dZcGhAh8FJ+MzYcdkjWgzSr1Yg+Z+EAgTmsvKaY5BuhW1XGz4CmjK2IhqQC45ctoYxrZ3JEdLKXpLu3VlayAFhRI0GPQ0GST0zCI47a8OtJ1fpFZ4sHAVPTV7eu9VD9Z1PaiHLRr2T+jn7OWtvWqsTJOVAFLkUmSosIQip+cyVH67+AaB3XEvQi0ccKxc8SC1Msqja1RLnTpN5hs41JWTPsxfqIBJ8MIpi+ElO/eLg0CX3OMsPO1SgXw8FDO+Bl9zp6K37cJxzY3iprX9AzazDnaq+SNF0hK9zI+Bd0uCjEJQWRfrqfMxfHqeT0mRsvQuZmmcpHM2yliSMfbV7HkxfzbUxwX+7Xgy6KK6/KzFDwAAAP//AwBQSwMEFAAGAAgAAAAhAM6w8+J1AQAAxgIAABAACAFkb2NQcm9wcy9hcHAueG1sIKIEASigAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnJJNT8MwDIbvSPyHqneWbqDBkJsJDSEOfEnt4BylbhuRJlESpu3f41JWirjRk/06fvPYDaz3nU526IOyJk/nsyxN0EhbKdPk6ba8O7tKkxCFqYS2BvP0gCFd89MTePHWoY8KQ0IWJuRpG6O7ZizIFjsRZlQ2VKmt70Sk1DfM1rWSeGvlR4cmskWWLRnuI5oKqzM3GqaD4/Uu/te0srLnC6/lwZEfhxI7p0VE/tR3amCjAKWNQpeqQ56RPCbwIhoMfAFsCODN+irw+fkK2BDCphVeyEjL45erJbBJDjfOaSVFpLXyRyW9DbaOyfMXa9L3A5seAeIvUH54FQ89xzSFB2UIgC4YAiLzovHCtYTT440ZFFJo3NDkvBY6ILAfATa2c8KQHRsj8nsPW1fa234T3y2/xcmQbyq2hROSEFbnF9NxJxUoSMWK+EeEUYB7+hte9/7Uaxqsjmf+FvoFvg7Pks+Xs4y+r40dNZp7fC/8EwAA//8DAFBLAQItABQABgAIAAAAIQDfpNJsWgEAACAFAAATAAAAAAAAAAAAAAAAAAAAAABbQ29udGVudF9UeXBlc10ueG1sUEsBAi0AFAAGAAgAAAAhAB6RGrfvAAAATgIAAAsAAAAAAAAAAAAAAAAAkwMAAF9yZWxzLy5yZWxzUEsBAi0AFAAGAAgAAAAhAJGlt0qCBgAAoC0AABEAAAAAAAAAAAAAAAAAswYAAHdvcmQvZG9jdW1lbnQueG1sUEsBAi0AFAAGAAgAAAAhANZks1H0AAAAMQMAABwAAAAAAAAAAAAAAAAAZA0AAHdvcmQvX3JlbHMvZG9jdW1lbnQueG1sLnJlbHNQSwECLQAUAAYACAAAACEAlKlShtQGAADHIAAAFQAAAAAAAAAAAAAAAACaDwAAd29yZC90aGVtZS90aGVtZTEueG1sUEsBAi0AFAAGAAgAAAAhAA7YnrwWBAAAxQoAABEAAAAAAAAAAAAAAAAAoRYAAHdvcmQvc2V0dGluZ3MueG1sUEsBAi0AFAAGAAgAAAAhAG3ARMLvCwAAtXUAAA8AAAAAAAAAAAAAAAAA5hoAAHdvcmQvc3R5bGVzLnhtbFBLAQItABQABgAIAAAAIQAChm4bXwEAAJwDAAAUAAAAAAAAAAAAAAAAAAInAAB3b3JkL3dlYlNldHRpbmdzLnhtbFBLAQItABQABgAIAAAAIQBz9p/eGgIAAD8IAAASAAAAAAAAAAAAAAAAAJMoAAB3b3JkL2ZvbnRUYWJsZS54bWxQSwECLQAUAAYACAAAACEAXkBchnsBAAD5AgAAEQAAAAAAAAAAAAAAAADdKgAAZG9jUHJvcHMvY29yZS54bWxQSwECLQAUAAYACAAAACEAzrDz4nUBAADGAgAAEAAAAAAAAAAAAAAAAACPLQAAZG9jUHJvcHMvYXBwLnhtbFBLBQYAAAAACwALAMECAAA6MAAAAAA="),
    "auditors_consent_letter": (".docx", "UEsDBBQABgAIAAAAIQAykW9XZgEAAKUFAAATAAgCW0NvbnRlbnRfVHlwZXNdLnhtbCCiBAIooAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC0lMtqwzAQRfeF/oPRtthKuiilxMmij2UbaPoBijRORPVCo7z+vuM4MaUkMTTJxiDP3HvPCDGD0dqabAkRtXcl6xc9loGTXmk3K9nX5C1/ZBkm4ZQw3kHJNoBsNLy9GUw2ATAjtcOSzVMKT5yjnIMVWPgAjiqVj1YkOsYZD0J+ixnw+17vgUvvEriUp9qDDQcvUImFSdnrmn43JBEMsuy5aayzSiZCMFqKRHW+dOpPSr5LKEi57cG5DnhHDYwfTKgrxwN2ug+6mqgVZGMR07uw1MVXPiquvFxYUhanbQ5w+qrSElp97Rail4BId25N0Vas0G7Pf5TDLewUIikvD9Jad0Jg2hjAyxM0vt3xkBIJrgGwc+5EWMH082oUv8w7QSrKnYipgctjtNadEInWADTf/tkcW5tTkdQ5jj4grZX4j7H3e6NW5zRwgJj06VfXJpL12fNBvZIUqAPZfLtkhz8AAAD//wMAUEsDBBQABgAIAAAAIQAekRq37wAAAE4CAAALAAgCX3JlbHMvLnJlbHMgogQCKKAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAArJLBasMwDEDvg/2D0b1R2sEYo04vY9DbGNkHCFtJTBPb2GrX/v082NgCXelhR8vS05PQenOcRnXglF3wGpZVDYq9Cdb5XsNb+7x4AJWFvKUxeNZw4gyb5vZm/cojSSnKg4tZFYrPGgaR+IiYzcAT5SpE9uWnC2kiKc/UYySzo55xVdf3mH4zoJkx1dZqSFt7B6o9Rb6GHbrOGX4KZj+xlzMtkI/C3rJdxFTqk7gyjWop9SwabDAvJZyRYqwKGvC80ep6o7+nxYmFLAmhCYkv+3xmXBJa/ueK5hk/Nu8hWbRf4W8bnF1B8wEAAP//AwBQSwMEFAAGAAgAAAAhAGqxL0pbBwAAWDEAABEAAAB3b3JkL2RvY3VtZW50LnhtbOxb227jOBJ9X2D/gfDTLpC0brZsGZMMfIkbeegg6MxgMI+0RFvcpkgNRfmyX79VlGQ7sadHce8mPbM2kLbEIk9RdaqKRcr9w4+bTJAV0wVX8qbjfXA7hMlYJVwubzo//zS7HnRIYahMqFCS3XS2rOj8ePv3v/2wHiYqLjMmDQEIWQzXeXzTSY3Jh45TxCnLaPEh47FWhVqYD7HKHLVY8Jg5a6UTx3c9117lWsWsKEDfhMoVLTo1XLxph5ZouobBCNh14pRqwzZ7DO/VID0ncgbHQP4ZQPCEvncMFbwaKnRwVkdA3bOAYFZHSL3zkE48XHgekn+M1D8PKThGGpyHdORO2bGDq5xJEC6UzqiBW710Mqq/lPk1AOfU8DkX3GwB0w0bGMrllzNmBKN2CFmQvBqh72QqYSJIGhR10ym1HNbjr3fjcerDanz9tRvBRDu1oC5y2MaIwjRjdRvbVcOndWKxVnM0E2BHJYuU57vskJ2LBsK0AVl9zQCrTDT91rnXMtR+L7VNKxr2gG2mX3OXiWrmX0f03BZsIsRuRJspPNfZzCQDD94rPss0B8b1WiafBsA/Aghj1nKxaDAGNYYT76MbcXjLsGpwKlYQh+8N67XMgS8ncwBQJCZJX4XiN3Z1cCw1NKXFztERkb1uUr0d3DY7sFG+/LZA+KhVme/R+Leh3e9T4hqLk1dg1QF1GOTFt03mKaU5ZMosHt4vpdJ0LmBGEB4EPJxYBvBfcBT8spdsY9uRa4I5pnMLVdVcJVv8zkHWHeZU03twyjC8i/zBeNyxrbAmGWzt1x9oHUIFl3y+6bjgCX7Ui3ZNj/pE45QtaCnMgcSqfNT268lsBUx2uKKQ7h8wHYhf2LzjoFBXfYp/N3JvgAKnljg7FH1yAgcQeqakKaAXLWIOjvCRQcbhFOeYjmRx0GIV/57G9dDcTqlhyZC43Wu3fw2aApSaqk81p2OLetFkMojcycWipyz6k2phwl449ruhP7uY8KQJU0bGiuqEqAWZcs1io3TRxjPdYNzreWjAi1mtRmhJk6YpFoxqHBkroUAfLY3C2wUXIJ3Bx3VfcjHBYlxuyQPNWAsGurNg4g7u7i4M/NcZGCWJhvWyDQlTfxb2wwsJBySUTQMWHIK9NPJTOR+SUZ4rLo09maEFMZCGngw1wJEG85cJhwtMSSioWWnBhn8XzSauO72wcbIAgYAgT1xftfFrL+oPxn333S35r7gRzBVsir9b62KBPixyGkM9nUPyYHrFOre/MJIokjLN5luy5CtGVKlJrGSBjm+UvZWQ78mcQbAQKNRzVbCEwP72ZYz8UXyQhVaZbQD8WJR4WNp0ecb4W+SAb0zEm83mjaf8h1SSkZQlFeQjk0zD9yfGDFIGJF5s/sY2f+H4XNpbiBmTwh4Ye2TPe+5K3KQpcfFmi9FXg3xokRTD6WTqB3fvvxv7syTF23tJaBwrnVAZw8Nwk1o6NPutBCIws1kiCgbhkxAKfyblwBTkwRUvFAbXE/CFUeUF0T+8f8JQmlRAO0HXe+4QnBVkFJsr4rteYEHnFHMq9OWyOji0YTo3lEtWqbUnJEkJngduJIRaQzukbHSQBdfZFVnbEMdr0ETN8LWh8nrfb+GQfe9u4Pai4N0dUpZZ1YuLlWj62AxjZfe7xOTVz74b8KdxZdwpW/p5QZjgSz4XNuUQerhMgyuBXCoDmab4DXIXX/B6OUcH3a3vh4NKmbBKfMJ/ryqBfcejYeAIwqmUhuJj2U5e1I3qyIHAKgUMBmWaLcv6jQTJaMJQqpnV1C7T+aNJf9C7ONbbONaBO1wRvrCUXZEipUJAZYjVX167CHhBVqXHBLzhq67ThmhvGvR8b/D+R7YXopFoXNjqakbwjINiQXkCe4i1tMuRPmAcarpUaW62X1n9WrnAqNeN7vqXReQNXOCBcUzEVbmKi4nEBURaCpFt4MRAqVuQlMJe0Qo08g29bIXC8CcvmAwkXlR1EFQMOZRCWCtBnwW+51ESimUocwxCATRWVyV0mTNYiOxaQO5lYTjsJxnKTy0v2H4Paigqx5ngbwWYsavc3vMaUalNG18Lxt1ZOPLRWy4HNCcSBJVfkFfYmLQ5pOm7o0E4Cd4/cr9La/4KTgnVPIUYWZRCtDk/dAfd8Z0XDv5KBn2m5sloJZe1jnc+b5hB8phhDmz5viP0vcAL+96FnLd4E3Jqw9GmmPB67qQ/vkTQm0TQ5weyqT9tAiiA9SLy/lLLxXfLDSY1LKEeq4quBT1+GERROH7/Vy7/D/S0p8Ud9YCU7uhCy/+cFkEL85nhBpclj3TJxprRLxbW3H5i2Rx2MynPyUOJl8Mq9Z1ksID90OPODC2pwfPkl7Qsn/AJ17iuRa4lO4XrcBBE1ePmy08U9RiV33QiF2N3qPkyBaCwuoMNqVHZ7lawxV6WMtj9w0z6vr1dKGUObpcl7t9umh0wWBGJqc+JsY9tTlT8UePP9YaCS/bITQwzDMLGspUl7GX1mz1n/18ibv8DAAD//wMAUEsDBBQABgAIAAAAIQCzvosdBQEAALYDAAAcAAgBd29yZC9fcmVscy9kb2N1bWVudC54bWwucmVscyCiBAEooAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKyTzWrDMBCE74W+g9h7LTttQwmRcymBXFv3AWR7/UP1Y6RNWr99RUoShwbTg44zYme+hdV6860VO6DzvTUCsiQFhqaydW9aAR/F9uEFmCdpaqmsQQEjetjk93frN1SSwpDv+sGzkGK8gI5oWHHuqw619Ikd0ISXxjotKUjX8kFWn7JFvkjTJXfTDMivMtmuFuB29SOwYhzwP9m2afoKX22112joRgX3SBQ28yFTuhZJwMlJQhbw2wiLqAg0KpwCHPVcfRaz3ux1iS5sfCE4W3MQy5gQFGbxAnCUv2Y2x/Ack6GxhgpZqgnH2ZqDeIoJ8YXl+5+TnJgnEH712/IfAAAA//8DAFBLAwQUAAYACAAAACEAlKlShtQGAADHIAAAFQAAAHdvcmQvdGhlbWUvdGhlbWUxLnhtbOxZW4sbNxR+L/Q/iHl3PDP2+BLiLb42TXaTkN2k9FFryzOKNaNBkndjQqCkT30pFNrShwb61odSGmihpS/9MQsJvfyISpqxZ2RrmtumhLJrWI+k7xx9Oufo6Fhz5b37MQEniHFMk57jXXIdgJIpneEk7Dl3jia1jgO4gMkMEpqgnrNC3Hlv7913rsDLIkIxAlI+4Zdhz4mESC/X63wquyG/RFOUyLE5ZTEUssnC+ozBU6k3JnXfdVv1GOLEAQmMpdqb8zmeInCkVDp7a+VjIv8lgquOKWGHSjUyJDR2tvDUF1/xIWHgBJKeI+eZ0dMjdF84gEAu5EDPcfWfU9+7Ut8IEVEhW5Kb6L9cLheYLXwtx8LjjaA79jtNb6NfA4jYxY076rPRpwFwOpUrzbiUsV7Qcjt+ji2BskeL7m7ba5j4kv7Grv5ua+A3DbwGZY/N3TVOuuNRYOA1KHsMdvB91x90GwZeg7LH1g6+Oe63/bGB16CI4GSxi261O51Wjt5A5pRctcK7rZbbHuXwAlUvRVcmn4iqWIvhPcomEqCdCwVOgFilaA6nEtdPBeVghHlK4MoBKUwol92u73ky8Jquv/loi8PLCJaks64p3+lSfACfMpyKnnNNanVKkKe//nr26OezR7+cffLJ2aMfwT4OI2GRuwqTsCz313ef//34Y/DnT9/+9cWXdjwv45/98Omz337/N/XCoPXVk2c/P3n69Wd/fP+FBd5n8LgMP8Ix4uAGOgW3aSwXaJkAHbOXkziKIC5L9JOQwwQqGQt6LCIDfWMFCbTgBsi0410m04UN+P7ynkH4MGJLgS3A61FsAA8oJQPKrGu6ruYqW2GZhPbJ2bKMuw3hiW3u4ZaXx8tUxj22qRxGyKB5i0iXwxAlSAA1RhcIWcQ+wtiw6wGeMsrpXICPMBhAbDXJET42oqkQuopj6ZeVjaD0t2Gbg7tgQIlN/QidmEi5NyCxqUTEMOP7cClgbGUMY1JG7kMR2UgertjUMDgX0tMhIhSMZ4hzm8xNtjLoXocyb1ndfkBWsYlkAi9syH1IaRk5oothBOPUyhknURn7AV/IEIXgFhVWEtTcIaot/QCTSnffxchw9/P39h2ZhuwBokaWzLYlEDX344rMIbIp77PYSLF9hq3RMViGRmjvI0TgKZwhBO58YMPT1LB5QfpaJLPKVWSzzTVoxqpqJ4jLWkkVNxbHYm6E7CEKaQWfg9VW4lnBJIasSvONhRky42MmN6MtXsl0YaRSzNSmtZO4yWNjfZVab0XQCCvV5vZ4XTHDfy+yx6TMvVeQQS8tIxP7C9vmCBJjgiJgjiAG+7Z0K0UM9xciajtpsaVVbm5u2sIN9a2iJ8bJcyqg/67ykfXF028eW7DnU+3Yga9T51Slku3qpgq3XdMMKZvht7+kGcFlcgvJU8QCvahoLiqa/31FU7WfL+qYizrmoo6xi7yBOqYoXfQF0PqaR2uJK+985piQQ7EiaJ/roofLvT+byE7d0EKbK6Y0ko/5dAYuZFA/A0bFh1hEhxFM5TSeniHkueqQg5RyWTjpbqtuNUCW8QGd5Td4qsLSt5pSAIqi3w02/bJIE1lvq11cgW7U61aor1nXBJTsy5AoTWaSaFhItNedzyGhV3YuLLoWFh2lvpKF/sq9Ig8nANWFeNDMGMlwkyE9U37K5NfePXdPVxnTXLZvWV5XcT0fTxskSuFmkiiFYSQPj+3uc/Z1t3CpQU+ZYpdGu/MmfK2SyFZuIInZAqdyzzUCqWYK054zlz+Y5GOcSn1cZSpIwqTnTEVu6FfJLCnjYgR5lMH0ULb+GAvEAMGxjPWyG0hScPP8tlrjW0qu6759ltNfZSej+RxNRUVP0ZRjmRLr6GuCVYMuJenDaHYKjsmS3YbSUEHbUwacYS421pxhVgruwopb6Srfisa7n2KLQpJGMD9Rysk8g+vnDZ3SOjTT7VWZ7Xwxx6Fy0mufus8XUgOlpFlxgKhT054/3twhX2JV5H2DVZa6t3Ndd53rqk6J1z8QStSKyQxqirGFWtFrUjvHgqA03SY0q86I8z4NtqNWHRDrulK3dl5r0+N7MvJHslpdEsE1VfmrhcHh+oVklgl07zq73BdgyXDPeeAG/ebQD4Y1txOMa81G0611gn6j1g+ChjcOPHc08B9Ko4go9oJs7on8sU9W+Vt73b/z5j5el9qXpjSuU10H17WwfnPv+dVv7gGWlnngj72m3/eHteHIa9Wa/qhV67Qb/drQb438vkxCrUn/oQNONNgbjEaTSeDXWkOJa7r9oNYfNIa1Vmc88CfeuDlyJThPhvfz9JHbYm3QvX8AAAD//wMAUEsDBBQABgAIAAAAIQBiofbrGAQAAMUKAAARAAAAd29yZC9zZXR0aW5ncy54bWykVttu4zYQfS/QfzD0XEeyLDuxsM7CsTcbt3G7iBPkmRIpizAvAkn50qL/3iElWs5msUjSF5uaM3NmODfp0+cDZ70dUZpKMQ0GF1HQIyKXmIrNNHh6vO1fBT1tkMCISUGmwZHo4PP1r7982qeaGANqugcUQqc8nwalMVUahjovCUf6QlZEAFhIxZGBR7UJOVLbuurnklfI0Iwyao5hHEXjoKWR06BWIm0p+pzmSmpZGGuSyqKgOWn/vIV6i9/GZCHzmhNhnMdQEQYxSKFLWmnPxj/KBmDpSXY/u8SOM6+3H0RvuO5eKnyyeEt41qBSMidaQ4E48wFS0TlOXhGdfF+A7/aKjgrMB5E7nUc+eh9B/IpgnJPD+ziuWo4QLM95KH4fz/jEQ7vEDsYfC+aMQGODy3exxD6vobVFBpVIn7rIMpL3BTU60R15lyPN3tI1DXRPM4VUM5Nty/A8XW6EVChjEA60Tg+q33PR2V9Iov1zR3JwcpuH4Bp2xN9S8t4+rYjKYVBgwURREFoAkwLVzDyibG1kBSo7BEFexi0s5Lda5KZ28/kHUQL62AF5iRTKDVHrCuUgnEthlGSeAMs/pZnDclHQ+w1Vs2qcTwuuBaoe5VdF8VLMCWNNNBZ5VoCQg3mmpnTeO+hJky9Im5mmSNwogrYPNSPa4Rsl97PayII2+o27dbMbISyBOCTtxb5bSQzLa5/Wir69utbAXXEwOr/X944wLQqiINcUGbKCDFOI79FW7o4gDHv+fzj+md9ak2dQhhYcPkKBtjfSGMnvjlVJhCvix/26lgjPCwlvK6z94UFKc1KFgYono0kTqUV/hIQnBp7arf1N+dMtdFOPNxZzxDNFUW9l93poNTK1vaHC4xmB4SHnyLrOPNjvN4DmiLFbSIgH3GV4iqmuFqRwZ7ZCatPxthrqh1IYm99PXHakiPqqZF016B46eCkw6S4xSJLWkgpzT7mX6zpbeysB434G1QL/tVMuT1169qmBchGbn3vkyu50ieg/rdu2YGptS0pWqKqazsg2g2nA6KY0A1tMA08YXv/uIdvELRY7LG4w94ByezPQbg+dLPayM72hlw07WeJlSScbedmok429bGxl5RH2FKNiC03qj1ZeSMbknuC7Dn8lareaXRZLkbMaE+gGLHO9FGsDG9bBukQVWTSbD7pPNoJ2FereLoXtA0nF1MBHV0UxRwe7MuOxZW+1GTrK2rzQtZhVrl4y2NdJO7XhC2M3Ad/FYjdyTqFb10eedfv0orkXoxomvoLVa6Ty2G8OGyRw63xpXwFJI0/ms8vb8dAFDS8Kt7KNWwrQFg+kuEGa4BbzpqPG9J8vt3GyuIwm/Wgxu+knl9GwP5uNov5sMh7HyWg2ia+if9sZ9t+f1/8BAAD//wMAUEsDBBQABgAIAAAAIQBf5rYmxgMAAHcWAAASAAAAd29yZC9udW1iZXJpbmcueG1szJfLbts4FIb3A8w7CNontORrhDpFmkwGGRTFAM2ga1qiLSG8CCTlyyz7Mn2EPlZfoYeUKNtxK8hyFtpY1rl8PPp5f/d+y6i3JlJlgs/94Hrge4THIsn4au7/9/x4NfM9pTFPMBWczP0dUf772z//eLeJeMEWREKgBwyuok0ez/1U6zxCSMUpYVhdsyyWQomlvo4FQ2K5zGKCNkImKBwEA/svlyImSgHnHvM1Vn6Fi7ftaInEG0g2wBGKUyw12e4ZwdmQMbpBs1NQ2AEEXxgGp6jh2agJMlWdgEadQFDVCWncjfSLj5t0I4WnpGk30vCUNOtGOhlO7HSAi5xwcC6FZFjDq1whhuVLkV8BOMc6W2Q00ztgDiYOgzP+0qEiyKoJbJicTZgiJhJCh4mjiLlfSB5V+Vd1vik9KvOrR51BaLtmobkbRLaaKu1yZRvtyvQHEReMcG1VQ5JQ0FFwlWZ5vTqwrjRwpg6ybhJgzaiL2+RBy6n2u6XtoeyGPbBN+VXfMVpW3kwMBi160yDqjDYlHLfpKmEwgvcNd5LmQNyg5eLjAOEJYBKTlpuFY8wqBor3s9twspbTynHKXjGcbC9s0HINfF3MAUAlOknPooROV2RyscYpVvVAN0RyXlHjGrdjBxrlq8smwt9SFPmell1Ge9oviRtzOjmDVU2ow0muLivmc4pzWClZHD2tuJB4QaEimB4ejHDP9oD5hYFiHvYv2Vq76WvPrDH+LRyr8EJpiWP9qWDe0dsTjE04ngEtkgTOZNIYyxPY3VIT+UES/GJCDIUr0060xrBgj8PpY3Dz18hHxsMKqrOPZE3o8y4nLsZaqbGWUZrl1PkGwYf7h+DuvvTQtXFk8HBt2VpccFBGweHwkdXGRUEp0XX+M+wMzvXj6/fa/k/srJQsq/D8X2nrASGqp4uBJkCNKBfQb9NwYMLRPjDj5vsNp/TCS4r5yp5rhxMXXdFl9XgUXCujuoozGJqfd2whqE29A0GPDBkHcEKWGIQrK1X/u8rqYiwX2W97LV1gKBq2Jdjb1sS8XyyleAMhg9GoSUnr7iLlvShkRqT3iWwO9HxtvVTU8O1F/fH12xvIGga1Tr+S1bq7yPoFos1dTR2Iemy7VNJhbyWdzRolNe5+Sjrqq6QgUZOk1t1PScd9lXQ0bNyZrLufkk76Kul40LhFWXc/JZ32VtJp4/Zk3f2UdNZXSSejxu3JuvsiKTq6Z1RiefbXXDrMUdVeXKKksNcaY5zBoXo4mwRjK/jRNcU15trihlk+y+vK7U8AAAD//wMAUEsDBBQABgAIAAAAIQBtwETC7wsAALV1AAAPAAAAd29yZC9zdHlsZXMueG1sxJ1dc9u6EYbvO9P/wNFVe5HI3048xznjOE7jaZz4RHZzDZGQhZokVIKM7fPrC4KQBGkJigtu3ZvEkrgPAbx4l1iSon77/TlLo1+8UELm56P9t3ujiOexTET+cD66v/v85t0oUiXLE5bKnJ+PXrga/f7hr3/57elMlS8pV5EG5Oosi89H87JcnI3HKp7zjKm3csFz/eFMFhkr9cviYZyx4rFavIlltmClmIpUlC/jg729k5HFFH0ocjYTMf8k4yrjeWnixwVPNVHmai4Wakl76kN7kkWyKGTMldKdztKGlzGRrzD7RwCUibiQSs7Kt7oztkUGpcP398xfWboGHOMABwBwEvNnHOOdZYx1pMsRCY5zsuKIxOGENcYBqKRM5ijKwXJcx3UsK9mcqblL5LhGHa9wL1k9Rll8dv2Qy4JNU03SqkdauMiA6391/+v/zJ/82bxfd2H0QXshkfEnPmNVWqr6ZXFb2Jf2lfnvs8xLFT2dMRULcT66E5m2zzf+FP2QGdOz7emMM1VeKMFaP5xf5Ko9LFbw7XG9y5TlD/rzXyw9H/H8zf1kcyert6Yi0WRWvJlc1IFj2+bmf6cni9WrZqutbmsLakNOmrygP+WzrzJ+5Mmk1B+cj/bqXek3769vCyEL7f3z0fv39s0Jz8QXkSQ8dzbM5yLhP+c8v1c8Wb//x2fjX/tGLKtc/314emKkSFVy9RzzRZ0N9Kc5y/Suv9UBab11JdY7N+H/WcL27Zi1xc85q1NitL+NMM1HIQ7qCOX0tp1ZbfXdbIXa0eFr7ejotXZ0/Fo7OnmtHZ2+1o7evdaODOZ/uSORJzr7mu3hbgB1F8fjRjTHYzY0x+MlNMdjFTTH4wQ0xzPR0RzPPEZzPNMUwSll7JuFzmQ/9Mz2bu7uY0QYd/chIYy7+wgQxt2d8MO4u/N7GHd3Og/j7s7eYdzdyRrPbZZa0bW2WV4OdtlMyjKXJY9K/jycxnLNMnUiDa8+6PGCpJMEmCaz2QPxYFrMzOvdM8SYNPx4XtblViRn0Uw8VAVXgxvO81881YV+xJJE8wiBBS+rwjMiIXO64DNe8DzmlBObDpqKnEd5lU0J5uaCPZCxeJ4QD9+SSJIUVhOaVeW8NokgmNQZiws5vGmSkeWHr0INH6saEn2s0pQTsb7RTDHDGl4bGMzw0sBghlcGBjO8MHA0oxoiSyMaKUsjGjBLIxq3Zn5SjZulEY2bpRGNm6UNH7c7UaYmxburjv3+5+4uU1mf2R/cjol4yJleAAw/3NhzptEtK9hDwRbzqD413I51+4zdz0eZvER3FMe0FYlqXW+myKXutcir4QO6QaMy14pHZK8Vj8hgK95wi93oZXK9QPtCU89MqmnZalpD6mXaCUurZkE73G2sHD7D1gb4LApFZoN2LMEM/lYvZ2s5KTLfupXDG7ZmDbfVdlYibZ5FErQylfEjTRr+8rLghS7LHgeTPss0lU88oSNOykI2c821/IGRpJflr7LFnClhaqUNRP9D/fKegOiGLQZ36DZlIqfR7epNxkQa0a0gvtzdfI3u5KIuM+uBoQF+lGUpMzKmPRP4t598+neaBl7oIjh/IertBdHpIQO7FAQHmYYkEyKSXmaKXJAcQw3vn/xlKlmR0NBuC97chlNyIuKEZYtm0UHgLZ0Xn3T+IVgNGd6/WCHq80JUprojgTmnDVU1/TePh6e6bzIiOTP0vSrN+Uez1DXRdLjhy4QN3PAlglFTHx7q+UvQ2Q3c8M5u4Kg6e5kypYT3Emowj6q7Sx51f4cXf5YnU1nMqpRuAJdAshFcAsmGUKZVlivKHhseYYcNj7q/hFPG8AhOyRnePwqRkIlhYFRKGBiVDAZGpYGBkQow/A4dBzb8Nh0HNvxenQZGtARwYFTzjPTwT3SVx4FRzTMDo5pnBkY1zwyMap4dfor4bKYXwXSHGAdJNeccJN2BJi95tpAFK16IkFcpf2AEJ0gb2m0hZ/X3M2Te3MRNgKzPUaeEi+0GRyXyTz4la1rNomwXwRlRlqZSEp1bWx9wTOTmvWu7wu7mPBteRt+mLOZzmSa88PTJH6vr5cmCxfY0Pbjc1+u051fxMC+jyXx1tt/FnOztjFwW7Bthu3fYNuYnBx1hNzwRVbZsKPwyxclh/2AzozeCj3YHr1cSG5HHPSPhPk92R65XyRuRpz0j4T7f9Yw0Pt2I7PLDJ1Y8tk6E0675s6rxPJPvtGsWrYJbd9s1kVaRbVPwtGsWbVgluojj+moBVKefZ/zx/czjj8e4yE/B2MlP6e0rP6LLYD/4L1Ef2TFJ0+xvdfcEyPtmEd0rc/5Ryea8/cYFp/5f6rrWC6dc8aiVc9j/wtVGlvGPY+9040f0zjt+RO8E5Ef0ykTecFRK8lN65yY/oneS8iPQ2QoeEXDZCsbjshWMD8lWkBKSrQasAvyI3ssBPwJtVIhAG3XASsGPQBkVhAcZFVLQRoUItFEhAm1UuADDGRXG44wK40OMCikhRoUUtFEhAm1UiEAbFSLQRoUItFED1/be8CCjQgraqBCBNipEoI1q1osDjArjcUaF8SFGhZQQo0IK2qgQgTYqRKCNChFoo0IE2qgQgTIqCA8yKqSgjQoRaKNCBNqozVcNw40K43FGhfEhRoWUEKNCCtqoEIE2KkSgjQoRaKNCBNqoEIEyKggPMiqkoI0KEWijQgTaqOZi4QCjwnicUWF8iFEhJcSokII2KkSgjQoRaKNCBNqoEIE2KkSgjArCg4wKKWijQgTaqBDRNT/tJUrfbfb7+LOe3jv2+1+6so364X6V20Ud9kctW+Vn9f8uwkcpH6PWLx4emnqjH0RMUyHNKWrPZXWXa26JQF34/H7Z/Q0flz7woUv2uxDmmimAH/WNBOdUjrqmvBsJiryjrpnuRoJV51FX9nUjwWHwqCvpGl8ub0rRhyMQ3JVmnOB9T3hXtnbC4RB35WgnEI5wV2Z2AuEAd+VjJ/A4qpPzdvRxz3E6Wd1fCghd09EhnPoJXdMSarVMx9AYfUXzE/qq5yf0ldFPQOnpxeCF9aPQCvtRYVJDm2GlDjeqn4CVGhKCpAaYcKkhKlhqiAqTGiZGrNSQgJU6PDn7CUFSA0y41BAVLDVEhUkND2VYqSEBKzUkYKUeeED2YsKlhqhgqSEqTGq4uMNKDQlYqSEBKzUkBEkNMOFSQ1Sw1BAVJjWoktFSQwJWakjASg0JQVIDTLjUEBUsNUR1SW3OomxIjVLYCcctwpxA3AHZCcQlZycwoFpyogOrJYcQWC1BrZaa46olVzQ/oa96fkJfGf0ElJ5eDF5YPwqtsB8VJjWuWmqTOtyofgJWaly15JUaVy11So2rljqlxlVLfqlx1VKb1LhqqU3q8OTsJwRJjauWOqXGVUudUuOqJb/UuGqpTWpctdQmNa5aapN64AHZiwmXGlctdUqNq5b8UuOqpTapcdVSm9S4aqlNaly15JUaVy11So2rljqlxlVLfqlx1VKb1LhqqU1qXLXUJjWuWvJKjauWOqXGVUudUuOqpRsdIggeATXJWFFGdM+L+8LUvGTDH054nxdcyfQXTyLarn5F9XL8tPHzVzXb/ECe3r7UY1Y/Ad35ulLSPAHWAs2G18nqZ6rq4Lolkf3pLvu2abC9XGv+3v5hseUve5lvtZ6PMpHL4sq+10SrP5fMA3sZVP15WYc67zm//mUaBrsSz3VfYvtsLE9X7DNuV1/SMk+43e6Y50G4pmHrCb7c2kq21qPZbkONpv2edpe1oTrabAzXqUHjSV8D39sks6uFuj3TtNFO/3GdJxrwZH+OrGlp8mwF059f8jS9Yc3WcuHfNOWzsvl0f888EmHr82nzdD9vfGEOA17AeLMxzcvuedI879/en+Cd8nWuaxluc7PM0JH2t23DjnGl9NAY5263L1MyN9LvgTauPrLjy/Q+v9dZBJh20Yitmi966y2m9bPv6n3tGSWalxdVKe0mthVspk222sq82tqo6aPh9+zrVrL5yae+ud48uHFX34bY4P88Lht5bDUu9kGm24Ni324bjtZc5xmcA3usbsnj04Z9qVqT8PIv9eG/AAAA//8DAFBLAwQUAAYACAAAACEAAoZuG18BAACcAwAAFAAAAHdvcmQvd2ViU2V0dGluZ3MueG1snNNfa8IwEADw98G+Q8m7psqUUazCGI69jMG2DxDTqw1LciUXre7T79qpc/hi99L86/24S7jZYudssoVABn0uRsNUJOA1Fsavc/Hxvhzci4Si8oWy6CEXeyCxmN/ezJqsgdUbxMh/UsKKp8zpXFQx1pmUpCtwioZYg+fDEoNTkZdhLZ0Kn5t6oNHVKpqVsSbu5ThNp+LAhGsULEuj4RH1xoGPXbwMYFlET5Wp6ag112gNhqIOqIGI63H2x3PK+BMzuruAnNEBCcs45GIOGXUUh4/SbubsLzDpB4wvgKmGXT/j/mBIjjx3TNHPmZ4cU5w5/0vmDKAiFlUvZXy8V9nGqqgqRdW5CP2Smpy4vWvvyOnsee0xqJVliV894YdLOrj9cv3t0E1h1+23JYg5N8SxcZIm2yqbiw0NFGljhGxPsY7GmS9YYngI2BCEbltZi83ryxMv5J+emn8DAAD//wMAUEsDBBQABgAIAAAAIQD5nH36YAIAAFAKAAASAAAAd29yZC9mb250VGFibGUueG1s3JVLj9MwEMfvSHyHKPdtHn1X265gH4gLh2URZ9dxGovYjjxu0357xk76Ii0ki0CCVG3sGc8vM397mtu7rci9DdPAlZz7US/0PSapSrhczf0vL083E98DQ2RCciXZ3N8x8O8Wb9/clrNUSQMexkuYCTr3M2OKWRAAzZgg0FMFk+hMlRbE4FSvAkH0t3VxQ5UoiOFLnnOzC+IwHPk1RrehqDTllD0ouhZMGhcfaJYjUUnIeAF7WtmGViqdFFpRBoA1i7ziCcLlARMNGiDBqVagUtPDYuqMHArDo9CNRH4EDLsB4gZgRNm2G2NSMwKMPOXwpBtndODw5ITzumROAJCYJOtEife6BjaWGJIRyE6JrFtSwwNuJ6xGgs4+rqTSZJkjCXfdw43zHNj+Yv325oZs6+y2BH9Rt4JXziQRGPl5J5Yqd/aCSAUsQteG5HM/HOInCu0RGYcjvA/DsR/YhTQjGphlVAvjypwSwfPd3qqVILJyFNzQbG/fEM1t0pUL+Aoda1iGyKkvv7JE2OHnlrixpn9uoY4zObdEJ2vwmUElQEOIFy4YeJ9Y6T27zC8pYrd1FPZRiQF+YxwNLivinvT7ijxizvHj09NRkXu0jCfD9w1Fpj9TxE2jitNekXu11pxpq8kVNcaowNSpYtUYdFJDqITpS3KkfMuS9loM+n9Di6/4d2tfM3ClUxpXh04ha6P+oUb5wPBNxMmVI1E1xrFB+n+0QVyy8WR8VOKHulsqUc2nHQ/Fu8Io8B44FDnZOT1alQklB+hUZnytzObZ/3WZ0avK/I/Kqwew+A4AAP//AwBQSwMEFAAGAAgAAAAhAMLLg8t7AQAA+QIAABEACAFkb2NQcm9wcy9jb3JlLnhtbCCiBAEooAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJySzU7DMBCE70i8Q+R7YidFCEVpED/iRCUkikDcXHtpTWPHsreEvD1O0qQU9cRtx/vtaD12cf2tq+gLnFe1mZM0YSQCI2qpzHpOXpYP8RWJPHIjeVUbmJMWPLkuz88KYXNRO3hytQWHCnwUnIzPhZ2TDaLNKfViA5r7JBAmND9qpzkG6dbUcrHla6AZY5dUA3LJkdPOMLaTI9lbSjFZ2p2regMpKFSgwaCnaZLSA4vgtD850Hd+kVpha+EkOjYn+turCWyaJmlmPRr2T+nb4vG5v2qsTJeVAFIWUuSosIKyoIcyVH63+gSBw/EkQi0ccKxdeSO1Msqj61RPjZ0u8y20Te2kD/NHKmASvHDKYnjJwf3oINAV97gIT/uhQN625YJvwDfcqeh5t3Jcc6O46W3/gN2sgy/V/ZEy7YlJFvvAhyVBRiGofIh17LzO7u6XD6TMWHYRsyxOsyW7zNlFzth7t+fR/MFQ7xf4t+NoMER1/FnLHwAAAP//AwBQSwMEFAAGAAgAAAAhAHO0XYdxAQAAyQIAABAACAFkb2NQcm9wcy9hcHAueG1sIKIEASigAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnFLLTsMwELwj8Q9R7q2TCiGEtq5QK8SBl9S0PVvOJrFwbMt2Ef171oSGIG7ktDPrHc9sDKuPXmfv6IOyZpmX8yLP0EhbK9Mu8111P7vJsxCFqYW2Bpf5CUO+4pcX8OqtQx8VhowkTFjmXYzulrEgO+xFmFPbUKexvheRoG+ZbRolcWPlsUcT2aIorhl+RDQ11jM3CuaD4u17/K9obWXyF/bVyZEehwp7p0VE/pwmNbCRgMpGoSvVIy+IHgG8ihYDXwAbCjhYXxMuiRlKWHfCCxlpebxclDQ9IeDOOa2kiLRX/qSkt8E2MXv5MpslAWDTI0ABtiiPXsVTMjKF8KgMOUg3DBV586L1wnXfBkcEWyk0rik7b4QOCOyHgLXtnTCkx8aK9N7CzlV2k3bxPfKbnMQ8qNhtnZDJzNXiV+BJC7bEYk0JRg8jAQ/0Q7xOF9CsabE+n/nbSCvcDy+Tl9fzgr6vnZ05Cj4+Gf4JAAD//wMAUEsBAi0AFAAGAAgAAAAhADKRb1dmAQAApQUAABMAAAAAAAAAAAAAAAAAAAAAAFtDb250ZW50X1R5cGVzXS54bWxQSwECLQAUAAYACAAAACEAHpEat+8AAABOAgAACwAAAAAAAAAAAAAAAACfAwAAX3JlbHMvLnJlbHNQSwECLQAUAAYACAAAACEAarEvSlsHAABYMQAAEQAAAAAAAAAAAAAAAAC/BgAAd29yZC9kb2N1bWVudC54bWxQSwECLQAUAAYACAAAACEAs76LHQUBAAC2AwAAHAAAAAAAAAAAAAAAAABJDgAAd29yZC9fcmVscy9kb2N1bWVudC54bWwucmVsc1BLAQItABQABgAIAAAAIQCUqVKG1AYAAMcgAAAVAAAAAAAAAAAAAAAAAJAQAAB3b3JkL3RoZW1lL3RoZW1lMS54bWxQSwECLQAUAAYACAAAACEAYqH26xgEAADFCgAAEQAAAAAAAAAAAAAAAACXFwAAd29yZC9zZXR0aW5ncy54bWxQSwECLQAUAAYACAAAACEAX+a2JsYDAAB3FgAAEgAAAAAAAAAAAAAAAADeGwAAd29yZC9udW1iZXJpbmcueG1sUEsBAi0AFAAGAAgAAAAhAG3ARMLvCwAAtXUAAA8AAAAAAAAAAAAAAAAA1B8AAHdvcmQvc3R5bGVzLnhtbFBLAQItABQABgAIAAAAIQAChm4bXwEAAJwDAAAUAAAAAAAAAAAAAAAAAPArAAB3b3JkL3dlYlNldHRpbmdzLnhtbFBLAQItABQABgAIAAAAIQD5nH36YAIAAFAKAAASAAAAAAAAAAAAAAAAAIEtAAB3b3JkL2ZvbnRUYWJsZS54bWxQSwECLQAUAAYACAAAACEAwsuDy3sBAAD5AgAAEQAAAAAAAAAAAAAAAAARMAAAZG9jUHJvcHMvY29yZS54bWxQSwECLQAUAAYACAAAACEAc7Rdh3EBAADJAgAAEAAAAAAAAAAAAAAAAADDMgAAZG9jUHJvcHMvYXBwLnhtbFBLBQYAAAAADAAMAAEDAABqNQAAAAA="),
    "auditors_appointment_letter": (".docx", "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"),
    "auditors_appointment_res": (".docx", "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"),
    "acceptance_continuance": (".xlsx", "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"),
    "engagement_letter_general": (".docx", "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"),
    "engagement_letter_icofar": (".docx", "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"),
    "independence_confirmation": (".docx", "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"),
    "audit_planning_checklist": (".xlsx", "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"),
    "minutes_team_planning": (".docx", "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"),
    "overall_strategy_memo": (".docx", "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"),
    "risk_assessment": (".xlsx", "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"),
}

# ══════════════════════════════════════════════════════════════════════════════
# Clause / Note Version Registry
# ══════════════════════════════════════════════════════════════════════════════
# HOW TO ADD A NEW REGULATORY VERSION (e.g. CARO is amended for FY 2026-27):
#   1. Define the new clause list, e.g.  CARO_ITEMS_2026 = [...]
#   2. Add it to the matching VERSIONS dict, e.g.  CARO_VERSIONS["caro_2026"] = CARO_ITEMS_2026
#   3. Add/update the FY entry, e.g.  CARO_VERSION_BY_FY["FY 2026-27"] = "caro_2026"
#   4. Define matching process notes dict and add to PROCESS_NOTES_VERSIONS dict
#   5. Bump APP_VERSION
# Old engagements keep their stamped version and are unaffected.
# ─────────────────────────────────────────────────────────────────────────────

FORM3CD_VERSIONS        = {"3cd_2018":   TAX_AUDIT_CLAUSES}
AS_NOTES_VERSIONS       = {"as_2023":    AS_NOTES}
INDAS_NOTES_VERSIONS    = {"indas_2023": IND_AS_NOTES}
CARO_VERSIONS           = {"caro_2020":  CARO_ITEMS}

TAX_PROCESS_NOTES_VERSIONS   = {"3cd_2018":   TAX_PROCESS_NOTES}
AS_PROCESS_NOTES_VERSIONS    = {"as_2023":    AS_PROCESS_NOTES}
INDAS_PROCESS_NOTES_VERSIONS = {"indas_2023": IND_AS_PROCESS_NOTES}

# ── FY → version map (the ONLY lines to edit when regulations change) ─────────
FORM3CD_VERSION_BY_FY = {
    "FY 2024-25": "3cd_2018",
    "FY 2025-26": "3cd_2018",
    "FY 2026-27": "3cd_2018",   # change to "3cd_2026" if Form 3CD is amended
}
CARO_VERSION_BY_FY = {
    "FY 2024-25": "caro_2020",
    "FY 2025-26": "caro_2020",
    "FY 2026-27": "caro_2020",  # change to "caro_2026" if CARO is amended
}
AS_NOTES_VERSION_BY_FY = {
    "FY 2024-25": "as_2023",
    "FY 2025-26": "as_2023",
    "FY 2026-27": "as_2023",
}
INDAS_NOTES_VERSION_BY_FY = {
    "FY 2024-25": "indas_2023",
    "FY 2025-26": "indas_2023",
    "FY 2026-27": "indas_2023",
}

def _default_ver(fy_map, fy):
    """Return the version for a FY, or the latest known version as fallback."""
    return fy_map.get(fy) or list(fy_map.values())[-1]


LS_STATUS_COLORS = {
    "Not Checked":   C["border"],
    "Compliant":     C["success"],
    "Non-Compliant": C["danger"],
    "N/A":           C["muted"],
}

STATUS_COLORS = {
    "Not Started": C["status_ns"],
    "In Progress":  C["status_ip"],
    "Completed":    C["status_done"],
    "N/A":          C["status_na"],
}
WORKPAPER_STATUSES = ["Not Started", "In Progress", "Completed", "N/A"]

# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def styled_button(parent, text, command, kind="primary", width=18, **kwargs):
    bg  = C["btn_primary"]  if kind == "primary" else C["btn_secondary"]
    fg  = C["bg"]           if kind == "primary" else C["text"]
    hov = C["btn_hover"]    if kind == "primary" else C["border"]
    btn = tk.Button(parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=hov, activeforeground=fg,
        font=FONT_LABEL, relief="flat", cursor="hand2",
        padx=16, pady=9, width=width, bd=0, **kwargs)
    btn.bind("<Enter>", lambda e: btn.config(bg=hov))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn

def styled_entry(parent, textvariable=None, width=34, **kwargs):
    return tk.Entry(parent, textvariable=textvariable,
        bg=C["input_bg"], fg=C["text"], insertbackground=C["accent"],
        relief="flat", font=FONT_BODY, highlightthickness=1,
        highlightbackground=C["input_border"], highlightcolor=C["accent"],
        width=width, **kwargs)

def divider(parent, color=None):
    tk.Frame(parent, height=1, bg=color or C["border"]).pack(fill="x", pady=8)

def _draw_capsule(cv, x1, y1, x2, y2, **kw):
    """Draw a pill/capsule shape on a Canvas (fully rounded ends)."""
    kw.setdefault("outline", "")
    h = y2 - y1
    cv.create_oval(x1, y1, x1 + h, y2, **kw)
    cv.create_oval(x2 - h, y1, x2, y2, **kw)
    cv.create_rectangle(x1 + h // 2, y1, x2 - h // 2, y2, **kw)

_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

def _safe_filename(name):
    """Strip characters that are invalid in Windows filenames."""
    return _INVALID_FILENAME_CHARS.sub("", name).strip() or "Untitled"


def _setup_ttk_styles(root):
    """Configure shared ttk styles (scrollbars, comboboxes, etc.) once at startup."""
    style = ttk.Style(root)
    style.theme_use("default")
    style.configure("Thin.Vertical.TScrollbar",
        gripcount=0,
        background=C["border"],
        darkcolor=C["border"],
        lightcolor=C["border"],
        troughcolor=C["bg"],
        bordercolor=C["bg"],
        arrowcolor=C["muted"],
        relief="flat",
        width=8)
    style.map("Thin.Vertical.TScrollbar",
        background=[("active", C["muted"]), ("pressed", C["muted"])])
    style.configure("TCombobox",
        fieldbackground=C["input_bg"], background=C["input_bg"],
        foreground=C["text"], selectbackground=C["highlight"],
        selectforeground=C["text"], arrowcolor=C["accent"])

def bind_tree(widget, event, handler, exclude=None):
    """Recursively bind event+handler to widget and all descendants."""
    if widget is exclude:
        return
    # For click events, skip widgets that have their own click behaviour
    # but DO bind Labels and Frames (they swallow events silently otherwise)
    if event == "<Button-1>" and isinstance(widget,
            (tk.Button, ttk.Button, tk.Entry, tk.Text, ttk.Combobox, ttk.Scrollbar)):
        # still recurse into children of these (e.g. a Frame inside a Button)
        for child in widget.winfo_children():
            bind_tree(child, event, handler, exclude=exclude)
        return
    widget.bind(event, handler)
    for child in widget.winfo_children():
        bind_tree(child, event, handler, exclude=exclude)

# ══════════════════════════════════════════════════════════════════════════════
# Data helpers
# ══════════════════════════════════════════════════════════════════════════════

def make_eng_id():
    return "eng_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def make_engagement(audit_type, fy, std=None):
    return {
        "id": make_eng_id(),
        "audit_type": audit_type,
        "accounting_standard": std if audit_type == "Statutory Audit" else None,
        "financial_year": fy,
        "engagement_notes": "",
        "created_at": datetime.now().isoformat(),
        "locked": False,
        # ── Regulatory version stamps ──────────────────────────────────────────
        # These pin the engagement to the exact clause lists that applied when
        # it was created.  Old files are backfilled by migrate().
        "form3cd_version":      _default_ver(FORM3CD_VERSION_BY_FY,     fy),
        "caro_version":         _default_ver(CARO_VERSION_BY_FY,        fy),
        "notes_as_version":     _default_ver(AS_NOTES_VERSION_BY_FY,    fy),
        "notes_indas_version":  _default_ver(INDAS_NOTES_VERSION_BY_FY, fy),
        # ──────────────────────────────────────────────────────────────────────
        "pre_audit_docs": {},
        "ifc": {},
        "sch3": {},
        "financials": {},
        "fin_checklist": {},
        "ifc_na": False,
        "caro_na": False,
        "workpapers": {},
        "legal_sec": {},
        "variance_analysis": {"balance_sheet": {}, "profit_loss": {},
                              "cy_label": "CY", "py_label": "PY"},
    }

def eng_label(eng):
    if eng["audit_type"] == "Statutory Audit":
        std = eng.get("accounting_standard") or "AS"
        return f"{eng['financial_year']}  •  Statutory ({std})"
    return f"{eng['financial_year']}  •  Tax Audit"

def items_for_eng(eng):
    """Return the clause/note list for this engagement using its stamped version."""
    if eng["audit_type"] == "Tax Audit":
        ver = eng.get("form3cd_version", _default_ver(FORM3CD_VERSION_BY_FY, eng.get("financial_year","")))
        return FORM3CD_VERSIONS.get(ver, TAX_AUDIT_CLAUSES)
    std = eng.get("accounting_standard") or "AS"
    if std == "Ind AS":
        ver = eng.get("notes_indas_version", _default_ver(INDAS_NOTES_VERSION_BY_FY, eng.get("financial_year","")))
        return INDAS_NOTES_VERSIONS.get(ver, IND_AS_NOTES)
    ver = eng.get("notes_as_version", _default_ver(AS_NOTES_VERSION_BY_FY, eng.get("financial_year","")))
    return AS_NOTES_VERSIONS.get(ver, AS_NOTES)

def caro_items_for_eng(eng):
    """Return the CARO checklist for this engagement using its stamped version."""
    ver = eng.get("caro_version", _default_ver(CARO_VERSION_BY_FY, eng.get("financial_year","")))
    return CARO_VERSIONS.get(ver, CARO_ITEMS)

def migrate(data):
    if "engagements" in data and isinstance(data["engagements"], list):
        for e in data["engagements"]:
            e.setdefault("legal_sec", {})
            e.setdefault("locked", False)
            e.setdefault("caro", {})
            e.setdefault("ifc", {})
            e.setdefault("sch3", {})
            e.setdefault("financials", {})
            e.setdefault("fin_checklist", {})
            e.setdefault("pre_audit_docs", {})
            e.setdefault("workpapers", {})
            e.setdefault("engagement_notes", "")
            e.setdefault("ifc_na", False)
            e.setdefault("caro_na", False)
            e.setdefault("variance_analysis", {
                "balance_sheet": {}, "profit_loss": {},
                "cy_label": "CY", "py_label": "PY"})
            # Back-fill version stamps for files created before versioning was added
            fy = e.get("financial_year", FINANCIAL_YEARS[0])
            e.setdefault("form3cd_version",     _default_ver(FORM3CD_VERSION_BY_FY,     fy))
            e.setdefault("caro_version",         _default_ver(CARO_VERSION_BY_FY,        fy))
            e.setdefault("notes_as_version",     _default_ver(AS_NOTES_VERSION_BY_FY,    fy))
            e.setdefault("notes_indas_version",  _default_ver(INDAS_NOTES_VERSION_BY_FY, fy))
        return data
    eng = make_engagement(
        data.get("audit_type", "Statutory Audit"),
        data.get("financial_year", FINANCIAL_YEARS[0]),
        data.get("accounting_standard"),
    )
    eng["engagement_notes"] = ""
    eng["created_at"] = data.get("created_at", datetime.now().isoformat())
    pad = data.get("pre_audit_docs", {})
    eng["pre_audit_docs"] = pad if isinstance(pad, dict) else {}
    wp  = data.get("workpapers", {})
    eng["workpapers"] = wp if isinstance(wp, dict) else {}
    return {
        "company_name":  data.get("company_name", "Untitled"),
        "company_notes": data.get("notes", ""),
        "created_at":    data.get("created_at", datetime.now().isoformat()),
        "modified_at":   datetime.now().isoformat(),
        "version":       APP_VERSION,
        "engagements":   [eng],
    }

# ══════════════════════════════════════════════════════════════════════════════
# Dialogs
# ══════════════════════════════════════════════════════════════════════════════

class NewFileDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.title("New Company File")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.grab_set()
        self.geometry("520x560")
        self._center(parent)
        self._build()
        self.wait_window()

    def _center(self, p):
        self.update_idletasks()
        x = p.winfo_x() + p.winfo_width()//2 - 260
        y = p.winfo_y() + p.winfo_height()//2 - 280
        self.geometry(f"520x560+{x}+{y}")

    def _build(self):
        tk.Frame(self, bg=C["accent"], height=5).pack(fill="x")
        tk.Label(self, text="✦  New Company File", bg=C["bg"],
                 fg=C["accent"], font=("Segoe UI", 15, "bold")).pack(pady=(20, 4))
        tk.Label(self, text="Engagements are added after creating the file.",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack()
        tk.Frame(self, height=1, bg=C["border"]).pack(fill="x", pady=12)

        card = tk.Frame(self, bg=C["panel"], padx=32, pady=20)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # Company Name
        tk.Label(card, text="Company Name *", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        self._name = tk.StringVar()
        e = styled_entry(card, textvariable=self._name, width=40)
        e.pack(fill="x", ipady=5, pady=(2, 10))
        e.focus_set()

        # CIN
        tk.Label(card, text="CIN  (Corporate Identity Number)",
                 bg=C["panel"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        self._cin = tk.StringVar()
        cin_entry = styled_entry(card, textvariable=self._cin, width=40)
        cin_entry.pack(fill="x", ipady=5, pady=(2, 10))

        # Address
        tk.Label(card, text="Registered Office Address",
                 bg=C["panel"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        self._address = tk.Text(card, height=3, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat", font=FONT_BODY,
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"])
        self._address.pack(fill="x", pady=(2, 10))

        # Notes
        tk.Label(card, text="Notes (optional)", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        self._notes = tk.Text(card, height=2, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat", font=FONT_BODY,
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"])
        self._notes.pack(fill="x", pady=(2, 0))

        bar = tk.Frame(self, bg=C["bg"])
        bar.pack(pady=(0, 20))
        styled_button(bar, "Cancel", self.destroy, kind="secondary", width=12
                      ).pack(side="left", padx=6)
        styled_button(bar, "✦  Create", self._submit, kind="primary", width=14
                      ).pack(side="left", padx=6)

    def _submit(self):
        name = self._name.get().strip()
        if not name:
            messagebox.showwarning("Required", "Company name cannot be empty.", parent=self)
            return
        now = datetime.now().isoformat()
        self.result = {
            "company_name":  name,
            "company_cin":   self._cin.get().strip().upper(),
            "company_addr":  self._address.get("1.0", "end").strip(),
            "company_notes": self._notes.get("1.0", "end").strip(),
            "created_at": now, "modified_at": now,
            "version": APP_VERSION, "engagements": []}
        self.destroy()


class EngagementDialog(tk.Toplevel):
    def __init__(self, parent, existing=None):
        super().__init__(parent)
        self.result = None
        self._ex = existing
        self.title("Edit Engagement" if existing else "Add Engagement")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.grab_set()
        self.geometry("500x540")
        self._center(parent)
        self._build()
        self.wait_window()

    def _center(self, p):
        self.update_idletasks()
        x = p.winfo_x() + p.winfo_width()//2 - 250
        y = p.winfo_y() + p.winfo_height()//2 - 270
        self.geometry(f"500x540+{x}+{y}")

    def _build(self):
        tk.Frame(self, bg=C["accent"], height=5).pack(fill="x")
        tk.Label(self, text="⊕  Engagement",
                 bg=C["bg"], fg=C["accent"],
                 font=("Segoe UI", 14, "bold")).pack(pady=(18, 4))
        tk.Frame(self, height=1, bg=C["border"]).pack(fill="x", pady=8)

        card = tk.Frame(self, bg=C["panel"], padx=30, pady=20)
        card.pack(fill="both", expand=True, padx=22, pady=(0, 16))

        # Audit type
        tk.Label(card, text="Type of Audit", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        start_audit = (self._ex or {}).get("audit_type", AUDIT_TYPES[0])
        self._audit = tk.StringVar(value=start_audit)
        af = tk.Frame(card, bg=C["panel"])
        af.pack(fill="x", pady=(2, 6))
        for at in AUDIT_TYPES:
            tk.Radiobutton(af, text=at, variable=self._audit, value=at,
                bg=C["panel"], fg=C["text"], activebackground=C["panel"],
                selectcolor=C["input_bg"], font=FONT_BODY,
                indicatoron=0, relief="flat", cursor="hand2",
                padx=14, pady=6, bd=1,
                highlightthickness=1,
                highlightbackground=C["border"]).pack(side="left", padx=(0, 8))

        # AS / IndAS
        self._as_frame = tk.Frame(card, bg=C["panel"])
        as_hdr = tk.Frame(self._as_frame, bg=C["panel"])
        as_hdr.pack(fill="x", pady=(4, 4))
        tk.Frame(as_hdr, bg=C["accent"], width=3).pack(side="left", fill="y", padx=(0, 6))
        tk.Label(as_hdr, text="Accounting Standard", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(side="left")
        start_std = (self._ex or {}).get("accounting_standard") or "AS"
        self._std = tk.StringVar(value=start_std)
        sf = tk.Frame(self._as_frame, bg=C["panel"])
        sf.pack(fill="x")
        for std, desc in [("AS", "AS  (Accounting Standards)"),
                           ("Ind AS", "Ind AS  (Indian AS)")]:
            tk.Radiobutton(sf, text=desc, variable=self._std, value=std,
                bg=C["panel"], fg=C["text"], activebackground=C["panel"],
                selectcolor=C["input_bg"], font=FONT_BODY,
                indicatoron=0, relief="flat", cursor="hand2",
                padx=12, pady=5, bd=1,
                highlightthickness=1,
                highlightbackground=C["border"]).pack(side="left", padx=(0, 8))

        def _toggle(*_):
            if self._audit.get() == "Statutory Audit":
                self._as_frame.pack(fill="x", pady=(0, 6))
            else:
                self._as_frame.pack_forget()
        self._audit.trace_add("write", _toggle)
        _toggle()

        # Financial year
        tk.Label(card, text="Financial Year", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(8, 2))
        start_fy = (self._ex or {}).get("financial_year", FINANCIAL_YEARS[0])
        self._fy = tk.StringVar(value=start_fy)
        ttk.Combobox(card, textvariable=self._fy, values=FINANCIAL_YEARS,
                     state="readonly", font=FONT_BODY, width=38
                     ).pack(fill="x", ipady=4)

        self._ver_lbl = tk.Label(card, text="", bg=C["panel"],
                                 fg=C["muted"], font=("Segoe UI", 8))
        self._ver_lbl.pack(anchor="w", pady=(2, 0))
        self._fy.trace_add("write", self._update_ver_lbl)
        self._update_ver_lbl()

        # Firm Name
        tk.Label(card, text="Name of Auditing Firm", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(12, 2))
        FIRM_NAMES = [
            "Pai Nayak & Associates",
            "H Gurudas Shenoy",
            "NP Pai & Co",
            "K Narasimha Kini & Associates",
        ]
        self._firm_name = ttk.Combobox(card, values=FIRM_NAMES,
            font=FONT_BODY, width=38)
        self._firm_name.pack(fill="x", ipady=4)
        self._firm_name.set((self._ex or {}).get("firm_name", ""))

        # Notes
        tk.Label(card, text="Engagement Notes (optional)", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(12, 2))
        self._eng_notes = tk.Text(card, height=3, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat", font=FONT_BODY,
            highlightthickness=1, highlightbackground=C["input_border"])
        self._eng_notes.pack(fill="x")
        self._eng_notes.insert("1.0", (self._ex or {}).get("engagement_notes", ""))

        bar = tk.Frame(self, bg=C["bg"])
        bar.pack(pady=(0, 18))
        styled_button(bar, "Cancel", self.destroy, kind="secondary", width=12
                      ).pack(side="left", padx=6)
        lbl = "✓  Save" if self._ex else "⊕  Add"
        styled_button(bar, lbl, self._submit, kind="primary", width=14
                      ).pack(side="left", padx=6)

    def _update_ver_lbl(self, *_):
        """Show which regulatory versions will be stamped for the selected FY."""
        fy   = self._fy.get()
        audit = self._audit.get()
        if not fy:
            self._ver_lbl.config(text="")
            return
        parts = []
        if audit == "Tax Audit":
            parts.append(f"Form 3CD: {_default_ver(FORM3CD_VERSION_BY_FY, fy)}")
        else:
            parts.append(f"CARO: {_default_ver(CARO_VERSION_BY_FY, fy)}")
            parts.append(f"AS Notes: {_default_ver(AS_NOTES_VERSION_BY_FY, fy)}")
            parts.append(f"Ind AS Notes: {_default_ver(INDAS_NOTES_VERSION_BY_FY, fy)}")
        self._ver_lbl.config(text="Regulatory versions: " + "  ·  ".join(parts))

    def _submit(self):
        audit = self._audit.get()
        std   = self._std.get() if audit == "Statutory Audit" else None
        fy    = self._fy.get()
        notes = self._eng_notes.get("1.0", "end").strip()
        firm  = self._firm_name.get().strip()
        if self._ex:
            self.result = {**self._ex, "audit_type": audit,
                           "accounting_standard": std,
                           "financial_year": fy, "engagement_notes": notes,
                           "firm_name": firm}
        else:
            e = make_engagement(audit, fy, std)
            e["engagement_notes"] = notes
            e["firm_name"] = firm
            self.result = e
        self.destroy()


class DeleteEngagementDialog(tk.Toplevel):
    def __init__(self, parent, eng):
        super().__init__(parent)
        self.confirmed = False
        self._eng = eng
        self.title("Delete Engagement")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.grab_set()
        self.geometry("460x360")
        self._center(parent)
        self._step1()
        self.wait_window()

    def _center(self, p):
        self.update_idletasks()
        x = p.winfo_x() + p.winfo_width()//2 - 230
        y = p.winfo_y() + p.winfo_height()//2 - 180
        self.geometry(f"460x360+{x}+{y}")

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _step1(self):
        self._clear()
        tk.Frame(self, bg=C["danger"], height=5).pack(fill="x")
        tk.Label(self, text="⚠  Delete Engagement?",
                 bg=C["bg"], fg=C["danger"],
                 font=("Segoe UI", 13, "bold")).pack(pady=(20, 2))
        tk.Label(self, text="Step 1 of 2 — Review what will be removed",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack()
        tk.Frame(self, height=1, bg=C["border"]).pack(fill="x", pady=10)

        body = tk.Frame(self, bg=C["bg"], padx=28)
        body.pack(fill="both", expand=True)

        is_tax = self._eng["audit_type"] == "Tax Audit"
        ac = C["accent2"] if is_tax else C["accent"]
        card = tk.Frame(body, bg=C["panel"],
                        highlightthickness=1, highlightbackground=ac)
        card.pack(fill="x", pady=(0, 12))
        tk.Frame(card, bg=ac, height=3).pack(fill="x")
        tk.Label(card, text=eng_label(self._eng), bg=C["panel"], fg=C["text"],
                 font=("Segoe UI", 10, "bold"), padx=12, pady=8
                 ).pack(anchor="w")

        wp = self._eng.get("workpapers", {})
        ls = self._eng.get("legal_sec", {})
        pad = self._eng.get("pre_audit_docs", {})
        stats = [
            (f"{len([v for v in wp.values() if v.get('status','') not in ('','Not Started')])} workpaper entries with data", ""),
            (f"{sum(len(v.get('attachments',[])) for v in wp.values())} workpaper attachments", ""),
            (f"{sum(len(v.get('attachments',[])) for v in ls.values())} legal & sec attachments", ""),
            (f"{sum(len(v) for v in pad.values() if isinstance(v, list))} pre-audit attachments", ""),
        ]
        for txt, _ in stats:
            tk.Label(body, text="•  " + txt, bg=C["bg"], fg=C["text"],
                     font=FONT_SMALL).pack(anchor="w", pady=1)

        bar = tk.Frame(self, bg=C["bg"], padx=28, pady=14)
        bar.pack(fill="x", side="bottom")
        cancel = tk.Button(bar, text="Cancel",
            bg=C["btn_secondary"], fg=C["text"],
            activebackground=C["border"], font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=14, pady=7, bd=0,
            command=self.destroy)
        cancel.pack(side="right")
        cancel.bind("<Enter>", lambda e: cancel.config(bg=C["border"]))
        cancel.bind("<Leave>", lambda e: cancel.config(bg=C["btn_secondary"]))
        cont = tk.Button(bar, text="Continue  →",
            bg=C["btn_primary"], fg=C["bg"],
            activebackground=C["btn_hover"], font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=14, pady=7, bd=0,
            command=self._step2)
        cont.pack(side="right", padx=(0, 8))
        cont.bind("<Enter>", lambda e: cont.config(bg=C["btn_hover"]))
        cont.bind("<Leave>", lambda e: cont.config(bg=C["btn_primary"]))

    def _step2(self):
        self._clear()
        tk.Frame(self, bg=C["danger"], height=5).pack(fill="x")
        tk.Label(self, text="⚠  Confirm Deletion",
                 bg=C["bg"], fg=C["danger"],
                 font=("Segoe UI", 13, "bold")).pack(pady=(20, 2))
        tk.Label(self, text="Step 2 of 2 — This cannot be undone",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack()
        tk.Frame(self, height=1, bg=C["border"]).pack(fill="x", pady=10)

        body = tk.Frame(self, bg=C["bg"], padx=28)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Permanently delete:", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        tk.Label(body, text=eng_label(self._eng), bg=C["bg"],
                 fg=C["danger"], font=("Segoe UI", 11, "bold")
                 ).pack(anchor="w", pady=(3, 12))
        warn = tk.Frame(body, bg="#2A1A1E", padx=12, pady=8)
        warn.pack(fill="x")
        tk.Label(warn, text="All data will be removed from the .cafe file.\n"
                             "Files on disk are NOT auto-deleted.",
                 bg="#2A1A1E", fg="#FFC4CC", font=FONT_SMALL,
                 justify="left").pack(anchor="w")

        bar = tk.Frame(self, bg=C["bg"], padx=28, pady=14)
        bar.pack(fill="x", side="bottom")
        back = tk.Button(bar, text="← Back",
            bg=C["bg"], fg=C["muted"],
            activebackground=C["highlight"], font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=10, pady=7, bd=0,
            command=self._step1)
        back.pack(side="left")
        back.bind("<Enter>", lambda e: back.config(bg=C["highlight"]))
        back.bind("<Leave>", lambda e: back.config(bg=C["bg"]))
        cancel = tk.Button(bar, text="Cancel",
            bg=C["btn_secondary"], fg=C["text"],
            activebackground=C["border"], font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=14, pady=7, bd=0,
            command=self.destroy)
        cancel.pack(side="right")
        cancel.bind("<Enter>", lambda e: cancel.config(bg=C["border"]))
        cancel.bind("<Leave>", lambda e: cancel.config(bg=C["btn_secondary"]))
        confirm = tk.Button(bar, text="🗑  Delete",
            bg=C["danger"], fg="#fff",
            activebackground="#C44A4A", font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=14, pady=7, bd=0,
            command=self._do_delete)
        confirm.pack(side="right", padx=(0, 8))
        confirm.bind("<Enter>", lambda e: confirm.config(bg="#C44A4A"))
        confirm.bind("<Leave>", lambda e: confirm.config(bg=C["danger"]))

    def _do_delete(self):
        self.confirmed = True
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
# Password Dialog  (for locking / unlocking engagements)
# ══════════════════════════════════════════════════════════════════════════════

class PasswordDialog(tk.Toplevel):
    """
    Modal dialog for setting or verifying an engagement lock password.

    mode = "set"    -> two fields (password + confirm); returns the new password
    mode = "verify" -> one field; returns the password the user typed
    self.result is the entered password on success, or None if cancelled.
    """
    def __init__(self, parent, mode, eng_label_text=""):
        super().__init__(parent)
        self.result = None
        self._mode = mode
        self._eng_label = eng_label_text
        is_set = (mode == "set")
        self.title("Lock Engagement" if is_set else "Unlock Engagement")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        h = 320 if is_set else 260
        self.geometry(f"440x{h}")
        self._center(parent, 440, h)
        self._build()
        self.bind("<Return>", lambda e: self._submit())
        self.bind("<Escape>", lambda e: self._cancel())
        self.wait_window()

    def _center(self, p, w, h):
        self.update_idletasks()
        x = p.winfo_x() + p.winfo_width()//2 - w//2
        y = p.winfo_y() + p.winfo_height()//2 - h//2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        is_set = (self._mode == "set")
        accent = C["accent2"] if is_set else C["accent"]
        tk.Frame(self, bg=accent, height=5).pack(fill="x")

        icon = "🔒" if is_set else "🔓"
        title = "Lock Engagement" if is_set else "Unlock Engagement"
        tk.Label(self, text=f"{icon}  {title}", bg=C["bg"], fg=accent,
                 font=("Segoe UI", 13, "bold")).pack(pady=(18, 2))
        subtitle = ("Set a password to protect this engagement"
                    if is_set else
                    "Enter the password to unlock this engagement")
        tk.Label(self, text=subtitle, bg=C["bg"], fg=C["muted"],
                 font=FONT_SMALL).pack()

        if self._eng_label:
            tk.Label(self, text=self._eng_label, bg=C["bg"], fg=C["text"],
                     font=("Segoe UI", 9, "italic")).pack(pady=(4, 0))

        tk.Frame(self, height=1, bg=C["border"]).pack(fill="x", pady=12)

        body = tk.Frame(self, bg=C["bg"], padx=28)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Password", bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self._pw1 = tk.Entry(body, show="•",
            bg=C["input_bg"], fg=C["text"], insertbackground=C["accent"],
            relief="flat", font=FONT_BODY, highlightthickness=1,
            highlightbackground=C["input_border"], highlightcolor=C["accent"])
        self._pw1.pack(fill="x", ipady=6, pady=(2, 8))

        if is_set:
            tk.Label(body, text="Confirm Password", bg=C["bg"], fg=C["muted"],
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            self._pw2 = tk.Entry(body, show="•",
                bg=C["input_bg"], fg=C["text"], insertbackground=C["accent"],
                relief="flat", font=FONT_BODY, highlightthickness=1,
                highlightbackground=C["input_border"], highlightcolor=C["accent"])
            self._pw2.pack(fill="x", ipady=6, pady=(2, 8))

        self._err = tk.Label(body, text="", bg=C["bg"], fg=C["danger"],
                             font=FONT_SMALL)
        self._err.pack(anchor="w", pady=(2, 0))

        bar = tk.Frame(self, bg=C["bg"], padx=28, pady=14)
        bar.pack(fill="x", side="bottom")
        cancel = tk.Button(bar, text="Cancel",
            bg=C["btn_secondary"], fg=C["text"],
            activebackground=C["border"], font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=14, pady=7, bd=0,
            command=self._cancel)
        cancel.pack(side="right")
        cancel.bind("<Enter>", lambda e: cancel.config(bg=C["border"]))
        cancel.bind("<Leave>", lambda e: cancel.config(bg=C["btn_secondary"]))
        ok_text = "Lock  🔒" if is_set else "Unlock  🔓"
        ok = tk.Button(bar, text=ok_text,
            bg=accent, fg=C["bg"],
            activebackground=C["btn_hover"], font=FONT_LABEL,
            relief="flat", cursor="hand2", padx=14, pady=7, bd=0,
            command=self._submit)
        ok.pack(side="right", padx=(0, 8))
        ok.bind("<Enter>", lambda e: ok.config(bg=C["btn_hover"]))
        ok.bind("<Leave>", lambda e: ok.config(bg=accent))

        self.after(50, self._pw1.focus_set)

    def _submit(self):
        pw1 = self._pw1.get()
        if not pw1:
            self._err.config(text="Password cannot be empty.")
            return
        if self._mode == "set":
            pw2 = self._pw2.get()
            if pw1 != pw2:
                self._err.config(text="Passwords do not match.")
                self._pw2.delete(0, "end")
                self._pw2.focus_set()
                return
            if len(pw1) < 4:
                self._err.config(text="Password must be at least 4 characters.")
                return
        self.result = pw1
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
# Engagement Window  (Toplevel with all working tabs)
# ══════════════════════════════════════════════════════════════════════════════

class EngagementWindow(tk.Toplevel):
    """
    Dedicated maximised window for one engagement.
    Contains tabs: Workpapers | Pre-Audit Documents | Legal & Secretarial (stat) | Variance
    """

    def __init__(self, parent_panel, eng, data, filepath):
        super().__init__()
        self._panel    = parent_panel   # DetailPanel reference (for save/refresh)
        self._eng      = eng
        self._data     = data
        self._filepath = filepath
        self._is_tax   = (eng["audit_type"] == "Tax Audit")
        self._accent   = C["accent2"] if self._is_tax else C["accent"]
        self._items    = items_for_eng(eng)
        self._num_lbl  = "Clause" if self._is_tax else "Note"

        # Per-window state
        self._wp_widgets      = {}   # key → {status, text}
        self._row_frames      = {}   # key → {row, strip, body, num_lbl, name_lbl}
        self._current_clause  = None
        self._content_area    = None
        self._placeholder     = None
        self._progress_lbl    = None
        self._show_hidden     = False
        self._sort_order      = "asc"      # "default" | "asc" | "desc"
        self._active_traces   = []   # (StringVar, trace_id) to cancel on clause switch

        self.title(f"{data.get('company_name','')}  ·  {eng_label(eng)}")
        self.configure(bg=C["bg"])
        self.state("zoomed")
        self.minsize(960, 600)

        self._build_top_bar()
        self._build_notebook()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Top bar ───────────────────────────────────────────────────────────────
    def _build_top_bar(self):
        top = tk.Frame(self, bg=C["sidebar"], pady=10, padx=20)
        top.pack(fill="x")
        tk.Frame(top, bg=self._accent, width=5).pack(side="left", fill="y")
        info = tk.Frame(top, bg=C["sidebar"], padx=14)
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=self._data.get("company_name", ""),
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        tk.Label(info, text=eng_label(self._eng),
                 bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")

        def _do_save():
            self._flush_clause()
            self._panel._invalidate_cache(self._eng.get("id"))
            self._panel._save()
            self._panel._rebuild_all_cards()
            self._panel._build_left_panel()

        close_btn = tk.Button(top, text="✕  Close",
            bg=C["btn_secondary"], fg=C["text"],
            activebackground=C["border"], font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", bd=0, padx=14, pady=6,
            command=self._on_close)
        close_btn.pack(side="right")
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg=C["border"]))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=C["btn_secondary"]))

        if not self._eng.get("locked", False):
            save_btn = tk.Button(top, text="💾  Save",
                bg=self._accent, fg=C["bg"],
                activebackground=C["btn_hover"], font=("Segoe UI", 9, "bold"),
                relief="flat", cursor="hand2", bd=0, padx=16, pady=6,
                command=_do_save)
            save_btn.pack(side="right", padx=(0, 8))
            save_btn.bind("<Enter>", lambda e: save_btn.config(bg=C["btn_hover"]))
            save_btn.bind("<Leave>", lambda e: save_btn.config(bg=self._accent))

        # Lock/Unlock toggle button
        is_locked = self._eng.get("locked", False)
        lock_text = "🔓  Unlock" if is_locked else "🔒  Lock"
        lock_fg   = C["accent"]  if is_locked else C["muted"]
        lock_btn  = tk.Button(top, text=lock_text,
            bg=C["btn_secondary"], fg=lock_fg,
            activebackground=C["border"], font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2", bd=0, padx=14, pady=6,
            command=self._toggle_lock_from_window)
        lock_btn.pack(side="right", padx=(0, 8))
        lock_btn.bind("<Enter>", lambda e: lock_btn.config(bg=C["border"]))
        lock_btn.bind("<Leave>", lambda e: lock_btn.config(bg=C["btn_secondary"]))


    def _toggle_lock_from_window(self):
        """Lock or unlock from inside the engagement window, then reopen."""
        is_locked = self._eng.get("locked", False)
        label = eng_label(self._eng)
        if is_locked:
            dlg = PasswordDialog(self, mode="verify", eng_label_text=label)
            if dlg.result is None:
                return
            if not _verify_password(dlg.result, self._eng):
                messagebox.showerror("Incorrect Password",
                    "The password you entered is incorrect.", parent=self)
                return
            self._eng["locked"] = False
            self._eng.pop("lock_password_hash", None)
        else:
            dlg = PasswordDialog(self, mode="set", eng_label_text=label)
            if dlg.result is None:
                return
            self._eng["lock_password_hash"] = _hash_password(
                dlg.result, self._eng.get("id", ""))
            self._eng["locked"] = True
        self._panel._mark_dirty()
        self._panel._invalidate_cache(self._eng.get("id"))
        self._panel._save()
        self._panel._rebuild_all_cards()
        self._panel._build_left_panel()
        # Reopen the window to reflect new state
        self.destroy()
        self._panel._open_eng_window(self._eng)

    def _apply_lock(self):
        """Disable all interactive widgets in this window when engagement is locked."""
        EDITABLE = (tk.Entry, tk.Text, ttk.Combobox)
        CLICKABLE = (tk.Button, ttk.Button)
        SKIP_TEXT = {"✕  Close", "🔒  Lock", "🔓  Unlock",
                     "💾  Save", "🖨  Print", "↗ Open", "📄  Template"}

        def _walk(widget):
            for child in widget.winfo_children():
                cls = type(child)
                if cls in EDITABLE:
                    child.config(state="disabled")
                elif cls in CLICKABLE:
                    # Keep Close, Lock/Unlock, and Print buttons active
                    lbl = child.cget("text") if hasattr(child, "cget") else ""
                    if any(s in lbl for s in SKIP_TEXT):
                        pass
                    else:
                        child.config(state="disabled", cursor="arrow")
                _walk(child)

        _walk(self)

    # ══════════════════════════════════════════════════════════════════════════
    # Print helpers
    # ══════════════════════════════════════════════════════════════════════════

    # Track all temp print files so they can be deleted on exit
    _temp_print_files: list = []

    def _print_html(self, title, body_html):
        """Write a styled HTML file to a temp path and open in the browser."""
        company = self._data.get("company_name", "")
        label   = eng_label(self._eng)
        cin     = self._data.get("company_cin", "")
        addr    = self._data.get("company_addr", "")
        firm    = self._eng.get("firm_name", "")
        cin_line  = f'<p style="margin:2px 0 0;color:#6B7E94;font-size:.78rem">CIN: {html.escape(cin)}</p>' if cin else ""
        addr_line = f'<p style="margin:2px 0 0;color:#6B7E94;font-size:.78rem">{html.escape(addr)}</p>' if addr else ""
        firm_line = f'<div style="border-top:1px solid #243447;margin:32px 36px 0;padding:14px 0 20px;text-align:center"><span style="color:#6B7E94;font-size:.9rem">{html.escape(firm)}</span></div>' if firm else ""
        css = """
        body{font-family:'Segoe UI',Arial,sans-serif;background:#fff;color:#1a2332;margin:0;padding:0}
        .hdr{background:#0F1923;color:#1DB8A8;padding:18px 36px;display:flex;justify-content:space-between;align-items:flex-end}
        .hdr h1{margin:0;font-size:1.1rem;font-weight:700}
        .hdr p{margin:0;font-size:.8rem;color:#6B7E94}
        .content{padding:32px 36px;max-width:960px}
        h2{font-size:1rem;color:#1DB8A8;border-bottom:1px solid #e2e8f0;padding-bottom:6px;margin-top:28px}
        h3{font-size:.9rem;color:#243447;margin:18px 0 6px}
        .badge{display:inline-block;padding:3px 10px;border-radius:3px;font-size:.75rem;font-weight:700;margin-left:10px}
        .b-completed{background:#2ECC71;color:#fff}
        .b-in-progress{background:#F4A633;color:#fff}
        .b-not-started{background:#4A6275;color:#fff}
        .b-na{background:#6B7E94;color:#fff}
        .b-compliant{background:#2ECC71;color:#fff}
        .b-non-compliant{background:#E05C5C;color:#fff}
        .b-not-checked{background:#6B7E94;color:#fff}
        .obs{background:#f7f9fc;border-left:3px solid #1DB8A8;padding:12px 16px;white-space:pre-wrap;font-size:.9rem;line-height:1.6}
        .proc{background:#f7f9fc;border-left:3px solid #F4A633;padding:12px 16px;white-space:pre-wrap;font-size:.9rem;line-height:1.6}
        .files ul{list-style:none;padding:0;margin:0}
        .files li{padding:4px 0;font-size:.85rem;border-bottom:1px solid #eee}
        table{width:100%;border-collapse:collapse;font-size:.88rem}
        th{background:#162030;color:#1DB8A8;padding:8px 10px;text-align:left}
        td{padding:7px 10px;border-bottom:1px solid #e2e8f0}
        tr.total td{background:#e8f0fe;font-weight:700}
        tr.section-hdr td{background:#f1f5f9;color:#6B7E94;font-size:.78rem;font-weight:700;padding:5px 10px}
        .pos{color:#2ECC71;font-weight:700} .neg{color:#E05C5C;font-weight:700}
        @media print{body{margin:0} .hdr{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
        """
        full_html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{html.escape(title)}</title>
<style>{css}</style></head><body>
<div class="hdr">
  <div><h1>{html.escape(company)}</h1>{cin_line}{addr_line}<p style="margin:4px 0 0;color:#6B7E94;font-size:.78rem">{html.escape(label)}</p></div>
  <div style="text-align:right"><p style="color:#1DB8A8;font-weight:700">{html.escape(title)}</p></div>
</div>
<div class="content">{body_html}</div>
{firm_line}
</body></html>"""
        import tempfile
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=".html", mode="w", encoding="utf-8")
        tmp.write(full_html)
        tmp.close()
        EngagementWindow._temp_print_files.append(tmp.name)
        webbrowser.open(f"file:///{tmp.name.replace(os.sep, '/')}")

    def _status_badge(self, status):
        cls = {
            "Completed":     "b-completed",
            "In Progress":   "b-in-progress",
            "Not Started":   "b-not-started",
            "N/A":           "b-na",
            "Compliant":     "b-compliant",
            "Non-Compliant": "b-non-compliant",
            "Not Checked":   "b-not-checked",
        }.get(status, "b-not-started")
        return f'<span class="badge {cls}">{html.escape(status)}</span>'

    def _att_list_html(self, files):
        if not files:
            return ""
        items = "".join(f"<li>📎 {html.escape(f)}</li>" for f in files)
        return f'<div class="files"><h3>Attachments</h3><ul>{items}</ul></div>'

    # ── Print: single clause / note ───────────────────────────────────────────
    def _print_clause(self, key, num, name):
        wp    = self._eng["workpapers"].get(key, {})
        is_tax = self._is_tax
        d_num  = num if is_tax else (wp.get("display_num") or str(num))
        d_name = name if is_tax else (wp.get("display_name") or name)
        status = wp.get("status", "Not Started")
        proc   = wp.get("process_notes", get_process_note(key, self._eng))
        obs    = wp.get("observations", "")
        files  = wp.get("attachments", [])

        body = f"""
<h2>{html.escape(self._num_lbl)} {html.escape(str(d_num))}: {html.escape(d_name)}
  {self._status_badge(status)}</h2>
<h3>Process Notes</h3>
<div class="proc">{html.escape(proc) if proc else '<i style="color:#9DAFC0">Not filled in.</i>'}</div>
<h3>Observations / Working Notes</h3>
<div class="obs">{html.escape(obs) if obs else '<i style="color:#9DAFC0">No observations recorded.</i>'}</div>
{self._att_list_html(files)}"""
        self._print_html(f"{self._num_lbl} {d_num}", body)

    # ── Print: all clauses / notes summary ────────────────────────────────────
    def _print_all_workpapers(self):
        wp    = self._eng.get("workpapers", {})
        rows  = ""
        for num, name in self._items:
            key    = f"{'cl' if self._is_tax else 'note'}_{num}"
            entry  = wp.get(key, {})
            d_num  = num if self._is_tax else (entry.get("display_num") or str(num))
            d_name = name if self._is_tax else (entry.get("display_name") or name)
            status = entry.get("status", "Not Started")
            obs    = entry.get("observations", "")
            proc   = entry.get("process_notes", get_process_note(key, self._eng))
            atts   = len(entry.get("attachments", []))
            att_str = f" 📎{atts}" if atts else ""
            rows += f"""
<tr>
  <td><b>{html.escape(str(d_num))}</b></td>
  <td>{html.escape(d_name)}</td>
  <td>{self._status_badge(status)}</td>
  <td style="font-size:.82rem;white-space:pre-wrap">{html.escape(obs[:120] + ('…' if len(obs)>120 else ''))}</td>
  <td style="text-align:center">{att_str}</td>
</tr>"""
        # Custom notes
        if not self._is_tax:
            custom_keys = sorted(
                [k for k in wp if k.startswith("note_CUSTOM_")],
                key=lambda k: wp[k].get("display_num", "").lower()
            )
            if custom_keys:
                rows += """<tr><td colspan="5" style="background:#1a2d42;color:#6B7E94;font-size:.78rem;padding:5px 10px;font-weight:700">CUSTOM NOTES</td></tr>"""
                for k in custom_keys:
                    entry  = wp.get(k, {})
                    d_num  = entry.get("display_num", "?")
                    d_name = entry.get("display_name", "Custom Note")
                    status = entry.get("status", "Not Started")
                    obs    = entry.get("observations", "")
                    atts   = len(entry.get("attachments", []))
                    att_str = f" 📎{atts}" if atts else ""
                    rows += f"""
<tr>
  <td><b>{html.escape(str(d_num))}</b></td>
  <td>{html.escape(d_name)}</td>
  <td>{self._status_badge(status)}</td>
  <td style="font-size:.82rem;white-space:pre-wrap">{html.escape(obs[:120] + ("…" if len(obs)>120 else ""))}</td>
  <td style="text-align:center">{att_str}</td>
</tr>"""

        body = f"""
<h2>{"Form 3CD Clauses" if self._is_tax else "Notes to Accounts"} — Summary</h2>
<table>
  <thead><tr>
    <th style="width:60px">{self._num_lbl}</th>
    <th>Description</th><th style="width:110px">Status</th>
    <th>Observation (preview)</th><th style="width:60px">Files</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>"""
        self._print_html(f"All {self._num_lbl}s — Summary", body)


    # ══════════════════════════════════════════════════════════════════════════
    # IFC CHECKLIST — Print + Build
    # ══════════════════════════════════════════════════════════════════════════

    def _print_ifc(self):
        ifc   = self._eng.get("ifc", {})
        label = eng_label(self._eng)
        body  = ""
        for sec_key, sec_name, questions in IFC_CHECKLISTS:
            sec_data = ifc.get(sec_key, {})
            rows = ""
            for q_key, q_text in questions:
                q = sec_data.get(q_key, {})
                if q.get("na"):
                    resp = "<span style='color:#888'>N/A</span>"
                    dot  = "⬜"
                else:
                    r = q.get("response", "")
                    dot  = "✅" if r == "Yes" else ("❌" if r == "No" else ("🔶" if r == "Partial" else "◻"))
                    resp = html.escape(r) if r else "—"
                comment = html.escape(q.get("comment","") or "—")
                files   = q.get("files", [])
                att     = html.escape(", ".join(files)) if files else "—"
                num     = q_key.replace("q_","")
                rows += f"""<tr>
  <td style='width:32px;text-align:center'>{dot}</td>
  <td style='width:28px;color:#aaa'>{num}</td>
  <td>{html.escape(q_text)}</td>
  <td style='width:70px;text-align:center'><b>{resp}</b></td>
  <td style='width:180px'>{comment}</td>
  <td style='width:100px'>{att}</td>
</tr>"""
            total    = len(questions)
            sec_d    = ifc.get(sec_key, {})
            na_cnt   = sum(1 for qk,_ in questions if sec_d.get(qk,{}).get("na"))
            ans_cnt  = sum(1 for qk,_ in questions
                          if sec_d.get(qk,{}).get("response") and not sec_d.get(qk,{}).get("na"))
            active   = total - na_cnt
            body += f"""
<h3 style='margin-top:24px;color:#1DB8A8'>{html.escape(sec_name)}</h3>
<p style='margin:2px 0 6px;color:#888;font-size:12px'>{ans_cnt}/{active} answered&nbsp;&nbsp;·&nbsp;&nbsp;{na_cnt} N/A</p>
<table style='width:100%;border-collapse:collapse;font-size:12px'>
<thead><tr style='background:#1a2a3a;color:#b0c4d4'>
  <th style='width:32px'></th><th style='width:28px'>#</th>
  <th>Question</th><th style='width:70px'>Response</th>
  <th style='width:180px'>Comment</th><th style='width:100px'>Attachments</th>
</tr></thead><tbody>{rows}</tbody></table>"""
        self._print_html("IFC Checklist", body)

    def _build_ifc(self, parent):
        self._eng.setdefault("ifc", {})
        accent = self._accent

        # ── Banner ────────────────────────────────────────────────────────────
        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=accent, height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="IFC CHECKLIST",
                 bg=C["sidebar"], fg=accent,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b, text="Internal Financial Controls — review each section.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")

        self._ifc_badge_var = tk.StringVar()
        tk.Label(banner, textvariable=self._ifc_badge_var,
                 bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="right")

        pr_ifc = tk.Button(banner, text="🖨  Print",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=self._print_ifc)
        pr_ifc.pack(side="right", padx=(0, 8))
        pr_ifc.bind("<Enter>", lambda e: pr_ifc.config(bg=C["highlight"]))
        pr_ifc.bind("<Leave>", lambda e: pr_ifc.config(bg=C["sidebar"]))

        # ── Body: sidebar + content ───────────────────────────────────────────
        # ── Not Applicable toggle
        ifc_na_btn = tk.Button(banner, text="",
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4)
        ifc_na_btn.pack(side="right", padx=(0, 6))

        body_wrap = tk.Frame(parent, bg=C["bg"])
        body_wrap.pack(fill="both", expand=True)

        body = tk.Frame(body_wrap, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left sidebar — section list
        list_out = tk.Frame(body, bg=C["sidebar"], width=220)
        list_out.pack(side="left", fill="y")
        list_out.pack_propagate(False)

        ls_cv = tk.Canvas(list_out, bg=C["sidebar"], highlightthickness=0)
        ls_sb = ttk.Scrollbar(list_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=ls_cv.yview)
        ls_cv.configure(yscrollcommand=ls_sb.set)
        ls_sb.pack(side="right", fill="y")
        ls_cv.pack(side="left", fill="both", expand=True)
        ls_inner = tk.Frame(ls_cv, bg=C["sidebar"])
        ls_win = ls_cv.create_window((0, 0), window=ls_inner, anchor="nw")
        ls_cv.bind("<Configure>",
                   lambda e, c=ls_cv, w=ls_win: c.itemconfig(w, width=e.width))
        ls_inner.bind("<Configure>",
                      lambda e, c=ls_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _mw_list(ev, c=ls_cv):
            c.yview_scroll(int(-1*(ev.delta/120)), "units")
        ls_cv.bind("<Enter>", lambda e: ls_cv.bind_all("<MouseWheel>", _mw_list))
        ls_cv.bind("<Leave>", lambda e: ls_cv.unbind_all("<MouseWheel>"))
        ls_cv.bind("<Button-4>", lambda e: ls_cv.yview_scroll(-1, "units"))
        ls_cv.bind("<Button-5>", lambda e: ls_cv.yview_scroll(+1, "units"))

        # Right content — scrollable question cards
        right = tk.Frame(body, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)

        r_cv  = tk.Canvas(right, bg=C["bg"], highlightthickness=0)
        r_sb  = ttk.Scrollbar(right, orient="vertical", style="Thin.Vertical.TScrollbar", command=r_cv.yview)
        r_cv.configure(yscrollcommand=r_sb.set)
        r_sb.pack(side="right", fill="y")
        r_cv.pack(side="left", fill="both", expand=True)
        r_inner = tk.Frame(r_cv, bg=C["bg"])
        r_win   = r_cv.create_window((0, 0), window=r_inner, anchor="nw")
        r_cv.bind("<Configure>",
                  lambda e, c=r_cv, w=r_win: c.itemconfig(w, width=e.width))
        r_inner.bind("<Configure>",
                     lambda e, c=r_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _mw_right(ev, c=r_cv):
            c.yview_scroll(int(-1*(ev.delta/120)), "units")
        r_cv.bind("<MouseWheel>", _mw_right)
        r_inner.bind("<MouseWheel>", _mw_right)

        # State
        self._ifc_current_sec  = tk.StringVar()
        self._ifc_sec_btns     = {}

        def _update_ifc_badge():
            ifc = self._eng.get("ifc", {})
            total = ans = na = 0
            for sk, _, qs in IFC_CHECKLISTS:
                sec_d = ifc.get(sk, {})
                for qk, _ in qs:
                    total += 1
                    qd = sec_d.get(qk, {})
                    if qd.get("na"):
                        na += 1
                    elif qd.get("response"):
                        ans += 1
            active = total - na
            na_txt = f"  ·  {na} N/A" if na else ""
            self._ifc_badge_var.set(f"{ans} / {active}  answered{na_txt}")

        self._ifc_update_badge = _update_ifc_badge

        def _show_section(sec_key):
            # Clear content
            for w in r_inner.winfo_children():
                w.destroy()
            # Highlight button
            for sk, btn in self._ifc_sec_btns.items():
                btn.config(bg=C["chip_hover"] if sk == sec_key else C["sidebar"],
                           fg=accent if sk == sec_key else C["muted"])
            self._ifc_current_sec.set(sec_key)
            # Find section
            sec_data_tuple = next((s for s in IFC_CHECKLISTS if s[0] == sec_key), None)
            if not sec_data_tuple:
                return
            _, sec_name, questions = sec_data_tuple
            # Section header
            hdr = tk.Frame(r_inner, bg=C["bg"], padx=24, pady=14)
            hdr.pack(fill="x")
            tk.Label(hdr, text=sec_name, bg=C["bg"], fg=accent,
                     font=("Segoe UI", 13, "bold")).pack(anchor="w")
            tk.Frame(hdr, height=1, bg=C["border"]).pack(fill="x", pady=(4, 0))
            # Render question cards
            self._eng["ifc"].setdefault(sec_key, {})
            for q_key, q_text in questions:
                self._ifc_question_card(r_inner, sec_key, q_key, q_text,
                                        accent, _update_ifc_badge, _mw_right)
            r_cv.yview_moveto(0)
            # Re-bind mousewheel to new cards
            r_inner.after(100, lambda: _rebind_mw(r_inner, _mw_right))

        def _rebind_mw(widget, fn):
            widget.bind("<MouseWheel>", fn)
            for child in widget.winfo_children():
                _rebind_mw(child, fn)

        # Build section buttons in sidebar
        tk.Frame(ls_inner, bg=C["sidebar"], height=8).pack()
        for sec_key, sec_name, questions in IFC_CHECKLISTS:
            btn = tk.Button(ls_inner, text=sec_name,
                bg=C["sidebar"], fg=C["muted"],
                activebackground=C["chip_hover"], activeforeground=accent,
                font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                bd=0, padx=14, pady=9, anchor="w",
                command=lambda sk=sec_key: _show_section(sk))
            btn.pack(fill="x", padx=4, pady=1)
            btn.bind("<Enter>", lambda e, b=btn, sk=sec_key:
                     b.config(bg=C["chip_hover"]) if self._ifc_current_sec.get() != sk else None)
            btn.bind("<Leave>", lambda e, b=btn, sk=sec_key:
                     b.config(bg=C["chip_hover"] if self._ifc_current_sec.get() == sk else C["sidebar"]))
            btn.bind("<MouseWheel>", _mw_list)
            self._ifc_sec_btns[sec_key] = btn
        tk.Frame(ls_inner, bg=C["sidebar"], height=8).pack()

        _update_ifc_badge()
        # Show first section
        if IFC_CHECKLISTS:
            _show_section(IFC_CHECKLISTS[0][0])

        # ── Wire NA toggle (after body is fully built) ─────────────────────────
        _ifc_overlay = [None]

        def _show_ifc_overlay():
            if _ifc_overlay[0] and _ifc_overlay[0].winfo_exists():
                _ifc_overlay[0].destroy()
            ov = tk.Frame(body_wrap, bg=C["sidebar"])
            ov.place(relx=0, rely=0, relwidth=1, relheight=1)
            tk.Frame(ov, bg=C["danger"], height=4).pack(fill="x")
            inner_ov = tk.Frame(ov, bg=C["sidebar"])
            inner_ov.place(relx=0.5, rely=0.38, anchor="center")
            tk.Label(inner_ov, text="🚫",
                     bg=C["sidebar"], fg=C["danger"],
                     font=("Segoe UI", 36)).pack()
            tk.Label(inner_ov,
                     text="IFC Checklist — Not Applicable",
                     bg=C["sidebar"], fg=C["text"],
                     font=("Segoe UI", 15, "bold")).pack(pady=(8, 2))
            tk.Label(inner_ov,
                     text="Click ‘IFC Applicable’ in the banner above to re-enable.",
                     bg=C["sidebar"], fg=C["muted"],
                     font=("Segoe UI", 10), justify="center").pack(pady=(0, 14))
            # Remarks box
            rem_frame = tk.Frame(inner_ov, bg=C["sidebar"])
            rem_frame.pack(fill="x", padx=4)
            tk.Label(rem_frame, text="Reason not applicable:",
                     bg=C["sidebar"], fg=C["muted"],
                     font=("Segoe UI", 9, "bold"), anchor="w").pack(anchor="w")
            ifc_rem_box = tk.Text(rem_frame, height=4, width=64,
                bg=C["input_bg"], fg=C["text"], relief="flat",
                font=FONT_SMALL, insertbackground=C["accent"],
                wrap="word", padx=8, pady=6)
            ifc_rem_box.pack(fill="x", pady=(4, 0))
            saved_rem = self._eng.get("ifc_na_reason", "")
            if saved_rem:
                ifc_rem_box.insert("1.0", saved_rem)
            def _save_ifc_rem(e=None):
                self._eng["ifc_na_reason"] = ifc_rem_box.get("1.0", "end").strip()
                self._panel._mark_dirty()
            ifc_rem_box.bind("<FocusOut>", _save_ifc_rem)
            ifc_rem_box.bind("<KeyRelease>", _save_ifc_rem)
            _ifc_overlay[0] = ov

        def _hide_ifc_overlay():
            if _ifc_overlay[0] and _ifc_overlay[0].winfo_exists():
                _ifc_overlay[0].destroy()
            _ifc_overlay[0] = None

        def _apply_ifc_na(is_na):
            if is_na:
                ifc_na_btn.config(
                    text="✔  IFC Applicable",
                    bg=C["success"], fg="#fff",
                    activebackground=C["success"], activeforeground="#fff")
                ifc_na_btn.bind("<Enter>", lambda e: ifc_na_btn.config(bg=C["success"]))
                ifc_na_btn.bind("<Leave>", lambda e: ifc_na_btn.config(bg=C["success"]))
                pr_ifc.config(state="disabled", fg=C["border"])
                self._ifc_badge_var.set("N/A")
                if hasattr(self, "_nb") and hasattr(self, "_tifc"):
                    self._nb.tab(self._tifc, text="  IFC Checklist (N/A)  ")
                _show_ifc_overlay()
            else:
                ifc_na_btn.config(
                    text="✕  Not Applicable",
                    bg=C["sidebar"], fg=C["muted"],
                    activebackground=C["danger"], activeforeground="#fff")
                ifc_na_btn.bind("<Enter>", lambda e: ifc_na_btn.config(bg=C["danger"], fg="#fff"))
                ifc_na_btn.bind("<Leave>", lambda e: ifc_na_btn.config(bg=C["sidebar"], fg=C["muted"]))
                pr_ifc.config(state="normal", fg=C["muted"])
                if hasattr(self, "_nb") and hasattr(self, "_tifc"):
                    self._nb.tab(self._tifc, text="  IFC Checklist  ")
                _hide_ifc_overlay()
                _update_ifc_badge()

        def _toggle_ifc_na():
            new_val = not self._eng.get("ifc_na", False)
            self._eng["ifc_na"] = new_val
            self._panel._mark_dirty()
            _apply_ifc_na(new_val)

        ifc_na_btn.config(command=_toggle_ifc_na)
        _apply_ifc_na(self._eng.get("ifc_na", False))

    def _ifc_question_card(self, parent, sec_key, q_key, q_text,
                           accent, update_badge, mw_fn):
        ifc_sec  = self._eng["ifc"].setdefault(sec_key, {})
        q_data   = ifc_sec.setdefault(q_key, {"response": "", "comment": "", "files": [], "na": False})

        is_na    = q_data.get("na", False)
        response = q_data.get("response", "")
        num      = q_key.replace("q_", "")

        # Card colours
        card_bg  = C["sidebar"] if is_na else C["panel"]

        card = tk.Frame(parent, bg=card_bg,
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x", padx=20, pady=4)
        card.bind("<MouseWheel>", mw_fn)

        # ── Header row ────────────────────────────────────────────────────────
        hdr = tk.Frame(card, bg=card_bg, padx=14, pady=8)
        hdr.pack(fill="x")
        hdr.bind("<MouseWheel>", mw_fn)

        # Dot indicator
        def _dot_color(r, na):
            if na:       return C["muted"]
            if r == "Yes":     return C["success"]
            if r == "No":      return C["danger"]
            if r == "Partial": return C["accent2"]
            return C["border"]

        dot = tk.Label(hdr, text="●", bg=card_bg,
                       fg=_dot_color(response, is_na), font=("Segoe UI", 10))
        dot.pack(side="left", padx=(0, 6))
        dot.bind("<MouseWheel>", mw_fn)

        # Question number chip
        num_lbl = tk.Label(hdr, text=f"Q{num}",
                           bg=C["highlight"], fg=C["text"],
                           font=("Segoe UI", 8, "bold"), padx=5, pady=2)
        num_lbl.pack(side="left", padx=(0, 8))
        num_lbl.bind("<MouseWheel>", mw_fn)

        # Question text — full text, wraplength updates dynamically on resize
        q_fg  = C["muted"] if is_na else C["text"]
        q_lbl = tk.Label(hdr, text=q_text, bg=card_bg, fg=q_fg,
                         font=FONT_SMALL, wraplength=700, justify="left", anchor="nw")
        q_lbl.pack(side="left", fill="x", expand=True, anchor="n")
        q_lbl.bind("<MouseWheel>", mw_fn)

        def _update_wrap(event, lbl=q_lbl):
            # Recalculate wrap width = card width minus dot+num+buttons+padding ≈ 240px
            new_w = max(200, event.width - 240)
            lbl.config(wraplength=new_w)
        card.bind("<Configure>", _update_wrap)

        # ── Right buttons ─────────────────────────────────────────────────────
        btn_frame = tk.Frame(hdr, bg=card_bg)
        btn_frame.pack(side="right", padx=(10, 0))
        btn_frame.bind("<MouseWheel>", mw_fn)

        # Response buttons: Yes / No / Partial
        resp_btns = {}
        resp_colors = {"Yes": C["success"], "No": C["danger"], "Partial": C["accent2"]}

        def _set_response(r, dk=q_key, sk=sec_key):
            qd = self._eng["ifc"][sk][dk]
            if qd.get("na"):
                return
            qd["response"] = r if qd.get("response") != r else ""
            _refresh_card()
            update_badge()

        for resp_val in IFC_RESPONSES:
            rc = resp_colors[resp_val]
            is_active = (response == resp_val and not is_na)
            rb = tk.Button(btn_frame, text=resp_val,
                bg=rc if is_active else C["btn_secondary"],
                fg=C["bg"] if is_active else C["muted"],
                font=("Segoe UI", 7, "bold"), relief="flat",
                cursor="hand2", padx=7, pady=3, bd=0,
                state="disabled" if is_na else "normal",
                command=lambda rv=resp_val: _set_response(rv))
            rb.pack(side="left", padx=(0, 3))
            rb.bind("<MouseWheel>", mw_fn)
            resp_btns[resp_val] = rb

        # N/A toggle
        na_btn_bg  = C["danger"] if is_na else C["sidebar"]
        na_btn_fg  = C["bg"]    if is_na else C["muted"]
        na_btn_txt = "✕ N/A" if is_na else "N/A"
        na_btn = tk.Button(btn_frame, text=na_btn_txt,
            bg=na_btn_bg, fg=na_btn_fg,
            font=("Segoe UI", 7, "bold"), relief="flat",
            cursor="hand2", padx=7, pady=3, bd=0)
        na_btn.pack(side="left", padx=(6, 0))
        na_btn.bind("<MouseWheel>", mw_fn)

        # ── Expandable body (comment + attach) ────────────────────────────────
        body_frame = tk.Frame(card, bg=card_bg)
        # Show body if there's content already
        has_content = (q_data.get("comment","").strip() or q_data.get("files",[]))
        if has_content and not is_na:
            body_frame.pack(fill="x", padx=14, pady=(0, 8))

        # Comment row
        comment_row = tk.Frame(body_frame, bg=card_bg)
        comment_row.pack(fill="x", pady=(0, 4))
        tk.Label(comment_row, text="Comment:", bg=card_bg, fg=C["muted"],
                 font=FONT_SMALL, width=9, anchor="w").pack(side="left")
        comment_var = tk.StringVar(value=q_data.get("comment", ""))
        c_entry = tk.Entry(comment_row, textvariable=comment_var,
                           bg=C["input_bg"], fg=C["text"],
                           insertbackground=accent, relief="flat",
                           font=FONT_SMALL, highlightthickness=1,
                           highlightbackground=C["input_border"],
                           highlightcolor=accent,
                           state="disabled" if is_na else "normal")
        c_entry.pack(side="left", fill="x", expand=True)

        def _save_comment(*_, dk=q_key, sk=sec_key, cv=comment_var):
            self._eng["ifc"][sk][dk]["comment"] = cv.get()
            self._panel._mark_dirty()

        comment_var.trace_add("write", _save_comment)

        # Files row
        files_row = tk.Frame(body_frame, bg=card_bg)
        files_row.pack(fill="x")

        att_btn = tk.Button(files_row, text="＋  Attach",
            bg=C["highlight"], fg=accent,
            activebackground=C["list_sel"], activeforeground=accent,
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=8, pady=3, bd=0,
            state="disabled" if is_na else "normal")
        att_btn.pack(side="right")
        att_btn.bind("<MouseWheel>", mw_fn)

        def _refresh_files(dk=q_key, sk=sec_key, fr=files_row, ab=att_btn):
            for w in fr.winfo_children():
                if w is not ab:
                    w.destroy()
            fl = self._eng["ifc"][sk][dk].get("files", [])
            for fname in fl:
                ak = f"{sk}_q_{dk.replace('q_', '')}"
                self._att_row(fr, ak, fname,
                              lambda: _refresh_card(), "ifc")
            update_badge()

        ifc_att_key = f"{sec_key}_q_{num}"

        def _do_attach(ak=ifc_att_key, rf=_refresh_files):
            self._attach(ak, rf, "ifc")

        att_btn.config(command=_do_attach)

        # Toggle body visibility (click on question label)
        body_visible = [bool(has_content and not is_na)]

        def _toggle_body(event=None):
            if is_na:
                return
            if body_visible[0]:
                body_frame.pack_forget()
                body_visible[0] = False
            else:
                body_frame.pack(fill="x", padx=14, pady=(0, 8))
                body_visible[0] = True

        q_lbl.bind("<Button-1>", _toggle_body)
        q_lbl.config(cursor="hand2")

        # N/A toggle logic
        def _toggle_na(dk=q_key, sk=sec_key):
            qd = self._eng["ifc"][sk][dk]
            new_na = not qd.get("na", False)
            qd["na"] = new_na
            _refresh_card()
            update_badge()

        na_btn.config(command=_toggle_na)

        # Full card refresh
        def _refresh_card(dk=q_key, sk=sec_key):
            qd      = self._eng["ifc"][sk][dk]
            _na     = qd.get("na", False)
            _resp   = qd.get("response", "")
            bg_new  = C["sidebar"] if _na else C["panel"]
            card.config(bg=bg_new)
            hdr.config(bg=bg_new)
            dot.config(bg=bg_new, fg=_dot_color(_resp, _na))
            q_lbl.config(bg=bg_new, fg=C["muted"] if _na else C["text"])
            num_lbl.config(bg=C["highlight"])
            btn_frame.config(bg=bg_new)
            body_frame.config(bg=bg_new)
            comment_row.config(bg=bg_new)
            for w in comment_row.winfo_children():
                if isinstance(w, tk.Label):
                    w.config(bg=bg_new)
            files_row.config(bg=bg_new)
            c_entry.config(state="disabled" if _na else "normal",
                           bg=C["input_bg"] if not _na else bg_new)
            att_btn.config(state="disabled" if _na else "normal")
            for rv, rb in resp_btns.items():
                rc = resp_colors[rv]
                is_act = (_resp == rv and not _na)
                rb.config(bg=rc if is_act else C["btn_secondary"],
                          fg=C["bg"] if is_act else C["muted"],
                          state="disabled" if _na else "normal")
            na_btn.config(text="✕ N/A" if _na else "N/A",
                          bg=C["danger"] if _na else C["sidebar"],
                          fg=C["bg"] if _na else C["muted"])
            if _na:
                body_frame.pack_forget()
                body_visible[0] = False
            _refresh_files()

        _refresh_files()


    # ── Print: pre-audit documents ────────────────────────────────────────────
    def _print_pre_audit(self):
        is_tax = self._is_tax
        docs   = PRE_AUDIT_DOCS_TAX if is_tax else PRE_AUDIT_DOCS_STAT
        pad    = self._eng.get("pre_audit_docs", {})
        rows   = ""
        for doc_key, doc_name in docs:
            pk    = f"pad_{doc_key}"
            files = pad.get(pk, [])
            att   = f"📎 {', '.join(files)}" if files else "—"
            tick  = "✓" if files else "○"
            color = "#2ECC71" if files else "#9DAFC0"
            rows += f"""<tr>
  <td style="color:{color};font-weight:700;font-size:1rem">{tick}</td>
  <td>{html.escape(doc_name)}</td>
  <td style="font-size:.82rem;color:#6B7E94">{html.escape(att[:80])}</td>
</tr>"""
        n_att = sum(1 for k, _ in docs if pad.get(f"pad_{k}"))
        body = f"""
<h2>Pre-Audit Documents
  <span style="font-size:.85rem;color:#6B7E94;margin-left:14px">
    {n_att} / {len(docs)} attached
  </span>
</h2>
<table>
  <thead><tr><th style="width:36px"></th><th>Document</th><th>Files Attached</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""
        self._print_html("Pre-Audit Documents", body)

    # ── Print: legal & secretarial ────────────────────────────────────────────
    def _print_legal_sec(self):
        ls    = self._eng.get("legal_sec", {})
        body  = "<h2>Legal & Secretarial Compliance</h2>"
        section = ""
        for key, label, kind in LEGAL_SEC_ITEMS:
            if kind == "header":
                body += f"<h3 style='margin-top:22px;color:#243447'>{html.escape(label)}</h3>"
                body += '<table><thead><tr><th style="width:36%">Item</th><th style="width:110px">Status</th><th>Notes</th><th style="width:60px">Files</th></tr></thead><tbody>'
                section = key
            else:
                entry  = ls.get(key, {})
                status = entry.get("status", "Not Checked")
                notes  = entry.get("notes", "")
                atts   = len(entry.get("attachments", []))
                att_s  = f"📎 {atts}" if atts else "—"
                body  += f"""<tr>
  <td>{html.escape(label)}</td>
  <td>{self._status_badge(status)}</td>
  <td style="font-size:.82rem;white-space:pre-wrap">{html.escape(notes[:120] + ('…' if len(notes)>120 else ''))}</td>
  <td style="text-align:center">{att_s}</td>
</tr>"""
        # Close last table
        body += "</tbody></table>"
        items    = [k for k, _, t in LEGAL_SEC_ITEMS if t == "item"]
        comp     = sum(1 for k in items if ls.get(k, {}).get("status") == "Compliant")
        non_comp = sum(1 for k in items if ls.get(k, {}).get("status") == "Non-Compliant")
        body = f"<p>✓ Compliant: <b>{comp}</b>   ✗ Non-Compliant: <b>{non_comp}</b>   of {len(items)} items</p>" + body
        self._print_html("Legal & Secretarial Compliance", body)

    # ── Print: variance analysis ──────────────────────────────────────────────
    def _print_variance(self):
        va    = self._eng.get("variance_analysis", {})
        cy_l  = va.get("cy_label", "CY")
        py_l  = va.get("py_label", "PY")
        body  = ""
        for kind, title, tmpl in [
            ("balance_sheet", "Balance Sheet",  BALANCE_SHEET_TEMPLATE),
            ("profit_loss",   "Profit & Loss",  PL_TEMPLATE),
        ]:
            dr    = va.get(kind, {})
            rows  = ""
            for ekey, label, etype in tmpl:
                if etype == "header":
                    rows += f'<tr class="section-hdr"><td colspan="6">{html.escape(label)}</td></tr>'
                else:
                    entry = dr.get(ekey, {})
                    cy_v  = entry.get("cy", "")
                    py_v  = entry.get("py", "")
                    try:
                        cy_f = float(cy_v.replace(",","")) if cy_v.strip() else None
                        py_f = float(py_v.replace(",","")) if py_v.strip() else None
                    except ValueError:
                        cy_f = py_f = None

                    if cy_f is not None and py_f is not None:
                        diff = cy_f - py_f
                        pct  = (diff / py_f * 100) if py_f else None
                        diff_s = f"{diff:,.0f}"
                        pct_s  = f"{pct:+.1f}%" if pct is not None else "—"
                        cls    = ""
                        if etype == "total":
                            cls = 'class="total"'
                        alert  = abs(pct or 0) > VARIANCE_THRESHOLD_PCT
                        pct_cls = "neg" if alert and diff < 0 else ("pos" if alert and diff > 0 else "")
                    else:
                        diff_s = pct_s = "—"
                        cls  = 'class="total"' if etype == "total" else ""
                        pct_cls = ""

                    rows += f"""<tr {cls}>
  <td>{html.escape(label)}</td>
  <td style="text-align:right">{html.escape(cy_v or '—')}</td>
  <td style="text-align:right">{html.escape(py_v or '—')}</td>
  <td style="text-align:right">{diff_s}</td>
  <td style="text-align:right" class="{pct_cls}">{pct_s}</td>
  <td>{html.escape(entry.get('remarks', ''))}</td>
</tr>"""

            body += f"""
<h2>{html.escape(title)}</h2>
<table>
  <thead><tr>
    <th>Line Item</th>
    <th style="text-align:right">{html.escape(cy_l)}</th>
    <th style="text-align:right">{html.escape(py_l)}</th>
    <th style="text-align:right">Variance</th>
    <th style="text-align:right">%</th>
    <th>Remarks</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>"""

        self._print_html("BS & P&L Variance Analysis", body)

    # ══════════════════════════════════════════════════════════════════════════
    # FINANCIALS TAB
    # ══════════════════════════════════════════════════════════════════════════

    def _build_financials(self, parent):
        self._eng.setdefault("financials", {})
        accent = self._accent
        docs   = FINANCIALS_DOCS_TAX if self._is_tax else FINANCIALS_DOCS_STAT

        # ── Banner ──────────────────────────────────────────────────────────────────────────────
        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=accent, height=3).pack(fill="x", pady=(0, 5))
        tab_title = "FINANCIALS — TAX AUDIT" if self._is_tax else "FINANCIALS — STATUTORY AUDIT"
        sub_title  = ("Attach Form 3CD, audit reports, financial statements and supporting records."
                      if self._is_tax else
                      "Attach financial statements, audit reports, schedules and supporting documents.")
        tk.Label(left_b, text=tab_title,
                 bg=C["sidebar"], fg=accent,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b, text=sub_title,
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")

        fin_badge_var = tk.StringVar()
        tk.Label(banner, textvariable=fin_badge_var,
                 bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="right")

        # ── Scrollable body ────────────────────────────────────────────────────────────────────────────
        outer = tk.Frame(parent, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        cv = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        sv = ttk.Scrollbar(outer, orient="vertical", style="Thin.Vertical.TScrollbar", command=cv.yview)
        cv.configure(yscrollcommand=sv.set)
        sv.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(cv, bg=C["bg"])
        cwin = cv.create_window((0, 0), window=inner, anchor="nw")
        cv.bind("<Configure>", lambda e, c=cv, w=cwin: c.itemconfig(w, width=e.width))
        inner.bind("<Configure>", lambda e, c=cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _on_fin_mw(event, c=cv):
            c.yview_scroll(int(-1 * (event.delta / 120)), "units")
        outer.bind("<Enter>", lambda e: cv.bind_all("<MouseWheel>", _on_fin_mw))
        outer.bind("<Leave>", lambda e: cv.unbind_all("<MouseWheel>"))
        outer.bind("<Button-4>", lambda e: cv.yview_scroll(-1, "units"))
        outer.bind("<Button-5>", lambda e: cv.yview_scroll(+1, "units"))

        # ── Badge updater ───────────────────────────────────────────────────────────────────────────
        def _update_fin_badge():
            att   = sum(1 for k, _, _ in docs
                        if self._eng["financials"].get(k))
            total = len(docs)
            fin_badge_var.set(f"{att} / {total}  attached")

        # ── Build sections with headers ─────────────────────────────────────────────────────────
        current_section = [None]
        for doc_key, doc_name, section in docs:
            if section != current_section[0]:
                current_section[0] = section
                sec_lbl = FINANCIALS_SECTION_LABELS.get(section, section.title())
                sh = tk.Frame(inner, bg=C["bg"])
                sh.pack(fill="x", padx=24, pady=(18, 4))
                tk.Frame(sh, bg=accent, height=2).pack(fill="x")
                tk.Label(sh, text=sec_lbl,
                         bg=C["bg"], fg=accent,
                         font=("Segoe UI", 9, "bold"),
                         pady=6).pack(anchor="w")
            self._fin_card(inner, doc_key, doc_name, accent, _update_fin_badge)

        # ── Statutory checklist section (shown for statutory audits only) ─────────
        if not self._is_tax:
            cl_frame = tk.Frame(inner, bg=C["bg"])
            cl_frame.pack(fill="x", padx=24, pady=(18, 4))
            tk.Frame(cl_frame, bg=accent, height=2).pack(fill="x")
            tk.Label(cl_frame,
                     text="📋  Additional Checks",
                     bg=C["bg"], fg=accent,
                     font=("Segoe UI", 9, "bold"), pady=6).pack(anchor="w")
            for fc_key, fc_name in FIN_CHECKLIST_ITEMS:
                self._fin_checklist_card(inner, fc_key, fc_name, accent)

        tk.Frame(inner, bg=C["bg"], height=20).pack()
        _update_fin_badge()

    def _fin_card(self, parent, doc_key, doc_name, accent, update_badge):
        files   = self._eng["financials"].get(doc_key, [])
        expanded = [bool(files)]

        card = tk.Frame(parent, bg=C["panel"],
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x", padx=24, pady=3)

        hdr = tk.Frame(card, bg=C["panel"], padx=16, pady=10)
        hdr.pack(fill="x")

        dot = tk.Label(hdr, text="●",
                       bg=C["panel"],
                       fg=C["success"] if files else C["border"],
                       font=("Segoe UI", 10), cursor="hand2")
        dot.pack(side="left", padx=(0, 4))

        chev = tk.Label(hdr, text="▼" if expanded[0] else "▶",
                        bg=C["panel"], fg=C["muted"],
                        font=("Segoe UI", 8), cursor="hand2")
        chev.pack(side="left", padx=(0, 8))

        name_lbl = tk.Label(hdr, text=doc_name,
                 bg=C["panel"], fg=C["text"],
                 font=("Segoe UI", 10, "bold"), cursor="hand2")
        name_lbl.pack(side="left")

        cnt_var = tk.StringVar(value=(
            f"{len(files)} file{'s' if len(files)!=1 else ''}"
            if files else "Not attached"))
        cnt_lbl = tk.Label(hdr, textvariable=cnt_var,
                 bg=C["panel"], fg=C["muted"],
                 font=FONT_SMALL, cursor="hand2")
        cnt_lbl.pack(side="left", padx=(10, 0))

        a_btn = tk.Button(hdr, text="＋  Attach",
            bg=C["highlight"], fg=accent,
            activebackground=C["list_sel"], activeforeground=accent,
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=10, pady=4, bd=0)
        a_btn.pack(side="right")
        a_btn.bind("<Enter>", lambda e: a_btn.config(bg=C["list_sel"]))
        a_btn.bind("<Leave>", lambda e: a_btn.config(bg=C["highlight"]))

        ff = tk.Frame(card, bg=C["panel"])
        if expanded[0]:
            ff.pack(fill="x", padx=16, pady=(0, 8))

        def _refresh(k=doc_key, frame=ff, cv=cnt_var, dl=dot):
            for w in frame.winfo_children():
                w.destroy()
            fl = self._eng["financials"].get(k, [])
            cv.set(f"{len(fl)} file{'s' if len(fl)!=1 else ''}"
                   if fl else "Not attached")
            dl.config(fg=C["success"] if fl else C["border"])
            if expanded[0]:
                frame.pack(fill="x", padx=16, pady=(0, 8))
                if fl:
                    for fname in fl:
                        self._att_row(frame, k, fname, _refresh, "fin")
                else:
                    tk.Label(frame, text="No files attached yet.",
                             bg=C["panel"], fg=C["border"],
                             font=FONT_SMALL).pack(anchor="w", pady=4)
            else:
                frame.pack_forget()
            update_badge()

        def _toggle_expand(e=None):
            expanded[0] = not expanded[0]
            chev.config(text="▼" if expanded[0] else "▶")
            _refresh()

        for w in (hdr, dot, chev, name_lbl, cnt_lbl):
            w.bind("<Button-1>", _toggle_expand)

        if expanded[0]:
            _refresh()

        a_btn.config(command=lambda k=doc_key, rf=_refresh:
                     self._attach(k, rf, "fin"))
    def _fin_checklist_card(self, parent, fc_key, fc_name, accent):
        self._eng.setdefault("fin_checklist", {})
        entry  = self._eng["fin_checklist"].get(fc_key, {})
        status = entry.get("status", "Not Checked")

        card = tk.Frame(parent, bg=C["panel"],
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x", padx=24, pady=3)

        hdr = tk.Frame(card, bg=C["panel"], padx=16, pady=10)
        hdr.pack(fill="x")

        sc = FIN_CL_STATUS_COLORS.get(status, C["border"])
        dot = tk.Label(hdr, text="\u25cf", bg=C["panel"], fg=sc,
                       font=("Segoe UI", 10))
        dot.pack(side="left", padx=(0, 8))

        parts = fc_name.split(" \u2014 ", 1)
        title = parts[0].strip()
        desc  = parts[1].strip() if len(parts) > 1 else ""

        name_frame = tk.Frame(hdr, bg=C["panel"])
        name_frame.pack(side="left", fill="x", expand=True)
        tk.Label(name_frame, text=title,
                 bg=C["panel"], fg=C["text"],
                 font=("Segoe UI", 10, "bold"), anchor="w").pack(anchor="w")
        if desc:
            tk.Label(name_frame, text=desc,
                     bg=C["panel"], fg=C["muted"],
                     font=FONT_SMALL, wraplength=540,
                     justify="left", anchor="w").pack(anchor="w")

        status_var   = tk.StringVar(value=status)
        expanded     = [False]
        detail_frame = tk.Frame(card, bg=C["panel"])

        def _toggle(e=None):
            if expanded[0]:
                detail_frame.pack_forget()
                tog_btn.config(text="\u25bc  Review")
            else:
                detail_frame.pack(fill="x", padx=16, pady=(0, 10))
                tog_btn.config(text="\u25b2  Close")
            expanded[0] = not expanded[0]

        tog_btn = tk.Button(hdr, text="\u25bc  Review",
            bg=C["highlight"], fg=accent,
            activebackground=C["list_sel"], activeforeground=accent,
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=10, pady=4, bd=0, command=_toggle)
        tog_btn.pack(side="right")
        tog_btn.bind("<Enter>", lambda e: tog_btn.config(bg=C["list_sel"]))
        tog_btn.bind("<Leave>", lambda e: tog_btn.config(bg=C["highlight"]))

        tk.Label(detail_frame, text="Status:", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(8, 2))
        btn_row = tk.Frame(detail_frame, bg=C["panel"])
        btn_row.pack(anchor="w", pady=(0, 10))

        def _save_cl(k=fc_key, sv=status_var, d=dot):
            e2 = self._eng["fin_checklist"].setdefault(k, {})
            e2["status"]       = sv.get()
            e2["observations"] = obs_text.get("1.0", "end").strip()
            col = FIN_CL_STATUS_COLORS.get(sv.get(), C["border"])
            d.config(fg=col)
            self._panel._mark_dirty()

        for s in FIN_CL_STATUSES:
            col = FIN_CL_STATUS_COLORS.get(s, C["border"])
            b = tk.Button(btn_row, text=s, relief="flat", cursor="hand2",
                          bd=0, padx=10, pady=4,
                          font=("Segoe UI", 8, "bold"),
                          command=lambda sv=status_var, st=s: (sv.set(st), _save_cl()))
            b.pack(side="left", padx=(0, 4))
            def _style(b=b, col=col, s=s, sv=status_var):
                active = sv.get() == s
                b.config(bg=col  if active else C["btn_secondary"],
                         fg="#fff" if active else C["muted"],
                         activebackground=col, activeforeground="#fff")
            _style()
            status_var.trace_add("write", lambda *_, f=_style: f())

        tk.Label(detail_frame, text="Observations:", bg=C["panel"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        obs_text = tk.Text(detail_frame, height=3, relief="flat",
                           bg=C["input_bg"], fg=C["text"],
                           font=FONT_SMALL, insertbackground=C["accent"],
                           wrap="word", padx=8, pady=6,
                           highlightthickness=1,
                           highlightbackground=C["border"],
                           highlightcolor=C["accent"])
        obs_text.pack(fill="x", pady=(4, 0))
        if entry.get("observations"):
            obs_text.insert("1.0", entry["observations"])
        obs_text.bind("<FocusOut>",   lambda e: _save_cl())
        obs_text.bind("<KeyRelease>", lambda e: _save_cl())


    # ══════════════════════════════════════════════════════════════════════════
    # GUIDANCE NOTES TAB
    # ══════════════════════════════════════════════════════════════════════════

    # ══════════════════════════════════════════════════════════════════════════════
    # OTHER RESOURCES TAB  (Guidance Notes + AS & Ind AS)
    # ══════════════════════════════════════════════════════════════════════════════

    def _build_other_resources(self, parent):
        accent   = self._accent
        is_stat  = not self._is_tax

        # ── Banner ──────────────────────────────────────────────────────────────────────────────
        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=accent, height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="OTHER RESOURCES",
                 bg=C["sidebar"], fg=accent,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b,
                 text="ICAI Guidance Notes, Accounting Standards (AS & Ind AS) and other official references.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")

        src_btn = tk.Button(banner, text="\U0001f310  ICAI Website",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4,
            command=lambda: webbrowser.open("https://www.icai.org/post/guidance-notes-on-auditing-aspects"))
        src_btn.pack(side="right", padx=(0, 8))
        src_btn.bind("<Enter>", lambda e: src_btn.config(bg=C["highlight"]))
        src_btn.bind("<Leave>", lambda e: src_btn.config(bg=C["sidebar"]))

        # AS / Ind AS toggle (statutory only)
        active_sec = tk.StringVar(value="Ind AS" if self._eng.get("accounting_standard") == "Ind AS" else "AS")
        btn_indas = btn_as = None
        if is_stat:
            toggle_bar = tk.Frame(banner, bg=C["sidebar"])
            toggle_bar.pack(side="right", padx=(0, 12))
            def _make_toggle(lbl, key):
                def _click():
                    active_sec.set(key)
                    _refresh()
                b = tk.Button(toggle_bar, text=lbl,
                    font=("Segoe UI", 8, "bold"), relief="flat",
                    cursor="hand2", bd=0, padx=12, pady=5)
                b.pack(side="left", padx=(0, 4))
                b.config(command=_click)
                return b
            btn_indas = _make_toggle("Ind AS", "Ind AS")
            btn_as    = _make_toggle("AS",     "AS")

        # ── Search bar ───────────────────────────────────────────────────────────────────────────
        search_bar = tk.Frame(parent, bg=C["panel"], padx=22, pady=8)
        search_bar.pack(fill="x")
        tk.Label(search_bar, text="\U0001f50d", bg=C["panel"], fg=C["muted"],
                 font=("Segoe UI", 11)).pack(side="left", padx=(0, 8))
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_bar, textvariable=search_var,
            bg=C["input_bg"], fg=C["text"], relief="flat",
            insertbackground=C["accent"], font=("Segoe UI", 10),
            highlightthickness=1, highlightbackground=C["border"],
            highlightcolor=C["accent"])
        search_entry.pack(side="left", fill="x", expand=True, ipady=5)
        tk.Label(search_bar, text="Filter resources\u2026",
                 bg=C["panel"], fg=C["muted"], font=FONT_SMALL).pack(side="left", padx=(8, 0))

        # ── Scrollable body ───────────────────────────────────────────────────────────────────────────
        outer = tk.Frame(parent, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        cv = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        sv = ttk.Scrollbar(outer, orient="vertical", style="Thin.Vertical.TScrollbar", command=cv.yview)
        cv.configure(yscrollcommand=sv.set)
        sv.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(cv, bg=C["bg"])
        cwin = cv.create_window((0, 0), window=inner, anchor="nw")
        cv.bind("<Configure>", lambda e, c=cv, w=cwin: c.itemconfig(w, width=e.width))
        inner.bind("<Configure>", lambda e, c=cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))
        outer.bind("<Enter>", lambda e: cv.bind_all("<MouseWheel>",
            lambda ev, c=cv: c.yview_scroll(int(-1*(ev.delta/120)), "units")))
        outer.bind("<Leave>", lambda e: cv.unbind_all("<MouseWheel>"))
        outer.bind("<Button-4>", lambda e: cv.yview_scroll(-1, "units"))
        outer.bind("<Button-5>", lambda e: cv.yview_scroll(+1, "units"))

        tag_colors = {"PDF": "#E05C5C", "WEB": accent}

        def _make_row(container, title, url, tag):
            row = tk.Frame(container, bg=C["panel"],
                           highlightthickness=1, highlightbackground=C["border"])
            row.pack(fill="x", padx=24, pady=2)
            ir = tk.Frame(row, bg=C["panel"], padx=14, pady=10)
            ir.pack(fill="x")
            tc = tag_colors.get(tag, C["muted"])
            tk.Label(ir, text=f" {tag} ", bg=tc, fg="#fff",
                     font=("Segoe UI", 7, "bold")).pack(side="left", padx=(0, 10))
            tk.Label(ir, text=title, bg=C["panel"], fg=C["text"],
                     font=("Segoe UI", 9), anchor="w",
                     wraplength=620, justify="left").pack(side="left", fill="x", expand=True)
            ob = tk.Button(ir, text="\u2197 Open",
                bg=C["highlight"], fg=accent,
                activebackground=C["list_sel"], activeforeground=accent,
                font=("Segoe UI", 8, "bold"), relief="flat",
                cursor="hand2", padx=10, pady=4, bd=0,
                command=lambda u=url: webbrowser.open(u))
            ob.pack(side="right")
            ob.bind("<Enter>", lambda e, b=ob: b.config(bg=C["list_sel"]))
            ob.bind("<Leave>", lambda e, b=ob: b.config(bg=C["highlight"]))
            return row

        def _sec_header(container, icon, title, source_url=None):
            sh = tk.Frame(container, bg=C["bg"])
            sh.pack(fill="x", padx=24, pady=(18, 4))
            tk.Frame(sh, bg=accent, height=2).pack(fill="x")
            hrow = tk.Frame(sh, bg=C["bg"])
            hrow.pack(fill="x")
            tk.Label(hrow, text=f"{icon}  {title}",
                     bg=C["bg"], fg=accent,
                     font=("Segoe UI", 9, "bold"), pady=6).pack(side="left")
            if source_url:
                slb = tk.Button(hrow, text="\U0001f310  Source",
                    bg=C["bg"], fg=C["muted"],
                    activebackground=C["highlight"], activeforeground=C["text"],
                    font=("Segoe UI", 7, "bold"), relief="flat",
                    cursor="hand2", bd=0, padx=8, pady=2,
                    command=lambda u=source_url: webbrowser.open(u))
                slb.pack(side="right")
                slb.bind("<Enter>", lambda e, b=slb: b.config(bg=C["highlight"]))
                slb.bind("<Leave>", lambda e, b=slb: b.config(bg=C["bg"]))
            return sh

        # ── Guidance Notes sections ───────────────────────────────────────────────────────────────
        gn_rows = []
        gn_sec_headers = []
        for sec in ICAI_GUIDANCE_NOTES:
            sh = _sec_header(inner, sec["icon"], sec["section"])
            gn_sec_headers.append(sh)
            for title, url in sec["items"]:
                tag = "PDF" if url.endswith(".pdf") else "WEB"
                row = _make_row(inner, title, url, tag)
                gn_rows.append((row, sh, title.lower()))

        # ── AS / Ind AS sections (statutory only) ──────────────────────────────────────────────────
        as_section_frames = {}
        if is_stat:
            for sec in OTHER_RESOURCES_STAT:
                sec_key   = "Ind AS" if "Ind AS" in sec["section"] else "AS"
                sec_panel = tk.Frame(inner, bg=C["bg"])
                rows_meta = []
                _sec_header(sec_panel, sec["icon"], sec["section"], sec.get("source_url"))
                for title, url, tag in sec["items"]:
                    row = _make_row(sec_panel, title, url, tag)
                    rows_meta.append((row, title.lower()))
                as_section_frames[sec_key] = (sec_panel, rows_meta)

        tk.Frame(inner, bg=C["bg"], height=20).pack()

        # ── Filter / toggle ───────────────────────────────────────────────────────────────────────
        def _refresh(*_):
            q   = search_var.get().strip().lower()
            cur = active_sec.get() if is_stat else None

            for row_frame, _sh, title_lc in gn_rows:
                vis = not q or q in title_lc
                if vis:
                    row_frame.pack(fill="x", padx=24, pady=2)
                else:
                    row_frame.pack_forget()

            if is_stat:
                btn_indas.config(
                    bg=accent if cur == "Ind AS" else C["btn_secondary"],
                    fg="#fff"  if cur == "Ind AS" else C["muted"],
                    activebackground=accent)
                btn_as.config(
                    bg=accent if cur == "AS" else C["btn_secondary"],
                    fg="#fff"  if cur == "AS" else C["muted"],
                    activebackground=accent)
                for sk, (panel, rows_meta) in as_section_frames.items():
                    if sk == cur:
                        panel.pack(fill="x")
                        for row_frame, title_lc in rows_meta:
                            if not q or q in title_lc:
                                row_frame.pack(fill="x", padx=24, pady=2)
                            else:
                                row_frame.pack_forget()
                    else:
                        panel.pack_forget()

            inner.update_idletasks()
            cv.configure(scrollregion=(0, 0, inner.winfo_width(), inner.winfo_reqheight()))

        search_var.trace_add("write", _refresh)
        _refresh()


    # ══════════════════════════════════════════════════════════════════════════
    # SCHEDULE III CHECKLIST TAB
    # ══════════════════════════════════════════════════════════════════════════

    def _build_sch3(self, parent):
        self._eng.setdefault("sch3", {})
        accent = self._accent

        # ── Banner ────────────────────────────────────────────────────────────
        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=accent, height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="SCHEDULE III CHECKLIST",
                 bg=C["sidebar"], fg=accent,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b,
                 text="Companies Act 2013 — Additional disclosure requirements under Schedule III.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")

        self._sch3_badge_var = tk.StringVar()
        tk.Label(banner, textvariable=self._sch3_badge_var,
                 bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="right")

        pr_btn = tk.Button(banner, text="\U0001f5a8  Print",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=self._print_sch3)
        pr_btn.pack(side="right", padx=(0, 8))
        pr_btn.bind("<Enter>", lambda e: pr_btn.config(bg=C["highlight"]))
        pr_btn.bind("<Leave>", lambda e: pr_btn.config(bg=C["sidebar"]))

        # ── Body: sidebar list (left) + detail panel (right) ──────────────────
        body = tk.Frame(parent, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left sidebar
        list_out = tk.Frame(body, bg=C["sidebar"], width=240)
        list_out.pack(side="left", fill="y")
        list_out.pack_propagate(False)

        ls_cv = tk.Canvas(list_out, bg=C["sidebar"], highlightthickness=0)
        ls_sb = ttk.Scrollbar(list_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=ls_cv.yview)
        ls_cv.configure(yscrollcommand=ls_sb.set)
        ls_sb.pack(side="right", fill="y")
        ls_cv.pack(side="left", fill="both", expand=True)
        ls_inner = tk.Frame(ls_cv, bg=C["sidebar"])
        ls_win = ls_cv.create_window((0, 0), window=ls_inner, anchor="nw")
        ls_cv.bind("<Configure>",
                   lambda e, c=ls_cv, w=ls_win: c.itemconfig(w, width=e.width))
        ls_inner.bind("<Configure>",
                      lambda e, c=ls_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _mw_list(ev, c=ls_cv):
            c.yview_scroll(int(-1*(ev.delta/120)), "units")
        ls_cv.bind("<MouseWheel>", _mw_list)
        ls_inner.bind("<MouseWheel>", _mw_list)

        # Right detail panel
        right = tk.Frame(body, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)

        r_cv = tk.Canvas(right, bg=C["bg"], highlightthickness=0)
        r_sb = ttk.Scrollbar(right, orient="vertical", style="Thin.Vertical.TScrollbar", command=r_cv.yview)
        r_cv.configure(yscrollcommand=r_sb.set)
        r_sb.pack(side="right", fill="y")
        r_cv.pack(side="left", fill="both", expand=True)
        r_inner = tk.Frame(r_cv, bg=C["bg"])
        r_win = r_cv.create_window((0, 0), window=r_inner, anchor="nw")
        r_cv.bind("<Configure>",
                  lambda e, c=r_cv, w=r_win: c.itemconfig(w, width=e.width))
        r_inner.bind("<Configure>",
                     lambda e, c=r_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _mw_right(ev, c=r_cv):
            c.yview_scroll(int(-1*(ev.delta/120)), "units")
        r_cv.bind("<MouseWheel>", _mw_right)
        r_inner.bind("<MouseWheel>", _mw_right)

        # Shared state
        ctx = {
            "r_inner":    r_inner,
            "r_cv":       r_cv,
            "current":    None,
            "row_frames": {},
            "widgets":    {},
        }

        # ── Badge updater ──────────────────────────────────────────────────────
        def _update_badge():
            items = [k for k, _, t in SCH3_ITEMS if t == "item"]
            checked = sum(1 for k in items
                         if self._eng["sch3"].get(k, {}).get("status", "Not Checked") != "Not Checked")
            self._sch3_badge_var.set(f"{checked} of {len(items)} checked")

        self._sch3_update_badge = _update_badge

        # ── Placeholder ────────────────────────────────────────────────────────
        ph = tk.Label(r_inner,
                      text="Select an item from the left to review",
                      bg=C["bg"], fg=C["border"], font=("Segoe UI", 11))
        ph.place(relx=0.5, rely=0.4, anchor="center")
        ctx["placeholder"] = ph

        # ── Build sidebar list ─────────────────────────────────────────────────
        tk.Frame(ls_inner, bg=C["sidebar"], height=8).pack()
        for key, label, kind in SCH3_ITEMS:
            if kind == "header":
                tk.Frame(ls_inner, bg=C["border"], height=1).pack(fill="x", padx=8, pady=(8, 2))
                tk.Label(ls_inner, text=label,
                         bg=C["sidebar"], fg=accent,
                         font=("Segoe UI", 8, "bold"),
                         padx=14, pady=4, anchor="w",
                         wraplength=200, justify="left").pack(fill="x")
                continue

            entry  = self._eng["sch3"].get(key, {})
            status = entry.get("status", "Not Checked")
            sc     = SCH3_STATUS_COLORS.get(status, C["border"])

            row   = tk.Frame(ls_inner, bg=C["sidebar"], cursor="hand2")
            rbody = tk.Frame(row, bg=C["sidebar"], padx=10, pady=7)
            rbody.pack(fill="x")
            dot = tk.Frame(rbody, bg=sc, width=4)
            dot.pack(side="left", fill="y", padx=(0, 8))
            # Short label for sidebar (first ~55 chars)
            short = label.split(" — ")[0]
            short = short[:55] + ("…" if len(short) > 55 else "")
            lbl_w = tk.Label(rbody, text=short,
                     bg=C["sidebar"], fg=C["text"],
                     font=FONT_SMALL, wraplength=190, justify="left",
                     anchor="w", cursor="hand2")
            lbl_w.pack(side="left", fill="x", expand=True)
            row.pack(fill="x")
            ctx["row_frames"][key] = {"row": row, "rbody": rbody, "dot": dot}

            for w in (row, rbody, dot, lbl_w):
                w.bind("<Button-1>", lambda e, k=key, l=label: self._sch3_select(k, l, ctx))
                w.bind("<MouseWheel>", _mw_list)

        tk.Frame(ls_inner, bg=C["sidebar"], height=8).pack()
        _update_badge()

        # Select first item
        first = next((k for k, _, t in SCH3_ITEMS if t == "item"), None)
        if first:
            first_lbl = next(l for k, l, t in SCH3_ITEMS if k == first)
            self._sch3_select(first, first_lbl, ctx)

    def _sch3_select(self, key, label, ctx):
        # Save previous
        if ctx.get("current") and ctx["current"] in ctx["widgets"]:
            self._sch3_save(ctx["current"], ctx)

        # De-highlight old row
        prev = ctx.get("current")
        if prev and prev in ctx["row_frames"]:
            rf = ctx["row_frames"][prev]
            rf["row"].config(bg=C["sidebar"])
            rf["rbody"].config(bg=C["sidebar"])

        ctx["current"] = key

        # Highlight selected row
        if key in ctx["row_frames"]:
            rf = ctx["row_frames"][key]
            rf["row"].config(bg=C["list_sel"])
            rf["rbody"].config(bg=C["list_sel"])

        # Hide placeholder
        try:
            if ctx.get("placeholder") and ctx["placeholder"].winfo_exists():
                ctx["placeholder"].place_forget()
        except Exception:
            pass

        # Clear right panel
        for w in ctx["r_inner"].winfo_children():
            w.destroy()

        entry = self._eng["sch3"].get(key, {})

        # ── Header ─────────────────────────────────────────────────────────────
        head = tk.Frame(ctx["r_inner"], bg=C["bg"])
        head.pack(fill="x", padx=22, pady=(18, 0))
        tk.Frame(head, bg=C["accent"], width=4).pack(side="left", fill="y")
        htxt = tk.Frame(head, bg=C["bg"], padx=12)
        htxt.pack(side="left", fill="x", expand=True)
        tk.Label(htxt, text="Schedule III — Additional Disclosure",
                 bg=C["bg"], fg=C["accent"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(htxt, text=label, bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 11, "bold"),
                 wraplength=580, justify="left").pack(anchor="w", pady=(4, 0))

        tk.Frame(ctx["r_inner"], height=1, bg=C["border"]).pack(fill="x", padx=22, pady=(12, 0))
        content = tk.Frame(ctx["r_inner"], bg=C["bg"], padx=22)
        content.pack(fill="both", expand=True, pady=(10, 0))

        # ── Status buttons ─────────────────────────────────────────────────────
        tk.Label(content, text="Status:", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        status_var = tk.StringVar(value=entry.get("status", "Not Checked"))
        btn_row = tk.Frame(content, bg=C["bg"])
        btn_row.pack(anchor="w", pady=(4, 14))

        for s in SCH3_STATUSES:
            col = SCH3_STATUS_COLORS.get(s, C["border"])
            b = tk.Button(btn_row, text=s, relief="flat", cursor="hand2",
                          bd=0, padx=10, pady=4,
                          font=("Segoe UI", 8, "bold"),
                          command=lambda sv=status_var, st=s, k=key, c=ctx:
                              (sv.set(st), self._sch3_save(k, c),
                               self._sch3_update_row(k, c),
                               self._sch3_update_badge()))
            b.pack(side="left", padx=(0, 4))
            def _apply_style(b=b, col=col, s=s, sv=status_var):
                active = sv.get() == s
                b.config(bg=col  if active else C["btn_secondary"],
                         fg="#fff" if active else C["muted"],
                         activebackground=col, activeforeground="#fff")
            _apply_style()
            status_var.trace_add("write", lambda *_, f=_apply_style: f())

        # ── Observations ───────────────────────────────────────────────────────
        tk.Label(content, text="Observations:", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        obs_text = tk.Text(content, height=5, relief="flat",
                           bg=C["input_bg"], fg=C["text"],
                           font=FONT_SMALL, insertbackground=C["accent"],
                           wrap="word", padx=8, pady=6,
                           highlightthickness=1,
                           highlightbackground=C["border"],
                           highlightcolor=C["accent"])
        obs_text.pack(fill="x", pady=(4, 0))
        if entry.get("observations"):
            obs_text.insert("1.0", entry["observations"])
        obs_text.bind("<FocusOut>",   lambda e, k=key, c=ctx: self._sch3_save(k, c))
        obs_text.bind("<KeyRelease>", lambda e, k=key, c=ctx:
            (self._sch3_save(k, c), self._panel._mark_dirty()))

        # ── Attachments ────────────────────────────────────────────────────────
        att_hdr = tk.Frame(content, bg=C["bg"])
        att_hdr.pack(fill="x", pady=(14, 4))
        tk.Label(att_hdr, text="Attachments", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(side="left")
        att_btn = tk.Button(att_hdr, text="\uff0b  Attach",
            bg=C["highlight"], fg=C["accent"],
            activebackground=C["list_sel"], activeforeground=C["accent"],
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=10, pady=3, bd=0)
        att_btn.pack(side="right")
        att_btn.bind("<Enter>", lambda e: att_btn.config(bg=C["list_sel"]))
        att_btn.bind("<Leave>", lambda e: att_btn.config(bg=C["highlight"]))

        files_frame = tk.Frame(content, bg=C["bg"])
        files_frame.pack(fill="x")

        def _refresh_files(k=key, ff=files_frame):
            for w in ff.winfo_children():
                w.destroy()
            fls = self._eng.get("sch3", {}).get(k, {}).get("attachments", [])
            if not fls:
                tk.Label(ff, text="No files attached yet.",
                         bg=C["bg"], fg=C["border"],
                         font=FONT_SMALL).pack(anchor="w", pady=2)
            else:
                for fname in fls:
                    self._att_row(ff, k, fname, _refresh_files, "sch3")

        att_btn.config(command=lambda k=key, rf=_refresh_files:
                       self._attach(k, rf, "sch3"))
        _refresh_files()

        ctx["widgets"][key] = {
            "status": status_var, "obs": obs_text}

        # Re-bind mousewheel to new content
        def _rebind(widget, fn):
            widget.bind("<MouseWheel>", fn)
            for ch in widget.winfo_children():
                _rebind(ch, fn)
        _rebind(ctx["r_inner"], lambda ev, c=ctx["r_cv"]:
                c.yview_scroll(int(-1*(ev.delta/120)), "units"))

    def _sch3_save(self, key, ctx):
        w = ctx["widgets"].get(key, {})
        if not w:
            return
        entry = self._eng["sch3"].setdefault(key, {})
        entry["status"]       = w["status"].get()
        entry["observations"] = w["obs"].get("1.0", "end").strip()
        self._sch3_update_row(key, ctx)

    def _sch3_update_row(self, key, ctx):
        if key not in ctx["row_frames"]:
            return
        status = self._eng["sch3"].get(key, {}).get("status", "Not Checked")
        col    = SCH3_STATUS_COLORS.get(status, C["border"])
        ctx["row_frames"][key]["dot"].config(bg=col)

    def _sch3_update_badge(self):
        if hasattr(self, "_sch3_update_badge_fn"):
            self._sch3_update_badge_fn()
        elif hasattr(self, "_sch3_update_badge"):
            items   = [k for k, _, t in SCH3_ITEMS if t == "item"]
            checked = sum(1 for k in items
                         if self._eng["sch3"].get(k, {}).get("status", "Not Checked") != "Not Checked")
            self._sch3_badge_var.set(f"{checked} of {len(items)} checked")

    def _print_sch3(self):
        sch3  = self._eng.get("sch3", {})
        body  = ""
        cur_hdr = None
        rows_buf = ""

        def flush(hdr, rows_html):
            if not hdr:
                return ""
            return (f"<h3 style='margin-top:22px;color:#1DB8A8'>{html.escape(hdr)}</h3>"
                    f"<table style='width:100%;border-collapse:collapse;font-size:12px'>"
                    f"<thead><tr style='background:#1a2a3a;color:#b0c4d4'>"
                    f"<th style='width:28px'></th><th>Disclosure Item</th>"
                    f"<th style='width:110px'>Status</th>"
                    f"<th style='width:230px'>Observations</th></tr></thead>"
                    f"<tbody>{rows_html}</tbody></table>")

        dot_map = {"Compliant": "\u2705", "Non-Compliant": "\u274c",
                   "N/A": "\u2b1c", "Not Checked": "\u25fb"}
        col_map = {"Compliant": "#27ae60", "Non-Compliant": "#e74c3c",
                   "N/A": "#888", "Not Checked": "#aaa"}

        for key, lbl, kind in SCH3_ITEMS:
            if kind == "header":
                body += flush(cur_hdr, rows_buf)
                cur_hdr = lbl; rows_buf = ""
            else:
                e      = sch3.get(key, {})
                status = e.get("status", "Not Checked")
                obs    = html.escape(e.get("observations", "") or "\u2014")
                dot    = dot_map.get(status, "\u25fb")
                scol   = col_map.get(status, "#aaa")
                rows_buf += (f"<tr style='border-bottom:1px solid #2a3a4a'>"
                             f"<td style='text-align:center;padding:5px 2px'>{dot}</td>"
                             f"<td style='padding:5px 8px;font-size:11px'>{html.escape(lbl)}</td>"
                             f"<td style='padding:5px 4px;font-weight:bold;color:{scol}'>"
                             f"{html.escape(status)}</td>"
                             f"<td style='padding:5px 8px;color:#aaa;font-size:11px'>{obs}</td></tr>")
        body += flush(cur_hdr, rows_buf)

        item_keys = [k for k, _, t in SCH3_ITEMS if t == "item"]
        compliant = sum(1 for k in item_keys if sch3.get(k, {}).get("status") == "Compliant")
        non_comp  = sum(1 for k in item_keys if sch3.get(k, {}).get("status") == "Non-Compliant")
        na_cnt    = sum(1 for k in item_keys if sch3.get(k, {}).get("status") == "N/A")
        checked   = compliant + non_comp + na_cnt
        total     = len(item_keys)
        summary   = (f"<div style='margin-bottom:16px;padding:10px 14px;"
                     f"background:#1a2a3a;border-radius:4px;font-size:12px;color:#b0c4d4'>"
                     f"<b>Schedule III Checklist \u2014 Summary</b>&nbsp;&nbsp;"
                     f"\u2705&nbsp;Compliant: <b>{compliant}</b>&nbsp;\u00b7&nbsp;"
                     f"\u274c&nbsp;Non-Compliant: <b>{non_comp}</b>&nbsp;\u00b7&nbsp;"
                     f"\u2b1c&nbsp;N/A: <b>{na_cnt}</b>&nbsp;\u00b7&nbsp;"
                     f"Checked: <b>{checked}/{total}</b></div>")
        self._print_html("Schedule III Checklist", summary + body)


    def _on_close(self):
        self._flush_clause()
        if self._panel._dirty:
            ans = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes.\n\nSave before closing?",
                parent=self)
            if ans is None:   # Cancel — don't close
                return
            if ans:           # Yes — save then close
                self._panel._save()
        self._panel._invalidate_cache(self._eng.get("id"))
        self._panel._rebuild_all_cards()
        self._panel._build_left_panel()
        self.destroy()

    # ── Notebook ──────────────────────────────────────────────────────────────
    def _build_notebook(self):
        # Lock banner
        if self._eng.get("locked", False):
            banner = tk.Frame(self, bg=C["lock_banner_bg"], pady=8, padx=20)
            banner.pack(fill="x")
            tk.Label(banner,
                     text="🔒  This engagement is locked and is read-only.  "
                          "Click  🔓 Unlock  in the top bar to make changes.",
                     bg=C["lock_banner_bg"], fg=C["lock_banner_fg"],
                     font=("Segoe UI", 9, "bold")).pack(side="left")

        style = ttk.Style()
        style.configure("EngWin.TNotebook",
            background=C["bg"], borderwidth=0, tabmargins=0)
        style.configure("EngWin.TNotebook.Tab",
            background=C["sidebar"], foreground=C["muted"],
            padding=[22, 10], font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("EngWin.TNotebook.Tab",
            background=[("selected", C["panel"])],
            foreground=[("selected", self._accent)],
            font=[("selected", ("Segoe UI", 10, "bold"))])

        # Accent line — sits between top bar and tab strip, tinted by engagement type
        tk.Frame(self, bg=self._accent, height=2).pack(fill="x")

        self._nb = ttk.Notebook(self, style="EngWin.TNotebook")
        self._nb.pack(fill="both", expand=True, pady=(0, 0))
        nb = self._nb

        # Tab 1 — Pre-Audit Documents
        t2 = tk.Frame(nb, bg=C["bg"])
        nb.add(t2, text="  Pre-Audit Documents  ")
        self._build_pre_audit(t2)

        # Tab 2 — Financials (both audit types)
        tfin = tk.Frame(nb, bg=C["bg"])
        nb.add(tfin, text="  Financials  ")
        self._build_financials(tfin)

        # Tab 3 — Workpapers (Notes to Accounts / Form 3CD Clauses)
        wp_lbl = "  Form 3CD Clauses  " if self._is_tax else "  Notes to Accounts  "
        t1 = tk.Frame(nb, bg=C["bg"])
        nb.add(t1, text=wp_lbl)
        self._build_workpapers(t1)

        # Tab 4 — Schedule III Checklist (Statutory only)
        if not self._is_tax:
            ts3 = tk.Frame(nb, bg=C["bg"])
            nb.add(ts3, text="  Schedule III  ")
            self._build_sch3(ts3)

        # Tab 4 — IFC Checklist (Statutory only)
        if not self._is_tax:
            self._tifc = tk.Frame(nb, bg=C["bg"])
            tifc = self._tifc
            nb.add(tifc, text="  IFC Checklist  ")
            self._build_ifc(tifc)

        # Tab 5 — CARO Checklist (Statutory only)
        if not self._is_tax:
            self._tc = tk.Frame(nb, bg=C["bg"])
            tc = self._tc
            nb.add(tc, text="  CARO Checklist  ")
            self._build_caro(tc)

        # Tab 6 — Legal & Secretarial (Statutory only)
        if not self._is_tax:
            t3 = tk.Frame(nb, bg=C["bg"])
            nb.add(t3, text="  Legal & Secretarial  ")
            self._build_legal_sec(t3)

        # Tab 7 — BS & P&L Variance (Statutory only)
        if not self._is_tax:
            t4 = tk.Frame(nb, bg=C["bg"])
            nb.add(t4, text="  BS & P&L Variance  ")
            self._build_variance(t4)

        # Tab 8 — Other Resources (both audit types)
        tor = tk.Frame(nb, bg=C["bg"])
        nb.add(tor, text="  Other Resources  ")
        self._build_other_resources(tor)

        # Apply read-only state after all tabs are built
        if self._eng.get("locked", False):
            self.after(100, self._apply_lock)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — WORKPAPERS
    # ══════════════════════════════════════════════════════════════════════════

    def _build_workpapers(self, parent):
        # Banner
        banner = tk.Frame(parent, bg=C["sidebar"], padx=20, pady=10)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=self._accent, height=3).pack(fill="x", pady=(0, 5))
        title = ("FORM 3CD CLAUSES" if self._is_tax
                 else ("NOTES TO ACCOUNTS — IND AS"
                       if (self._eng.get("accounting_standard") or "AS") == "Ind AS"
                       else "NOTES TO ACCOUNTS — AS"))
        tk.Label(left_b, text=title, bg=C["sidebar"],
                 fg=self._accent, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self._progress_lbl = tk.Label(left_b, text="", bg=C["sidebar"],
                                       fg=C["muted"], font=FONT_SMALL)
        self._progress_lbl.pack(anchor="w")

        # Print All button
        def _print_all():
            self._flush_clause()
            self._print_all_workpapers()
        pr_btn = tk.Button(banner, text="🖨  Print All",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=_print_all)
        pr_btn.pack(side="right", padx=(0, 6))
        pr_btn.bind("<Enter>", lambda e: pr_btn.config(bg=C["highlight"]))
        pr_btn.bind("<Leave>", lambda e: pr_btn.config(bg=C["sidebar"]))

        # New Note button (statutory only)
        if not self._is_tax:
            new_note_btn = tk.Button(banner, text="＋  New Note",
                bg=self._accent, fg=C["bg"],
                activebackground=C["btn_hover"], activeforeground=C["bg"],
                font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
                bd=0, padx=10, pady=4, command=self._add_custom_note)
            new_note_btn.pack(side="right", padx=(0, 6))
            new_note_btn.bind("<Enter>", lambda e: new_note_btn.config(bg=C["btn_hover"]))
            new_note_btn.bind("<Leave>", lambda e: new_note_btn.config(bg=self._accent))

        # Sort toggle (statutory only)
        if not self._is_tax:
            self._sort_var = tk.StringVar(value="↑  Asc")
            self._sort_btn = tk.Button(banner, textvariable=self._sort_var,
                bg=C["sidebar"], fg=C["muted"],
                activebackground=C["highlight"], activeforeground=C["text"],
                font=FONT_SMALL, relief="flat", cursor="hand2", bd=0,
                padx=10, pady=4, command=self._cycle_sort_order)
            self._sort_btn.pack(side="right", padx=(0, 4))

        # Hidden toggle
        self._hidden_var = tk.StringVar()
        self._show_hidden = False
        hid_btn = tk.Button(banner, textvariable=self._hidden_var,
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=FONT_SMALL, relief="flat", cursor="hand2", bd=0,
            padx=10, pady=4, command=self._toggle_hidden_panel)
        hid_btn.pack(side="right")

        # Body: clause list + detail
        body = tk.Frame(parent, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left: scrollable clause list
        list_out = tk.Frame(body, bg=C["sidebar"], width=310)
        list_out.pack(side="left", fill="y")
        list_out.pack_propagate(False)

        cv = tk.Canvas(list_out, bg=C["sidebar"], highlightthickness=0)
        sb = ttk.Scrollbar(list_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)

        def _wp_scroll(e, c=cv):
            c.yview_scroll(int(-1*(e.delta/120)), "units")
        cv.bind("<MouseWheel>", _wp_scroll)
        cv.bind("<Enter>", lambda e, c=cv: c.bind_all("<MouseWheel>", _wp_scroll))
        cv.bind("<Leave>", lambda e, c=cv: c.unbind_all("<MouseWheel>"))

        self._list_inner = tk.Frame(cv, bg=C["sidebar"])
        cwin = cv.create_window((0, 0), window=self._list_inner, anchor="nw")
        cv.bind("<Configure>", lambda e, c=cv, w=cwin: c.itemconfig(w, width=e.width))
        self._list_inner.bind("<Configure>",
            lambda e, c=cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))
        cv.bind("<MouseWheel>",
            lambda e, c=cv: c.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Right: detail
        self._content_area = tk.Frame(body, bg=C["bg"])
        self._content_area.pack(side="right", fill="both", expand=True)
        self._placeholder = tk.Label(self._content_area,
            text=f"Select a {self._num_lbl.lower()} to view details",
            bg=C["bg"], fg=C["border"], font=("Segoe UI", 11))
        self._placeholder.place(relx=0.5, rely=0.5, anchor="center")

        self._rebuild_clause_list()
        self._update_progress()
        self._update_hidden_btn()

    @staticmethod
    def _note_sort_key(display_num):
        """Smart sort key: splits '2A' → (2, 'A') so numeric parts sort correctly."""
        import re
        parts = re.split(r'(\d+)', str(display_num))
        result = []
        for p in parts:
            if p.isdigit():
                result.append((0, int(p), ''))
            else:
                result.append((1, 0, p.lower()))
        return result

    def _cycle_sort_order(self):
        orders = ["asc", "desc"]
        idx = orders.index(self._sort_order) if self._sort_order in orders else 0
        self._sort_order = orders[(idx + 1) % 2]
        labels = {"asc": "↑  Asc", "desc": "↓  Desc"}
        if hasattr(self, "_sort_var"):
            self._sort_var.set(labels[self._sort_order])
        if hasattr(self, "_sort_btn"):
            self._sort_btn.config(fg=C["accent"])
        self._rebuild_clause_list()

    def _rebuild_clause_list(self):
        for w in self._list_inner.winfo_children():
            w.destroy()
        self._row_frames.clear()

        wp = self._eng.get("workpapers", {})
        hidden_keys = [k for k, v in wp.items() if v.get("hidden")]

        # Hidden banner
        if hidden_keys:
            n = len(hidden_keys)
            lbl = f"  ▸ Hidden items ({n}) — {'Hide' if self._show_hidden else 'Show'}"
            tk.Button(self._list_inner, text=lbl,
                bg=C["sidebar"], fg=C["muted"],
                activebackground=C["highlight"], activeforeground=C["text"],
                font=("Segoe UI", 8), relief="flat", cursor="hand2", bd=0,
                anchor="w", padx=14, pady=5,
                command=self._toggle_hidden_panel).pack(fill="x")
            tk.Frame(self._list_inner, bg=C["border"], height=1).pack(fill="x")

        sort = getattr(self, "_sort_order", "default")

        if sort in ("asc", "desc") and not self._is_tax:
            # ── Merged + sorted view ──────────────────────────────────────
            all_rows = []
            # Standard notes
            for num, name in self._items:
                key = f"note_{num}"
                entry = wp.get(key, {})
                disp_num  = entry.get("display_num", str(num)) or str(num)
                disp_name = entry.get("display_name", name) or name
                all_rows.append((key, disp_num, disp_name,
                                  entry.get("hidden", False), False))
            # Custom notes
            for k in wp:
                if not k.startswith("note_CUSTOM_"):
                    continue
                entry = wp[k]
                disp_num  = entry.get("display_num", "?")
                disp_name = entry.get("display_name", "Custom Note")
                all_rows.append((k, disp_num, disp_name,
                                  entry.get("hidden", False), True))

            all_rows.sort(
                key=lambda r: self._note_sort_key(r[1]),
                reverse=(sort == "desc")
            )
            for key, disp_num, disp_name, hidden, custom in all_rows:
                if hidden and not self._show_hidden:
                    continue
                self._build_clause_row(key, disp_num, disp_name, hidden, custom=custom)
        else:
            # ── Default view: standard notes first, custom section below ──
            for num, name in self._items:
                key = f"{'cl' if self._is_tax else 'note'}_{num}"
                entry = wp.get(key, {})
                hidden = entry.get("hidden", False)
                if hidden and not self._show_hidden:
                    continue
                self._build_clause_row(key, num, name, hidden)

            # Custom notes section
            if not self._is_tax:
                custom_keys = sorted(
                    [k for k in wp if k.startswith("note_CUSTOM_")],
                    key=lambda k: self._note_sort_key(wp[k].get("display_num", ""))
                )
                if custom_keys:
                    tk.Frame(self._list_inner, bg=C["border"], height=1).pack(fill="x", pady=(4, 0))
                    tk.Label(self._list_inner, text="  CUSTOM NOTES",
                             bg=C["sidebar"], fg=C["muted"],
                             font=("Segoe UI", 7, "bold")).pack(anchor="w", padx=10, pady=(4, 2))
                for k in custom_keys:
                    entry = wp.get(k, {})
                    hidden = entry.get("hidden", False)
                    if hidden and not self._show_hidden:
                        continue
                    disp_num  = entry.get("display_num", "?")
                    disp_name = entry.get("display_name", "Custom Note")
                    self._build_clause_row(k, disp_num, disp_name, hidden, custom=True)

    def _build_clause_row(self, key, num, name, hidden, custom=False):
        wp     = self._eng.get("workpapers", {})
        entry  = wp.get(key, {})
        stat   = entry.get("status", "Not Started")
        is_sel = (key == self._current_clause)

        row_bg = C["list_sel"] if is_sel else C["sidebar"]
        row   = tk.Frame(self._list_inner, bg=row_bg, cursor="hand2")
        row.pack(fill="x")
        strip_col = C["border"] if hidden else STATUS_COLORS.get(stat, C["muted"])
        strip = tk.Frame(row, bg=strip_col, width=3)
        strip.pack(side="left", fill="y")
        body = tk.Frame(row, bg=row_bg, padx=10, pady=7)
        body.pack(side="left", fill="both", expand=True)

        num_fg  = C["border"] if hidden else self._accent
        name_fg = C["border"] if hidden else C["text"]
        prefix  = "🙈  " if hidden else ""

        disp_num  = num if self._is_tax else (entry.get("display_num") or num)
        disp_name = name if self._is_tax else (entry.get("display_name") or name)

        num_lbl = tk.Label(body, text=f"{prefix}{self._num_lbl} {disp_num}",
            bg=row_bg, fg=num_fg, font=("Segoe UI", 8, "bold"))
        num_lbl.pack(anchor="w")

        short = disp_name if len(disp_name) <= 48 else disp_name[:45] + "…"
        name_lbl = tk.Label(body, text=short, bg=row_bg, fg=name_fg,
            font=FONT_SMALL, anchor="w", wraplength=240, justify="left")
        name_lbl.pack(anchor="w")

        self._row_frames[key] = {
            "row": row, "strip": strip, "body": body,
            "num_lbl": num_lbl, "name_lbl": name_lbl,
        }

        def _click(e, k=key, n=num, nm=name):
            self._select_clause(k, n, nm)

        def _rmenu(e, k=key, hd=hidden, cu=custom):
            m = tk.Menu(self, tearoff=0, bg=C["sidebar"], fg=C["text"])
            m.add_command(label="Unhide" if hd else "Hide",
                command=lambda: self._set_hidden(k, not hd))
            if cu:
                m.add_separator()
                m.add_command(label="🗑  Delete this note",
                    command=lambda: self._delete_custom_note(k))
            m.tk_popup(e.x_root, e.y_root)

        bind_tree(row, "<Button-1>", _click)
        bind_tree(row, "<Button-3>", _rmenu)

    def _select_clause(self, key, num, name):
        self._flush_clause()

        # Deselect previous — guard against stale/destroyed widget refs
        if self._current_clause and self._current_clause in self._row_frames:
            rf = self._row_frames[self._current_clause]
            for wk in ("row", "body", "num_lbl", "name_lbl"):
                try:
                    w = rf.get(wk)
                    if w and w.winfo_exists():
                        w.config(bg=C["sidebar"])
                except Exception:
                    pass

        self._current_clause = key

        # Highlight new selection — guard likewise
        if key in self._row_frames:
            rf = self._row_frames[key]
            for wk in ("row", "body", "num_lbl", "name_lbl"):
                try:
                    w = rf.get(wk)
                    if w and w.winfo_exists():
                        w.config(bg=C["list_sel"])
                except Exception:
                    pass

        # Cancel any stale StringVar traces from the previous note before clearing
        for trace_id in getattr(self, "_active_traces", []):
            try:
                trace_id[0].trace_remove("write", trace_id[1])
            except Exception:
                pass
        self._active_traces = []

        # Clear content area
        try:
            if self._placeholder and self._placeholder.winfo_exists():
                self._placeholder.place_forget()
        except Exception:
            pass
        self._placeholder = None

        for w in self._content_area.winfo_children():
            w.destroy()

        wp    = self._eng.get("workpapers", {})
        entry = wp.get(key, {})

        # ── Heading ──────────────────────────────────────────────────────────
        head = tk.Frame(self._content_area, bg=C["bg"])
        head.pack(fill="x", padx=24, pady=(18, 0))
        tk.Frame(head, bg=self._accent, width=4).pack(side="left", fill="y")
        htxt = tk.Frame(head, bg=C["bg"], padx=12)
        htxt.pack(side="left", fill="x", expand=True)

        disp_num  = entry.get("display_num") or str(num)
        disp_name = entry.get("display_name") or name

        if self._is_tax:
            # Tax audit — fixed, never editable
            tk.Label(htxt, text=f"{self._num_lbl} {num}",
                bg=C["bg"], fg=self._accent,
                font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(htxt, text=name, bg=C["bg"], fg=C["text"],
                font=("Segoe UI", 13, "bold"),
                wraplength=520, justify="left").pack(anchor="w")
        else:
            # Statutory audit — show labels, Edit → entries appear, Save commits
            num_row = tk.Frame(htxt, bg=C["bg"])
            num_row.pack(anchor="w", fill="x")

            # ── Display state (default) ──
            display_frame = tk.Frame(htxt, bg=C["bg"])
            display_frame.pack(anchor="w", fill="x")

            num_disp = tk.Label(display_frame,
                text=f"Note {disp_num}",
                bg=C["bg"], fg=self._accent,
                font=("Segoe UI", 9, "bold"))
            num_disp.pack(anchor="w")

            name_disp = tk.Label(display_frame,
                text=disp_name, bg=C["bg"], fg=C["text"],
                font=("Segoe UI", 13, "bold"),
                wraplength=520, justify="left")
            name_disp.pack(anchor="w")

            # ── Edit state (hidden until Edit clicked) ──
            edit_frame = tk.Frame(htxt, bg=C["bg"])
            # edit_frame is NOT packed yet

            nr = tk.Frame(edit_frame, bg=C["bg"])
            nr.pack(anchor="w", fill="x")
            tk.Label(nr, text="Note No.", bg=C["bg"],
                fg=self._accent,
                font=("Segoe UI", 9, "bold")).pack(side="left")
            num_var = tk.StringVar(value=disp_num)
            num_ent = tk.Entry(nr, textvariable=num_var,
                bg=C["input_bg"], fg=self._accent,
                insertbackground=self._accent, relief="flat",
                font=("Segoe UI", 9, "bold"),
                highlightthickness=1,
                highlightbackground=C["input_border"],
                highlightcolor=self._accent, width=10)
            num_ent.pack(side="left", padx=(8, 0), ipady=3)

            tk.Label(edit_frame, text="Note Name", bg=C["bg"],
                fg=C["muted"],
                font=FONT_SMALL).pack(anchor="w", pady=(8, 2))
            nm_var = tk.StringVar(value=disp_name)
            nm_ent = tk.Entry(edit_frame, textvariable=nm_var,
                bg=C["input_bg"], fg=C["text"],
                insertbackground=C["accent"], relief="flat",
                font=("Segoe UI", 12, "bold"),
                highlightthickness=1,
                highlightbackground=C["input_border"],
                highlightcolor=self._accent)
            nm_ent.pack(fill="x", ipady=5)

            # Save / Cancel row inside edit_frame
            save_row = tk.Frame(edit_frame, bg=C["bg"])
            save_row.pack(anchor="w", pady=(8, 0))

            def _enter_edit(
                    df=display_frame, ef=edit_frame,
                    eb=None):    # edit_btn ref patched below
                df.pack_forget()
                ef.pack(anchor="w", fill="x")
                num_ent.focus_set()
                num_ent.icursor("end")

            def _commit_edit(k=key, nv=num_var, nnamev=nm_var,
                              default_name=name,
                              df=display_frame, ef=edit_frame,
                              nd=num_disp, namd=name_disp):
                new_num  = nv.get().strip()     or str(num)
                new_name = nnamev.get().strip()  or default_name
                # Persist
                self._eng["workpapers"].setdefault(k, {})["display_num"]  = new_num
                self._eng["workpapers"].setdefault(k, {})["display_name"] = new_name
                self._panel._mark_dirty()
                # Refresh display labels
                nd.config(text=f"Note {new_num}")
                namd.config(text=new_name)
                # Update sidebar row
                if k in self._row_frames:
                    rf = self._row_frames[k]
                    if rf.get("num_lbl") and rf["num_lbl"].winfo_exists():
                        rf["num_lbl"].config(text=f"Note {new_num}")
                    if rf.get("name_lbl") and rf["name_lbl"].winfo_exists():
                        short = new_name if len(new_name) <= 48 else new_name[:45] + "…"
                        rf["name_lbl"].config(text=short)
                # Swap back to display view
                ef.pack_forget()
                df.pack(anchor="w", fill="x")

            def _cancel_edit(k=key, nv=num_var, nnamev=nm_var,
                             df=display_frame, ef=edit_frame):
                # Restore entry values from saved data
                ex = self._eng["workpapers"].get(k, {})
                nv.set(ex.get("display_num", str(num)) or str(num))
                nnamev.set(ex.get("display_name", name) or name)
                ef.pack_forget()
                df.pack(anchor="w", fill="x")

            # Save button
            save_btn = tk.Button(save_row, text="✓  Save",
                bg=self._accent, fg=C["bg"],
                activebackground=C["btn_hover"], activeforeground=C["bg"],
                font=("Segoe UI", 8, "bold"), relief="flat",
                cursor="hand2", bd=0, padx=12, pady=4,
                command=_commit_edit)
            save_btn.pack(side="left")
            save_btn.bind("<Enter>", lambda e: save_btn.config(bg=C["btn_hover"]))
            save_btn.bind("<Leave>", lambda e: save_btn.config(bg=self._accent))

            # Cancel button
            cancel_btn = tk.Button(save_row, text="✕  Cancel",
                bg=C["btn_secondary"], fg=C["text"],
                activebackground=C["border"], activeforeground=C["text"],
                font=("Segoe UI", 8, "bold"), relief="flat",
                cursor="hand2", bd=0, padx=12, pady=4,
                command=_cancel_edit)
            cancel_btn.pack(side="left", padx=(6, 0))
            cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg=C["border"]))
            cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg=C["btn_secondary"]))

            # Also save on Enter key in either entry
            num_ent.bind("<Return>", lambda e: _commit_edit())
            nm_ent.bind("<Return>",  lambda e: _commit_edit())
            num_ent.bind("<Escape>", lambda e: _cancel_edit())
            nm_ent.bind("<Escape>",  lambda e: _cancel_edit())

        # Action buttons (right side) — Edit only shown for statutory
        acts = tk.Frame(head, bg=C["bg"])
        acts.pack(side="right", padx=(8, 0))

        if not self._is_tax:
            edit_btn = tk.Button(acts, text="✎  Edit",
                bg=C["bg"], fg=C["muted"],
                activebackground=C["highlight"], activeforeground=C["accent"],
                font=("Segoe UI", 8, "bold"), relief="flat",
                cursor="hand2", bd=0, padx=8, pady=4,
                command=_enter_edit)
            edit_btn.pack(side="left", padx=(0, 6))
            edit_btn.bind("<Enter>", lambda e: edit_btn.config(bg=C["highlight"]))
            edit_btn.bind("<Leave>", lambda e: edit_btn.config(bg=C["bg"]))

        is_hidden = entry.get("hidden", False)

        pr_btn = tk.Button(acts, text="🖨  Print",
            bg=C["bg"], fg=C["muted"],
            activebackground=C["highlight"], font=("Segoe UI", 8, "bold"),
            relief="flat", cursor="hand2", bd=0, padx=8, pady=4,
            command=lambda k=key, n=num, nm=name: (
                self._flush_clause(),
                self._print_clause(k, n, nm)))
        pr_btn.pack(side="left", padx=(0, 6))
        pr_btn.bind("<Enter>", lambda e: pr_btn.config(bg=C["highlight"]))
        pr_btn.bind("<Leave>", lambda e: pr_btn.config(bg=C["bg"]))

        hbtn = tk.Button(acts,
            text="👁  Unhide" if is_hidden else "🙈  Hide",
            bg=C["bg"], fg=C["accent"] if is_hidden else C["muted"],
            activebackground=C["highlight"], font=("Segoe UI", 8, "bold"),
            relief="flat", cursor="hand2", bd=0, padx=8, pady=4,
            command=lambda k=key, h=is_hidden: (
                self._set_hidden(k, not h),
                self._select_clause(k, num, name)))
        hbtn.pack(side="left")
        hbtn.bind("<Enter>", lambda e: hbtn.config(bg=C["highlight"]))
        hbtn.bind("<Leave>", lambda e: hbtn.config(bg=C["bg"]))

        tk.Frame(self._content_area, height=1, bg=C["border"]
                 ).pack(fill="x", padx=24, pady=10)

        inner = tk.Frame(self._content_area, bg=C["bg"], padx=24)
        inner.pack(fill="both", expand=True)

        # ── Status buttons ────────────────────────────────────────────────────
        tk.Label(inner, text="Status:", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        status_var = tk.StringVar(value=entry.get("status", "Not Started"))
        stat_row = tk.Frame(inner, bg=C["bg"])
        stat_row.pack(anchor="w", pady=(4, 12))

        def _mk_stat_btn(s):
            col    = STATUS_COLORS[s]
            is_sel = (status_var.get() == s)
            b = tk.Button(stat_row, text=s, font=FONT_SMALL, relief="flat",
                cursor="hand2", padx=10, pady=5, bd=0,
                bg=col if is_sel else C["btn_secondary"],
                fg=C["bg"] if is_sel else C["muted"],
                activebackground=col, activeforeground=C["bg"])
            b.pack(side="left", padx=(0, 6))
            def _set(s=s):
                status_var.set(s)
                for btn2 in stat_row.winfo_children():
                    s2 = btn2.cget("text")
                    c2 = STATUS_COLORS.get(s2, C["muted"])
                    btn2.config(bg=c2 if s2==s else C["btn_secondary"],
                                fg=C["bg"] if s2==s else C["muted"])
                self._save_clause(key, status_var, obs_text)
                self._update_strip(key)
                self._update_progress()
                self._panel._mark_dirty()
            b.config(command=_set)

        for s in WORKPAPER_STATUSES:
            _mk_stat_btn(s)

        # ── Process Notes (before Observations) ──────────────────────────────
        proc_hdr = tk.Frame(inner, bg=C["bg"])
        proc_hdr.pack(fill="x", pady=(0, 0))
        tk.Label(proc_hdr, text="Process Notes",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(side="left")
        tk.Label(proc_hdr,
                 text="  Audit procedures performed, steps followed, standards referred",
                 bg=C["bg"], fg=C["border"], font=("Segoe UI", 8)).pack(side="left")
        proc_text = tk.Text(inner, height=5, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=("Segoe UI", 10), wrap="word",
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"], padx=10, pady=8)
        proc_text.pack(fill="x", pady=(4, 0))

        # Auto-fill default process notes if field is empty
        saved_proc = entry.get("process_notes", "")
        if not saved_proc:
            saved_proc = get_process_note(key, self._eng)
        proc_text.insert("1.0", saved_proc)

        # ── Observations / Working Notes ──────────────────────────────────────
        tk.Label(inner, text="Observations / Working Notes",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(10, 0))
        obs_text = tk.Text(inner, height=5, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=("Segoe UI", 10), wrap="word",
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"], padx=10, pady=8)
        obs_text.pack(fill="x", pady=(4, 0))
        obs_text.insert("1.0", entry.get("observations", ""))

        def _on_edit(e, k=key, sv=status_var, ot=obs_text, pt=proc_text):
            self._save_clause(k, sv, ot, pt)
            self._panel._mark_dirty()

        obs_text.bind("<KeyRelease>", _on_edit)
        proc_text.bind("<KeyRelease>", _on_edit)

        self._wp_widgets[key] = {"status": status_var, "text": obs_text, "proc": proc_text}

        # ── Attachments ───────────────────────────────────────────────────────
        tk.Frame(inner, height=1, bg=C["border"]).pack(fill="x", pady=(12, 0))
        ah = tk.Frame(inner, bg=C["bg"])
        ah.pack(fill="x", pady=(8, 6))
        tk.Label(ah, text="📎  Working Papers / Attachments",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        att_btn = tk.Button(ah, text="＋  Attach",
            bg=C["highlight"], fg=self._accent,
            activebackground=C["list_sel"], activeforeground=self._accent,
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            padx=10, pady=4, bd=0)
        att_btn.pack(side="right")
        att_btn.bind("<Enter>", lambda e: att_btn.config(bg=C["list_sel"]))
        att_btn.bind("<Leave>", lambda e: att_btn.config(bg=C["highlight"]))

        att_out = tk.Frame(inner, bg=C["panel"],
                           highlightthickness=1, highlightbackground=C["border"])
        att_out.pack(fill="both", expand=True, pady=(0, 4))
        att_cv = tk.Canvas(att_out, bg=C["panel"], highlightthickness=0, height=110)
        att_sv = ttk.Scrollbar(att_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=att_cv.yview)
        att_cv.configure(yscrollcommand=att_sv.set)
        att_sv.pack(side="right", fill="y")
        att_cv.pack(side="left", fill="both", expand=True)
        att_list = tk.Frame(att_cv, bg=C["panel"])
        aw = att_cv.create_window((0, 0), window=att_list, anchor="nw")
        att_cv.bind("<Configure>", lambda e, c=att_cv, w=aw: c.itemconfig(w, width=e.width))
        att_list.bind("<Configure>",
            lambda e, c=att_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _refresh_att(k=key, lst=att_list):
            for w in lst.winfo_children():
                w.destroy()
            files = self._eng["workpapers"].get(k, {}).get("attachments", [])
            if not files:
                tk.Label(lst, text="No files attached yet.",
                    bg=C["panel"], fg=C["border"],
                    font=FONT_SMALL).pack(anchor="w", padx=12, pady=8)
            else:
                for fname in files:
                    self._att_row(lst, k, fname, _refresh_att, "wp")

        _refresh_att()
        att_btn.config(command=lambda k=key, rf=_refresh_att:
                       self._attach(k, rf, "wp"))

    def _add_custom_note(self):
        """Dialog to create a new custom note under Notes to Accounts."""
        dlg = tk.Toplevel(self)
        dlg.title("Add Custom Note")
        dlg.configure(bg=C["bg"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.geometry("480x320")
        dlg.update_idletasks()
        x = self.winfo_x() + self.winfo_width()  // 2 - 240
        y = self.winfo_y() + self.winfo_height() // 2 - 160
        dlg.geometry(f"480x320+{x}+{y}")

        tk.Frame(dlg, bg=C["accent"], height=4).pack(fill="x")
        hdr = tk.Frame(dlg, bg=C["sidebar"], padx=24, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="New Custom Note",
                 bg=C["sidebar"], fg=C["accent"],
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(hdr, text="This note will appear in the Custom Notes section",
                 bg=C["sidebar"], fg=C["muted"],
                 font=("Segoe UI", 8)).pack(anchor="w")
        tk.Frame(dlg, bg=C["border"], height=1).pack(fill="x")

        # Footer buttons packed FIRST so they anchor to bottom
        tk.Frame(dlg, bg=C["border"], height=1).pack(side="bottom", fill="x")
        btn_bar = tk.Frame(dlg, bg=C["sidebar"], padx=24, pady=10)
        btn_bar.pack(side="bottom", fill="x")

        body = tk.Frame(dlg, bg=C["bg"], padx=24, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Note Number",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 3))
        num_var   = tk.StringVar()
        num_entry = styled_entry(body, textvariable=num_var, width=12)
        num_entry.pack(anchor="w", ipady=5)

        tk.Label(body, text="Note Name / Description",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(12, 3))
        name_text = tk.Text(body, height=3,
            bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=FONT_BODY, wrap="word",
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"], padx=10, pady=8)
        name_text.pack(fill="x")

        def _create():
            n_num  = num_var.get().strip()
            n_name = name_text.get("1.0", "end").strip()
            if not n_num or not n_name:
                messagebox.showwarning("Missing Fields",
                    "Please enter both a note number and a name.",
                    parent=dlg)
                return
            import uuid
            key = f"note_CUSTOM_{uuid.uuid4().hex[:8]}"
            self._eng["workpapers"][key] = {
                "status":       "Not Started",
                "observations": "",
                "process_notes": "",
                "attachments":  [],
                "hidden":       False,
                "display_num":  n_num,
                "display_name": n_name,
            }
            self._panel._mark_dirty()
            dlg.destroy()
            self._rebuild_clause_list()
            self._update_progress()
            # Auto-select the new note
            self._select_clause(key, n_num, n_name)

        add_btn = tk.Button(btn_bar, text="＋  Add Note",
            bg=C["accent"], fg=C["bg"],
            activebackground=C["btn_hover"], activeforeground=C["bg"],
            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=16, pady=8, command=_create)
        add_btn.pack(side="left")
        add_btn.bind("<Enter>", lambda e: add_btn.config(bg=C["btn_hover"]))
        add_btn.bind("<Leave>", lambda e: add_btn.config(bg=C["accent"]))

        cancel_btn = tk.Button(btn_bar, text="Cancel",
            bg=C["btn_secondary"], fg=C["text"],
            activebackground=C["border"],
            font=("Segoe UI", 9), relief="flat", cursor="hand2",
            bd=0, padx=12, pady=8, command=dlg.destroy)
        cancel_btn.pack(side="left", padx=(8, 0))

        num_entry.bind("<Return>", lambda e: _create())
        dlg.wait_window()

    def _delete_custom_note(self, key):
        """Delete a custom note after confirmation."""
        entry = self._eng["workpapers"].get(key, {})
        label = f"Note {entry.get('display_num','?')} — {entry.get('display_name','')}"
        if not messagebox.askyesno("Delete Custom Note",
                f"Delete this custom note?\n\n{label}\n\n"
                "All observations, process notes and attachments for this note will be lost.",
                parent=self):
            return
        # Clear selection if this note is active
        if self._current_clause == key:
            self._current_clause = None
            for w in self._content_area.winfo_children():
                w.destroy()
            self._placeholder = tk.Label(self._content_area,
                text=f"Select a {self._num_lbl.lower()} to view details",
                bg=C["bg"], fg=C["border"], font=("Segoe UI", 11))
            self._placeholder.place(relx=0.5, rely=0.5, anchor="center")
        # Remove from workpapers
        self._eng["workpapers"].pop(key, None)
        self._panel._mark_dirty()
        self._rebuild_clause_list()
        self._update_progress()

    def _flush_clause(self):
        k = self._current_clause
        if k and k in self._wp_widgets:
            w = self._wp_widgets[k]
            self._save_clause(k, w["status"], w["text"], w.get("proc"))

    def _save_clause(self, key, status_var, obs_text, proc_text=None):
        ex = self._eng["workpapers"].get(key, {})
        self._eng["workpapers"][key] = {
            "status":        status_var.get(),
            "observations":  obs_text.get("1.0", "end").strip(),
            "process_notes": (proc_text.get("1.0", "end").strip()
                              if proc_text else ex.get("process_notes", "")),
            "attachments":   ex.get("attachments", []),
            "hidden":        ex.get("hidden", False),
            "display_num":   ex.get("display_num", ""),
            "display_name":  ex.get("display_name", ""),
        }

    def _update_strip(self, key):
        if key not in self._row_frames:
            return
        stat = self._eng["workpapers"].get(key, {}).get("status", "Not Started")
        try:
            strip = self._row_frames[key]["strip"]
            if strip and strip.winfo_exists():
                strip.config(bg=STATUS_COLORS.get(stat, C["muted"]))
        except Exception:
            pass

    def _update_progress(self):
        wp           = self._eng.get("workpapers", {})
        custom_count = sum(1 for k in wp if k.startswith("note_CUSTOM_"))
        total        = len(self._items) + custom_count
        done  = sum(1 for v in wp.values() if v.get("status") == "Completed")
        na    = sum(1 for v in wp.values() if v.get("status") == "N/A")
        pct   = min(100, int((done + na) / total * 100)) if total else 0
        if self._progress_lbl and self._progress_lbl.winfo_exists():
            self._progress_lbl.config(
                text=f"{done} done · {na} N/A · {pct}% of {total}")

    def _update_hidden_btn(self):
        wp = self._eng.get("workpapers", {})
        n  = sum(1 for v in wp.values() if v.get("hidden"))
        if n == 0:
            self._hidden_var.set("  No hidden items  ")
        elif self._show_hidden:
            self._hidden_var.set(f"  🙈 Hide hidden ({n})  ")
        else:
            self._hidden_var.set(f"  👁 Show hidden ({n})  ")

    def _toggle_hidden_panel(self):
        self._show_hidden = not self._show_hidden
        self._rebuild_clause_list()
        self._update_hidden_btn()

    def _set_hidden(self, key, hidden):
        self._eng["workpapers"].setdefault(key, {})["hidden"] = hidden
        self._panel._mark_dirty()
        if hidden and self._current_clause == key and not self._show_hidden:
            self._current_clause = None
            for w in self._content_area.winfo_children():
                w.destroy()
            self._placeholder = tk.Label(self._content_area,
                text=f"Select a {self._num_lbl.lower()} to view details",
                bg=C["bg"], fg=C["border"], font=("Segoe UI", 11))
            self._placeholder.place(relx=0.5, rely=0.5, anchor="center")
        self._rebuild_clause_list()
        self._update_hidden_btn()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — PRE-AUDIT DOCUMENTS
    # ══════════════════════════════════════════════════════════════════════════

    def _build_pre_audit(self, parent):
        docs   = PRE_AUDIT_DOCS_TAX if self._is_tax else PRE_AUDIT_DOCS_STAT
        accent = self._accent

        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=accent, height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="PRE-AUDIT DOCUMENTS",
                 bg=C["sidebar"], fg=accent,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b, text="Attach engagement-acceptance documents below.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        badge_var = tk.StringVar()
        tk.Label(banner, textvariable=badge_var, bg=C["sidebar"],
                 fg=C["text"], font=("Segoe UI", 11, "bold")).pack(side="right")
        pr_pad = tk.Button(banner, text="🖨  Print",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=self._print_pre_audit)
        pr_pad.pack(side="right", padx=(0, 8))
        pr_pad.bind("<Enter>", lambda e: pr_pad.config(bg=C["highlight"]))
        pr_pad.bind("<Leave>", lambda e: pr_pad.config(bg=C["sidebar"]))

        outer = tk.Frame(parent, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        cv = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        sv = ttk.Scrollbar(outer, orient="vertical", style="Thin.Vertical.TScrollbar", command=cv.yview)
        cv.configure(yscrollcommand=sv.set)
        sv.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(cv, bg=C["bg"])
        cwin = cv.create_window((0, 0), window=inner, anchor="nw")
        cv.bind("<Configure>", lambda e, c=cv, w=cwin: c.itemconfig(w, width=e.width))
        inner.bind("<Configure>", lambda e, c=cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _on_pad_mw(event, c=cv):
            c.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_pad_mw(widget):
            widget.bind("<MouseWheel>", _on_pad_mw)
            for child in widget.winfo_children():
                _bind_pad_mw(child)

        outer.bind("<MouseWheel>", _on_pad_mw)
        cv.bind("<MouseWheel>", _on_pad_mw)
        inner.bind("<MouseWheel>", _on_pad_mw)
        outer.after(300, lambda: _bind_pad_mw(inner))

        def _update_badge():
            na_keys  = {k for k, _ in docs if self._eng["pre_audit_docs"].get(f"na_{k}")}
            att      = sum(1 for k, _ in docs
                          if self._eng["pre_audit_docs"].get(f"pad_{k}") and k not in na_keys)
            active   = len(docs) - len(na_keys)
            na_txt   = f"  ·  {len(na_keys)} N/A" if na_keys else ""
            badge_var.set(f"{att} / {active}  attached{na_txt}")

        for doc_key, doc_name in docs:
            self._pad_card(inner, doc_key, doc_name, accent, _update_badge)

        _update_badge()

    def _pad_card(self, parent, doc_key, doc_name, accent, update_badge):
        pad_key = f"pad_{doc_key}"
        na_key  = f"na_{doc_key}"
        files   = self._eng["pre_audit_docs"].get(pad_key, [])
        is_na   = self._eng["pre_audit_docs"].get(na_key, False)

        # card bg dims when N/A
        card_bg = C["sidebar"] if is_na else C["panel"]
        card = tk.Frame(parent, bg=card_bg,
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x", padx=24, pady=6)

        hdr = tk.Frame(card, bg=card_bg, padx=16, pady=10)
        hdr.pack(fill="x")

        # dot indicator: grey when N/A, green when attached, dim border otherwise
        dot_fg = C["muted"] if is_na else (C["success"] if files else C["border"])
        dot = tk.Label(hdr, text="●", bg=card_bg, fg=dot_fg, font=("Segoe UI", 10))
        dot.pack(side="left", padx=(0, 8))

        name_fg = C["muted"] if is_na else C["text"]
        name_lbl = tk.Label(hdr, text=doc_name, bg=card_bg, fg=name_fg,
                 font=("Segoe UI", 10, "bold"))
        name_lbl.pack(side="left")

        cnt_init = "N/A" if is_na else (
            f"{len(files)} file{'s' if len(files)!=1 else ''}" if files else "Not attached")
        cnt_var = tk.StringVar(value=cnt_init)
        cnt_lbl = tk.Label(hdr, textvariable=cnt_var, bg=card_bg,
                 fg=C["muted"], font=FONT_SMALL)
        cnt_lbl.pack(side="left", padx=(8, 0))

        # Attach button
        a_btn = tk.Button(hdr, text="＋  Attach",
            bg=C["highlight"], fg=accent,
            activebackground=C["list_sel"], activeforeground=accent,
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=10, pady=4, bd=0,
            state="disabled" if is_na else "normal")
        a_btn.pack(side="right")
        if not is_na:
            a_btn.bind("<Enter>", lambda e: a_btn.config(bg=C["list_sel"]))
            a_btn.bind("<Leave>", lambda e: a_btn.config(bg=C["highlight"]))

        # Template button
        t_btn = None
        if doc_key in PAD_TEMPLATES:
            t_btn = tk.Button(hdr, text="📄  Template",
                bg=C["sidebar"], fg=C["muted"],
                activebackground=C["highlight"], activeforeground=C["text"],
                font=("Segoe UI", 8, "bold"), relief="flat",
                cursor="hand2", padx=10, pady=4, bd=0,
                state="disabled" if is_na else "normal",
                command=lambda dk=doc_key, dn=doc_name: self._open_pad_template(dk, dn))
            t_btn.pack(side="right", padx=(0, 6))
            if not is_na:
                t_btn.bind("<Enter>", lambda e: t_btn.config(bg=C["highlight"]))
                t_btn.bind("<Leave>", lambda e: t_btn.config(bg=C["sidebar"]))

        # N/A toggle button
        na_btn_bg  = C["danger"] if is_na else C["sidebar"]
        na_btn_fg  = C["bg"]    if is_na else C["muted"]
        na_btn_txt = "✕ N/A"   if is_na else "N/A"
        na_btn = tk.Button(hdr, text=na_btn_txt,
            bg=na_btn_bg, fg=na_btn_fg,
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=8, pady=4, bd=0)
        na_btn.pack(side="right", padx=(0, 6))

        # expand/collapse state
        expanded = [bool(files) and not is_na]

        # chevron label in header (packed left, after dot)
        chev = tk.Label(hdr, text="▼" if expanded[0] else "▶",
                        bg=card_bg, fg=C["muted"],
                        font=("Segoe UI", 8), cursor="hand2")
        chev.pack(side="left", padx=(0, 6))
        # Re-pack name_lbl after chev (chev must come before name_lbl)
        # name_lbl is already packed; chev packs before it because we call
        # lower() to reorder — but tkinter pack order is fixed at creation.
        # So instead we destroy and re-create name_lbl after chev.
        name_lbl.pack_forget()
        chev.pack(side="left", padx=(0, 6))
        name_lbl.pack(side="left")

        ff = tk.Frame(card, bg=card_bg)
        if expanded[0]:
            ff.pack(fill="x", padx=16, pady=(0, 8))

        def _refresh(k=pad_key, frame=ff, cv=cnt_var, dl=dot):
            for w in frame.winfo_children():
                w.destroy()
            fl = self._eng["pre_audit_docs"].get(k, [])
            _na = self._eng["pre_audit_docs"].get(na_key, False)
            if _na:
                cv.set("N/A")
                dl.config(fg=C["muted"])
            else:
                cv.set(f"{len(fl)} file{'s' if len(fl)!=1 else ''}" if fl else "Not attached")
                dl.config(fg=C["success"] if fl else C["border"])
            if not _na and expanded[0]:
                frame.pack(fill="x", padx=16, pady=(0, 8))
                if fl:
                    for fname in fl:
                        self._att_row(frame, k, fname, _refresh, "pad")
                else:
                    tk.Label(frame, text="No files attached yet.",
                             bg=card_bg, fg=C["border"],
                             font=FONT_SMALL).pack(anchor="w", pady=4)
            else:
                frame.pack_forget()
            update_badge()

        def _toggle_expand(e=None):
            if self._eng["pre_audit_docs"].get(na_key, False):
                return
            expanded[0] = not expanded[0]
            chev.config(text="▼" if expanded[0] else "▶")
            _refresh()

        # bind click-to-expand on header widgets (but NOT buttons)
        for w in (hdr, dot, chev, name_lbl, cnt_lbl):
            w.bind("<Button-1>", _toggle_expand)
            w.config(cursor="hand2")

        if expanded[0]:
            _refresh()

        def _toggle_na(dk=doc_key, nk=na_key, ab=a_btn, tb=t_btn,
                       nb=na_btn, dl=dot, cv=cnt_var, nl=name_lbl,
                       cl=cnt_lbl, fr=ff, cd=card, hf=hdr):
            cur_na = self._eng["pre_audit_docs"].get(nk, False)
            new_na = not cur_na
            self._eng["pre_audit_docs"][nk] = new_na
            bg_new = C["sidebar"] if new_na else C["panel"]
            cd.config(bg=bg_new)
            hf.config(bg=bg_new)
            dl.config(bg=bg_new, fg=C["muted"] if new_na else (
                C["success"] if self._eng["pre_audit_docs"].get(f"pad_{dk}") else C["border"]))
            nl.config(bg=bg_new, fg=C["muted"] if new_na else C["text"])
            cl.config(bg=bg_new)
            fr.config(bg=bg_new)
            ab.config(state="disabled" if new_na else "normal",
                      bg=C["sidebar"] if new_na else C["highlight"])
            if tb:
                tb.config(state="disabled" if new_na else "normal")
            if new_na:
                cv.set("N/A")
                nb.config(text="✕ N/A", bg=C["danger"], fg=C["bg"])
                fr.pack_forget()
            else:
                _refresh()
                nb.config(text="N/A", bg=C["sidebar"], fg=C["muted"])
            update_badge()

        na_btn.config(command=_toggle_na)
        na_btn.bind("<Enter>", lambda e: na_btn.config(
            bg=C["muted"] if not self._eng["pre_audit_docs"].get(na_key) else C["danger"]))
        na_btn.bind("<Leave>", lambda e: na_btn.config(
            bg=C["danger"] if self._eng["pre_audit_docs"].get(na_key) else C["sidebar"]))

        a_btn.config(command=lambda k=pad_key, rf=_refresh:
                     self._attach(k, rf, "pad"))
    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — LEGAL & SECRETARIAL
    # ══════════════════════════════════════════════════════════════════════════

    def _build_legal_sec(self, parent):
        self._eng.setdefault("legal_sec", {})

        # ctx holds all mutable state for this tab
        ctx = {
            "current":     None,
            "row_frames":  {},
            "widgets":     {},
            "badge_var":   tk.StringVar(),
            "detail":      None,
            "placeholder": None,
        }

        # Banner
        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=C["accent"], height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="LEGAL & SECRETARIAL COMPLIANCE",
                 bg=C["sidebar"], fg=C["accent"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b,
                 text="Company Law, Meetings, Registers, Governance & SEBI obligations.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        tk.Label(banner, textvariable=ctx["badge_var"],
                 bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="right")
        pr_ls = tk.Button(banner, text="🖨  Print",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=self._print_legal_sec)
        pr_ls.pack(side="right", padx=(0, 8))
        pr_ls.bind("<Enter>", lambda e: pr_ls.config(bg=C["highlight"]))
        pr_ls.bind("<Leave>", lambda e: pr_ls.config(bg=C["sidebar"]))

        # Body: list + detail
        body = tk.Frame(parent, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left list
        list_out = tk.Frame(body, bg=C["sidebar"], width=380)
        list_out.pack(side="left", fill="y")
        list_out.pack_propagate(False)

        ls_cv = tk.Canvas(list_out, bg=C["sidebar"], highlightthickness=0)
        ls_sb = ttk.Scrollbar(list_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=ls_cv.yview)
        ls_cv.configure(yscrollcommand=ls_sb.set)
        ls_sb.pack(side="right", fill="y")
        ls_cv.pack(side="left", fill="both", expand=True)

        def _scroll(e, c=ls_cv):
            c.yview_scroll(int(-1*(e.delta/120)), "units")
        ls_cv.bind("<MouseWheel>", _scroll)
        ls_cv.bind("<Enter>", lambda e, c=ls_cv: c.bind_all("<MouseWheel>", _scroll))
        ls_cv.bind("<Leave>", lambda e, c=ls_cv: c.unbind_all("<MouseWheel>"))

        ls_inner = tk.Frame(ls_cv, bg=C["sidebar"])
        lwin = ls_cv.create_window((0, 0), window=ls_inner, anchor="nw")
        ls_cv.bind("<Configure>",
            lambda e, c=ls_cv, w=lwin: c.itemconfig(w, width=e.width))
        ls_inner.bind("<Configure>",
            lambda e, c=ls_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))
        ls_cv.bind("<MouseWheel>",
            lambda e, c=ls_cv: c.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Right detail
        ctx["detail"] = tk.Frame(body, bg=C["bg"])
        ctx["detail"].pack(side="right", fill="both", expand=True)
        ctx["placeholder"] = tk.Label(ctx["detail"],
            text="Select a compliance item to view details",
            bg=C["bg"], fg=C["border"], font=("Segoe UI", 11))
        ctx["placeholder"].place(relx=0.5, rely=0.5, anchor="center")

        # Build rows
        for key, label, kind in LEGAL_SEC_ITEMS:
            if kind == "header":
                fr = tk.Frame(ls_inner, bg=C["sidebar"])
                fr.pack(fill="x", pady=(10, 0))
                tk.Frame(fr, bg=C["accent"], height=2).pack(fill="x")
                tk.Label(fr, text=label.upper(),
                    bg=C["sidebar"], fg=C["accent"],
                    font=("Segoe UI", 8, "bold"),
                    padx=14, pady=5).pack(anchor="w")
            else:
                entry  = self._eng["legal_sec"].get(key, {})
                status = entry.get("status", "Not Checked")
                sc     = LS_STATUS_COLORS.get(status, C["border"])

                row   = tk.Frame(ls_inner, bg=C["sidebar"], cursor="hand2")
                row.pack(fill="x")
                strip = tk.Frame(row, bg=sc, width=3)
                strip.pack(side="left", fill="y")
                rbody = tk.Frame(row, bg=C["sidebar"], padx=10, pady=7)
                rbody.pack(side="left", fill="both", expand=True)
                lbl_w = tk.Label(rbody, text=label, bg=C["sidebar"],
                    fg=C["text"], font=FONT_SMALL, anchor="w",
                    wraplength=310, justify="left")
                lbl_w.pack(anchor="w")
                sl = tk.Label(rbody, text=status, bg=C["sidebar"],
                    fg=sc, font=("Segoe UI", 7, "bold"))
                sl.pack(anchor="w")

                ctx["row_frames"][key] = {
                    "row": row, "strip": strip, "rbody": rbody,
                    "status_lbl": sl,
                }

                def _click(e, k=key, lbl=label, c=ctx):
                    self._ls_select(k, lbl, c)

                bind_tree(row, "<Button-1>", _click)

        self._ls_update_badge(ctx)

    def _ls_select(self, key, label, ctx):
        # Save previous
        if ctx["current"] and ctx["current"] in ctx["widgets"]:
            self._ls_save(ctx["current"], ctx)

        # Deselect previous
        if ctx["current"] and ctx["current"] in ctx["row_frames"]:
            pf = ctx["row_frames"][ctx["current"]]
            pf["row"].config(bg=C["sidebar"])
            pf["rbody"].config(bg=C["sidebar"])

        ctx["current"] = key

        if key in ctx["row_frames"]:
            cf = ctx["row_frames"][key]
            cf["row"].config(bg=C["list_sel"])
            cf["rbody"].config(bg=C["list_sel"])

        # Clear detail
        try:
            if ctx["placeholder"] and ctx["placeholder"].winfo_exists():
                ctx["placeholder"].place_forget()
        except Exception:
            pass

        for w in ctx["detail"].winfo_children():
            w.destroy()

        entry = self._eng["legal_sec"].get(key, {})

        # Heading
        head = tk.Frame(ctx["detail"], bg=C["bg"])
        head.pack(fill="x", padx=22, pady=(18, 0))
        tk.Frame(head, bg=C["accent"], width=4).pack(side="left", fill="y")
        htxt = tk.Frame(head, bg=C["bg"], padx=12)
        htxt.pack(side="left", fill="x", expand=True)
        tk.Label(htxt, text="Legal & Secretarial",
                 bg=C["bg"], fg=C["accent"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(htxt, text=label, bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 13, "bold"),
                 wraplength=520, justify="left").pack(anchor="w")

        tk.Frame(ctx["detail"], height=1, bg=C["border"]
                 ).pack(fill="x", padx=22, pady=10)

        content = tk.Frame(ctx["detail"], bg=C["bg"], padx=22)
        content.pack(fill="both", expand=True)

        # Status buttons
        tk.Label(content, text="Compliance Status:",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        status_var = tk.StringVar(value=entry.get("status", "Not Checked"))
        stat_row = tk.Frame(content, bg=C["bg"])
        stat_row.pack(anchor="w", pady=(4, 12))

        def _refresh_stat_btns():
            for btn in stat_row.winfo_children():
                if not isinstance(btn, tk.Button):
                    continue
                s   = btn.cget("text")
                col = LS_STATUS_COLORS.get(s, C["border"])
                sel = (status_var.get() == s)
                btn.config(bg=col if sel else C["btn_secondary"],
                           fg="#fff" if sel else C["muted"])

        for s in LS_STATUSES:
            col    = LS_STATUS_COLORS.get(s, C["border"])
            is_sel = (status_var.get() == s)
            btn = tk.Button(stat_row, text=s, font=FONT_SMALL,
                relief="flat", cursor="hand2", padx=10, pady=5, bd=0,
                bg=col if is_sel else C["btn_secondary"],
                fg="#fff" if is_sel else C["muted"],
                activebackground=col, activeforeground="#fff")
            btn.pack(side="left", padx=(0, 6))
            def _set(s=s, v=status_var, k=key, c=ctx):
                v.set(s)
                _refresh_stat_btns()
                self._ls_save(k, c)
                self._ls_update_row_strip(k, c)
                self._ls_update_badge(c)
                self._panel._mark_dirty()
            btn.config(command=_set)

        # Notes
        tk.Label(content, text="Notes / Observations",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        notes_text = tk.Text(content, height=6, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=("Segoe UI", 10), wrap="word",
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"], padx=10, pady=8)
        notes_text.pack(fill="x", pady=(4, 0))
        notes_text.insert("1.0", entry.get("notes", ""))
        notes_text.bind("<KeyRelease>",
            lambda e, k=key, sv=status_var, nt=notes_text, c=ctx:
            (self._ls_save(k, c, sv, nt), self._panel._mark_dirty()))

        ctx["widgets"][key] = {"status": status_var, "notes": notes_text}

        # Attachments
        tk.Frame(content, height=1, bg=C["border"]).pack(fill="x", pady=(12, 0))
        ah = tk.Frame(content, bg=C["bg"])
        ah.pack(fill="x", pady=(8, 6))
        tk.Label(ah, text="📎  Supporting Documents",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        a_btn = tk.Button(ah, text="＋  Attach Files",
            bg=C["highlight"], fg=C["accent"],
            activebackground=C["list_sel"], activeforeground=C["accent"],
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=10, pady=4, bd=0)
        a_btn.pack(side="right")
        a_btn.bind("<Enter>", lambda e: a_btn.config(bg=C["list_sel"]))
        a_btn.bind("<Leave>", lambda e: a_btn.config(bg=C["highlight"]))

        att_out = tk.Frame(content, bg=C["panel"],
                           highlightthickness=1, highlightbackground=C["border"])
        att_out.pack(fill="both", expand=True, pady=(0, 8))
        att_cv = tk.Canvas(att_out, bg=C["panel"], highlightthickness=0, height=100)
        att_sv = ttk.Scrollbar(att_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=att_cv.yview)
        att_cv.configure(yscrollcommand=att_sv.set)
        att_sv.pack(side="right", fill="y")
        att_cv.pack(side="left", fill="both", expand=True)
        att_list = tk.Frame(att_cv, bg=C["panel"])
        aw = att_cv.create_window((0, 0), window=att_list, anchor="nw")
        att_cv.bind("<Configure>",
            lambda e, c=att_cv, w=aw: c.itemconfig(w, width=e.width))
        att_list.bind("<Configure>",
            lambda e, c=att_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _refresh_ls_att(k=key, lst=att_list):
            for w in lst.winfo_children():
                w.destroy()
            files = self._eng["legal_sec"].get(k, {}).get("attachments", [])
            if not files:
                tk.Label(lst, text="No documents attached yet.",
                    bg=C["panel"], fg=C["border"],
                    font=FONT_SMALL).pack(anchor="w", padx=12, pady=8)
            else:
                for fname in files:
                    self._att_row(lst, k, fname, _refresh_ls_att, "ls")

        _refresh_ls_att()
        a_btn.config(command=lambda k=key, rf=_refresh_ls_att:
                     self._attach(k, rf, "ls"))

    def _ls_save(self, key, ctx, status_var=None, notes_text=None):
        ls   = self._eng.setdefault("legal_sec", {})
        ex   = ls.get(key, {})
        w    = ctx["widgets"].get(key, {})
        sv   = status_var or w.get("status")
        nt   = notes_text or w.get("notes")
        ls[key] = {
            "status":      sv.get() if sv else ex.get("status", "Not Checked"),
            "notes":       nt.get("1.0", "end").strip() if nt else ex.get("notes", ""),
            "attachments": ex.get("attachments", []),
        }

    def _ls_update_row_strip(self, key, ctx):
        if key not in ctx["row_frames"]:
            return
        status = self._eng["legal_sec"].get(key, {}).get("status", "Not Checked")
        col    = LS_STATUS_COLORS.get(status, C["border"])
        fr     = ctx["row_frames"][key]
        if fr["strip"].winfo_exists():
            fr["strip"].config(bg=col)
        if fr["status_lbl"].winfo_exists():
            fr["status_lbl"].config(text=status, fg=col)

    def _ls_update_badge(self, ctx):
        items     = [k for k, _, t in LEGAL_SEC_ITEMS if t == "item"]
        ls        = self._eng.get("legal_sec", {})
        compliant = sum(1 for k in items if ls.get(k, {}).get("status") == "Compliant")
        non_comp  = sum(1 for k in items if ls.get(k, {}).get("status") == "Non-Compliant")
        ctx["badge_var"].set(f"✓ {compliant}  ✗ {non_comp}  of {len(items)} items")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — BS & P&L VARIANCE
    # ══════════════════════════════════════════════════════════════════════════


    # ══════════════════════════════════════════════════════════════════════════
    # ── Print: CARO checklist ──────────────────────────────────────────────────────────────────────────────
    def _print_caro(self):
        caro  = self._eng.get("caro", {})
        body  = ""
        current_header = None
        rows_buf = ""

        def flush_section(hdr, rows_html):
            if not hdr:
                return ""
            return (f"<h3 style='margin-top:24px;color:#1DB8A8'>{html.escape(hdr)}</h3>"
                    f"<table style='width:100%;border-collapse:collapse;font-size:12px'>"
                    f"<thead><tr style='background:#1a2a3a;color:#b0c4d4'>"
                    f"<th style='width:32px'></th>"
                    f"<th>Clause</th>"
                    f"<th style='width:110px'>Status</th>"
                    f"<th style='width:260px'>Observations</th>"
                    f"</tr></thead><tbody>{rows_html}</tbody></table>")

        status_dot = {"Compliant": "✅", "Non-Compliant": "❌", "N/A": "⬜"}
        status_col = {"Compliant": "#27ae60", "Non-Compliant": "#e74c3c", "N/A": "#888"}

        for key, lbl, kind in caro_items_for_eng(self._eng):
            if kind == "header":
                body += flush_section(current_header, rows_buf)
                current_header = lbl
                rows_buf = ""
            else:
                entry  = caro.get(key, {})
                status = entry.get("status", "Not Checked")
                obs    = html.escape(entry.get("observations", "") or "—")
                dot    = status_dot.get(status, "◻")
                scol   = status_col.get(status, "#aaa")
                rows_buf += (f"<tr style='border-bottom:1px solid #2a3a4a'>"
                             f"<td style='width:32px;text-align:center;padding:6px 2px'>{dot}</td>"
                             f"<td style='padding:6px 8px'>{html.escape(lbl)}</td>"
                             f"<td style='width:110px;padding:6px 4px;font-weight:bold;color:{scol}'>{html.escape(status)}</td>"
                             f"<td style='width:260px;padding:6px 8px;color:#aaa'>{obs}</td>"
                             f"</tr>")

        body += flush_section(current_header, rows_buf)

        items     = [k for k, _, t in caro_items_for_eng(self._eng) if t == "item"]
        compliant = sum(1 for k in items if caro.get(k, {}).get("status") == "Compliant")
        non_comp  = sum(1 for k in items if caro.get(k, {}).get("status") == "Non-Compliant")
        na_cnt    = sum(1 for k in items if caro.get(k, {}).get("status") == "N/A")
        total     = len(items)
        summary   = (f"<div style='margin-bottom:18px;padding:10px 14px;background:#1a2a3a;"
                     f"border-radius:4px;font-size:12px;color:#b0c4d4'>"
                     f"<b>Summary —</b>&nbsp;&nbsp;"
                     f"✅&nbsp;Compliant: <b>{compliant}</b>&nbsp;&nbsp;·&nbsp;&nbsp;"
                     f"❌&nbsp;Non-Compliant: <b>{non_comp}</b>&nbsp;&nbsp;·&nbsp;&nbsp;"
                     f"⬜&nbsp;N/A: <b>{na_cnt}</b>&nbsp;&nbsp;·&nbsp;&nbsp;"
                     f"Checked: <b>{compliant+non_comp+na_cnt}/{total}</b></div>")
        self._print_html("CARO 2020 Checklist", summary + body)

    # TAB 4 — CARO CHECKLIST
    # ══════════════════════════════════════════════════════════════════════════

    def _build_caro(self, parent):
        self._eng.setdefault("caro", {})

        ctx = {
            "badge_var":  tk.StringVar(),
            "detail":     None,
            "placeholder": None,
            "row_frames": {},
            "widgets":    {},
        }

        # Banner
        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=12)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=C["accent"], height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="CARO 2020 CHECKLIST",
                 bg=C["sidebar"], fg=C["accent"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b,
                 text="Companies (Auditor's Report) Order 2020 — clause-by-clause compliance.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        tk.Label(banner, textvariable=ctx["badge_var"],
                 bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="right")

        pr_caro = tk.Button(banner, text="🖨  Print",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=self._print_caro)
        pr_caro.pack(side="right", padx=(0, 8))
        pr_caro.bind("<Enter>", lambda e: pr_caro.config(bg=C["highlight"]))
        pr_caro.bind("<Leave>", lambda e: pr_caro.config(bg=C["sidebar"]))

        # ── Not Applicable toggle
        caro_na_btn = tk.Button(banner, text="",
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4)
        caro_na_btn.pack(side="right", padx=(0, 6))

        body_wrap = tk.Frame(parent, bg=C["bg"])
        body_wrap.pack(fill="both", expand=True)

        # Body: list (left) + detail (right)
        body = tk.Frame(body_wrap, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left scrollable list
        list_out = tk.Frame(body, bg=C["sidebar"], width=420)
        list_out.pack(side="left", fill="y")
        list_out.pack_propagate(False)

        cv = tk.Canvas(list_out, bg=C["sidebar"], highlightthickness=0)
        sb = ttk.Scrollbar(list_out, orient="vertical", style="Thin.Vertical.TScrollbar", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        ls_inner = tk.Frame(cv, bg=C["sidebar"])
        lwin = cv.create_window((0, 0), window=ls_inner, anchor="nw")
        cv.bind("<Configure>", lambda e, c=cv, w=lwin: c.itemconfig(w, width=e.width))
        ls_inner.bind("<Configure>", lambda e, c=cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))
        cv.bind("<Enter>",  lambda e, c=cv: c.bind_all("<MouseWheel>",
            lambda ev, c2=cv: c2.yview_scroll(int(-1*(ev.delta/120)), "units")))
        cv.bind("<Leave>",  lambda e, c=cv: c.unbind_all("<MouseWheel>"))

        # Right detail pane
        ctx["detail"] = tk.Frame(body, bg=C["bg"])
        ctx["detail"].pack(side="right", fill="both", expand=True)
        ctx["placeholder"] = tk.Label(ctx["detail"],
            text="Select a CARO clause to view details",
            bg=C["bg"], fg=C["border"], font=("Segoe UI", 11))
        ctx["placeholder"].place(relx=0.5, rely=0.5, anchor="center")

        # Build rows
        for key, label, kind in caro_items_for_eng(self._eng):
            if kind == "header":
                fr = tk.Frame(ls_inner, bg=C["sidebar"])
                fr.pack(fill="x", pady=(10, 0))
                tk.Frame(fr, bg=C["accent"], height=2).pack(fill="x")
                tk.Label(fr, text=label, bg=C["sidebar"], fg=C["accent"],
                         font=("Segoe UI", 8, "bold"),
                         padx=14, pady=5).pack(anchor="w")
            else:
                entry  = self._eng["caro"].get(key, {})
                status = entry.get("status", "Not Checked")
                sc     = LS_STATUS_COLORS.get(status, C["border"])

                row   = tk.Frame(ls_inner, bg=C["sidebar"], cursor="hand2")
                row.pack(fill="x")
                strip = tk.Frame(row, bg=sc, width=3)
                strip.pack(side="left", fill="y")
                rbody = tk.Frame(row, bg=C["sidebar"], padx=10, pady=7)
                rbody.pack(side="left", fill="both", expand=True)
                lbl_w = tk.Label(rbody, text=label, bg=C["sidebar"],
                    fg=C["text"], font=FONT_SMALL, anchor="w",
                    wraplength=360, justify="left")
                lbl_w.pack(anchor="w")
                sl = tk.Label(rbody, text=status, bg=C["sidebar"],
                    fg=sc, font=("Segoe UI", 7, "bold"))
                sl.pack(anchor="w")

                ctx["row_frames"][key] = {
                    "row": row, "strip": strip, "rbody": rbody,
                    "status_lbl": sl,
                }

                def _click(e, k=key, lbl=label, c=ctx):
                    self._caro_select(k, lbl, c)

                bind_tree(row, "<Button-1>", _click)

        self._caro_update_badge(ctx)

        # ── Wire CARO NA toggle (after body fully built) ───────────────────────
        _caro_overlay = [None]

        def _show_caro_overlay():
            if _caro_overlay[0] and _caro_overlay[0].winfo_exists():
                _caro_overlay[0].destroy()
            ov = tk.Frame(body_wrap, bg=C["sidebar"])
            ov.place(relx=0, rely=0, relwidth=1, relheight=1)
            tk.Frame(ov, bg=C["danger"], height=4).pack(fill="x")
            inner_ov = tk.Frame(ov, bg=C["sidebar"])
            inner_ov.place(relx=0.5, rely=0.38, anchor="center")
            tk.Label(inner_ov, text="🚫",
                     bg=C["sidebar"], fg=C["danger"],
                     font=("Segoe UI", 36)).pack()
            tk.Label(inner_ov,
                     text="CARO 2020 Checklist — Not Applicable",
                     bg=C["sidebar"], fg=C["text"],
                     font=("Segoe UI", 15, "bold")).pack(pady=(8, 2))
            tk.Label(inner_ov,
                     text="Click ‘CARO Applicable’ in the banner above to re-enable.",
                     bg=C["sidebar"], fg=C["muted"],
                     font=("Segoe UI", 10), justify="center").pack(pady=(0, 14))
            # Remarks box
            rem_frame = tk.Frame(inner_ov, bg=C["sidebar"])
            rem_frame.pack(fill="x", padx=4)
            tk.Label(rem_frame, text="Reason not applicable:",
                     bg=C["sidebar"], fg=C["muted"],
                     font=("Segoe UI", 9, "bold"), anchor="w").pack(anchor="w")
            caro_rem_box = tk.Text(rem_frame, height=4, width=64,
                bg=C["input_bg"], fg=C["text"], relief="flat",
                font=FONT_SMALL, insertbackground=C["accent"],
                wrap="word", padx=8, pady=6)
            caro_rem_box.pack(fill="x", pady=(4, 0))
            saved_rem = self._eng.get("caro_na_reason", "")
            if saved_rem:
                caro_rem_box.insert("1.0", saved_rem)
            def _save_caro_rem(e=None):
                self._eng["caro_na_reason"] = caro_rem_box.get("1.0", "end").strip()
                self._panel._mark_dirty()
            caro_rem_box.bind("<FocusOut>", _save_caro_rem)
            caro_rem_box.bind("<KeyRelease>", _save_caro_rem)
            _caro_overlay[0] = ov

        def _hide_caro_overlay():
            if _caro_overlay[0] and _caro_overlay[0].winfo_exists():
                _caro_overlay[0].destroy()
            _caro_overlay[0] = None

        def _apply_caro_na(is_na):
            if is_na:
                caro_na_btn.config(
                    text="✔  CARO Applicable",
                    bg=C["success"], fg="#fff",
                    activebackground=C["success"], activeforeground="#fff")
                caro_na_btn.bind("<Enter>", lambda e: caro_na_btn.config(bg=C["success"]))
                caro_na_btn.bind("<Leave>", lambda e: caro_na_btn.config(bg=C["success"]))
                pr_caro.config(state="disabled", fg=C["border"])
                ctx["badge_var"].set("N/A")
                if hasattr(self, "_nb") and hasattr(self, "_tc"):
                    self._nb.tab(self._tc, text="  CARO Checklist (N/A)  ")
                _show_caro_overlay()
            else:
                caro_na_btn.config(
                    text="✕  Not Applicable",
                    bg=C["sidebar"], fg=C["muted"],
                    activebackground=C["danger"], activeforeground="#fff")
                caro_na_btn.bind("<Enter>", lambda e: caro_na_btn.config(bg=C["danger"], fg="#fff"))
                caro_na_btn.bind("<Leave>", lambda e: caro_na_btn.config(bg=C["sidebar"], fg=C["muted"]))
                pr_caro.config(state="normal", fg=C["muted"])
                if hasattr(self, "_nb") and hasattr(self, "_tc"):
                    self._nb.tab(self._tc, text="  CARO Checklist  ")
                _hide_caro_overlay()
                self._caro_update_badge(ctx)

        def _toggle_caro_na():
            new_val = not self._eng.get("caro_na", False)
            self._eng["caro_na"] = new_val
            self._panel._mark_dirty()
            _apply_caro_na(new_val)

        caro_na_btn.config(command=_toggle_caro_na)
        _apply_caro_na(self._eng.get("caro_na", False))

    def _caro_select(self, key, label, ctx):
        # Save previous
        if ctx.get("current") and ctx["current"] in ctx["widgets"]:
            self._caro_save(ctx["current"], ctx)

        # Deselect previous
        if ctx.get("current") and ctx["current"] in ctx["row_frames"]:
            pf = ctx["row_frames"][ctx["current"]]
            pf["row"].config(bg=C["sidebar"])
            pf["rbody"].config(bg=C["sidebar"])

        ctx["current"] = key

        if key in ctx["row_frames"]:
            cf = ctx["row_frames"][key]
            cf["row"].config(bg=C["list_sel"])
            cf["rbody"].config(bg=C["list_sel"])

        # Clear detail
        try:
            if ctx["placeholder"] and ctx["placeholder"].winfo_exists():
                ctx["placeholder"].place_forget()
        except Exception:
            pass

        for w in ctx["detail"].winfo_children():
            w.destroy()

        entry = self._eng["caro"].get(key, {})

        # Heading
        head = tk.Frame(ctx["detail"], bg=C["bg"])
        head.pack(fill="x", padx=22, pady=(18, 0))
        tk.Frame(head, bg=C["accent"], width=4).pack(side="left", fill="y")
        htxt = tk.Frame(head, bg=C["bg"], padx=12)
        htxt.pack(side="left", fill="x", expand=True)
        tk.Label(htxt, text="CARO 2020", bg=C["bg"],
                 fg=C["accent"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(htxt, text=label, bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 12, "bold"),
                 wraplength=560, justify="left").pack(anchor="w")

        tk.Frame(ctx["detail"], height=1, bg=C["border"]
                 ).pack(fill="x", padx=22, pady=10)

        content = tk.Frame(ctx["detail"], bg=C["bg"], padx=22)
        content.pack(fill="both", expand=True)

        # Status buttons
        tk.Label(content, text="Status:", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        status_var = tk.StringVar(value=entry.get("status", "Not Checked"))
        stat_row = tk.Frame(content, bg=C["bg"])
        stat_row.pack(anchor="w", pady=(4, 12))

        def _refresh_btns():
            for btn in stat_row.winfo_children():
                if not isinstance(btn, tk.Button):
                    continue
                s   = btn.cget("text")
                col = LS_STATUS_COLORS.get(s, C["border"])
                sel = (status_var.get() == s)
                btn.config(bg=col if sel else C["btn_secondary"],
                           fg="#fff" if sel else C["muted"])

        for s in LS_STATUSES:
            col    = LS_STATUS_COLORS.get(s, C["border"])
            is_sel = (status_var.get() == s)
            btn = tk.Button(stat_row, text=s, font=FONT_SMALL,
                relief="flat", cursor="hand2", padx=10, pady=5, bd=0,
                bg=col if is_sel else C["btn_secondary"],
                fg="#fff" if is_sel else C["muted"],
                activebackground=col, activeforeground="#fff")
            btn.pack(side="left", padx=(0, 6))
            def _set(s=s, v=status_var, k=key, c=ctx):
                v.set(s)
                _refresh_btns()
                self._caro_save(k, c, v)
                self._caro_update_row_strip(k, c)
                self._caro_update_badge(c)
                self._panel._mark_dirty()
            btn.config(command=_set)

        # Observations
        tk.Label(content, text="Observations / Notes", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(anchor="w")
        obs_text = tk.Text(content, height=8, bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=("Segoe UI", 10), wrap="word",
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"], padx=10, pady=8)
        obs_text.pack(fill="x", pady=(4, 0))
        obs_text.insert("1.0", entry.get("observations", ""))
        obs_text.bind("<KeyRelease>",
            lambda e, k=key, sv=status_var, ot=obs_text, c=ctx:
            (self._caro_save(k, c, sv, ot), self._panel._mark_dirty()))

        # ── Attachments ────────────────────────────────────────────────────────────────────
        att_hdr = tk.Frame(content, bg=C["bg"])
        att_hdr.pack(fill="x", pady=(14, 4))
        tk.Label(att_hdr, text="Attachments", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack(side="left")
        att_btn = tk.Button(att_hdr, text="＋  Attach",
            bg=C["highlight"], fg=C["accent"],
            activebackground=C["list_sel"], activeforeground=C["accent"],
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", padx=10, pady=3, bd=0)
        att_btn.pack(side="right")
        att_btn.bind("<Enter>", lambda e: att_btn.config(bg=C["list_sel"]))
        att_btn.bind("<Leave>", lambda e: att_btn.config(bg=C["highlight"]))

        files_frame = tk.Frame(content, bg=C["bg"])
        files_frame.pack(fill="x")

        def _refresh_caro_files(k=key, ff=files_frame):
            for w in ff.winfo_children():
                w.destroy()
            fls = self._eng.get("caro", {}).get(k, {}).get("attachments", [])
            if not fls:
                tk.Label(ff, text="No files attached yet.",
                         bg=C["bg"], fg=C["border"], font=FONT_SMALL
                         ).pack(anchor="w", pady=2)
            else:
                for fname in fls:
                    self._att_row(ff, k, fname, _refresh_caro_files, "caro")

        att_btn.config(command=lambda k=key, rf=_refresh_caro_files:
                       self._attach(k, rf, "caro"))
        _refresh_caro_files()

        ctx["widgets"][key] = {"status": status_var, "obs": obs_text, "files_refresh": _refresh_caro_files}

    def _caro_save(self, key, ctx, status_var=None, obs_text=None):
        ca   = self._eng.setdefault("caro", {})
        ex   = ca.get(key, {})
        w    = ctx["widgets"].get(key, {})
        sv   = status_var or w.get("status")
        ot   = obs_text   or w.get("obs")
        ca[key] = {
            "status":       sv.get() if sv else ex.get("status", "Not Checked"),
            "observations": ot.get("1.0", "end").strip() if ot else ex.get("observations", ""),
            "attachments":  ex.get("attachments", []),
        }

    def _caro_update_row_strip(self, key, ctx):
        if key not in ctx["row_frames"]:
            return
        status = self._eng["caro"].get(key, {}).get("status", "Not Checked")
        col    = LS_STATUS_COLORS.get(status, C["border"])
        fr     = ctx["row_frames"][key]
        if fr["strip"].winfo_exists():
            fr["strip"].config(bg=col)
        if fr["status_lbl"].winfo_exists():
            fr["status_lbl"].config(text=status, fg=col)

    def _caro_update_badge(self, ctx):
        items     = [k for k, _, t in caro_items_for_eng(self._eng) if t == "item"]
        ca        = self._eng.get("caro", {})
        compliant = sum(1 for k in items if ca.get(k, {}).get("status") == "Compliant")
        non_comp  = sum(1 for k in items if ca.get(k, {}).get("status") == "Non-Compliant")
        total     = len(items)
        ctx["badge_var"].set(f"✓ {compliant}  ✗ {non_comp}  of {total} clauses")

    def _var_autofill_py(self, va):
        """
        For any PY field that is currently empty, fill it from the CY figures
        of the matching engagement for the previous financial year.

        Matching criteria:
          - Same audit_type
          - Same accounting_standard (for Statutory)
          - Financial year that is exactly one year earlier
        """
        # Parse the current FY, e.g. "FY 2024-25" → start year 2024
        fy = self._eng.get("financial_year", "")
        try:
            start_yr = int(fy.replace("FY ", "").split("-")[0].strip())
        except (ValueError, IndexError):
            return

        prev_fy_str = f"FY {start_yr - 1}-{str(start_yr)[-2:]}"

        # Find the previous-year engagement
        prev_eng = None
        for e in self._data.get("engagements", []):
            if e["id"] == self._eng["id"]:
                continue
            if e.get("financial_year") != prev_fy_str:
                continue
            if e.get("audit_type") != self._eng.get("audit_type"):
                continue
            # For Statutory, also match accounting standard
            if self._eng.get("audit_type") == "Statutory Audit":
                if e.get("accounting_standard") != self._eng.get("accounting_standard"):
                    continue
            prev_eng = e
            break

        if prev_eng is None:
            return

        prev_va = prev_eng.get("variance_analysis", {})

        filled = False
        for kind in ("balance_sheet", "profit_loss"):
            src  = prev_va.get(kind, {})   # previous year's data
            dest = va.setdefault(kind, {})  # current year's PY cells

            for ekey, cy_val_dict in src.items():
                cy_val = cy_val_dict.get("cy", "").strip() if isinstance(cy_val_dict, dict) else ""
                if not cy_val:
                    continue
                # Only fill if PY is empty — never overwrite user data
                dest.setdefault(ekey, {})
                if not dest[ekey].get("py", "").strip():
                    dest[ekey]["py"] = cy_val
                    filled = True

        if filled:
            self._panel._mark_dirty()

    def _build_variance(self, parent):
        va = self._eng.setdefault("variance_analysis",
                                  {"balance_sheet": {}, "profit_loss": {},
                                   "cy_label": "CY", "py_label": "PY"})

        # ── Auto-fill PY from previous year's CY ─────────────────────────────
        self._var_autofill_py(va)

        banner = tk.Frame(parent, bg=C["sidebar"], padx=22, pady=10)
        banner.pack(fill="x")
        left_b = tk.Frame(banner, bg=C["sidebar"])
        left_b.pack(side="left")
        tk.Frame(left_b, bg=self._accent, height=3).pack(fill="x", pady=(0, 5))
        tk.Label(left_b, text="BS & P&L VARIANCE ANALYSIS",
                 bg=C["sidebar"], fg=self._accent,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left_b, text="Enter current & prior year figures; variance is calculated automatically.",
                 bg=C["sidebar"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")

        # Print button
        pr_var = tk.Button(banner, text="🖨  Print",
            bg=C["sidebar"], fg=C["muted"],
            activebackground=C["highlight"], activeforeground=C["text"],
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=10, pady=4, command=self._print_variance)
        pr_var.pack(side="right", padx=(0, 8))
        pr_var.bind("<Enter>", lambda e: pr_var.config(bg=C["highlight"]))
        pr_var.bind("<Leave>", lambda e: pr_var.config(bg=C["sidebar"]))

        # CY/PY labels
        label_row = tk.Frame(banner, bg=C["sidebar"])
        label_row.pack(side="right")
        tk.Label(label_row, text="CY Label:", bg=C["sidebar"],
                 fg=C["muted"], font=FONT_SMALL).pack(side="left", padx=(0, 4))
        cy_var = tk.StringVar(value=va.get("cy_label", "CY"))
        tk.Entry(label_row, textvariable=cy_var, width=10, bg=C["input_bg"],
                 fg=C["text"], relief="flat", font=FONT_SMALL,
                 insertbackground=C["accent"]).pack(side="left")
        tk.Label(label_row, text="  PY Label:", bg=C["sidebar"],
                 fg=C["muted"], font=FONT_SMALL).pack(side="left", padx=(8, 4))
        py_var = tk.StringVar(value=va.get("py_label", "PY"))
        tk.Entry(label_row, textvariable=py_var, width=10, bg=C["input_bg"],
                 fg=C["text"], relief="flat", font=FONT_SMALL,
                 insertbackground=C["accent"]).pack(side="left")

        def _lbl_changed(*_):
            va["cy_label"] = cy_var.get().strip() or "CY"
            va["py_label"] = py_var.get().strip() or "PY"
            self._panel._mark_dirty()
        cy_var.trace_add("write", _lbl_changed)
        py_var.trace_add("write", _lbl_changed)

        # Inner notebook: BS + PL
        style = ttk.Style()
        style.configure("Var.TNotebook",
            background=C["bg"], borderwidth=0, tabmargins=0)
        style.configure("Var.TNotebook.Tab",
            background=C["sidebar"], foreground=C["muted"],
            padding=[14, 6], font=("Segoe UI", 9, "bold"), borderwidth=0)
        style.map("Var.TNotebook.Tab",
            background=[("selected", C["panel"])],
            foreground=[("selected", self._accent)])

        nb2 = ttk.Notebook(parent, style="Var.TNotebook")
        nb2.pack(fill="both", expand=True)

        bs_frame = tk.Frame(nb2, bg=C["bg"])
        nb2.add(bs_frame, text="  Balance Sheet  ")
        self._build_var_table(bs_frame, va, "balance_sheet",
                              BALANCE_SHEET_TEMPLATE, cy_var, py_var)

        pl_frame = tk.Frame(nb2, bg=C["bg"])
        nb2.add(pl_frame, text="  Profit & Loss  ")
        self._build_var_table(pl_frame, va, "profit_loss",
                              PL_TEMPLATE, cy_var, py_var)

    def _build_var_table(self, parent, va, kind, template, cy_var, py_var):
        outer = tk.Frame(parent, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        cv = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", style="Thin.Vertical.TScrollbar", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(cv, bg=C["bg"])
        cwin = cv.create_window((0, 0), window=inner, anchor="nw")
        cv.bind("<Configure>", lambda e, c=cv, w=cwin: c.itemconfig(w, width=e.width))
        inner.bind("<Configure>", lambda e, c=cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        # Mouse-wheel scrolling — bound to `outer` so it stays active even when
        # the pointer moves over Entry widgets inside the canvas window.
        def _on_mw(event, c=cv):
            c.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def _bind_mw(e, c=cv, f=_on_mw):
            c.bind_all("<MouseWheel>", f)
        def _unbind_mw(e, c=cv):
            c.unbind_all("<MouseWheel>")
        outer.bind("<Enter>", _bind_mw)
        outer.bind("<Leave>", _unbind_mw)
        # Also bind Linux scroll buttons
        outer.bind("<Button-4>", lambda e, c=cv: c.yview_scroll(-1, "units"))
        outer.bind("<Button-5>", lambda e, c=cv: c.yview_scroll(+1, "units"))

        data_root = va.setdefault(kind, {})

        # total_widgets: ekey -> {cy_lbl, py_lbl, var_lbl, pct_lbl, fg, bg, font}
        total_widgets = {}

        # Column header
        hdr = tk.Frame(inner, bg=C["panel"])
        hdr.pack(fill="x", padx=12, pady=(12, 0))
        for txt, w in [("Line Item", 36), ("CY", 13), ("PY", 13), ("Variance", 13), ("%", 9), ("Remarks", 28)]:
            tk.Label(hdr, text=txt, bg=C["panel"], fg=C["accent"],
                     font=("Segoe UI", 8, "bold"), width=w, anchor="w"
                     ).pack(side="left", padx=2)

        for ekey, label, etype in template:
            self._var_row(inner, data_root, ekey, label, etype,
                          kind, va, cy_var, py_var, total_widgets)

        # Initial total computation once all rows are built
        self._recalc_var_totals(data_root, total_widgets)

    def _recalc_var_totals(self, data_root, total_widgets):
        """Recompute every total row from VARIANCE_TOTALS and update its labels.
        Blank fields are treated as 0 so totals always show once any data exists."""
        computed = {}  # key -> (cy_f, py_f) — may be None if a chained total failed
        for tot_key, components in VARIANCE_TOTALS.items():
            cy_sum = 0.0
            py_sum = 0.0
            any_data = False   # True once at least one non-blank component is found
            parse_err = False
            for sign, comp_key in components:
                if comp_key in computed:
                    c_cy, c_py = computed[comp_key]
                    if c_cy is None:
                        parse_err = True; break
                    cy_sum += sign * c_cy
                    py_sum += sign * c_py
                    any_data = True
                else:
                    entry = data_root.get(comp_key, {})
                    cy_s  = entry.get("cy", "").strip()
                    py_s  = entry.get("py", "").strip()
                    try:
                        cy_f = float(cy_s.replace(",", "")) if cy_s else 0.0
                        py_f = float(py_s.replace(",", "")) if py_s else 0.0
                    except ValueError:
                        parse_err = True; break
                    if cy_s or py_s:
                        any_data = True
                    cy_sum += sign * cy_f
                    py_sum += sign * py_f
            ok = any_data and not parse_err
            computed[tot_key] = (cy_sum, py_sum) if ok else (None, None)
            if tot_key not in total_widgets:
                continue
            tw = total_widgets[tot_key]
            if not ok:
                tw["cy_lbl"].config(text="—")
                tw["py_lbl"].config(text="—")
                tw["var_lbl"].config(text="")
                tw["pct_lbl"].config(text="")
                continue
            diff = cy_sum - py_sum
            pct  = (diff / py_sum * 100) if py_sum else None
            tw["cy_lbl"].config(text=f"{cy_sum:,.0f}")
            tw["py_lbl"].config(text=f"{py_sum:,.0f}")
            tw["var_lbl"].config(text=f"{diff:,.0f}")
            if pct is not None:
                col = C["danger"] if abs(pct) > VARIANCE_THRESHOLD_PCT else C["success"]
                tw["pct_lbl"].config(text=f"{pct:+.1f}%", fg=col)
            else:
                tw["pct_lbl"].config(text="—", fg=tw["fg"])

    def _var_row(self, parent, data_root, ekey, label, etype,
                 kind, va, cy_var, py_var, total_widgets):
        if etype == "header":
            fr = tk.Frame(parent, bg=C["sidebar"])
            fr.pack(fill="x", padx=12, pady=(8, 0))
            tk.Label(fr, text=label, bg=C["sidebar"], fg=C["muted"],
                     font=("Segoe UI", 8, "bold"), padx=6, pady=3).pack(anchor="w")
            return

        entry  = data_root.get(ekey, {})
        is_tot = (etype == "total")
        bg     = C["highlight"] if is_tot else C["bg"]
        fg     = C["text"]      if is_tot else C["muted"]
        font   = ("Segoe UI", 9, "bold") if is_tot else FONT_SMALL

        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", padx=12, pady=1)

        tk.Label(row, text=label, bg=bg, fg=fg, font=font,
                 width=36, anchor="w").pack(side="left", padx=2)

        var_lbl = tk.Label(row, text="", bg=bg, fg=fg, font=font, width=13, anchor="e")
        pct_lbl = tk.Label(row, text="", bg=bg, fg=fg, font=font, width=9,  anchor="e")

        if is_tot:
            cy_lbl = tk.Label(row, text="—", bg=bg, fg=fg, font=font, width=13, anchor="e")
            cy_lbl.pack(side="left", padx=2)
            py_lbl = tk.Label(row, text="—", bg=bg, fg=fg, font=font, width=13, anchor="e")
            py_lbl.pack(side="left", padx=2)
            var_lbl.pack(side="left", padx=2)
            pct_lbl.pack(side="left", padx=2)
            total_widgets[ekey] = {
                "cy_lbl": cy_lbl, "py_lbl": py_lbl,
                "var_lbl": var_lbl, "pct_lbl": pct_lbl,
                "fg": fg, "bg": bg, "font": font,
            }
        else:
            cy_var2 = tk.StringVar(value=entry.get("cy", ""))
            py_var2 = tk.StringVar(value=entry.get("py", ""))
            cy_e = tk.Entry(row, textvariable=cy_var2, width=13,
                bg=C["input_bg"], fg=C["text"], relief="flat",
                font=FONT_SMALL, insertbackground=C["accent"])
            cy_e.pack(side="left", padx=2, ipady=2)
            py_e = tk.Entry(row, textvariable=py_var2, width=13,
                bg=C["input_bg"], fg=C["text"], relief="flat",
                font=FONT_SMALL, insertbackground=C["accent"])
            py_e.pack(side="left", padx=2, ipady=2)
            var_lbl.pack(side="left", padx=2)
            pct_lbl.pack(side="left", padx=2)

            def _calc(*_, ek=ekey, cv=cy_var2, pv=py_var2,
                      vl=var_lbl, pl=pct_lbl, dr=data_root, tw=total_widgets):
                try:
                    cy_f = float(cv.get().replace(",", "")) if cv.get().strip() else None
                    py_f = float(pv.get().replace(",", "")) if pv.get().strip() else None
                except ValueError:
                    vl.config(text="—"); pl.config(text="—"); return
                dr.setdefault(ek, {})
                dr[ek]["cy"] = cv.get().strip()
                dr[ek]["py"] = pv.get().strip()
                self._panel._mark_dirty()
                if cy_f is None or py_f is None:
                    vl.config(text="—"); pl.config(text="—")
                else:
                    diff = cy_f - py_f
                    pct  = (diff / py_f * 100) if py_f else None
                    vl.config(text=f"{diff:,.0f}")
                    if pct is not None:
                        col = C["danger"] if abs(pct) > VARIANCE_THRESHOLD_PCT else C["success"]
                        pl.config(text=f"{pct:+.1f}%", fg=col)
                    else:
                        pl.config(text="—")
                self._recalc_var_totals(dr, tw)

            cy_var2.trace_add("write", _calc)
            py_var2.trace_add("write", _calc)
            _calc()

        # Remarks (all row types)
        rem_var = tk.StringVar(value=entry.get("remarks", ""))
        rem_e   = tk.Entry(row, textvariable=rem_var, width=28,
            bg=C["input_bg"], fg=C["text"], relief="flat",
            font=FONT_SMALL, insertbackground=C["accent"])
        rem_e.pack(side="left", padx=2, ipady=2, fill="x", expand=True)

        def _save_remark(*_, ek=ekey, rv=rem_var, dr=data_root):
            dr.setdefault(ek, {})["remarks"] = rv.get()
            self._panel._mark_dirty()

        rem_var.trace_add("write", _save_remark)

    # ══════════════════════════════════════════════════════════════════════════
    # Shared attachment helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _open_pad_template(self, doc_key, doc_name):
        """Extract the embedded template for a pre-audit document and open it."""
        if doc_key not in PAD_TEMPLATES:
            messagebox.showinfo("No Template",
                f"No embedded template for '{doc_name}'.", parent=self)
            return
        ext, b64 = PAD_TEMPLATES[doc_key]
        import base64, tempfile
        data = base64.b64decode(b64)
        # Build a clean filename from the doc name
        safe = doc_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        safe = "".join(c for c in safe if c.isalnum() or c in "_-")
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=ext,
            prefix=f"PNA_{safe}_",
            dir=tempfile.gettempdir())
        tmp.write(data)
        tmp.close()
        try:
            if sys.platform == "win32":
                os.startfile(tmp.name)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", tmp.name])
            else:
                subprocess.Popen(["xdg-open", tmp.name])
        except Exception as e:
            messagebox.showerror("Open Error", str(e), parent=self)

    def _att_dir(self, key, bucket):
        """Return (and create) the folder for attachments in a given bucket."""
        if not self._filepath:
            return None
        base = os.path.splitext(self._filepath)[0] + "_files"
        d = os.path.join(base, "engagements", self._eng["id"], bucket, key)
        os.makedirs(d, exist_ok=True)
        return d

    def _attach(self, key, refresh_fn, bucket):
        if not self._filepath:
            messagebox.showinfo("Save First",
                "Please save the file before attaching.",
                parent=self); return
        paths = filedialog.askopenfilenames(
            title="Attach Files",
            filetypes=[("All supported",
                "*.pdf *.xlsx *.xls *.xlsm *.doc *.docx *.csv *.txt *.png *.jpg"),
                ("All files", "*.*")],
            parent=self)
        if not paths:
            return
        d = self._att_dir(key, bucket)
        if bucket == "wp":
            store = self._eng["workpapers"].setdefault(key, {})
            lst   = store.setdefault("attachments", [])
        elif bucket == "pad":
            lst = self._eng["pre_audit_docs"].setdefault(key, [])
        elif bucket == "ifc":
            # key format: "{sec_key}_q_{num}"  e.g. "assets_q_1"
            sk, num_part = key.split("_q_", 1)
            dk = "q_" + num_part
            q_store = self._eng["ifc"].setdefault(sk, {}).setdefault(
                dk, {"response": "", "comment": "", "files": [], "na": False})
            lst = q_store.setdefault("files", [])
        elif bucket == "fin":
            lst = self._eng.setdefault("financials", {}).setdefault(key, [])
        elif bucket == "sch3":
            lst = self._eng.setdefault("sch3", {}).setdefault(key, {}).setdefault("attachments", [])
        elif bucket == "caro":
            lst = self._eng.setdefault("caro", {}).setdefault(key, {}).setdefault("attachments", [])
        else:
            store = self._eng["legal_sec"].setdefault(key, {})
            lst   = store.setdefault("attachments", [])

        added, skipped = 0, []
        for p in paths:
            fname = os.path.basename(p)
            if fname in lst:
                skipped.append(fname); continue
            try:
                shutil.copy2(p, os.path.join(d, fname))
                lst.append(fname); added += 1
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=self)
        if skipped:
            messagebox.showinfo("Skipped",
                f"Already attached: {', '.join(skipped)}", parent=self)
        if added:
            self._panel._mark_dirty()
            refresh_fn()

    def _att_row(self, parent, key, fname, refresh_fn, bucket):
        ext = os.path.splitext(fname)[1].lower()
        tag_colors = {".pdf": "#E05C5C", ".xlsx": "#2ECC71", ".xls": "#2ECC71",
                      ".xlsm": "#2ECC71", ".doc": "#4A90D9", ".docx": "#4A90D9"}
        tag_bg  = tag_colors.get(ext, C["muted"])
        tag_txt = ext.lstrip(".").upper() if ext else "FILE"

        row = tk.Frame(parent, bg=C["highlight"],
                       highlightthickness=1, highlightbackground=C["border"])
        row.pack(fill="x", padx=8, pady=2)
        inner_row = tk.Frame(row, bg=C["highlight"], padx=6, pady=5)
        inner_row.pack(fill="x")
        tk.Label(inner_row, text=f" {tag_txt} ", bg=tag_bg, fg="#fff",
                 font=("Segoe UI", 7, "bold")).pack(side="left", padx=(0, 8))
        disp = fname if len(fname) <= 50 else fname[:47] + "…"
        name_lbl = tk.Label(inner_row, text=disp, bg=C["highlight"], fg=C["text"],
                 font=FONT_SMALL, anchor="w", cursor="hand2")
        name_lbl.pack(side="left", fill="x", expand=True)
        name_lbl.bind("<Button-1>", lambda e: _open())

        def _remove(k=key, fn=fname, rf=refresh_fn, b=bucket):
            if not messagebox.askyesno("Remove Attachment",
                    f"Remove '{fn}'?\n\nThis will delete the file from disk permanently.",
                    parent=self):
                return
            if b == "wp":
                atts = self._eng["workpapers"].get(k, {}).get("attachments", [])
            elif b == "pad":
                atts = self._eng["pre_audit_docs"].get(k, [])
            elif b == "ifc":
                sk2, np2 = k.split("_q_", 1)
                dk2 = "q_" + np2
                atts = self._eng["ifc"].get(sk2, {}).get(dk2, {}).get("files", [])
            elif b == "fin":
                atts = self._eng.get("financials", {}).get(k, [])
            elif b == "sch3":
                atts = self._eng.get("sch3", {}).get(k, {}).get("attachments", [])
            elif b == "caro":
                atts = self._eng.get("caro", {}).get(k, {}).get("attachments", [])
            else:
                atts = self._eng["legal_sec"].get(k, {}).get("attachments", [])
            if fn in atts:
                atts.remove(fn)
            d = self._att_dir(k, b)
            if d:
                fpath = os.path.join(d, fn)
                try:
                    os.remove(fpath)
                except FileNotFoundError:
                    pass
                except Exception as ex:
                    messagebox.showwarning("Delete Failed",
                        f"Removed from record, but could not delete file from disk:\n{fpath}\n\n{ex}",
                        parent=self)
            self._panel._mark_dirty()
            rf()

        def _open(k=key, fn=fname, b=bucket):
            d = self._att_dir(k, b)
            if not d: return
            path = os.path.join(d, fn)
            if not os.path.exists(path):
                messagebox.showerror("Not Found", f"File not found:\n{path}",
                                     parent=self); return
            try:
                if sys.platform == "win32": os.startfile(path)
                elif sys.platform == "darwin": subprocess.Popen(["open", path])
                else: subprocess.Popen(["xdg-open", path])
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=self)

        if not self._eng.get("locked", False):
            tk.Button(inner_row, text="✕", font=("Segoe UI", 8),
                bg=C["highlight"], fg=C["danger"],
                activebackground=C["highlight"], relief="flat", cursor="hand2",
                bd=0, padx=6, command=_remove).pack(side="right")
        ob = tk.Button(inner_row, text="↗ Open", font=("Segoe UI", 8),
            bg=C["accent"], fg="#fff",
            activebackground=C["btn_hover"], relief="flat", cursor="hand2",
            bd=0, padx=8, pady=3, command=_open)
        ob.pack(side="right", padx=(0, 4))
        ob.bind("<Enter>", lambda e: ob.config(bg=C["btn_hover"]))
        ob.bind("<Leave>", lambda e: ob.config(bg=C["accent"]))


# ══════════════════════════════════════════════════════════════════════════════
# DetailPanel — Company + Engagements list
# ══════════════════════════════════════════════════════════════════════════════

class DetailPanel(tk.Frame):
    """Company dashboard — shown when a .cafe file is open."""

    def __init__(self, parent, data, filepath, on_save, on_close):
        super().__init__(parent, bg=C["bg"])
        self._data       = migrate(dict(data))
        self._filepath   = filepath
        self._on_save    = on_save
        self._on_close   = on_close
        self._dirty      = False
        self._active     = None
        self._prog_cache = {}          # eng id → progress dict
        self._build()

    # ══════════════════════════════════════════════════════════════════════
    # Progress computation
    # ══════════════════════════════════════════════════════════════════════

    def _compute_eng_progress(self, eng):
        """Return dict of tab_key→float (0–1) and 'overall'→float."""
        eid = eng["id"]
        if eid in self._prog_cache:
            return self._prog_cache[eid]

        is_tax = (eng.get("audit_type") == "Tax Audit")
        p = {}

        # Pre-Audit Docs — storage keys are prefixed "pad_"
        pad_slots = PRE_AUDIT_DOCS_TAX if is_tax else PRE_AUDIT_DOCS_STAT
        pad       = eng.get("pre_audit_docs", {})
        att_count = sum(1 for k, _ in pad_slots if pad.get(f"pad_{k}"))
        p["preaudit"] = att_count / len(pad_slots) if pad_slots else 0.0

        # Financials
        fin_slots = FINANCIALS_DOCS_TAX if is_tax else FINANCIALS_DOCS_STAT
        fin       = eng.get("financials", {})
        fin_count = sum(1 for k, _, _ in fin_slots if fin.get(k))
        p["financials"] = fin_count / len(fin_slots) if fin_slots else 0.0

        # Notes to Accounts / Form 3CD
        wp    = eng.get("workpapers", {})
        its   = items_for_eng(eng)
        total = len(its)
        if total:
            done = sum(1 for v in wp.values()
                       if v.get("status") in ("Completed", "N/A"))
            p["notes"] = done / total
        else:
            p["notes"] = 0.0

        # Schedule III (statutory only)
        if not is_tax:
            sch3_its = [k for k, _, t in SCH3_ITEMS if t == "item"]
            sch3     = eng.get("sch3", {})
            sch3_done = sum(1 for k in sch3_its
                            if sch3.get(k, {}).get("status", "Not Checked") != "Not Checked")
            p["sch3"] = sch3_done / len(sch3_its) if sch3_its else 0.0
        else:
            p["sch3"] = None   # not applicable

        # IFC — responses stored under "response" key, valid values: Yes/No/Partial or na=True
        ifc_total = sum(len(qs) for _, _, qs in IFC_CHECKLISTS)
        ifc       = eng.get("ifc", {})
        if eng.get("ifc_na"):
            p["ifc"] = 1.0
        elif ifc_total:
            ifc_done = 0
            for sk, _, qs in IFC_CHECKLISTS:
                sec = ifc.get(sk, {})
                for qk, _ in qs:
                    ans = sec.get(qk, {})
                    if isinstance(ans, dict) and (
                            ans.get("response") in ("Yes", "No", "Partial")
                            or ans.get("na")):
                        ifc_done += 1
            p["ifc"] = ifc_done / ifc_total
        else:
            p["ifc"] = 0.0

        # CARO (statutory only) — only count "item" rows, default status is "Not Checked"
        if not is_tax:
            all_caro  = caro_items_for_eng(eng)
            caro_keys = [k for k, lbl, kind, *_ in all_caro if kind == "item"]
            caro      = eng.get("caro", {})
            if eng.get("caro_na"):
                p["caro"] = 1.0
            elif caro_keys:
                caro_done = sum(1 for k in caro_keys
                                if caro.get(k, {}).get("status", "Not Checked") != "Not Checked")
                p["caro"] = caro_done / len(caro_keys)
            else:
                p["caro"] = 0.0
        else:
            p["caro"] = None

        # Legal & Secretarial (statutory only)
        if not is_tax:
            ls_its  = [k for k, _, t in LEGAL_SEC_ITEMS if t == "item"]
            ls      = eng.get("legal_sec", {})
            ls_done = sum(1 for k in ls_its
                          if ls.get(k, {}).get("status", "Not Checked") != "Not Checked")
            p["legalsec"] = ls_done / len(ls_its) if ls_its else 0.0
        else:
            p["legalsec"] = None

        # Variance — check for any non-zero CY values in variance_analysis
        va = eng.get("variance_analysis", {})
        cy_vals = []
        for section in ("balance_sheet", "profit_loss"):
            for item_data in va.get(section, {}).values():
                if isinstance(item_data, dict):
                    cy = item_data.get("cy")
                    if cy not in (None, "", "0", 0, 0.0):
                        cy_vals.append(cy)
        p["variance"] = 1.0 if cy_vals else 0.0

        # Overall = mean of applicable tabs
        vals = [v for v in p.values() if v is not None]
        p["overall"] = sum(vals) / len(vals) if vals else 0.0

        self._prog_cache[eid] = p
        return p

    def _invalidate_cache(self, eid=None):
        if eid:
            self._prog_cache.pop(eid, None)
        else:
            self._prog_cache.clear()

    # ══════════════════════════════════════════════════════════════════════
    # Build
    # ══════════════════════════════════════════════════════════════════════

    def _build(self):
        # ── Top bar ──────────────────────────────────────────────────────
        top = tk.Frame(self, bg=C["sidebar"], pady=6)
        top.pack(fill="x")

        # Left: accent bar + company name + filepath
        tb_left = tk.Frame(top, bg=C["sidebar"])
        tb_left.pack(side="left", fill="y")
        tk.Frame(tb_left, bg=C["accent"], width=4).pack(side="left", fill="y")
        tb_info = tk.Frame(tb_left, bg=C["sidebar"], padx=16, pady=10)
        tb_info.pack(side="left")
        self._title_lbl = tk.Label(tb_info,
            text=self._data["company_name"],
            bg=C["sidebar"], fg=C["text"],
            font=("Segoe UI", 12, "bold"))
        self._title_lbl.pack(anchor="w")
        fname = os.path.basename(self._filepath) if self._filepath else "Unsaved"
        self._file_lbl = tk.Label(tb_info, text=fname,
            bg=C["sidebar"], fg=C["muted"], font=FONT_MONO)
        self._file_lbl.pack(anchor="w")

        # Right: offline badge + back + save
        tb_right = tk.Frame(top, bg=C["sidebar"], padx=16)
        tb_right.pack(side="right", fill="y")

        styled_button(tb_right, "← Back", self._on_close,
                      kind="secondary", width=10).pack(side="left", padx=(0, 6))
        self._save_btn = styled_button(tb_right, "💾  Save", self._save,
                                       kind="primary", width=12)
        self._save_btn.pack(side="left")

        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

        # ── 3-zone body ──────────────────────────────────────────────────
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Left panel (fixed 230px)
        self._left_panel = tk.Frame(body, bg=C["sidebar"], width=230)
        self._left_panel.pack(side="left", fill="y")
        self._left_panel.pack_propagate(False)
        tk.Frame(body, bg=C["border"], width=1).pack(side="left", fill="y")

        # Right main area
        self._right_panel = tk.Frame(body, bg=C["bg"])
        self._right_panel.pack(side="left", fill="both", expand=True)

        self._build_left_panel()
        self._build_right_panel()

    # ══════════════════════════════════════════════════════════════════════
    # Left panel — company identity
    # ══════════════════════════════════════════════════════════════════════

    def _build_left_panel(self):
        for w in self._left_panel.winfo_children():
            w.destroy()

        p = self._left_panel
        engs = self._data.get("engagements", [])

        # Avatar
        av_frame = tk.Frame(p, bg=C["sidebar"], pady=22)
        av_frame.pack(fill="x", padx=20)
        name = self._data.get("company_name", "?")
        initials = "".join(w[0].upper() for w in name.split()[:2]) or "?"
        av_canvas = tk.Canvas(av_frame, width=54, height=54,
                              bg=C["sidebar"], highlightthickness=0)
        av_canvas.pack()
        av_canvas.create_oval(2, 2, 52, 52,
            fill=C["highlight"], outline=C["accent"], width=1)
        av_canvas.create_text(27, 27, text=initials,
            font=("Segoe UI", 18, "bold"), fill=C["accent"])

        # Company name
        tk.Label(p, text=name, bg=C["sidebar"], fg=C["text"],
                 font=("Segoe UI", 11, "bold"),
                 wraplength=190, justify="center").pack(padx=14, pady=(0, 4))

        # CIN chip
        cin = self._data.get("company_cin", "")
        if cin:
            cin_frm = tk.Frame(p, bg=C["chip_active"],
                               padx=8, pady=3)
            cin_frm.pack(padx=20, pady=(0, 4))
            tk.Label(cin_frm, text=f"CIN: {cin}",
                     bg=C["chip_active"], fg=C["muted"],
                     font=("Consolas", 8)).pack()

        # Address
        addr = self._data.get("company_addr", "")
        if addr:
            tk.Label(p, text=addr[:80] + ("…" if len(addr) > 80 else ""),
                     bg=C["sidebar"], fg=C["muted"],
                     font=("Segoe UI", 8), wraplength=190,
                     justify="center").pack(padx=14, pady=(0, 6))

        tk.Frame(p, bg=C["border"], height=1).pack(fill="x", padx=16, pady=8)

        # Quick stats
        total_e  = len(engs)
        locked_e = sum(1 for e in engs if e.get("locked"))
        progs    = [self._compute_eng_progress(e)["overall"] for e in engs]
        done_e   = sum(1 for v in progs if v >= 1.0)

        stats = [
            ("📁", f"{total_e}", "Engagement" + ("s" if total_e != 1 else ""), C["text"]),
            ("🔒", f"{locked_e}", "Locked",   C["accent2"] if locked_e else C["muted"]),
            ("✓",  f"{done_e}",  "Complete",  C["success"] if done_e else C["muted"]),
        ]
        for icon, val, lbl, fg in stats:
            row = tk.Frame(p, bg=C["panel"], padx=14, pady=8,
                           highlightthickness=1, highlightbackground=C["border"])
            row.pack(fill="x", padx=16, pady=3)
            tk.Label(row, text=icon, bg=C["panel"],
                     font=("Segoe UI", 12)).pack(side="left")
            tk.Label(row, text=f"  {val}", bg=C["panel"], fg=fg,
                     font=("Segoe UI", 13, "bold")).pack(side="left")
            tk.Label(row, text=f"  {lbl}", bg=C["panel"], fg=C["muted"],
                     font=("Segoe UI", 8)).pack(side="left")

        tk.Frame(p, bg=C["border"], height=1).pack(fill="x", padx=16, pady=10)

        # Edit company details — opens a proper dialog
        edit_btn = tk.Button(p, text="✎  Edit Company Details",
            bg=C["sidebar"], fg=C["accent"],
            activebackground=C["chip_active"], activeforeground=C["accent"],
            font=("Segoe UI", 8, "bold"), relief="flat",
            cursor="hand2", bd=0, pady=6,
            command=self._open_edit_dialog)
        edit_btn.pack(padx=16, anchor="w")

        # Spacer + filepath at bottom
        tk.Frame(p, bg=C["sidebar"]).pack(fill="both", expand=True)
        fname = os.path.basename(self._filepath) if self._filepath else "Unsaved"
        tk.Label(p, text=fname, bg=C["sidebar"], fg=C["border"],
                 font=("Consolas", 8), wraplength=200).pack(
                 side="bottom", pady=10, padx=10)

    def _open_edit_dialog(self):
        """Open a full-size dialog for editing company details."""
        dlg = tk.Toplevel(self.winfo_toplevel())
        dlg.title("Edit Company Details")
        dlg.configure(bg=C["bg"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.geometry("560x610")

        # Centre
        dlg.update_idletasks()
        root = self.winfo_toplevel()
        x = root.winfo_x() + root.winfo_width()  // 2 - 280
        y = root.winfo_y() + root.winfo_height() // 2 - 305
        dlg.geometry(f"560x610+{x}+{y}")

        # Header
        tk.Frame(dlg, bg=C["accent"], height=4).pack(fill="x")
        hdr = tk.Frame(dlg, bg=C["sidebar"], padx=28, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Company Details",
                 bg=C["sidebar"], fg=C["accent"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(hdr, text="Edit company information stored in this file",
                 bg=C["sidebar"], fg=C["muted"],
                 font=("Segoe UI", 9)).pack(anchor="w")
        tk.Frame(dlg, bg=C["border"], height=1).pack(fill="x")

        # Button bar — packed BEFORE body so it always anchors to bottom
        tk.Frame(dlg, bg=C["border"], height=1).pack(side="bottom", fill="x")
        btn_bar = tk.Frame(dlg, bg=C["sidebar"], padx=28, pady=14)
        btn_bar.pack(side="bottom", fill="x")

        def _save_and_close():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Missing Name",
                    "Company name cannot be blank.", parent=dlg)
                return
            self._data["company_name"]  = name
            self._data["company_cin"]   = cin_var.get().strip().upper()
            self._data["company_addr"]  = addr_text.get("1.0", "end").strip()
            self._data["company_notes"] = notes_text.get("1.0", "end").strip()
            self._mark_dirty()
            self._title_lbl.config(text=self._data["company_name"])
            self._build_left_panel()
            dlg.destroy()

        save_btn = tk.Button(btn_bar, text="✓  Save Changes",
            bg=C["btn_primary"], fg=C["bg"],
            activebackground=C["btn_hover"], activeforeground=C["bg"],
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=20, pady=10, command=_save_and_close)
        save_btn.pack(side="left")
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg=C["btn_hover"]))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=C["btn_primary"]))

        cancel_btn = tk.Button(btn_bar, text="Cancel",
            bg=C["btn_secondary"], fg=C["text"],
            activebackground=C["border"], activeforeground=C["text"],
            font=("Segoe UI", 10), relief="flat", cursor="hand2",
            bd=0, padx=16, pady=10, command=dlg.destroy)
        cancel_btn.pack(side="left", padx=(10, 0))
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg=C["border"]))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg=C["btn_secondary"]))

        # Body — fills remaining space between header and button bar
        body = tk.Frame(dlg, bg=C["bg"], padx=28, pady=20)
        body.pack(fill="both", expand=True)

        # Company Name
        tk.Label(body, text="Company Name",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 3))
        name_var = tk.StringVar(value=self._data.get("company_name", ""))
        styled_entry(body, textvariable=name_var, width=50
                     ).pack(fill="x", ipady=6)

        # CIN
        tk.Label(body, text="CIN  (Corporate Identity Number)",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(14, 3))
        cin_var = tk.StringVar(value=self._data.get("company_cin", ""))
        styled_entry(body, textvariable=cin_var, width=50
                     ).pack(fill="x", ipady=6)

        # Address
        tk.Label(body, text="Registered Office Address",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(14, 3))
        addr_text = tk.Text(body, height=4,
            bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=FONT_BODY,
            highlightthickness=1, highlightbackground=C["input_border"],
            highlightcolor=C["accent"])
        addr_text.pack(fill="x")
        addr_text.insert("1.0", self._data.get("company_addr", ""))

        # Notes
        tk.Label(body, text="Notes",
                 bg=C["bg"], fg=C["muted"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(14, 3))
        notes_text = tk.Text(body, height=4,
            bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"], relief="flat",
            font=FONT_BODY,
            highlightthickness=1, highlightbackground=C["input_border"])
        notes_text.pack(fill="x")
        notes_text.insert("1.0", self._data.get("company_notes", ""))

        dlg.wait_window()
    # ══════════════════════════════════════════════════════════════════════
    # Right panel — engagement cards
    # ══════════════════════════════════════════════════════════════════════

    def _build_right_panel(self):
        p = self._right_panel

        # Toolbar
        toolbar = tk.Frame(p, bg=C["sidebar"], padx=20, pady=10)
        toolbar.pack(fill="x")
        tk.Label(toolbar, text="ENGAGEMENTS",
                 bg=C["sidebar"], fg=C["muted"],
                 font=("Segoe UI", 8, "bold")).pack(side="left")

        add_btn = tk.Button(toolbar, text="＋  New Engagement",
            font=("Segoe UI", 9, "bold"),
            bg=C["accent"], fg=C["bg"],
            activebackground=C["btn_hover"], activeforeground=C["bg"],
            relief="flat", cursor="hand2", bd=0, padx=14, pady=6,
            command=self._add_eng)
        add_btn.pack(side="right")
        add_btn.bind("<Enter>", lambda e: add_btn.config(bg=C["btn_hover"]))
        add_btn.bind("<Leave>", lambda e: add_btn.config(bg=C["accent"]))

        tk.Frame(p, bg=C["border"], height=1).pack(fill="x")

        # Scrollable card area
        self._cards_frame = tk.Frame(p, bg=C["bg"])
        self._cards_frame.pack(fill="both", expand=True)

        self._eng_canvas = tk.Canvas(self._cards_frame, bg=C["bg"],
                                     highlightthickness=0)
        eng_sb = ttk.Scrollbar(self._cards_frame, orient="vertical",
                               style="Thin.Vertical.TScrollbar",
                               command=self._eng_canvas.yview)
        self._eng_canvas.configure(yscrollcommand=eng_sb.set)
        eng_sb.pack(side="right", fill="y")
        self._eng_canvas.pack(side="left", fill="both", expand=True)

        self._eng_inner = tk.Frame(self._eng_canvas, bg=C["bg"])
        self._eng_cwin  = self._eng_canvas.create_window(
            (0, 0), window=self._eng_inner, anchor="nw")
        self._eng_canvas.bind("<Configure>",
            lambda e: self._eng_canvas.itemconfig(
                self._eng_cwin, width=e.width))
        self._eng_inner.bind("<Configure>",
            lambda e: self._eng_canvas.configure(
                scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))

        def _mw(ev, c=self._eng_canvas):
            c.yview_scroll(int(-1*(ev.delta/120)), "units")
        self._cards_frame.bind("<Enter>",
            lambda e: self._eng_canvas.bind_all("<MouseWheel>", _mw))
        self._eng_canvas.bind("<Enter>",
            lambda e: self._eng_canvas.bind_all("<MouseWheel>", _mw))
        self._cards_frame.bind("<Leave>",
            lambda e: self._eng_canvas.unbind_all("<MouseWheel>"))

        self._rebuild_all_cards()

    def _rebuild_all_cards(self):
        for w in self._eng_inner.winfo_children():
            w.destroy()

        engs = self._data.get("engagements", [])
        if not engs:
            empty = tk.Frame(self._eng_inner, bg=C["bg"])
            empty.pack(expand=True, pady=80)
            tk.Label(empty, text="✦", bg=C["bg"], fg=C["border"],
                     font=("Segoe UI", 32)).pack()
            tk.Label(empty, text="No engagements yet",
                     bg=C["bg"], fg=C["text"],
                     font=("Segoe UI", 13, "bold")).pack(pady=(8, 4))
            tk.Label(empty, text="Click  ＋ New Engagement  to begin",
                     bg=C["bg"], fg=C["muted"],
                     font=("Segoe UI", 10)).pack()
            return

        def _sort_key(e):
            fy    = e.get("financial_year", "")
            parts = fy.replace("FY ", "").split("-")
            try:    yr = int(parts[0])
            except: yr = 0
            typ = 0 if e.get("audit_type") == "Statutory Audit" else 1
            return (-yr, typ)

        for eng in sorted(engs, key=_sort_key):
            self._build_eng_card(eng)
        tk.Frame(self._eng_inner, bg=C["bg"], height=24).pack()

    # ── Rich engagement card ──────────────────────────────────────────────

    def _build_eng_card(self, eng):
        eid       = eng["id"]
        is_tax    = (eng.get("audit_type") == "Tax Audit")
        is_active = (eid == self._active)
        is_locked = eng.get("locked", False)
        accent    = C["accent2"] if is_tax else C["accent"]
        card_bg   = C["highlight"] if is_active else C["panel"]
        bdr_col   = accent if is_active else C["border"]

        prog = self._compute_eng_progress(eng)
        overall_pct = prog["overall"]

        # Card outer
        card = tk.Frame(self._eng_inner, bg=card_bg,
                        highlightthickness=1, highlightbackground=bdr_col)
        card.pack(fill="x", padx=24, pady=(10, 0))
        hover_bg = C["highlight"] if not is_active else card_bg
        card.bind("<Enter>", lambda e, f=card, bg=hover_bg: f.config(bg=bg) if not is_active else None)
        card.bind("<Leave>", lambda e, f=card, bg=card_bg: f.config(bg=bg))

        # Left accent bar
        tk.Frame(card, bg=accent, width=5).pack(side="left", fill="y")

        # Card body
        body = tk.Frame(card, bg=card_bg, padx=18, pady=14)
        body.pack(side="left", fill="both", expand=True)

        # ── Row 1: badges + lock/firm ──
        row1 = tk.Frame(body, bg=card_bg)
        row1.pack(fill="x")

        # FY badge
        fy_badge = tk.Label(row1,
            text=f" {eng.get('financial_year','').replace('FY ','')} ",
            bg=C["chip_active"], fg=C["text"],
            font=("Segoe UI", 8, "bold"), padx=6, pady=2)
        fy_badge.pack(side="left", padx=(0, 5))

        # Audit type badge
        if is_tax:
            type_txt, type_bg, type_fg = "TAX AUDIT", "#2A1F0F", "#D4A060"
        else:
            type_txt, type_bg, type_fg = "STATUTORY", "#0F1A2A", "#8AA8E8"
        tk.Label(row1, text=f" {type_txt} ",
                 bg=type_bg, fg=type_fg,
                 font=("Segoe UI", 7, "bold"), padx=6, pady=2
                 ).pack(side="left", padx=(0, 5))

        # AS/Ind AS badge (statutory only)
        if not is_tax:
            std = eng.get("accounting_standard", "AS")
            tk.Label(row1, text=f" {std} ",
                     bg="#0F1F1A", fg="#5CB8AC",
                     font=("Segoe UI", 7, "bold"), padx=6, pady=2
                     ).pack(side="left", padx=(0, 5))

        # Lock indicator
        if is_locked:
            tk.Label(row1, text="  🔒 Locked",
                     bg=card_bg, fg=C["danger"],
                     font=("Segoe UI", 8, "bold")).pack(side="left", padx=(4, 0))

        # Firm name (right-aligned)
        firm = eng.get("firm_name", "")
        if firm:
            tk.Label(row1, text=firm,
                     bg=card_bg, fg=C["muted"],
                     font=("Segoe UI", 8, "italic")).pack(side="right")

        # ── Row 2: engagement label ──
        label_row = tk.Frame(body, bg=card_bg)
        label_row.pack(fill="x", pady=(8, 2))
        tk.Label(label_row, text=eng_label(eng),
                 bg=card_bg, fg=C["text"],
                 font=("Segoe UI", 11, "bold"),
                 anchor="w").pack(side="left")
        if is_active:
            tk.Label(label_row, text="  ◈ active",
                     bg=card_bg, fg=accent,
                     font=("Segoe UI", 8, "bold")).pack(side="left")

        # Engagement notes preview
        notes_preview = eng.get("engagement_notes", "").strip()
        if notes_preview:
            tk.Label(body,
                     text=notes_preview[:90] + ("…" if len(notes_preview) > 90 else ""),
                     bg=card_bg, fg=C["muted"],
                     font=("Segoe UI", 8), anchor="w").pack(fill="x", pady=(0, 4))

        # ── Progress bar (capsule) ──
        pct_clamp = max(0.0, min(1.0, overall_pct))
        if pct_clamp >= 1.0:
            bar_color = C["success"]
        elif pct_clamp >= 0.5:
            bar_color = C["accent"]
        else:
            bar_color = C["accent2"]

        pbar_cv = tk.Canvas(body, height=8, bg=card_bg, highlightthickness=0)
        pbar_cv.pack(fill="x", pady=(6, 2))

        def _draw_bar(ev, cv=pbar_cv, pct=pct_clamp, col=bar_color):
            cv.delete("all")
            w = ev.width
            if w < 2:
                return
            _draw_capsule(cv, 0, 0, w, 8, fill=C["border"])
            fw = int(w * pct)
            if fw >= 8:
                _draw_capsule(cv, 0, 0, fw, 8, fill=col)
            elif fw > 0:
                cv.create_oval(0, 0, 8, 8, fill=col, outline="")

        pbar_cv.bind("<Configure>", _draw_bar)

        pct_lbl = f"{int(overall_pct * 100)}% complete"
        tk.Label(body, text=pct_lbl,
                 bg=card_bg, fg=C["muted"],
                 font=("Segoe UI", 7, "bold")).pack(anchor="w", pady=(0, 6))

        # ── Tab status strip ──
        if is_tax:
            tab_defs = [
                ("preaudit",  "Pre-Audit"),
                ("financials","Financials"),
                ("notes",     "Form 3CD"),
                ("ifc",       "IFC"),
                ("variance",  "Variance"),
            ]
        else:
            tab_defs = [
                ("preaudit",  "Pre-Audit"),
                ("financials","Financials"),
                ("notes",     "Notes"),
                ("sch3",      "Sch III"),
                ("ifc",       "IFC"),
                ("caro",      "CARO"),
                ("legalsec",  "L&S"),
                ("variance",  "Variance"),
            ]

        strip = tk.Frame(body, bg=card_bg)
        strip.pack(fill="x", pady=(0, 4))

        for tab_key, tab_name in tab_defs:
            v = prog.get(tab_key)
            if v is None:
                continue
            if v >= 1.0:
                dot_col, txt_col = C["success"], C["success"]
            elif v > 0:
                dot_col, txt_col = C["accent2"], C["accent2"]
            else:
                dot_col, txt_col = C["border"], C["muted"]

            chip_border = dot_col if v > 0 else C["border"]
            chip = tk.Frame(strip, bg=C["chip_active"],
                            padx=8, pady=4,
                            highlightthickness=1,
                            highlightbackground=chip_border)
            chip.pack(side="left", padx=(0, 4), pady=1)
            tk.Label(chip, text="●", bg=C["chip_active"], fg=dot_col,
                     font=("Segoe UI", 6)).pack(side="left", padx=(0, 4))
            tk.Label(chip, text=tab_name,
                     bg=C["chip_active"], fg=txt_col,
                     font=("Segoe UI", 7, "bold")).pack(side="left")
            if v > 0:
                tk.Label(chip, text=f" {int(v*100)}%",
                         bg=C["chip_active"], fg=C["muted"],
                         font=("Segoe UI", 7)).pack(side="left")

        # ── Buttons column (right side of card) ──
        btn_col = tk.Frame(card, bg=card_bg, padx=14)
        btn_col.pack(side="right", fill="y")

        open_btn = tk.Button(btn_col, text="Open  →",
            bg=accent, fg=C["bg"],
            activebackground=C["btn_hover"], activeforeground=C["bg"],
            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
            bd=0, padx=16, pady=7,
            command=lambda e=eng: self._open_eng_window(e))
        open_btn.pack(pady=(16, 5))
        open_btn.bind("<Enter>", lambda e, b=open_btn: b.config(bg=C["btn_hover"]))
        open_btn.bind("<Leave>", lambda e, b=open_btn, a=accent: b.config(bg=a))

        lock_lbl = "🔓  Unlock" if is_locked else "🔒  Lock"
        lock_fg  = C["accent"] if is_locked else C["muted"]
        lock_btn = tk.Button(btn_col, text=lock_lbl,
            bg=C["btn_secondary"], fg=lock_fg,
            activebackground=C["border"], font=("Segoe UI", 8),
            relief="flat", cursor="hand2", bd=0, padx=10, pady=4,
            command=lambda eid2=eid: self._toggle_lock(eid2))
        lock_btn.pack(pady=(0, 4))

        edit_btn = tk.Button(btn_col, text="✎  Edit",
            bg=C["btn_secondary"], fg=C["text"] if not is_locked else C["border"],
            activebackground=C["border"], font=("Segoe UI", 8),
            relief="flat", cursor="hand2" if not is_locked else "arrow",
            bd=0, padx=10, pady=4,
            state="normal" if not is_locked else "disabled",
            command=lambda eid2=eid: self._edit_eng(eid2))
        edit_btn.pack(pady=(0, 4))

        del_btn = tk.Button(btn_col, text="🗑  Delete",
            bg=C["btn_secondary"],
            fg=C["danger"] if not is_locked else C["border"],
            activebackground=C["border"], font=("Segoe UI", 8),
            relief="flat", cursor="hand2" if not is_locked else "arrow",
            bd=0, padx=10, pady=4,
            state="normal" if not is_locked else "disabled",
            command=lambda eid2=eid: self._del_eng(eid2))
        del_btn.pack(pady=(0, 14))

        # Card click to select
        def _click(ev, target=eid):
            if target != self._active:
                self._active = target
                self._rebuild_all_cards()

        def _do_bind(c=card, bc=btn_col, clk=_click,
                     is_act=is_active, ac=accent, bd=bdr_col):
            bind_tree(c, "<Button-1>", clk, exclude=bc)
            if not is_act:
                bind_tree(c, "<Enter>",
                    lambda ev, w=c: w.config(highlightbackground=ac),
                    exclude=bc)
                bind_tree(c, "<Leave>",
                    lambda ev, w=c, b=bd: w.config(highlightbackground=b),
                    exclude=bc)

        card.after(0, _do_bind)

    # ══════════════════════════════════════════════════════════════════════
    # CRUD
    # ══════════════════════════════════════════════════════════════════════

    def _toggle_lock(self, eid):
        eng = next((e for e in self._data["engagements"] if e["id"] == eid), None)
        if not eng:
            return
        parent = self.winfo_toplevel()
        label = eng_label(eng)
        if eng.get("locked"):
            dlg = PasswordDialog(parent, mode="verify", eng_label_text=label)
            if dlg.result is None:
                return
            if not _verify_password(dlg.result, eng):
                messagebox.showerror("Incorrect Password",
                    "The password you entered is incorrect.", parent=parent)
                return
            eng["locked"] = False
            eng.pop("lock_password_hash", None)
        else:
            dlg = PasswordDialog(parent, mode="set", eng_label_text=label)
            if dlg.result is None:
                return
            eng["lock_password_hash"] = _hash_password(
                dlg.result, eng.get("id", ""))
            eng["locked"] = True
        self._invalidate_cache(eid)
        self._mark_dirty()
        self._save()
        self._rebuild_all_cards()

    def _add_eng(self):
        dlg = EngagementDialog(self.winfo_toplevel())
        if dlg.result:
            self._data["engagements"].append(dlg.result)
            self._active = dlg.result["id"]
            self._mark_dirty()
            self._invalidate_cache()
            self._rebuild_all_cards()
            self._build_left_panel()

    def _edit_eng(self, eid=None):
        eid = eid or self._active
        if not eid:
            return
        eng = next((e for e in self._data["engagements"] if e["id"] == eid), None)
        if not eng:
            return
        dlg = EngagementDialog(self.winfo_toplevel(), existing=eng)
        if dlg.result:
            idx = next(i for i, e in enumerate(self._data["engagements"])
                       if e["id"] == eid)
            self._data["engagements"][idx] = dlg.result
            self._invalidate_cache(eid)
            self._mark_dirty()
            self._rebuild_all_cards()

    def _del_eng(self, eid=None):
        eid = eid or self._active
        if not eid:
            return
        eng = next((e for e in self._data["engagements"] if e["id"] == eid), None)
        if not eng:
            return
        dlg = DeleteEngagementDialog(self.winfo_toplevel(), eng)
        if not dlg.confirmed:
            return
        self._data["engagements"] = [
            e for e in self._data["engagements"] if e["id"] != eid]
        if self._active == eid:
            self._active = (self._data["engagements"][0]["id"]
                           if self._data["engagements"] else None)
        self._invalidate_cache(eid)
        self._mark_dirty()
        self._rebuild_all_cards()
        self._build_left_panel()

    def _open_eng_window(self, eng):
        self._active = eng["id"]
        self._rebuild_all_cards()
        EngagementWindow(self, eng, self._data, self._filepath)

    def _on_name(self, *_):
        self._mark_dirty()
        n = self._name_var.get()
        self._title_lbl.config(text=n)

    # ══════════════════════════════════════════════════════════════════════
    # Dirty / Save
    # ══════════════════════════════════════════════════════════════════════

    def _mark_dirty(self, *_):
        if not self._dirty:
            self._dirty = True
            self._save_btn.config(text="💾  Save *")

    def _save(self):
        # _data is updated directly by _open_edit_dialog before calling _save
        self._data["modified_at"] = datetime.now().isoformat()

        if not self._filepath:
            self._filepath = filedialog.asksaveasfilename(
                defaultextension=FILE_EXT,
                filetypes=[(FILE_EXT_DESC, f"*{FILE_EXT}"), ("All", "*.*")],
                initialfile=f"{_safe_filename(self._data['company_name'].replace(' ', '_'))}{FILE_EXT}")
            if not self._filepath:
                return

        try:
            _cafe_save(self._filepath, self._data)
            self._dirty = False
            self._save_btn.config(text="💾  Save")
            self._file_lbl.config(text=os.path.basename(self._filepath))
            self._on_save(self._filepath, self._data)
            # Refresh left panel to show updated stats/name
            self._build_left_panel()
        except Exception as ex:
            messagebox.showerror("Save Error", str(ex))



# ══════════════════════════════════════════════════════════════════════════════
# Home Screen
# ══════════════════════════════════════════════════════════════════════════════

class HomeScreen(tk.Frame):
    def __init__(self, parent, on_new, on_open, recent):
        super().__init__(parent, bg=C["bg"])
        self._on_new  = on_new
        self._on_open = on_open
        self._recent  = recent
        self._build()

    def _build(self):
        left = tk.Frame(self, bg=C["sidebar"], width=320)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        logo = tk.Frame(left, bg=C["sidebar"], pady=28)
        logo.pack(fill="x", padx=20)
        try:
            self._logo_img = _load_firm_logo(width=280, height=50)
            tk.Label(logo, image=self._logo_img,
                     bg=C["sidebar"]).pack(pady=(0, 4))
        except Exception:
            tk.Label(logo, text="Pai Nayak & Associates",
                     bg=C["sidebar"], fg=C["text"],
                     font=("Segoe UI", 13, "bold")).pack()
        tk.Frame(logo, height=1, bg=C["border"]).pack(fill="x", pady=12)

        btns = tk.Frame(left, bg=C["sidebar"], padx=36)
        btns.pack(fill="x")
        tk.Frame(btns, bg=C["border"], height=1).pack(fill="x", pady=(0, 12))
        styled_button(btns, "✦   New File", self._on_new,
                      kind="primary", width=22).pack(fill="x", pady=4)
        styled_button(btns, "📂   Open File", self._on_open,
                      kind="secondary", width=22).pack(fill="x", pady=4)

        tk.Label(left, text=f"v{APP_VERSION}", bg=C["sidebar"],
                 fg=C["border"], font=FONT_MONO).pack(side="bottom", pady=14)

        right = tk.Frame(self, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True, padx=44, pady=36)
        tk.Label(right, text="Recent Files", bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(right, text=f"Your recently opened {FILE_EXT_DESC}s",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w", pady=(2, 14))
        tk.Frame(right, height=1, bg=C["border"]).pack(fill="x")

        # Scrollable recent cards
        r_outer = tk.Frame(right, bg=C["bg"])
        r_outer.pack(fill="both", expand=True, pady=(10, 0))
        r_cv = tk.Canvas(r_outer, bg=C["bg"], highlightthickness=0)
        r_sb = ttk.Scrollbar(r_outer, orient="vertical", style="Thin.Vertical.TScrollbar", command=r_cv.yview)
        r_cv.configure(yscrollcommand=r_sb.set)
        r_sb.pack(side="right", fill="y")
        r_cv.pack(side="left", fill="both", expand=True)
        r_inner = tk.Frame(r_cv, bg=C["bg"])
        r_cwin = r_cv.create_window((0, 0), window=r_inner, anchor="nw")
        r_cv.bind("<Configure>",
            lambda e, c=r_cv, w=r_cwin: c.itemconfig(w, width=e.width))
        r_inner.bind("<Configure>",
            lambda e, c=r_cv: c.configure(scrollregion=(0, 0, e.width, e.widget.winfo_reqheight())))
        def _mw_rec(ev, c=r_cv):
            c.yview_scroll(int(-1*(ev.delta/120)), "units")
        r_outer.bind("<Enter>", lambda e: r_cv.bind_all("<MouseWheel>", _mw_rec))
        r_cv.bind("<Enter>", lambda e: r_cv.bind_all("<MouseWheel>", _mw_rec))
        r_outer.bind("<Leave>", lambda e: r_cv.unbind_all("<MouseWheel>"))
        r_outer.bind("<Button-4>", lambda e: r_cv.yview_scroll(-1, "units"))
        r_outer.bind("<Button-5>", lambda e: r_cv.yview_scroll(+1, "units"))

        if not self._recent:
            ph = tk.Frame(r_inner, bg=C["panel"], pady=32)
            ph.pack(fill="x", pady=14)
            tk.Label(ph, text="⭡", bg=C["panel"], fg=C["border"],
                     font=("Segoe UI", 28)).pack()
            tk.Label(ph, text="No recent files", bg=C["panel"],
                     fg=C["muted"], font=FONT_BODY).pack(pady=(4, 2))
        else:
            for fp, data in self._recent:
                self._recent_card(r_inner, fp, data)

    def _recent_card(self, parent, fp, data):
        engs = data.get("engagements", [])
        if not engs and data.get("audit_type"):
            engs = [{"audit_type": data["audit_type"]}]
        ac = C["accent2"] if engs and engs[0].get("audit_type") == "Tax Audit" else C["accent"]

        card = tk.Frame(parent, bg=C["panel"], cursor="hand2", pady=12, padx=16)
        card.pack(fill="x", pady=4)
        tk.Frame(card, bg=ac, width=4).pack(side="left", fill="y")

        info = tk.Frame(card, bg=C["panel"], padx=12)
        info.pack(side="left", fill="both", expand=True)
        tk.Label(info, text=data.get("company_name", "Unknown"),
                 bg=C["panel"], fg=C["text"],
                 font=FONT_HEADING, anchor="w").pack(anchor="w")
        n = len(engs)
        tk.Label(info, text=f"{n} engagement{'s' if n!=1 else ''}",
                 bg=C["panel"], fg=C["muted"], font=FONT_SMALL).pack(anchor="w")

        tk.Label(card, text=os.path.basename(fp), bg=C["panel"],
                 fg=C["border"], font=FONT_MONO).pack(side="right")

        _open_cmd = lambda e, f=fp: self._on_open(f)
        _enter_cmd = lambda e, c=card: c.config(bg=C["highlight"])
        _leave_cmd = lambda e, c=card: c.config(bg=C["panel"])

        def _bind_recursive(widget, fn_click, fn_enter, fn_leave):
            widget.bind("<Button-1>", fn_click)
            widget.bind("<Enter>", fn_enter)
            widget.bind("<Leave>", fn_leave)
            for child in widget.winfo_children():
                _bind_recursive(child, fn_click, fn_enter, fn_leave)

        _bind_recursive(card, _open_cmd, _enter_cmd, _leave_cmd)


# ══════════════════════════════════════════════════════════════════════════════
# Application
# ══════════════════════════════════════════════════════════════════════════════

class App:
    RECENT = os.path.join(os.path.expanduser("~"), ".pna_recent.json")

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("1080x680")
        self.root.minsize(860, 540)
        self.root.configure(bg=C["bg"])
        _setup_ttk_styles(self.root)
        self._recent = self._load_recent()
        self._panel  = None
        self._setup_menu()
        self._show_home()

    def _setup_menu(self):
        mb = tk.Menu(self.root, bg=C["sidebar"], fg=C["text"],
                     activebackground=C["highlight"], activeforeground=C["text"],
                     relief="flat")
        fm = tk.Menu(mb, tearoff=0, bg=C["sidebar"], fg=C["text"],
                     activebackground=C["highlight"], activeforeground=C["text"])
        fm.add_command(label="New File      Ctrl+N", command=self._new)
        fm.add_command(label="Open File...  Ctrl+O", command=self._open)
        fm.add_separator()
        fm.add_command(label="Home", command=self._show_home)
        fm.add_separator()
        fm.add_command(label="Exit", command=self._on_exit)
        mb.add_cascade(label="File", menu=fm)
        hm = tk.Menu(mb, tearoff=0, bg=C["sidebar"], fg=C["text"],
                     activebackground=C["highlight"], activeforeground=C["text"])
        hm.add_command(label="About", command=self._about)
        mb.add_cascade(label="Help", menu=hm)
        self.root.config(menu=mb)
        self.root.bind("<Control-n>", lambda e: self._new())
        self.root.bind("<Control-o>", lambda e: self._open())

    def _clear(self):
        if self._panel:
            self._panel.destroy()
            self._panel = None

    def _show_home(self):
        self._clear()
        h = HomeScreen(self.root, on_new=self._new,
                       on_open=self._open, recent=self._recent)
        h.pack(fill="both", expand=True)
        self._panel = h
        self.root.title(APP_NAME)

    def _show_detail(self, data, fp):
        self._clear()
        d = DetailPanel(self.root, data, fp,
                        on_save=self._on_save,
                        on_close=self._show_home)
        d.pack(fill="both", expand=True)
        self._panel = d
        self.root.title(f"{data.get('company_name','Untitled')} — {APP_NAME}")

    def _new(self, *_):
        dlg = NewFileDialog(self.root)
        if not dlg.result:
            return
        data = dlg.result
        fp = filedialog.asksaveasfilename(
            defaultextension=FILE_EXT,
            filetypes=[(FILE_EXT_DESC, f"*{FILE_EXT}"), ("All", "*.*")],
            initialfile=f"{_safe_filename(data['company_name'].replace(' ', '_'))}{FILE_EXT}",
            title="Save New Company File")
        if not fp:
            return
        try:
            _cafe_save(fp, data)
        except Exception as ex:
            messagebox.showerror("Error", str(ex)); return
        self._push_recent(fp, data)
        self._show_detail(data, fp)

    def _open(self, filepath=None, *_):
        if filepath is None:
            filepath = filedialog.askopenfilename(
                filetypes=[(FILE_EXT_DESC, f"*{FILE_EXT}"), ("All", "*.*")],
                title=f"Open {FILE_EXT_DESC}")
        if not filepath:
            return
        if not os.path.exists(filepath):
            messagebox.showerror("Not Found", f"File not found:\n{filepath}"); return
        is_legacy = not _cafe_is_encrypted(filepath)
        if is_legacy:
            choice = messagebox.askyesnocancel(
                "Unencrypted File",
                "This file is in the legacy plain-text format and is not "
                "encrypted. Its contents can be read by anyone with file "
                "access.\n\n"
                "Do you want to upgrade it to the encrypted format?\n\n"
                "• Yes — open and re-save as encrypted\n"
                "• No — open as-is (stays unencrypted)\n"
                "• Cancel — don't open",
                parent=self.root, icon="warning")
            if choice is None:
                return
        try:
            data = _cafe_load(filepath)
        except Exception as ex:
            messagebox.showerror("Error", str(ex)); return
        data = migrate(data)
        if is_legacy and choice:
            try:
                _cafe_save(filepath, data)
            except Exception as ex:
                messagebox.showerror("Upgrade Failed",
                    f"Could not re-save the file as encrypted:\n{ex}",
                    parent=self.root)
        self._push_recent(filepath, data)
        self._show_detail(data, filepath)

    def _on_save(self, fp, data):
        self._push_recent(fp, data)
        self.root.title(f"{data.get('company_name','Untitled')} — {APP_NAME}")

    def _load_recent(self):
        try:
            if os.path.exists(self.RECENT):
                with open(self.RECENT, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                return [(p, d) for p, d in raw if os.path.exists(p)]
        except Exception:
            pass
        return []

    def _push_recent(self, fp, data):
        self._recent = [(p, d) for p, d in self._recent if p != fp]
        self._recent.insert(0, (fp, copy.deepcopy(data)))
        self._recent = self._recent[:10]
        try:
            with open(self.RECENT, "w", encoding="utf-8") as f:
                json.dump(self._recent, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _about(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("About")
        dlg.geometry("380x260")
        dlg.configure(bg=C["bg"])
        dlg.resizable(False, False)
        dlg.grab_set()
        try:
            self._about_logo = _load_firm_logo(width=320, height=57)
            tk.Label(dlg, image=self._about_logo,
                     bg=C["bg"]).pack(pady=(28, 8))
        except Exception:
            tk.Label(dlg, text="Pai Nayak & Associates", bg=C["bg"],
                     fg=C["text"], font=("Segoe UI", 15, "bold")).pack(pady=(28, 4))
        tk.Label(dlg, text=f"Version {APP_VERSION}", bg=C["bg"],
                 fg=C["muted"], font=FONT_SMALL).pack()
        tk.Frame(dlg, height=1, bg=C["border"]).pack(fill="x", pady=10)
        tk.Label(dlg, text="Audit Management Software\nOffline · Portable · Secure",
                 bg=C["bg"], fg=C["muted"], font=FONT_SMALL,
                 justify="center").pack(pady=8)
        styled_button(dlg, "Close", dlg.destroy,
                      kind="primary", width=12).pack(pady=12)

    @staticmethod
    def _cleanup_print_files():
        """Delete all temporary HTML print files generated during the session."""
        for path in EngagementWindow._temp_print_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass
        EngagementWindow._temp_print_files.clear()

    def _on_exit(self):
        if hasattr(self._panel, "_dirty") and self._panel._dirty:
            ans = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes.\n\nSave before closing?",
                parent=self.root)
            if ans is None:
                return
            if ans:
                self._panel._save()
        self._cleanup_print_files()
        self.root.quit()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
