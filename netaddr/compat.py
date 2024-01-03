#-----------------------------------------------------------------------------
#   Copyright (c) 2008 by David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------

try:
    from importlib import resources as _importlib_resources
except ImportError:
    import importlib_resources as _importlib_resources


if hasattr(_importlib_resources, 'files'):
    def _open_binary(pkg, res):
        return _importlib_resources.files(pkg).joinpath(res).open('rb')
else:
    _open_binary = _importlib_resources.open_binary
