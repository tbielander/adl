"""
apirequests.py bietet Wrapper-Klassen für die HTTP-Requests der Alma REST API
"""

import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib import parse
import requests
from requests.exceptions import Timeout
from adl.api import BASE_URL, API
from adl.message import SuccessMsg, ErrorMsg, InfoMsg


class Request:
    """
    Klasse zur vereinfachten Formulierung von API-Requests
    """
    def __init__(self, api_template, apikey="", content_type="application/xml", accept="application/xml", timeout=300):
        self.url_template = BASE_URL + API[api_template]
        self.url = ""
        self.params = {"apikey":apikey}
        self.headers = {"Content-Type":content_type, "Accept":accept}
        self.timeout = timeout
        self.data_dict = dict()
        self.data_root = ET.Element("root")
        self.response_dict = dict()
        self.response_root = ET.Element("root")
        self.error_dict = dict()
        self.error_root = ET.Element("root")
        self.msg = InfoMsg()

    def keep_response(self, response):
        if "application/json" in response.headers["Content-Type"]:
            self.response_dict = json.loads(response.text)
            msg = SuccessMsg(text="JSON --> response_dict")
        elif "application/xml" in response.headers["Content-Type"]:
            self.response_root = ET.fromstring(response.text)
            msg = SuccessMsg(text="XML --> response_root")
        else:
            msg = ErrorMsg(text="ungültiges Format")
        return msg

    def error_log(self, xmlns=None):
        if not xmlns:
            xmlns = {"xmlbeans": "http://com/exlibris/urm/general/xmlbeans"}
        if self.response_dict:
            error_list = self.response_dict.get("errorList", {})
            err_msg = str(error_list) if error_list else str(self.response_dict)
        elif self.response_root.tag:
            error_list = self.response_root.find("xmlbeans:errorList", namespaces=xmlns)
            if error_list:
                err_msg = "; ".join([e[0].text + " - " + e[1].text.rstrip("; ") for e in error_list])
            else:
                err_msg = ET.tostring(self.response_root)
        else:
            err_msg = "Keine Fehler-Details verfügbar"
        return err_msg

    def get(self, backup=True, backup_dir=os.getcwd(), backup_name="backup", details=False, dry_run=False, special_params=None):
        if dry_run:
            self.msg = InfoMsg(text="TESTLAUF")
            return self.msg
        get_params = {**self.params, **special_params} if special_params else self.params
        try:
            rget = requests.get(self.url, params=get_params, headers=self.headers, timeout=self.timeout)
        except Timeout:
            self.msg = ErrorMsg(text="TIMEOUT_ERROR")
            return self.msg
        self.msg = self.keep_response(rget)
        if rget.ok:
            self.data_root = self.response_root
            self.data_dict = self.response_dict
        else:
            self.msg = ErrorMsg(text=self.error_log()) if details else ErrorMsg()
        if backup:
            backup_file = os.path.join(backup_dir, backup_name + "_" + datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f"))
            with open(backup_file + "." + self.headers["Accept"].split("/")[1], "w", encoding="utf-8") as b:
                b.write(rget.text)
        return self.msg

    def put(self, dry_run=True, details=False, special_params=None):
        if dry_run:
            self.msg = InfoMsg(text="TESTLAUF")
            return self.msg
        if self.headers["Content-Type"] == "application/json":
            if not self.data_dict:
                self.msg = ErrorMsg(text="data_dict leer")
                return self.msg
            put_data = json.dumps(self.data_dict, indent=4)
        elif self.headers["Content-Type"] == "application/xml":
            if not self.data_root.tag:
                self.msg = ErrorMsg(text="data_root fehlt")
                return self.msg
            put_data = ET.tostring(self.data_root)
        else:
            self.msg = ErrorMsg(text="ungültiges Format")
            return self.msg
        put_params = {**self.params, **special_params} if special_params else self.params
        try:
            rput = requests.put(self.url, data=put_data, headers=self.headers, params=put_params, timeout=self.timeout)
        except Timeout:
            self.msg = ErrorMsg(text="TIMEOUT_ERROR")
            return self.msg
        self.msg = self.keep_response(rput)
        if not rput.ok:
            self.msg = ErrorMsg(text=self.error_log()) if details else ErrorMsg()
        return self.msg

    def post(self, dry_run=True, details=False, special_params=None):
        if dry_run:
            self.msg = InfoMsg(text="TESTLAUF")
            return self.msg
        if self.headers["Content-Type"] == "application/json":
            if not self.data_dict:
                self.msg = ErrorMsg(text="data_dict leer")
                return self.msg
            post_data = json.dumps(self.data_dict, indent=4)
        elif self.headers["Content-Type"] == "application/xml":
            if not self.data_root.tag:
                self.msg = ErrorMsg(text="data_root fehlt")
                return self.msg
            post_data = ET.tostring(self.data_root)
        else:
            self.msg = ErrorMsg(text="ungültiges Format")
            return self.msg
        post_params = {**self.params, **special_params} if special_params else self.params
        try:
            rpost = requests.post(self.url, data=post_data, headers=self.headers, params=post_params, timeout=self.timeout)
        except Timeout:
            self.msg = ErrorMsg(text="TIMEOUT_ERROR")
            return self.msg
        self.msg = self.keep_response(rpost)
        if not rpost.ok:
            self.msg = ErrorMsg(text=self.error_log()) if details else ErrorMsg()
        return self.msg

class EmptyRequest(Request):
    def __init__(self):
        super().__init__("empty")

# BIB

class BibRequest(Request):
    def __init__(self, mms_id, apikey=""):
        super().__init__("bib", apikey=apikey)
        self.url = self.url_template.format(
            mms_id = parse.quote(mms_id))

class HoldingsRequest(Request):
    def __init__(self, mms_id, apikey=""):
        super().__init__("holdings", apikey=apikey)
        self.url = self.url_template.format(
            mms_id = parse.quote(mms_id))

class HoldingRequest(Request):
    def __init__(self, mms_id, holding_id, apikey=""):
        super().__init__("holding", apikey=apikey)
        self.url = self.url_template.format(
            mms_id = parse.quote(mms_id),
            holding_id = parse.quote(holding_id))

class ItemsRequest(Request):
    def __init__(self, mms_id, holding_id, apikey=""):
        super().__init__("items", apikey=apikey)
        self.url = self.url_template.format(
            mms_id = parse.quote(mms_id),
            holding_id = parse.quote(holding_id))

class ItemRequest(Request):
    def __init__(self, mms_id, holding_id, item_pid, apikey=""):
        super().__init__("item", apikey=apikey)
        self.url = self.url_template.format(
            mms_id = parse.quote(mms_id),
            holding_id = parse.quote(holding_id),
            item_pid = parse.quote(item_pid))

# Item Loans and Requests

class LoansByItemRequest(Request):
    def __init__(self, mms_id, holding_id, item_pid, apikey=""):
        super().__init__("item_loans", apikey=apikey)
        self.url = self.url_template.format(
            mms_id = parse.quote(mms_id),
            holding_id = parse.quote(holding_id),
            item_pid = parse.quote(item_pid))

class RequestsByItemRequest(Request):
    def __init__(self, mms_id, holding_id, item_pid, apikey=""):
        super().__init__("item_requests", apikey=apikey)
        self.url = self.url_template.format(
            mms_id = parse.quote(mms_id),
            holding_id = parse.quote(holding_id),
            item_pid = parse.quote(item_pid))

# Acquisitions

class LicenseRequest(Request):
    def __init__(self, license_code, apikey=""):
        super().__init__("license", apikey=apikey)
        self.url = self.url_template.format(
            license_code = parse.quote(license_code))

class POLsRequest(Request):
    def __init__(self, apikey=""):
        super().__init__("pols", apikey=apikey)
        self.url = self.url_template

class POLRequest(Request):
    def __init__(self, po_line_id, apikey=""):
        super().__init__("pol", apikey=apikey)
        self.url = self.url_template.format(
            po_line_id = parse.quote(po_line_id))

class VendorsRequest(Request):
    def __init__(self, apikey=""):
        super().__init__("vendors", apikey=apikey)
        self.url = self.url_template

class VendorRequest(Request):
    def __init__(self, vendor_code, apikey=""):
        super().__init__("vendor", apikey=apikey)
        self.url = self.url_template.format(
            vendor_code = parse.quote(vendor_code))

class VendorPOLsRequest(Request):
    def __init__(self, vendor_code, apikey=""):
        super().__init__("vendor_pols", apikey=apikey)
        self.url = self.url_template.format(
            vendor_code = parse.quote(vendor_code))

class VendorInvoicesRequest(Request):
    def __init__(self, vendor_code, apikey=""):
        super().__init__("vendor_invoices", apikey=apikey)
        self.url = self.url_template.format(
            vendor_code = parse.quote(vendor_code))

# Electronic

class PortfolioRequest(Request):
    def __init__(self, collection_id, service_id, portfolio_id, apikey=""):
        super().__init__("portfolio", apikey=apikey)
        self.url = self.url_template.format(
            collection_id = collection_id,
            service_id = service_id,
            portfolio_id = portfolio_id)
