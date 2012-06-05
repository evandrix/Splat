"""Software project version numbering tool, similar to 'vertoo'

    This is partly intended to show how much simpler it is to develop a
    full-featured application when infrastructure like configuration files,
    transactions, and a commandline app framework are already provided by PEAK.

    The application uses two input files.  The first one is an executable
    configuration file that describes the version numbering scheme(s) used by
    the project, and lists all the files that should be edited when the version
    number is updated, and what strings to change in those files, using what
    version formats.  The second file is a simple data file that contains the
    project's current version number.

    To show or update the current version number(s), or perform other
    version-related functions, one simply executes the configuration file,
    passing any appropriate arguments.  If necessary, the version data file
    will be automatically updated along with the files that are edited.  Any
    changes made are done atomically: either all edits should succeed, or all
    changes will be rolled back.

    The application is not completed yet, however, as other, higher-priority
    projects have been taking precedence.  For a sample of what version
    configuration and data files will probably look like, see 'version' and
    'version.dat' in the main PEAK source tree (same directory as 'setup.py').
"""
