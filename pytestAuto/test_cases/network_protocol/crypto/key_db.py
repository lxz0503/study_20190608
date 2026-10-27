#!/usr/bin/env python
#############################################################################
#
# Copyright (c) 2006-2014, 2021-2023 Wind River Systems, Inc.
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
Write you module description here
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
#                        CLASSES
###########################################################################

class pkey_import:
    """
    Verify that public key pairs can be imported into the key database
    """

    def config(self):
	self.eta = 2
	self.hosts = 1
	self.v6 = False

    def test(self, log, target, v6, _):

        try:
            download_key_files(target)

            target.send("keydb import key kalle rsa_1024.pem")
            i = target.expect([re.escape(target.s.prompt),
                              "ipcom_shell : Unknown command: 'keydb'",
                              "Cmd: 'keydb' not found"])
            if i != 0:
                return "skipped"

            target.send("keydb list key")
            target.expect("kalle")
            target.wait_prompt()

            target.send("keydb import key kalle dsa_1024.pem")
            i = target.expect(["Failed: already installed", re.escape(target.s.prompt)])
            if i == 1:
                raise test_fail ('Import succeeded when it should have failed')
            target.wait_prompt()

            target.send_and_wait_prompt("keydb import key nisse dsa_1024.pem")
            target.send("keydb list key")
            target.expect("nisse")
            target.wait_prompt()

            target.send_and_wait_prompt("keydb delete key kalle")
            target.send("keydb list key")
            i = target.expect(["kalle", re.escape(target.s.prompt)])
            if i == 0:
                raise test_fail('Failed to delete key_id kalle')

            target.send_and_wait_prompt("keydb delete key nisse")
            target.send("keydb list key")
            i = target.expect(["nisse", re.escape(target.s.prompt)])
            if i == 0:
                raise test_fail('Failed to delete key_id nisse')

        finally:
            target.send_and_wait_prompt("keydb delete key kalle")
            target.send_and_wait_prompt("keydb delete key nisse")


class pkey_find:
    """
    Verify that a key can be found matching an X509 certificate.
    """

    def config(self):
	self.eta = 2
	self.hosts = 1
	self.v6 = False

    def test(self, log, target, v6, _):

        try:
            download_key_files(target)

            # Verify that no key is found when the key of the cert is not installed
            target.send("keydb find rsa_1024_cert.pem")
            i = target.expect(["Key matching certificate found",
                               "No matching key found.",
                               "ipcom_shell : Unknown command: 'keydb'",
                               "Cmd: 'keydb' not found"])
            if i == 2 or i == 3:
                return "skipped"
            if i == 0:
                raise test_fail('Matching key found, when no key should be found')
            target.wait_prompt()

            # Verify that a key is found when the key of the cert is installed
            target.send_and_wait_prompt("keydb import key rsa_1024 rsa_1024.pem")
            target.send("keydb find rsa_1024_cert.pem")
            i = target.expect(["Key matching certificate found. key_id: rsa_1024",
                               "No matching key found."])
            if i == 1:
                raise test_fail('Matching key not found for cert rsa_1024')
            target.wait_prompt()

            # Install a DSA key and verify that the correct key is found for
            # RSA and DSA certs, respectively
            target.send_and_wait_prompt("keydb import key dsa_1024 dsa_1024.pem")
            target.send("keydb find dsa_1024_cert.pem")
            i = target.expect(["Key matching certificate found. key_id: dsa_1024",
                               "No matching key found."])
            if i == 1:
                raise test_fail('Matching key not found for cert dsa_1024')
            target.wait_prompt()
            target.send("keydb find rsa_1024_cert.pem")
            i = target.expect(["Key matching certificate found. key_id: rsa_1024",
                               "No matching key found."])
            if i == 1:
                raise test_fail('Matching key not found for cert rsa_1024')
            target.wait_prompt()

            # Remove rsa_1024 key, verify that a key for dsa_1024_cert is still found
            target.send_and_wait_prompt("keydb delete key rsa_1024")
            target.send("keydb find dsa_1024_cert.pem")
            i = target.expect(["Key matching certificate found. key_id: dsa_1024",
                               "No matching key found."])
            if i == 1:
                raise test_fail('Matching key not found for cert dsa_1024')

        finally:
            # Cleanup
            target.send_and_wait_prompt("keydb delete key dsa_1024")
            target.send_and_wait_prompt("keydb delete key rsa_1024")

class pkey_print:
    """
    Verify that public keys can be printed of key pairs stored in the key database
    """

    def config(self):
	self.eta = 2
	self.hosts = 1
	self.v6 = False

    def test(self, log, target, v6, _):

        try:
            download_key_files(target)

            target.send("keydb import key rsa_1024 rsa_1024.pem")
            i = target.expect([re.escape(target.s.prompt),
                              "ipcom_shell : Unknown command: 'keydb'",
                              "Cmd: 'keydb' not found"])
            if i != 0:
                return "skipped"

            target.send_and_wait_prompt("keydb import key dsa_1024 dsa_1024.pem")

            target.send("keydb print rsa_1024")
            target.expect_exact("Public-Key: (1024 bit)")
            target.expect_exact(["Modulus:", "Modulus (1024 bit):"])
            target.expect_exact("Exponent")
            target.wait_prompt()

            target.send("keydb print dsa_1024")
            target.expect_exact("Public-Key: (1024 bit)")
            target.expect_exact("pub:")
            target.expect_exact("P:")
            target.expect_exact("Q:")
            target.expect_exact("G:")
            target.wait_prompt()

        finally:
            # Cleanup
            target.send_and_wait_prompt("keydb delete key dsa_1024")
            target.send_and_wait_prompt("keydb delete key rsa_1024")

class buf_import_delete:
    """
    Verify that pre-shared keys or buffers can be imported into, and deleted from,
    the key database
    """

    def config(self):
	self.eta = 2
	self.hosts = 1
	self.v6 = False

    def test(self, log, target, v6, _):

        try:
            target.send("keydb")
            i = target.expect([re.escape(target.s.prompt),
                              "ipcom_shell : Unknown command: 'keydb'",
                              "Cmd: 'keydb' not found"])
            if i != 0:
                return "skipped"

            # Normal, successful case
            import_buf(target, "kalle", "kallekalle")
            verify_buf_exists(target, "kalle")

            # Normal, successful case, add 2nd key
            import_buf(target, "nisse", "nissenisse")
            verify_buf_exists(target, "nisse")

            # Should fail, already installed
            target.send("keydb import buf kalle")
            target.expect("Enter key:")
            target.send("kallekalle")
            target.expect("Re-type key:")
            target.send("kallekalle")
            target.expect("Failed: already installed")
            target.wait_prompt()

            # Should fail, key mismatch
            target.send("keydb import buf kalle")
            target.expect("Enter key:")
            target.send("kalle")
            target.expect("Re-type key:")
            target.send("ellak")
            target.expect("Failed. Entered keys do not match")
            target.wait_prompt()

            # Verify that a key can be deleted
            target.send_and_wait_prompt("keydb delete buf kalle")
            verify_buf_does_not_exist(target, "kalle")

            # Verify that key be added, after it's been deleted
            import_buf(target, "kalle", "kallekalle")
            verify_buf_exists(target, "kalle")

            # Delete the key once more
            target.send_and_wait_prompt("keydb delete buf kalle")
            verify_buf_does_not_exist(target, "kalle")


        finally:
            # Cleanup to leave target in known state in case anything fails above
            target.send_and_wait_prompt("keydb delete buf kalle")
            target.send_and_wait_prompt("keydb delete buf nisse")


class buf_verify:
    """
    Verify that the value of a buffer key can be verified.
    """

    def config(self):
	self.eta = 2
	self.hosts = 1
	self.v6 = False

    def test(self, log, target, v6, _):
        try:
            # Verify that keydb command is available
            target.send("keydb")
            i = target.expect([re.escape(target.s.prompt),
                              "ipcom_shell : Unknown command: 'keydb'",
                              "Cmd: 'keydb' not found"])
            if i != 0:
                return "skipped"

            # Normal case
            import_buf(target, "kalle", "kalle")
            verify_buf_value(target, "kalle", "kalle")

            # Minimal buffer length
            import_buf(target, "1", "1")
            verify_buf_value(target, "1", "1")

            # Maximum buffer length, 128
            max_pw_str = "01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567"
            import_buf(target, "max_buf", max_pw_str)
            verify_buf_value(target, "max_buf", max_pw_str)

            # Exceed Maximum buffer length, 128 + 1
            exceed_buf = max_pw_str  + "X"
            target.send("keydb import buf exceeded_buf")
            target.expect("Enter key:")
            target.send(exceed_buf)
            target.expect("Re-type key:")
            target.send(exceed_buf)
            target.expect("Failed: invalid argument")
            target.wait_prompt()
            verify_buf_does_not_exist(target, "exceeded_buf")

            # 1 byte padding
            import_buf(target, "kalle15", "012345678901234")
            verify_buf_value(target, "kalle15", "012345678901234")

            # 16 byte padding
            import_buf(target, "kalle16", "0123456789012345")
            verify_buf_value(target, "kalle16", "0123456789012345")

            # 15 byte padding
            import_buf(target, "kalle17", "01234567890123456")
            verify_buf_value(target, "kalle17", "01234567890123456")

            # This particular key is used by ike in tests
            import_buf(target, "ike", "this_should_be_secret")
            verify_buf_value(target, "ike", "this_should_be_secret")

        finally:
            target.send_and_wait_prompt("keydb delete buf kalle")
            target.send_and_wait_prompt("keydb delete buf max_buf")
            target.send_and_wait_prompt("keydb delete buf 1")
            target.send_and_wait_prompt("keydb delete buf kalle15")
            target.send_and_wait_prompt("keydb delete buf kalle16")
            target.send_and_wait_prompt("keydb delete buf kalle17")
            target.send_and_wait_prompt("keydb delete buf ike")

###########################################################################
#                       FUNCTIONS
###########################################################################

def download_key_files(target):
    import ftplib

    files = ('rsa_1024.pem', 'dsa_1024.pem', 'rsa_1024_cert.pem', 'dsa_1024_cert.pem')
    ftp = ftplib.FTP(target.login_ip().addr)
    ftp.login('ftp', 'interpeak')
    for file in files:
        path = os.path.join(config.productroot, config.productpath['ipcrypto'], 'test/CA/keys/', file)
        data = open(path)
        ftp.storbinary('STOR %s' % os.path.basename(file), data)
        data.close()


def import_buf(target, key_id, buf):
    target.send("keydb import buf "+key_id)
    target.expect("Enter key:")
    target.send(buf)
    target.expect("Re-type key:")
    target.send(buf)
    target.wait_prompt()


def verify_buf_exists(target, key_id):
    target.send("keydb list buf")
    target.expect(key_id)
    target.wait_prompt()


def verify_buf_value(target, key_id, key_value):
    target.send("keydb verify "+key_id)
    target.expect("Enter key:")
    target.send(key_value)
    i = target.expect(["Keys match", "Keys do not match"])
    target.wait_prompt()
    if i == 1:
        raise 'Incorrect key value'


def verify_buf_does_not_exist(target, key_id):
    target.send("keydb list buf")
    i = target.expect([key_id, re.escape(target.s.prompt)])
    if i == 0:
        raise test_fail('key_id '+key_id+' exists when it should not')


##########################################################################
#                       END OF FILE
###########################################################################
