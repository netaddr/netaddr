#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2010, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
Compatibility wrappers providing uniform behaviour for Python code required to
run under both Python 2.x and 3.x.

All operations emulate 2.x behaviour where applicable.
"""
import sys as _sys

try:
    _bytes = bytes
except NameError:
    _bytes = str

if _sys.version_info[0] == 3:
    #   Python 3.x specific logic.
    _sys_maxint = _sys.maxsize

    _is_str = lambda x: isinstance(x, (str, _bytes))

    _is_int = lambda x: isinstance(x, int)

    _callable = lambda x: hasattr(x, '__call__')

    _func_doc = lambda x: x.__doc__

    _dict_keys = lambda x: list(x.keys())

    _dict_items = lambda x: list(x.items())

    _iter_dict_keys = lambda x: x.keys()

    def _bytes_join(*args): return _bytes().join(*args)

    def _zip(*args): return list(zip(*args))

    def _range(*args, **kwargs): return list(range(*args, **kwargs))

    _iter_range = range

    def _func_name(f, name=None):
        if name is not None: f.__name__ = name
        else: return f.__name__

    def _func_doc(f, docstring=None):
        if docstring is not None: f.__doc__ = docstring
        else: return f.__doc__

elif  _sys.version_info[0:2] > [2, 3]:
    #   Python 2.4 or higher.
    _sys_maxint = _sys.maxint

    # NB - not using basestring here for maximum 2.x compatibility.
    _is_str = lambda x: isinstance(x, (str, unicode))

    _is_int = lambda x: isinstance(x, (int, long))

    _callable = lambda x: callable(x)

    _dict_keys = lambda x: x.keys()

    _dict_items = lambda x: x.items()

    _iter_dict_keys = lambda x: iter(x.keys())

    def _bytes_join(*args): return ''.join(*args)

    def _zip(*args): return zip(*args)

    def _range(*args, **kwargs): return range(*args, **kwargs)

    _iter_range = xrange

    def _func_name(f, name=None):
        if name is not None: f.func_name = name
        else: return f.func_name

    def _func_doc(f, docstring=None):
        if docstring is not None: f.func_doc = docstring
        else: return f.func_doc

else:
    #   Unsupported versions.
    raise RuntimeError(
        'this module only supports Python 2.4.x or higher (including 3.x)!')

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    #   string and integer detection tests.
    assert _is_int(_sys_maxint)
    assert not _is_str(_sys_maxint)
    assert _is_str('')
    assert _is_str(''.encode())

    try:
        assert _is_str(unicode(''))
    except NameError:
        #   Ignore Python 3.x exception.
        pass

    #   byte string join tests.
    if _sys.version_info[0] == 3:
        #   Python 3.x
        #   cannot use b'' literals under Python 2.x so using ''.encode() here
        str_8bit = _bytes_join(['a'.encode(), 'b'.encode(), 'c'.encode()])
        assert str_8bit == _bytes('abc'.encode())
        assert "b'abc'" == '%r' % str_8bit
    else:
        #   Python 2.x - 8 bit strings are just regular strings
        str_8bit = _bytes_join(['a', 'b', 'c'])
        assert str_8bit == _bytes('abc')
        assert "'abc'" == '%r' % str_8bit

    #   dict operation tests.
    d = { 'a' : 0, 'b' : 1, 'c' : 2 }

    assert sorted(_dict_keys(d)) == ['a', 'b', 'c']
    assert sorted(_dict_items(d)) == [('a', 0), ('b', 1), ('c', 2)]

    #   zip() BIF tests.
    l2 = _zip([0], [1])

    assert hasattr(_zip(l2), 'pop')
    assert l2 == [(0, 1)]

    #   range/xrange() tests.
    l1 = _range(3)

    assert isinstance(l1, list)
    assert hasattr(l1, 'pop')
    assert l1 == [0, 1, 2]

    it = _iter_range(3)

    assert not isinstance(it, list)
    assert hasattr(it, '__iter__')
    assert not it == [0, 1, 2]
    assert list(it) == [0, 1, 2]

    #   callable() and function meta-data tests.
    i = 1
    def f1():
        """docstring"""
        pass
    f2 = lambda x: x

    assert not _callable(i)
    assert _callable(f1)
    assert _callable(f2)
    assert _func_name(f1) == 'f1'
    assert _func_doc(f1) == 'docstring'

