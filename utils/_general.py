""" A module for general utilities for use internally in the package. """

__author__ = "Mihaly Konda"
__version__ = '1.0.0'

# Built-in modules
from collections import UserDict
from typing import Generic, TypeVar


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
