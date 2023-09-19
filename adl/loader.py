"""
adl (kurz für 'Alma Data Loader') ist eine Sammlung von Klassen,
die die Einspielung von Daten über die Alma REST API vereinfachen soll
"""

import os
import csv
from datetime import datetime, timedelta
from adl.message import InfoMsg, Condition
from adl.apirequest import EmptyRequest


class Input:
    def __init__(self, file):
        self.file = file
        self.filename = os.path.basename(file)
        self.reader = self.read()
        self.headers = None

    def read(self):
        open_file = open(self.file,"r", encoding="utf-8")
        reader = csv.reader(open_file, delimiter="\t")
        return reader


class Log:
    def __init__(self, filepath):
        self.file = open(filepath, "w", encoding="utf-8")
        self.writer = csv.writer(self.file, delimiter="\t")
        self.heading = []

    def begin(self):
        if self.heading:
            for row in self.heading:
                self.write(row, blank_line_after=(self.heading.index(row)!=len(self.heading)-1))
        return self.heading

    def write(self, row, blank_line_before=False, blank_line_after=False):
        if blank_line_before:
            self.writer.writerow([])
        self.writer.writerow(row)
        if blank_line_after:
            self.writer.writerow([])

    def complete(self, closing, end_time):
        for row in closing:
            self.write(row, blank_line_before=True)
        self.file.close()
        completed_log = self.file.name.split(".")[0] + "_" + end_time + ".csv"
        os.rename(self.file.name, completed_log)


class ADL:
    """
    Alma Data Loader
    """
    def __init__(self, project, input_file, logtitle, logfields, dry_run, backup=True):

        workdir = os.getcwd()
        todo = "todo"
        input_path = os.path.join(workdir, todo, project)
        csv_input = os.path.join(input_path, input_file)
        backup_dir = os.path.join(input_path, "backup")
        log_dir = os.path.join(input_path, "log")
        logfile = input_file.split(".")[0] + ".csv"
        if dry_run:
            logfile = "TEST_" + logfile
        log = os.path.join(log_dir, logfile)

        self.input = Input(csv_input)
        self.input_reader = self.input.read()
        self.backup_dir = backup_dir
        self.log_dir = log_dir
        self.subdirs = [self.backup_dir, self.log_dir] if backup else [self.log_dir]
        self.make_dirs(self.subdirs)
        self.log = Log(log)
        self.log.heading = [[logtitle], [self.input.filename], logfields]
        self.start = self.end = self.duration = self.entries_processed = None

    def make_dirs(self, listing):
        for subdir in listing:
            if not os.path.exists(subdir):
                os.mkdir(subdir)
            else:
                continue

    def take_step(self, step_function, condition):
        result = step_function(condition)
        if result.msg.type == "end_of_row":
            self.log.write(result.log_row)
        else:
            result.step_num += 1
            result = self.take_step(step_function, result)
        return result

    def process(self, input_reader, step_function):
        start_msg = InfoMsg(text="start")
        start_request = EmptyRequest()
        condition = Condition(1, start_msg, [], start_request, [])
        entries_processed = 0
        for row in input_reader:
            condition.input_row = row
            # row_start = Condition(1, start_msg, row, EmptyRequest, [])
            condition = self.take_step(step_function, condition)
            entries_processed += 1
            print(str(entries_processed) + ":", condition.log_row)
            condition.step_num = 1
            condition.msg = start_msg
            condition.request = start_request
            condition.log_row = []
        return entries_processed

    def run(self, step_function):
        self.start = datetime.now()
        self.log.begin()
        self.input.headers = next(self.input.reader)
        self.entries_processed = self.process(self.input.reader, step_function)
        self.end = datetime.now()
        self.duration = self.end - self.start
        self.duration = self.duration - timedelta(microseconds=self.duration.microseconds)
        self.log.complete([
                ["Dauer: " + str(self.duration)],
                ["Anzahl Ersetzungen: " + str(self.entries_processed)]
            ],
            self.end.strftime("%Y-%m-%dT%H-%M-%S")
        )
        print("Die Einspielung der Daten ist beendet.")
