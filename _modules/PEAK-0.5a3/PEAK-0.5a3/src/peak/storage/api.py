from interfaces import *
from transactions import *
from data_managers import *
from connections import *
from caches import *
from lazy_loader import *

from peak.util.imports import lazyModule

xmi = lazyModule('peak.storage.xmi')

del lazyModule

def DMFor(*classes):
    from peak.api import config
    return config.ProviderOf(IDataManager,*classes)


