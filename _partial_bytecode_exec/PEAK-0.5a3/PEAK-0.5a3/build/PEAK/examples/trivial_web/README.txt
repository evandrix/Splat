Trivial 'peak.web' Example

 This example is a very trivial 'peak.web' application.  It's nothing
 more than a "hello world" at present.  To use it, you need to create a file 
 something like this::

   #!/bin/sh -login
   export PYTHONPATH=/wherever/PEAK/examples/trivial_web
   exec peak CGI import:webapp.WebApp

 There is a sample file 'webapp.cgi', that you can edit to do this.  Note 
 that if PEAK itself is not installed in your Python's site-packages 
 directory, you'll need to add its location to the PYTHONPATH as well.
 Also note that 'peak.web' uses packages from Zope X3, so you need to
 have the Zope X3 milestone 3 release installed in site-packages, or on
 the PYTHONPATH as well.

 To run the application as a FastCGI, you must have a web server that
 supports FastCGI.  For Apache, this means having 'mod_fastcgi' installed.
 Please see the 'mod_fastcgi' documentation for details of configuring
 Apache for FastCGI use.  If basic configuration is completed, you should
 be able to do something like::

   <Files webapp.cgi>
   SetHandler fastcgi-script
   </Files>

 in the appropriate '.htaccess' file.

 This app doesn't do anything useful; it's just intended to be the simplest
 possible 'peak.web' application.

