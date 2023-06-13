"""
Message und Condition zur standardisierten Definition des Prozesses
"""

DEFAULT_MESSAGE = {
    "success": "OK",
    "error": "FEHLER",
    "info": "INFO"
}


class Message:
    def __init__(self, msg_type, text="DEFAULT_MESSAGE"):
        self.type = msg_type
        self.boolean = False if msg_type == "error" else True
        if text == "DEFAULT_MESSAGE":
            self.text = DEFAULT_MESSAGE[msg_type]
        else:
            self.text = text

    def __str__(self):
        return self.text

    def __bool__(self):
        return self.boolean


class SuccessMsg(Message):
    def __init__(self, text="DEFAULT_MESSAGE"):
        super().__init__("success", text=text)


class ErrorMsg(Message):
    def __init__(self, text="DEFAULT_MESSAGE"):
        super().__init__("error", text=text)


class InfoMsg(Message):
    def __init__(self, text="DEFAULT_MESSAGE"):
        super().__init__("info", text=text)


class ControlMsg(Message):
    def __init__(self, subtype, text=""):
        super().__init__(subtype, text=text)


class EndOfRowMsg(ControlMsg):
    def __init__(self):
        super().__init__("end_of_row", text="row finished")


class Condition:
    def __init__(self, step_num, msg, input_row, request, log_row):
        self.step_num = step_num
        self.msg = msg
        self.input_row = input_row
        self.request = request
        self.log_row = log_row
        self.data = dict()
