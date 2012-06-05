##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# Python datetime prototype.

# This package contains the prototype datetime Python module whose C
# version is included in Python 2.3.  We've turned it into a package to
# make it easier to deal with in CVS for now.  This __init__ file makes the
# package look like the eventual module.

from datetime._datetime import MINYEAR, MAXYEAR
from datetime._datetime import timedelta
from datetime._datetime import time, date, datetime
from datetime._datetime import tzinfo

