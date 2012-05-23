from peak.api import binding, naming, protocols, adapt
import smtplib

class smtpURL(naming.URL.Base):

    supportedSchemes = ('smtp', )
    defaultFactory = 'peak.naming.factories.smtp.SMTPFactory'

    class user(naming.URL.Field):
        pass

    class port(naming.URL.IntField):
        defaultValue=smtplib.SMTP_PORT

    class host(naming.URL.RequiredField):
        pass

    class auth(naming.URL.Field):
        pass

    syntax = naming.URL.Sequence(
        '//',
        (   user,
            (naming.URL.StringConstant(';AUTH=',False), auth),
            '@',
        ),
        host, (':', port)
    )


class SMTPFactory(binding.Singleton):

    protocols.advise(classProvides=[naming.IObjectFactory])

    def getObjectInstance(self, context, refInfo, name, attrs=None):
        addr, = refInfo.addresses
        addr = adapt(addr, smtpURL)
        return smtplib.SMTP(addr.host, addr.port)

