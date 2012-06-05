from peak.api import *
from interfaces import *
from peak.naming.factories.openable import FileURL
from html_doc import HTMLDocument
from urllib import basejoin




































class ViewRunner(binding.Component):
    """Run tests in a web browser, by proxying documents"""

    usage="""Usage: peak ddt.web baseURL

Launch a DDT viewer in a web browser, initially retrieving and displaying
the specified base URL.
"""
    protocols.advise(
        instancesProvide=[running.IRerunnableCGI]
    )

    argv    = binding.Obtain(commands.ARGV)
    baseURL = binding.Make(lambda self: self.argv[1])

    def runCGI(self,stdin,stdout,stderr,environ):
        path = environ.get('PATH_INFO','/')
        for suffix in ('/','.htm','.html','.HTM','.HTML'):
            if path.endswith(suffix):
                break
        else:
            print >>stdout,"Location:", basejoin(self.baseURL,path)
            print >>stdout
            return

        sane_path = '/'.join([p for p in path.split('/') if p and p<>'..'])
        sane_path = sane_path and '/'+sane_path or ''

        print >>stdout, "Content-type: text/html"
        print >>stdout
        HTMLRunner(
            self,
            argv = ['HTMLRunner', self.baseURL+sane_path],
            stdin = stdin,
            stdout = stdout,
            stderr = stderr,
            environ = environ
        ).run()

        # XXX error trapping

class HTMLRunner(commands.AbstractCommand):

    usage="""Usage: peak ddt inputfile.html [outputfile.html]

Process the tests specified by the input file, sending an annotated version
to the output file, if specified, or to standard output if not specified.
Both the input and output files may be filenames or URLs.

A summary of the tests' pass/fail scores is output to stderr, and the command's
exitlevel is nonzero if there were any problems.
"""

    def DM(self):
        stream = self.inputFactory.open('b')
        dm = HTMLDocument(self,text = stream.read(), useAC = True)
        stream.close()
        if self.outputURL:
            dm.output = self.lookupComponent(
                self.outputURL,adaptTo=naming.IStreamFactory
            )
        else:
            dm.stream = self.stdout
        return dm

    DM = binding.Make(DM)

    inputFactory = binding.Obtain(
        naming.Indirect('inputURL'),adaptTo=naming.IStreamFactory
    )
    
    def inputURL(self):
        if len(self.argv)<2:
            raise commands.InvocationError("Input filename required")
        return naming.toName(self.argv[1], FileURL.fromFilename)
    inputURL = binding.Make(inputURL)

    def outputURL(self):
        if len(self.argv)>2:
            return naming.toName(self.argv[2], FileURL.fromFilename)
    outputURL = binding.Make(outputURL)

    def _run(self):

        dm = self.DM

        storage.beginTransaction(dm)

        summary = dm.document.summary
        summary['Input file'] = self.argv[1]
        if self.outputURL:
            summary['Output file'] = self.outputURL

        testZone = config.ServiceArea(self)     # tests happen in here
        processor = testZone.lookupComponent(IDocumentProcessor)
        processor.processDocument(dm.document)

        score = dm.document.score   # capture the final score
        dm.flush()                  # force DM to flush even if no changes made

        storage.commitTransaction(dm)

        print >>self.stderr,score   # Output scores to stderr
        return (score.wrong or score.exceptions) and 1 or 0



















