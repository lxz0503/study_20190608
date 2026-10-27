#!/usr/bin/env python
#############################################################################
#
# Copyright (c) 2006-2013, 2021-2022 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################


###########################################################################
#                       DESCRIPTION
###########################################################################
"""
Test script for ipcrypto
"""

###########################################################################
#                       INCLUDE FILES
###########################################################################

import glob
import config
import os
import pexpect
import re
import string
import subprocess
import sys
import time


###########################################################################
#                        VARIABLES
###########################################################################


###########################################################################
#                        FUNCTIONS
###########################################################################

def fips_mode(target):
    target.send("fips_ctrl mode show")
    i = target.expect(["FIPS mode on",
                       "ipcom_shell : Unknown command: 'fips_ctrl'",
                       "Cmd: 'fips_ctrl' not found"])
    target.wait_prompt()
    if i == 0:
        return True
    return False


###########################################################################
#                        CLASSES
###########################################################################

class bntest:
    """
    Run openssl Big Number tests
    """

    def config(self):
        self.eta = 100
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.s.s.timeout = 300

        target.send("bntest")
        target.expect("bntest +successfully")
        target.wait_prompt()

        target.send("exptest")
        target.expect("exptest +successfully")
        target.wait_prompt()


class ectest:
    """
    Run openssl Elliptic Curve tests
    """

    def config(self):
        self.eta = 15
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.s.s.timeout = 120
        target.send("ectest")
        i = target.expect(["Curve .* cardinality test",
                           "ipcom_shell : Unknown command: 'ectest'",
                           "Cmd: 'ectest' not found"])
        if i != 0:
            return "skipped"

        target.expect("ectest +successfully ")
        target.wait_prompt()


class ecdhtest:
    """
    Run openssl ECDH tests
    """

    def config(self):
        self.eta = 6
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.s.s.timeout = 120
        target.send("ecdhtest")
        i = target.expect(["Testing key generation with NIST Prime-Curve P-192 \.* ok",
                           "ipcom_shell : Unknown command: 'ecdhtest'",
                           "Cmd: 'ecdhtest' not found"])
        if i != 0:
            return "skipped"

        target.expect("Testing key generation with NIST Prime-Curve P-224 \.* ok")
        target.expect("Testing key generation with NIST Prime-Curve P-256 \.* ok")
        target.expect("Testing key generation with NIST Prime-Curve P-384 \.* ok")
        target.expect("Testing key generation with NIST Prime-Curve P-521 \.* ok")
        target.expect("Testing ECDH shared secret with Brainpool Prime-Curve brainpoolP256r1 ok")
        target.expect("Testing ECDH shared secret with Brainpool Prime-Curve brainpoolP384r1 ok")
        target.expect("Testing ECDH shared secret with Brainpool Prime-Curve brainpoolP512r1 ok")

        target.wait_prompt()


class ecdsatest:
    """
    Run openssl ECDSA tests
    """

    def config(self):
        self.eta = 30
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.s.s.timeout = 120

        target.send("ecdsatest")
        i = target.expect(["1..2",
                           "ipcom_shell : Unknown command: 'ecdsatest'",
                           "Cmd: 'ecdsatest' not found"])
        if i != 0:
            return "skipped"

        target.expect("ecdsatest +successfully")
        target.wait_prompt()


class exptest:
    """
    Run openssl exp tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("exptest")
        target.expect("exptest +successfully")
        target.wait_prompt()


class md2test:
    """
    Run openssl MD2 tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("md2test")
        i = target.expect(["test 1 ok",
                           "ipcom_shell : Unknown command: 'md2test'",
                           "Cmd: 'md2test' not found"])
        if i != 0:
            return "skipped"

        target.expect("test 2 ok")
        target.expect("test 3 ok")
        target.expect("test 4 ok")
        target.expect("test 5 ok")
        target.expect("test 6 ok")
        target.expect("test 7 ok")

        target.wait_prompt()


class md4test:
    """
    Run openssl MD4 tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        if fips_mode(target) == True:
            return "skipped"

        target.send("md4test")
        i = target.expect(["test 1 ok",
                           "ipcom_shell : Unknown command: 'md4test'",
                           "Cmd: 'md4test' not found"])
        if i != 0:
            return "skipped"

        target.expect("test 2 ok")
        target.expect("test 3 ok")
        target.expect("test 4 ok")
        target.expect("test 5 ok")
        target.expect("test 6 ok")
        target.expect("test 7 ok")

        target.wait_prompt()


class md5test:
    """
    Run openssl MD5 tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        if fips_mode(target) == True:
            return "skipped"

        target.send("md5test")
        target.expect("test 1 ok")
        target.expect("test 2 ok")
        target.expect("test 3 ok")
        target.expect("test 4 ok")
        target.expect("test 5 ok")
        target.expect("test 6 ok")
        target.expect("test 7 ok")

        target.wait_prompt()


class hmactest:
    """
    Run openssl HMAC tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        if fips_mode(target) == True:
            return "skipped"

        target.send("hmactest")
        target.expect("hmactest +successfully")
        target.wait_prompt()


class rc2test:
    """
    Run openssl RC2 tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("rc2test")
        i = target.expect(["ecb RC2 ok",
                           "ipcom_shell : Unknown command: 'rc2test'",
                           "Cmd: 'rc2test' not found"])
        if i != 0:
            return "skipped"

        target.wait_prompt()


class rc4test:
    """
    Run openssl RC4 tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("rc4test")
        i = target.expect(["Subtest:",
                           "ipcom_shell : Unknown command: 'rc4test'",
                           "Cmd: 'rc4test' not found"])
        if i != 0:
            return "skipped"

        target.expect("rc4test +successfully")
        target.wait_prompt()


class rc5test:
    """
    Run openssl RC5 tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("rc5test")
        i = target.expect([re.escape(target.s.prompt),
                           "ipcom_shell : Unknown command: 'rc5test'",
                           "Cmd: 'rc5test' not found"])
        if i != 0:
            return "skipped"

        target.wait_prompt()


class destest:
    """
    Run openssl DES tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("destest")
        target.expect("destest +successfully")
        target.wait_prompt()


class shatest:
    """
    Run openssl SHA tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("shatest")
        i = target.expect(["test 1 ok",
                           "ipcom_shell : Unknown command: 'shatest'",
                           "Cmd: 'shatest' not found"])
        if i != 0:
            return "skipped"

        target.expect("test 2 ok")
        target.expect("test 3 ok")

        target.wait_prompt()


class sha1test:
    """
    Run openssl SHA1 tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("sha1test")
        target.expect("test 1 ok")
        target.expect("test 2 ok")
        target.expect("test 3 ok")

        target.wait_prompt()


class sha256test:
    """
    Run openssl SHA256 tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("sha256test")
        target.expect("Testing SHA-256 ... passed.")
        target.expect("Testing SHA-224 ... passed.")

        target.wait_prompt()


class sha512test:
    """
    Run openssl SHA512 and SHA384 tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("sha512test")

        i = target.expect(["Testing SHA-512 ... passed.",
                           "ipcom_shell : Unknown command: 'sha512test'",
                           "Cmd: 'sha512test' not found"])
        if i != 0:
            return "skipped"

        target.expect_exact("Testing SHA-384 ... passed.")

        target.wait_prompt()


class mdc2test:
    """
    Run openssl MDC2 tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("mdc2test")
        i = target.expect(["pad1 - ok",
                           "ipcom_shell : Unknown command: 'mdc2test'",
                           "Cmd: 'mdc2test' not found"])
        if i != 0:
            return "skipped"

        target.expect("pad2 - ok")

        target.wait_prompt()


class rmdtest:
    """
    Run openssl Ripemd tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("rmdtest")
        i = target.expect(["test 1 ok",
                           "ipcom_shell : Unknown command: 'rmdtest'",
                           "Cmd: 'rmdtest' not found",
                           "No ripemd support"])
        if i != 0:
            return "skipped"

        target.expect("test 2 ok")
        target.expect("test 3 ok")
        target.expect("test 4 ok")
        target.expect("test 5 ok")
        target.expect("test 6 ok")
        target.expect("test 7 ok")
        target.expect("test 8 ok")

        target.wait_prompt()


class randtest:
    """
    Run openssl RAND tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("randtest")
        i = target.expect(["test 1 done",
                           "ipcom_shell : Unknown command: 'randtest'",
                           "Cmd: 'randtest' not found"])
        if i != 0:
            return "skipped"

        target.expect("test 2 done")
        target.expect("test 3 done")
        target.expect("test 4 done")

        target.wait_prompt()


# class dhtest:
#    """
#    Run openssl DH tests
#    """

#    def config(self):
#	self.eta = 10
#	self.hosts = 1
#	self.v6 = False

#   def test(self, log, target, v6, _):
#        if fips_mode(target) == True:
#            return "skipped"

#	target.send("dhtest")
#	target.expect("dh_test")
#	target.expect("rfc5114_test")
#	target.expect("successfully")

#	target.wait_prompt()

class casttest:
    """
    Run openssl CAST tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("casttest")
        i = target.expect(["Subtest:",
                           "ipcom_shell : Unknown command: 'casttest'",
                           "Cmd: 'casttest not found",
                           "No CAST support"])
        if i != 0:
            return "skipped"

        target.expect("casttest +successfully")
        target.wait_prompt()


class bftest:
    """
    Run openssl Blowfish tests
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("bftest")
        i = target.expect(["Subtest:",
                           "ipcom_shell : Unknown command: 'bftest'",
                           "Cmd: 'bftest' not found"])
        if i != 0:
            return "skipped"

        target.expect("bftest +successfully ")

        target.wait_prompt()


class dsatest:
    """
    Run openssl DSA tests
    """

    def config(self):
        self.eta = 10
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        if fips_mode(target) == True:
            return "skipped"

        target.s.s.timeout = 120
        target.send("dsatest")
        target.expect("dsatest +successfully ")
        target.wait_prompt()


class rsatest:
    """
    Run openssl RSA tests
    """

    def config(self):
        self.eta = 10
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        if fips_mode(target) == True:
            return "skipped"

        target.s.s.timeout = 300
        target.send("rsa_test")
        target.expect("rsa_test +successfully")

        target.wait_prompt()


class evptest:
    """
    Run openssl EVP tests
    """

    def config(self):
        self.eta = 15
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        import ftplib

        # Download evp test config file
        ftp = ftplib.FTP(target.login_ip().addr)
        ftp.login('ftp', 'interpeak')
        dir = os.path.join(config.productroot, config.productpath['ipcrypto'], 'test')
        fp = open(dir + '/evptests.txt')
        ftp.storbinary('STOR evptests.txt', fp)
        fp.close()
        fp = open(dir + '/evptests-fips-140-2.txt')
        ftp.storbinary('STOR evptests-fips-140-2.txt', fp)
        fp.close()
        ftp.quit()

        target.send("fips_ctrl mode show")
        i = target.expect(["FIPS mode on",
                           "ipcom_shell : Unknown command: 'fips_ctrl'",
                           "Cmd: 'fips_ctrl' not found"])
        if i == 0:
            target.send("evp_test evptests-fips-140-2.txt")
        else:
            target.send("evp_test evptests.txt")

        while True:
            i = target.expect(
                [re.escape(target.s.prompt), "Testing digest", "Testing cipher", "disabled", "failed", "mismatch",
                 "doesn't match"])
            if i == 0:
                break  # Tests completed
            elif i == 1 or i == 2 or i == 3:
                continue  # Tests ongoing
            else:
                raise test_fail("EVP Tests failed")


# class x509test:
#    """
#    Run openssl X509 tests
#    """

#    def config(self):
#	self.eta = 3
#	self.hosts = 1
#	self.v6 = False

#   def test(self, log, target, v6, _):
#	target.send("tabtest")
#	target.expect("Order OK")
#	target.wait_prompt()


class aescmac_test:
    """
    Verify the AES CMAC algorithm using test vectors
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("cmactest")
        target.expect("AES128 Gen Sub Key1 Passed")
        target.expect("AES128 Gen Sub Key2 Passed")
        target.expect("Invalid outputLength test pass")
        target.expect("AES128 0 Byte Message Passed")
        target.expect("AES128 0 Byte Message Blockmode, Context reuse Passed")
        target.expect("AES128 16 Byte Message aesCmacBlock Passed")
        target.expect("AES128 40 Byte Message aesCmacBlock Passed")
        target.expect("AES128 64 Byte Message aesCmacBlock Passed")
        target.expect("AES192 Gen Sub Key1 Passed")
        target.expect("AES192 Gen Sub Key2 Passed")
        target.expect("AES192 0 Byte Message Passed")
        target.expect("AES192 0 Byte Message Blockmode, Context reuse Passed")
        target.expect("AES192 16 Byte Message aesCmacBlock Passed")
        target.expect("AES192 40 Byte Message aesCmacBlock Passed")
        target.expect("AES192 64 Byte Message aesCmacBlock Passed")
        target.expect("AES256 Gen Sub Key1 Passed")
        target.expect("AES256 Gen Sub Key2 Passed")
        target.expect("AES256 0 Byte Message Passed")
        target.expect("AES256 0 Byte Message Blockmode, Context reuse Passed")
        target.expect("AES256 16 Byte Message aesCmacBlock Passed")
        target.expect("AES256 40 Byte Message aesCmacBlock Passed")
        target.expect("AES256 64 Byte Message aesCmacBlock Passed")
        target.expect("AES-CMAC-PRF-128 18 byte key Passed")
        target.expect("AES-CMAC-PRF-128 16 byte key Passed")
        target.expect("AES-CMAC-PRF-128 10 byte key Passed")
        target.expect("cmactest succeeds")
        target.wait_prompt()


class aeskeywrap_test:
    """
    Verify the AES Key Wrap algorithm using test vectors
    """

    def config(self):
        self.eta = 3
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.send("aeskeywraptest")
        target.expect("AES Keywrap: 128 KEK, 128 Key Encrypt Passed")
        target.expect("AES Keywrap: 128 KEK, 128 Key Decrypt Passed")
        target.expect("AES Keywrap: 192 KEK, 128 Key Encrypt Passed")
        target.expect("AES Keywrap: 192 KEK, 128 Key Decrypt Passed")
        target.expect("AES Keywrap: 256 KEK, 128 Key Encrypt Passed")
        target.expect("AES Keywrap: 256 KEK, 128 Key Decrypt Passed")
        target.expect("AES Keywrap: 192 KEK, 192 Key Encrypt Passed")
        target.expect("AES Keywrap: 192 KEK, 192 Key Decrypt Passed")
        target.expect("AES Keywrap: 256 KEK, 192 Key Encrypt Passed")
        target.expect("AES Keywrap: 256 KEK, 192 Key Decrypt Passed")
        target.expect("AES Keywrap: 256 KEK, 256 KEK Encrypt Passed")
        target.expect("AES Keywrap: 256 KEK, 256 KEK Decrypt Passed")
        target.expect("aeskeywraptest succeeds")

##########################################################################
#                       END OF FILE
###########################################################################
