#!/usr/bin/env python
from fusil.application import Application
from fusil.process.create import ProjectProcess
from fusil.process.watch import WatchProcess
from fusil.process.stdout import WatchStdout
from fusil.process.create import CreateProcess
from fusil.bytes_generator import BytesGenerator, ASCII0
from random import randint, choice

class Fuzzer(Application):
    def setupProject(self):
        process = ProjectProcess(self.project, ['echo', '"Hello World!"'])
        WatchProcess(process)
        WatchStdout(process)

class EchoProcess(CreateProcess):
    OPTIONS = ("-e", "-E", "-n")

    def __init__(self, project):
        CreateProcess.__init__(self, project, ["echo"])
        self.datagen = BytesGenerator(1, 10, ASCII0)

    def createCmdline(self):
        arguments = ['echo']
        for index in xrange(randint(3, 6)):
            if randint(1, 5) == 1:
                option = choice(self.OPTIONS)
                arguments.append(option)
            else:
                data = self.datagen.createValue()
                arguments.append(data)
        return arguments

    def on_session_start(self):
        self.cmdline.arguments = self.createCmdline()
        self.createProcess()

if __name__ == "__main__":
    Fuzzer().main()
