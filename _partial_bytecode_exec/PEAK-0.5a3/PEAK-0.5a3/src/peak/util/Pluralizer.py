"""Class for converting identifiers to plural form"""

class Pluralizer:

    """Convert an identifier to plural form

    Instances of 'Pluralizer' can be called on identifier strings to convert
    them to plural form, using either a mapping object lookup or a set of
    regular expression replacement rules.  Non-alphabetic suffixes are left
    untouched, and an attempt is made to match the capitalization of the
    original string.  Thus the string '"__harmony__"' would be pluralized
    to '"__harmonies__"', and '"PARENTHESIS_27"' would become
    '"PARENTHESES_27"'.
    """

    def __init__(self,pluralsFile=None,customMapping=None,**kw):

        plurals = self.plurals = {}

        if pluralsFile:
            for l in open(pluralsFile).readlines():
                if '=' in l:
                    [k,v]=split(strip(l),'=',1)
                    plurals[k]=v

        if customMapping: plurals.update(customMapping)
        if kw: plurals.update(kw)














    from re import compile, IGNORECASE

    prefix = r"^([^a-zA-Z]*)"
    infix  = r"(.*?)"
    suffix = r"([^a-zA-Z]*)$"

    consonant = r"([bcdfghjklmnpqrstvwxz])"
    sibilant         = r"([xs])"
    prefixedSibilant = r"(\w[xs])"

    other = compile(prefix+infix+suffix,IGNORECASE).match

    pluralPatterns = (
        (compile(consonant + "y" + suffix, IGNORECASE).subn, r'\1ies\2'),
        (compile(prefixedSibilant + "is" + suffix, IGNORECASE).subn, r'\1es\2'),
        (compile(sibilant + suffix, IGNORECASE).subn, r'\1es\2'),
        (compile(suffix,IGNORECASE).subn, r's\1'),
    )

    del compile, IGNORECASE


    def upperize(self,s,new):

        """Try to capitalize 'new' to match capitalization of 's'"""

        if new != new.lower():
            return new

        if s==s.upper():
            return new.upper()

        elif s[:1]==s[:1].upper():
            return new.capitalize()

        return new





    def lookup(self,s):

        """Look up identifier in mapping object, trying alternative forms"""

        get = self.plurals.get

        new = get(s)
        if new: return new

        new = get(s.lower())
        if new: return self.upperize(s,new)

        match = self.other(s)
        key = match.group(2)

        new = get(key)
        if new: return match.group(1)+new+match.group(3)

        new = get(key.lower())
        if new: return match.group(1)+self.upperize(key,new)+match.group(3)


    def __call__(self,s):

        """Pluralize by looking up in mapping or applying regex rules"""

        new = self.lookup(s)
        if new: return new

        for pat,repl in self.pluralPatterns:
            new, ct = pat(repl,s)
            if ct: break

        if s==s.upper(): new = new.upper()
        return new






