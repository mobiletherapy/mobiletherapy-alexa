# -*- coding: utf-8 -*-
#
#  SelfTest/Hash/common.py: Common code for Cryptodome.SelfTest.Hash
#
# Written in 2008 by Dwayne C. Litzenberger <dlitz@dlitz.net>
#
# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================

"""Self-testing for PyCryptodome hash modules"""

import sys
import unittest
import binascii
import Cryptodome.Hash
from Cryptodome.Util.py3compat import b, tobytes
from Cryptodome.Util.strxor import strxor_c

class HashDigestSizeSelfTest(unittest.TestCase):

    def __init__(self, hashmod, description, expected):
        unittest.TestCase.__init__(self)
        self.hashmod = hashmod
        self.expected = expected
        self.description = description

    def shortDescription(self):
        return self.description

    def runTest(self):
        self.assertTrue(hasattr(self.hashmod, "digest_size"))
        self.assertEqual(self.hashmod.digest_size, self.expected)
        h = self.hashmod.new()
        self.assertTrue(hasattr(h, "digest_size"))
        self.assertEqual(h.digest_size, self.expected)


class HashSelfTest(unittest.TestCase):

    def __init__(self, hashmod, description, expected, input):
        unittest.TestCase.__init__(self)
        self.hashmod = hashmod
        self.expected = expected
        self.input = input
        self.description = description

    def shortDescription(self):
        return self.description

    def runTest(self):
        h = self.hashmod.new()
        h.update(self.input)

        out1 = binascii.b2a_hex(h.digest())
        out2 = h.hexdigest()

        h = self.hashmod.new(self.input)

        out3 = h.hexdigest()
        out4 = binascii.b2a_hex(h.digest())

        # PY3K: hexdigest() should return str(), and digest() bytes
        self.assertEqual(self.expected, out1)   # h = .new(); h.update(data); h.digest()
        if sys.version_info[0] == 2:
            self.assertEqual(self.expected, out2)   # h = .new(); h.update(data); h.hexdigest()
            self.assertEqual(self.expected, out3)   # h = .new(data); h.hexdigest()
        else:
            self.assertEqual(self.expected.decode(), out2)   # h = .new(); h.update(data); h.hexdigest()
            self.assertEqual(self.expected.decode(), out3)   # h = .new(data); h.hexdigest()
        self.assertEqual(self.expected, out4)   # h = .new(data); h.digest()

        # Verify that the .new() method produces a fresh hash object, except
        # for MD5 and SHA1, which are hashlib objects.  (But test any .new()
        # method that does exist.)
        if self.hashmod.__name__ not in ('Cryptodome.Hash.MD5', 'Cryptodome.Hash.SHA1') or hasattr(h, 'new'):
            h2 = h.new()
            h2.update(self.input)
            out5 = binascii.b2a_hex(h2.digest())
            self.assertEqual(self.expected, out5)

class HashTestOID(unittest.TestCase):
    def __init__(self, hashmod, oid):
        unittest.TestCase.__init__(self)
        self.hashmod = hashmod
        self.oid = oid

    def runTest(self):
        h = self.hashmod.new()
        self.assertEqual(h.oid, self.oid)


class GenericHashConstructorTest(unittest.TestCase):
    def __init__(self, hashmod):
        unittest.TestCase.__init__(self)
        self.hashmod = hashmod

    def runTest(self):
        obj1 = self.hashmod.new("foo")
        obj2 = self.hashmod.new()
        obj3 = Cryptodome.Hash.new(obj1.name, "foo")
        obj4 = Cryptodome.Hash.new(obj1.name)
        obj5 = Cryptodome.Hash.new(obj1, "foo")
        obj6 = Cryptodome.Hash.new(obj1)
        self.assertTrue(isinstance(self.hashmod, obj1))
        self.assertTrue(isinstance(self.hashmod, obj2))
        self.assertTrue(isinstance(self.hashmod, obj3))
        self.assertTrue(isinstance(self.hashmod, obj4))
        self.assertTrue(isinstance(self.hashmod, obj5))
        self.assertTrue(isinstance(self.hashmod, obj6))

class MACSelfTest(unittest.TestCase):

    def __init__(self, module, description, result, input, key, params):
        unittest.TestCase.__init__(self)
        self.module = module
        self.result = result
        self.input = input
        self.key = key
        self.params = params
        self.description = description

    def shortDescription(self):
        return self.description

    def runTest(self):
        key = binascii.a2b_hex(b(self.key))
        data = binascii.a2b_hex(b(self.input))

        # Strip whitespace from the expected string (which should be in lowercase-hex)
        expected = b("".join(self.result.split()))

        h = self.module.new(key, **self.params)
        h.update(data)
        out1_bin = h.digest()
        out1 = binascii.b2a_hex(h.digest())
        out2 = h.hexdigest()

        # Verify that correct MAC does not raise any exception
        h.hexverify(out1)
        h.verify(out1_bin)

        # Verify that incorrect MAC does raise ValueError exception
        wrong_mac = strxor_c(out1_bin, 255)
        self.assertRaises(ValueError, h.verify, wrong_mac)
        self.assertRaises(ValueError, h.hexverify, "4556")

        h = self.module.new(key, data, **self.params)

        out3 = h.hexdigest()
        out4 = binascii.b2a_hex(h.digest())

        # Test .copy()
        h2 = h.copy()
        h.update(b("blah blah blah"))  # Corrupt the original hash object
        out5 = binascii.b2a_hex(h2.digest())    # The copied hash object should return the correct result

        # PY3K: Check that hexdigest() returns str and digest() returns bytes
        if sys.version_info[0] > 2:
            self.assertTrue(isinstance(h.digest(), type(b(""))))
            self.assertTrue(isinstance(h.hexdigest(), type("")))

        # PY3K: Check that .hexverify() accepts bytes or str
        if sys.version_info[0] > 2:
            h.hexverify(h.hexdigest())
            h.hexverify(h.hexdigest().encode('ascii'))

        # PY3K: hexdigest() should return str, and digest() should return bytes
        self.assertEqual(expected, out1)
        if sys.version_info[0] == 2:
            self.assertEqual(expected, out2)
            self.assertEqual(expected, out3)
        else:
            self.assertEqual(expected.decode(), out2)
            self.assertEqual(expected.decode(), out3)
        self.assertEqual(expected, out4)
        self.assertEqual(expected, out5)

def make_hash_tests(module, module_name, test_data, digest_size, oid=None):
    tests = []
    for i in range(len(test_data)):
        row = test_data[i]
        (expected, input) = list(map(tobytes,row[0:2]))
        if len(row) < 3:
            description = repr(input)
        else:
            description = row[2]
        name = "%s #%d: %s" % (module_name, i+1, description)
        tests.append(HashSelfTest(module, name, expected, input))
    name = "%s #%d: digest_size" % (module_name, i+1)
    tests.append(HashDigestSizeSelfTest(module, name, digest_size))

    if oid is not None:
        tests.append(HashTestOID(module, oid))

    if getattr(module, 'name', None) is not None:
        tests.append(GenericHashConstructorTest(module))

    return tests

def make_mac_tests(module, module_name, test_data):
    tests = []
    for i in range(len(test_data)):
        row = test_data[i]
        (key, data, results, description, params) = row
        name = "%s #%d: %s" % (module_name, i+1, description)
        tests.append(MACSelfTest(module, name, results, data, key, params))
    return tests

# vim:set ts=4 sw=4 sts=4 expandtab:
