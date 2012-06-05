from peak.api import *
from interfaces import *
import os
from cStringIO import StringIO
from runners import HTMLRunner, FileURL


class TestDocument(web.FileResource):

    def getStreamAndSize(self):

        output = StringIO()

        HTMLRunner(
            config.ServiceArea(self),
            argv = ['HTMLRunner', FileURL.fromFilename(self.filename)],
            stdout = output,
            stderr = StringIO(),
        ).run()

        size = output.tell()
        output.seek(0)
       
        return output,size

















class IndexedDirectory(web.ResourceDirectory):

    index_html = web.bindResource(
        'directoryIndex', permissionNeeded=security.Anybody
    )

    def contents(self):
        contents = []
        names = os.listdir(self.filename); names.sort()
        for name in names:
            if name not in ['.','..']:
                try:
                    ob = self[name]
                except KeyError:
                    pass    # print name
                else:
                    contents.append(ob)

        return contents

    contents = binding.Make(contents, permissionNeeded=security.Anybody)


class PublishedDirectory(IndexedDirectory):

    isRoot = True

    resourceDefaultsIni = binding.Make(
        lambda: config.fileNearModule('peak.ddt','resource_defaults.ini'),
        offerAs = ['peak.web.resourceDefaultsIni']
    )

    filename = binding.Make(
        lambda self: self.lookupComponent(commands.ARGV)[1]
    )

    resourcePath = ''




