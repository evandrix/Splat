"""Trivial Interfaces and Adaptation"""

from api import *
from adapters import NO_ADAPTER_NEEDED,DOES_NOT_SUPPORT,Adapter,StickyAdapter
from interfaces import *
from advice import metamethod, supermeta
from classic import ProviderMixin
from generate import protocolForType, protocolForURI
from generate import sequenceOf, IBasicSequence
