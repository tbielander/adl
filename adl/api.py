"""
Liste der APIs mit Platzhaltern
"""

BASE_URL = "https://api-eu.hosted.exlibrisgroup.com/almaws/v1/"

API = {
    "empty": "",
    # BIBs
    "bibs": "bibs",
    "bib": "bibs/{mms_id}",
    "holdings": "bibs/{mms_id}/holdings",
    "holding": "bibs/{mms_id}/holdings/{holding_id}",
    "items": "bibs/{mms_id}/holdings/{holding_id}/items",
    "item": "bibs/{mms_id}/holdings/{holding_id}/items/{item_pid}",
    "barcode": "items",
    # Item Loans and Requests
    "item_loans": "bibs/{mms_id}/holdings/{holding_id}/items/{item_pid}/loans",
    "item_requests": "bibs/{mms_id}/holdings/{holding_id}/items/{item_pid}/requests",
    # Acquisitions
    "licenses": "acq/licenses",
    "license": "acq/licenses/{license_code}",
    "pols": "acq/po-lines",
    "pol": "acq/po-lines/{po_line_id}",
    "vendors": "acq/vendors",
    "vendor": "acq/vendors/{vendor_code}",
    "vendor_pols": "acq/vendors/{vendor_code}/po-lines",
    "vendor_invoices": "acq/vendors/{vendor_code}/invoices"
    # Electronic
    "portfolio": "electronic/e-collections/{collection_id}/e-services/{service_id}/portfolios/{portfolio_id}"
}
