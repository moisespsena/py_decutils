'''
Python Decorator Utilities

Created on Feb 15, 2013

@author: Moises P Sena
'''
__author__ = 'Moises P Sena <moisespsena@gmail.com>'
from inspect import isclass

try:
    from ordereddict import OrderedDict
except ImportError:
    from collections import OrderedDict 


class decorator(object):
    def __init__(self, target=None, *args, **kwargs):
        self._target = target
        self.caller = None
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        data = []
        if self._target:
            data.apped("target=%r" % self._target)
        if self.kwargs:
            data.append("**%r" % self.kwargs)

        return "<%s(%s)(%s)>" % (self.__class__.__name__, ", ".join(data),
                                 self.caller)

    @property
    def target(self):
        return self._target if self._target else self.caller

    def __call__(self, caller, keys=()):
        self.caller = caller
        keys = set(keys + (self.__class__,))
        target = self.target

        decs = Decs.changed(target)

        for key in keys:
            decs[key] = self

        return caller

    @classmethod
    def by(cls, fn):
        return Decs.get_dec(fn, cls)


FN_DEC_ATT_NAME = 'decutils_fn_decorators'


def make_init_method(cls=None):
    def __init__(self):
        super(self.__class__, self).__init__()
    if cls:
        __init__.im_class = cls
    return __init__



def ql_class_name(cls):
    return "%s.%s" % (cls.__module__, cls.__name__)


def ql_fn_name(fn):
    return "%s.%s" % (ql_class_name(fn.im_class), fn.__name__)

def ql_name(obj):
    if isclass(obj):
        return ql_class_name(obj)
    return ql_fn_name(obj)


class Decs(object):
    def __init__(self, target, map=None, readonly=False):
        self.target = target
        self._readonly = readonly
        self.map = map if map is not None else OrderedDict()

    def __setitem__(self, key, dec):
        assert not self._readonly
        self.map[key]= dec

    def __getitem__(self, key):
        return self.map.get(key)

    def __contains__(self, key):
        return key in self.map

    def __repr__(self):
        name = ql_name(self.target)
        return "<Decorators(%s, %r)>" % (name, self.map)

    def __iter__(self):
        return iter(self.map.iterkeys())

    def iteritems(self):
        return self.map.iteritems()

    @classmethod
    def changed(cls, fn):
        decs = getattr(fn, FN_DEC_ATT_NAME, None)
        if decs is None:
            decs = cls(fn)
            try:
                setattr(fn, FN_DEC_ATT_NAME, decs)
            except:
                if fn.__name__ == '__init__':
                    new_fn = make_init_method(fn.im_class)
                    return cls.changed(new_fn)
                else:
                    raise
        return decs

    @classmethod
    def readonly(cls, fn, forced=True):
        decs = getattr(fn, FN_DEC_ATT_NAME, None)
        if decs is None:
            if forced:
                decs = cls(fn, readonly=True)
        else:
            decs = cls(fn, decs.map, readonly=True)
        return decs

    @classmethod
    def alias(cls, src, dst):
        decs = cls.changed(src)
        setattr(dst, FN_DEC_ATT_NAME, decs)

    @classmethod
    def get_dec(cls, fn, dec):
        decs = cls.readonly(fn)
        return decs[dec]

    @classmethod
    def contains_dec(cls, fn, dec_cls):
        decs = decs = cls.readonly(fn, False)
        if decs is not None:
            if dec_cls in decs:
                return True
        return False


def pointer(source, destination, raw=False, decoratorssrc=None):
    raise NotImplementedError()


class override(decorator):
    def invoke(self, *args, **kwargs):
        return self.caller(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        caller = super(override, self).__call__(*args, **kwargs)
        def invoke(*args, **kwargs):
            return self.invoke(*args, **kwargs)
        invoke.__repr__ = self.__repr__
        invoke.__name__ = caller.__name__
        Decs.alias(caller, invoke)
        return invoke
