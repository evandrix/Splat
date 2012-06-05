Trivial CGI Example

 This example is a very trivial CGI/FastCGI program.  It does not use 
 'peak.web' at all; just the CGI/FastCGI part of 'peak.running'.  To
 use it, you need to create a file something like this::

   #!/bin/sh -login
   export PYTHONPATH=/wherever/PEAK/examples/trivial_cgi
   exec peak CGI import:the_cgi.DemoCGI

 There is a sample file 'trivial.cgi', that you can edit.  Note that if 
 PEAK itself is not installed in your Python's site-packages directory,
 you'll need to add its location to the PYTHONPATH as well.

 To run the application as a FastCGI, you must have a web server that
 supports FastCGI.  For Apache, this means having 'mod_fastcgi' installed.
 Please see the 'mod_fastcgi' documentation for details of configuring
 Apache for FastCGI use.  If basic configuration is completed, you should
 be able to do something like::

   <Files trivial.cgi>
   SetHandler fastcgi-script
   </Files>

 in the appropriate '.htaccess' file.  If you are successful, repeatedly
 invoking the CGI should result in the displayed count value going up.
 If your server is configured to start multiple FastCGI processes, it may
 take a while for the count to increase.  That is, if the server starts 3
 FastCGI processes, then the displayed count may only increase every 3
 requests, as each process takes a turn serving new requests.  You should
 be able to use 'ps' to list the running FastCGI servers.

 If you are running the application as a plain CGI script, the counter will
 not increase, since after each invocation the script will exit.

