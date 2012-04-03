"""Utilities for dealing with clusters of loosely-coupled systems.

 Many enterprise applications will be run, rather than on a single
 computer, in a loosely-coupled cluster of machines.  A set of several
 web-servers, for example.  We have found the
 "clusterit tools":http://www.garbled.net/clusterit.html to be very useful
 in such situations.  Clusterit, inspired by the tools provided in IBM's
 PSSP, is simple to set up and use, if somewhat quirky in implementation.

 PEAK supports the cluster definition file used by Clusterit-2.0, providing
 the information contained therein via the properties mechanism.  Note
 that you don't have to have the Clusterit tools installed to make use of
 this, or for it to be useful.  Nor will anything break if you make use
 of these properties in your application and they haven't been set up.
 In the abscence of a cluster definition file, PEAK will behave as if
 the local hostname was listed in the cluster file, without being part
 of a group.  In other words, in the abscence of other information, the
 cluster consists of just the local machine.

 Then environment variable 'CLUSTER' (or, in PEAK's case, the property
 'peak.running.cluster._filename', if it exists, else
 '__main__.CLUSTER', which falls back to 'environ.CLUSTER')
 specifies a file defining the cluster.  A cluster may be subdivided into
 groups.  In PEAK it is allowable for groups to have overlapping
 membership.  Let's look at a fairly complicated example::

    foo.baz.com
    bar.baz.com
    GROUP:odd
    one.baz.com
    three.baz.com
    five.baz.com
    GROUP:even
    two.baz.com
    four.baz.com
    six.baz.com
    GROUP:prime
    one.baz.com
    two.baz.com
    three.baz.com
    five.baz.com
    GROUP:qux
    frob.baz.com
    one.baz.com
    LUMP:weird
    qux
    prime

 PEAK treats this file as if it had seven groups.  The existance and
 memberships of the first four groups, 'odd', 'even', 'prime', and 'qux',
 should be clear.  A "lump" is a group defined in terms of other groups or
 lumps.  In this case the group 'weird' contains the union of the groups
 'qux' and 'prime'.  Note that one.baz.com is a member of both qux and prime.
 The group 'weird' will contain it only once, however -- duplicates are
 removed automatically.  Another group, '__orphans__', contains any hosts
 that were listed at the beginning of the file before any 'GROUP:' lines.
 Lastly the group '__all__' contains all hosts listed in the file.

 Each group is exported as a property 'peak.running.cluster.groups.<groupname>'
 (for example, 'peak.running.cluster.groups.prime') with its value a tuple of
 strings of the hostnames of the members.

 The property 'peak.running.cluster.groups' will contain a tuple of strings
 naming each group except the '__orphans__' and '__all__' groups (that
 is, it names all the explicitly-created groups).

 The property 'peak.running.cluster.hosts.<hostname>' will be a tuple of
 strings of the names of all groups the host belongs to (except the
 __all__ group).  For example, in the example above,
 'peak.running.cluster.hosts.one.baz.com'is '("odd", "prime", "qux", "wierd")'.

 The property 'peak.running.cluster.hosts' is a shortcut for
 'peak.running.cluster.groups.__all__', listing all hosts in the cluster.

 Finally, the property 'peak.running.cluster.hostname' is a string with
 the local machine's network hostname (per 'socket.gethostname()'), and
 'peak.running.cluster.shortname' is the the same, truncated after the
 first '"."', if any.
"""



from peak.api import *
import os
from kjbuckets import *

def parseCluster(prefix, fn):

    try:
        import socket
        hn = socket.gethostname()
    except:
        hn = 'NO_NAME'

    props = {}
    props[prefix + 'hostname'] = hn
    props[prefix + 'shortname'] = hn.split('.', 1)[0]

    if fn is None or not os.path.exists(fn):
        file = [hn]
    else:
        file = open(fn, 'r')

    all    = kjGraph()
    groups = kjSet()
    hosts  = kjSet()
    order  = kjDict()
    gname  = '__orphans__'
    inLump = False
    lineno = 0

    for l in file:

        lineno += 1; l = l.strip()
        lumpline = l.startswith('LUMP:')

        if not l or l.startswith('#'):
            continue





        if lumpline or l.startswith('GROUP:'):

            inLump  = lumpline
            gname = l.split(':', 1)[1]
            groups.add(gname)

            if not order.has_key(gname):
                order[gname] = lineno, gname

        else:
            all.add(l, gname)

            if inLump:
                groups.add(l)
            else:
                hosts.add(l)

            if not order.has_key(l):
                order[l] = lineno, l

        def ordered_tuple(set):
            values = (set * order).values()
            values.sort()
            return tuple([v for (k,v) in values])

    host_pre  = prefix+'hosts.'
    group_pre = prefix+'groups.'

    for host in hosts.values():
        props[host_pre + host] = ordered_tuple(all.reachable(host))

    g = ~all    # get reverse mappping from groups to hosts

    for group in groups.values() + ['__orphans__']:
        props[group_pre + group] = ordered_tuple(
            # don't include groups in groups' membership
            (g.reachable(group) - groups)
        )



    props[prefix + 'groups']           = ordered_tuple(groups)
    props[prefix + 'hosts']            = ordered_tuple(hosts)
    props[prefix + 'groups.__all__']   = ordered_tuple(hosts)

    return props






def loadCluster(configMap, filename=None, prefix='peak.running.cluster.*',
                propertyName=None, includedFrom=None
    ):

    prefix = PropertyName(prefix).asPrefix()

    r = parseCluster(prefix, filename)

    for k,v in r.items():
        configMap.registerProvider(
            PropertyName(k), config.Value(v)
        )

    if propertyName:
        return r.get(propertyName, NOT_FOUND)

    return NOT_FOUND

protocols.adviseObject(loadCluster, provides=[config.ISettingLoader])











