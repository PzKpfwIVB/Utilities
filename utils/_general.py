""" A module for general utilities for use internally in the package. """

__author__ = "Mihaly Konda"
__version__ = '1.1.0'

# Built-in modules
from collections import UserDict
from dataclasses import is_dataclass
from functools import cached_property
import inspect
import os
import sys
from types import FunctionType, MethodType
from typing import Generic, TypeVar

# Qt6 modules
from PySide6.QtCore import Signal


class BijectiveDict(UserDict):
    """ A custom dictionary providing bijective mapping. """

    def __init__(self, main_key_type):
        super().__init__()
        self._internal_dict = {}
        self._main_key_type = main_key_type

    def __getitem__(self, item):
        return self._internal_dict[item]

    def __setitem__(self, key, value):
        if key in self._internal_dict:
            dict.__delitem__(self._internal_dict, key)

        if value in self._internal_dict:
            dict.__delitem__(self._internal_dict, value)

        dict.__setitem__(self._internal_dict, key, value)
        dict.__setitem__(self._internal_dict, value, key)

    def __delitem__(self, item):
        dict.__delitem__(self._internal_dict, self[item])
        dict.__delitem__(self._internal_dict, item)

    def __len__(self):
        return dict.__len__(self._internal_dict) // 2

    def __repr__(self):
        return dict.__repr__(self._internal_dict)

    def keys(self, main_only=True):
        mains = [k for k in self._internal_dict.keys()
                 if isinstance(k, self._main_key_type)]

        if main_only:
            return mains

        secondaries = [k for k in self._internal_dict.keys()
                       if not isinstance(k, self._main_key_type)]

        return mains, secondaries

    def values(self, secondary_only=True):
        secondaries = [k for k in self._internal_dict.keys()
                       if not isinstance(k, self._main_key_type)]

        if secondary_only:
            return secondaries

        mains = [k for k in self._internal_dict.keys()
                 if isinstance(k, self._main_key_type)]

        return mains, secondaries


class ReadOnlyDescriptor:
    """ Read-only descriptor for use with protected storage attributes. """

    def __set_name__(self, owner, name):
        """ Sets the name of the storage attribute.
        Owner is the managed class, name is the managed attribute's name. """

        self._storage_name = f"_{name}"

    def __get__(self, instance, instance_type=None):
        """ Returns the value of the protected storage attribute. """

        if instance is None:
            return self  # Class accession: return the descriptor itself

        return getattr(instance, self._storage_name)

    def __set__(self, instance, value):
        """ Raises an exception notifying the user about the attribute
        being read-only. """

        raise AttributeError(f"attribute '{self._storage_name[1:]}' of "
                             f"'{instance.__class__.__name__}' object "
                             f"is read-only")


_T = TypeVar('_T')


class SignalBlocker(Generic[_T]):
    """ Temporarily blocks the signals of the handled QObject. """

    def __init__(self, obj: _T):
        """ Initializer for the class.

        Parameters
        ----------
        obj : QObject
            An object whose signals should be blocked temporarily.
        """

        self._obj = obj

    def __enter__(self) -> _T:
        """ Blocks the signals of the handled QObject. """

        self._obj.blockSignals(True)
        return self._obj

    def __exit__(self, exc_type, exc_value, traceback):
        """ Unblocks the signals of the handled QObject. """

        self._obj.blockSignals(False)


class Singleton(type):
    """ A metaclass making instance classes singletons. """

    _instances = {}  # Shared between instance classes, hence the dict

    def __call__(cls, *args, **kwargs):
        """ Returns the existing instance or creates a new one. """

        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def resource_path(relative_path) -> str:
    """ Get absolute path to resource (for apps built with PyInstaller).

    Parameters
    ----------
    relative_path : str
        A string representing a relative path to the requested resource.
    """

    # PyInstaller creates a temp folder and stores path in _MEIPASS
    return os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')),
                        relative_path)


def _stub_repr_function_like(f, class_bound):
    """ Creates a stub representation for a function-like object.

    Parameters
    ----------
    f : cached_property, FunctionType, MethodType
        The object whose stub representation is to be made.

    class_bound : bool
        A flag directing the function to add 'self' to the representation.
    """

    decorator = ''
    if isinstance(f, cached_property):
        f = f.func
        decorator = '\t@cached_property\n'
    elif isinstance(f, MethodType):  # Cannot yet differentiate static methods
        decorator = '\t@classmethod\n'

    anns = []
    defaults = [] if f.__defaults__ is None else list(f.__defaults__)

    # Using reverse order to get the default values
    for param, typ in list(f.__annotations__.items())[::-1]:
        if param == 'return':  # Return annotation is handled on its own
            continue

        # The type is passed as a string if the source has __future__ annot.
        if not isinstance(typ, str) and typ is not None:
            typ = typ.__name__

        default_value = ''
        if defaults:
            dv = defaults.pop()
            if isinstance(dv, str):
                default_value = f" = '{dv}'"
            else:
                default_value = f" = {dv}"

        anns.append(f"{param}: {typ}{default_value}")

    if isinstance(f, MethodType):  # Refers to a class method
        anns.append('cls')
    elif class_bound:
        anns.append('self')

    try:
        ret_type = f.__annotations__['return']
    except KeyError:  # Return annotation is not provided in the function def
        return_annotation = ''
    else:
        # The type is passed as a string if the source has __future__ annot.
        if not isinstance(ret_type, str) and ret_type is not None:
            ret_type = ret_type.__name__
        return_annotation = f" -> {ret_type}"

    func_repr = f"{decorator}{'\t' if class_bound else ''}" \
                f"def {f.__name__}({', '.join(anns[::-1])}" \
                f"){return_annotation}: ...\n"

    return func_repr


def stub_repr(obj: object, signals: list[str] | None = None,
              extra_cvs: str | None = None) -> str:
    """ Creates a specifically formatted stub representation of an object. """

    # Cannot yet handle static methods, so they are changed to class methods

    repr_ = ''
    if inspect.isclass(obj):
        function_likes = []
        class_vars = []
        signal_reprs = []
        properties = []
        for dir_item in dir(obj):
            if not dir_item.startswith('__'):
                cls_attr = getattr(obj, dir_item)
                # print(f"{str(obj):<40}{str(cls_attr):<75}{type(cls_attr)}")
                if any(isinstance(cls_attr, typ) for typ in
                       [cached_property, FunctionType, MethodType]):
                    function_likes.append(
                        _stub_repr_function_like(cls_attr, True))
                elif isinstance(cls_attr, ReadOnlyDescriptor):
                    repr_ = f"\t{dir_item}: ReadOnlyDescriptor = " \
                            "ReadOnlyDescriptor()\n"
                    class_vars.append(repr_)
                elif isinstance(cls_attr, Signal) and signals is not None:
                    for sig in signals:
                        if (sig_name := sig.split('(')[0]) in str(cls_attr):
                            signal_reprs.append(f"\t{sig_name} : "
                                                "ClassVar[Signal] = "
                                                f"...  # {sig}\n")
                elif isinstance(cls_attr, property):
                    prop_funcs = {'fget': 'property',
                                  'fset': '{fn}.setter',
                                  'fdel': '{fn}.deleter'}

                    for attr, deco in prop_funcs.items():
                        if (func := getattr(cls_attr, attr)) is not None:
                            if '{' in deco:
                                deco = deco.format(fn=func.__name__)

                            repr_ = f"\t@{deco}\n" \
                                    f"{_stub_repr_function_like(func, True)}"
                            properties.append(repr_)

        bases = ''
        if obj.__bases__[0].__name__ != 'object':
            bases = ', '.join([b.__name__ for b in obj.__bases__])
            if isinstance(obj, Singleton):
                bases += f", metaclass={type(obj).__name__}"

            bases = f'({bases})'
        elif isinstance(obj, Singleton):
            bases = f'(metaclass={type(obj).__name__})'

        class_decorator = '@dataclass\n' if is_dataclass(obj) else ''

        repr_ = f"{class_decorator}class {obj.__name__}{bases}:\n" \
                f"{''.join(signal_reprs) + '\n' if signal_reprs else ''}" \
                f"{extra_cvs + '\n' if extra_cvs is not None else ''}" \
                f"{''.join(class_vars) + '\n' if class_vars else ''}" \
                f"{_stub_repr_function_like(obj.__init__, True)}" \
                f"{''.join(function_likes)}" \
                f"{''.join(properties)}"
    elif inspect.isfunction(obj):
        repr_ = _stub_repr_function_like(obj, False)

    return repr_
