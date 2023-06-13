"""
Unter Verwendung des adl-Moduls (Alma Data Loader) definiert die Datei dataloader.py
den spezifischen Prozess der Einspielung und den Aufbau der entsprechenden Logdatei
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from adl.loader import ADL
from adl.message import EndOfRowMsg
from adl.apirequest import ItemsRequest

# Vor jeder Ausführung den DRY_RUN-Wert überprüfen!!!

DRY_RUN = True

PROJECT = "VERZ_Exemplare-API"
INPUT_FILE = "VERZ_Exemplare-API_20220511.csv"
LOG_TITLE = "Exemplare erstellen"
LOG_FIELDS = [
    "MMS-ID",
    "Holding-ID",
    "POST Exemplar",
    "Exemplar-PID",
    "Barcode"
]

BIBS_PROD_RW = ""

dl = ADL(PROJECT, INPUT_FILE, LOG_TITLE, LOG_FIELDS, DRY_RUN, logfields_only=True)

def step(c):

    """
    Die step-Funktion definiert die einzelnen Schritte der Dateneinspielung
    """
    
    # Projekt-spezifisches Skript beginnt hier...
    
    c.request = ItemsRequest(c.input_row[0], c.input_row[1], apikey=BIBS_PROD_RW)
    c.log_row += [c.input_row[0], c.input_row[1]]
    item_tree = ET.parse("/home/adl/create-items/todo/" + PROJECT + "/item_object.xml")
    root = item_tree.getroot()
    root.find("holding_data/holding_id").text = c.input_row[1]
    root.find("item_data/physical_material_type/xml_value").text = c.input_row[2]
    root.find("item_data/policy/xml_value").text = c.input_row[3]
    root.find("item_data/year_of_issue").text = c.input_row[5]
    root.find("item_data/enumeration_a").text = c.input_row[4]
    root.find("item_data/chronology_i").text = c.input_row[5]
    root.find("item_data/description").text = c.input_row[6]
    root.find("item_data/internal_note_1").text = c.input_row[7] + ", " + datetime.now().strftime("%d.%m.%Y")
    root.find("item_data/statistics_note_2").text = c.input_row[8]
    c.request.data_root = root
    c.msg = c.request.post(dry_run=DRY_RUN, details=True)
    c.log_row += [c.msg.text]
    if c.msg.type == "success":
        pid = c.request.response_root.find("item_data/pid").text
        barcode = c.request.response_root.find("item_data/barcode").text
        c.log_row += [pid, barcode]
    
    # ...und endet hier

    c.msg = EndOfRowMsg()
    return c

dl.run(step)
