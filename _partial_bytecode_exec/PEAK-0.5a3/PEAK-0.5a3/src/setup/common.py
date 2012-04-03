"""This is a set of commonly useful distutils enhancements,
designed to be 'execfile()'d in a 'setup.py' file.  Don't import it,
it's not a package!  It also doesn't get installed with the rest of
the package; it's only actually used while 'setup.py' is running."""

# Set up default parameters

if 'TEST_MODULE' not in globals():
    TEST_MODULE = packages[0]+'.tests'

if 'HAPPYDOC_OUTPUT_PATH' not in globals():
    HAPPYDOC_OUTPUT_PATH = 'docs/html/reference'

if 'HAPPYDOC_IGNORE' not in globals():
    HAPPYDOC_IGNORE = ['-i', 'tests']

if 'HAPPYDOC_TITLE' not in globals():
    HAPPYDOC_TITLE = PACKAGE_NAME + ' API Reference'


from distutils.core import setup, Command, Extension
from distutils.command.install_data import install_data
from distutils.command.sdist import sdist as old_sdist
from distutils.command.build_ext import build_ext as old_build_ext
import sys


try:
    from Pyrex.Distutils.build_ext import build_ext
    EXT = '.pyx'

except ImportError:
    build_ext = old_build_ext
    EXT = '.c'







class install_data(install_data):

    """Variant of 'install_data' that installs data to module directories"""
    
    def finalize_options (self):
        self.set_undefined_options('install',
                                   ('install_lib', 'install_dir'),
                                   ('root', 'root'),
                                   ('force', 'force'),
                                  )

class sdist(old_sdist):

    """Variant of 'sdist' that (re)builds the documentation first"""
   
    def run(self):
        # Build docs before source distribution
        try:
            import happydoclib
        except ImportError:
            pass
        else:
            self.run_command('happy')

        # Run the standard sdist command
        old_sdist.run(self)















class test(Command):

    """Command to run unit tests after installation"""

    description = "Run unit tests after installation"

    user_options = [
        ('test-module=','m','Test module (default='+TEST_MODULE+')'),
    ]

    def initialize_options(self):
        self.test_module = None

    def finalize_options(self):

        if self.test_module is None:
            self.test_module = TEST_MODULE

        self.test_args = [self.test_module+'.test_suite']

        if self.verbose:
            self.test_args.insert(0,'--verbose')

    def run(self):

        # Install before testing
        self.run_command('install')

        if not self.dry_run:
            from unittest import main
            main(None, None, sys.argv[:1]+self.test_args)










class happy(Command):

    """Command to generate documentation using HappyDoc

        I should probably make this more general, and contribute it to either
        HappyDoc or the distutils, but this does the trick for PEAK for now...
    """

    description = "Generate docs using happydoc"

    user_options = []

    def initialize_options(self):
        self.happy_options = None
        self.doc_output_path = None


    def finalize_options(self):

        if self.doc_output_path is None:
            self.doc_output_path = HAPPYDOC_OUTPUT_PATH

        if self.happy_options is None:
            self.happy_options = [
                '-t', HAPPYDOC_TITLE, '-d', self.doc_output_path,
            ] + HAPPYDOC_IGNORE + [ '.' ]
            if not self.verbose: self.happy_options.insert(0,'-q')

    def run(self):
        from distutils.dir_util import remove_tree, mkpath
        from happydoclib import HappyDoc

        mkpath(self.doc_output_path, 0755, self.verbose, self.dry_run)
        remove_tree(self.doc_output_path, self.verbose, self.dry_run)

        if not self.dry_run:
            HappyDoc(self.happy_options).run()




SETUP_COMMANDS = {
    'install_data': install_data,
    'sdist': sdist,
    'happy': happy,
    'test': test,
    'sdist_nodoc': old_sdist,
    'build_ext': build_ext,
}


