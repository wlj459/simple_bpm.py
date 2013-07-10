"""
bpm.kernel.features
===================

Built-in kernel features.

Features
--------
"""

all_feature_names = frozenset([
    "internal_import",
])

INTERNAL_IMPORT = 0b0001

_ALL_FEATURES = {
    INTERNAL_IMPORT: "Internal Import",
}


class _Feature(object):

    def __init__(self, importer_flag):
        self.importer_flag = importer_flag

    def __add__(self, other):
        return self.__class__(self.importer_flag | other.importer_flag)

    def __contains__(self, item):
        if item in _ALL_FEATURES:
            return True if self.importer_flag & item else False

        return False

    def __repr__(self):
        features = []
        for feature in _ALL_FEATURES:
            if self.importer_flag & feature:
                features.append(_ALL_FEATURES[feature])

        return "_Feature(%s)" % ", ".join(features)


internal_import = _Feature(INTERNAL_IMPORT)