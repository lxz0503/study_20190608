#!/usr/bin/env python
#############################################################################
#
# Copyright (c) 2006-2013, 2022 Wind River Systems, Inc.
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
Test script for ipcrypto shell commands
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

class rsa_cmds:
    """
    Test the genrsa and rsa shell commands.
    """

    def config(self):
        self.eta = 10
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):

        target.s.s.timeout = 360

        target.send("genrsa 1024 ")
        target.expect(["-----BEGIN RSA PRIVATE KEY-----",
                       "-----BEGIN PRIVATE KEY-----"])
        target.expect(["-----END RSA PRIVATE KEY-----",
                       "-----END PRIVATE KEY-----"])
        target.wait_prompt()

        target.send("genrsa 2048 ")
        target.expect(["-----BEGIN RSA PRIVATE KEY-----",
                       "-----BEGIN PRIVATE KEY-----"])
        target.expect(["-----END RSA PRIVATE KEY-----",
                       "-----END PRIVATE KEY-----"])
        target.wait_prompt()

        target.send("genrsa -aes128 1024")
        target.expect("Enter PEM pass phrase:")
        target.send("Goofy")
        target.expect("Verifying - Enter PEM pass phrase:")
        target.send("Goofy")
        i = target.expect(["-----BEGIN RSA PRIVATE KEY-----",
                           "-----BEGIN ENCRYPTED PRIVATE KEY-----"])
        if (i != 1):
            target.expect("DEK-Info: AES-128-CBC")

        target.expect(["-----END RSA PRIVATE KEY-----",
                       "-----END ENCRYPTED PRIVATE KEY-----"])
        target.wait_prompt()

        target.send("genrsa -out rsa_key.pem -aes128 1024")
        target.expect("Enter PEM pass phrase:")
        target.send("Goofy")
        target.expect("Verifying - Enter PEM pass phrase:")
        target.send("Goofy")
        target.wait_prompt()

        target.send("cat rsa_key.pem")
        i = target.expect(["-----BEGIN RSA PRIVATE KEY-----",
                           "-----BEGIN ENCRYPTED PRIVATE KEY-----"])
        if (i != 1):
            target.expect("DEK-Info: AES-128-CBC")

        target.expect(["-----END RSA PRIVATE KEY-----",
                       "-----END ENCRYPTED PRIVATE KEY-----"])
        target.wait_prompt()

        target.send("rsa -in rsa_key.pem -text")
        target.expect("Enter pass phrase for rsa_key.pem:")
        target.send("Goofy")
        target.expect("modulus:")
        target.expect("publicExponent:")
        target.expect("privateExponent:")
        target.expect("prime1:")
        target.expect("prime2:")
        target.expect("exponent1:")
        target.expect("exponent2:")
        target.expect("coefficient:")
        target.expect(["-----BEGIN RSA PRIVATE KEY-----",
                       "-----BEGIN PRIVATE KEY-----"])
        target.expect(["-----END RSA PRIVATE KEY-----",
                       "-----END PRIVATE KEY-----"])
        target.wait_prompt()

        target.send("rm rsa_key.pem")
        target.wait_prompt()


class dsa_cmds:
    """
    Test the dsaparam, gendsa and dsa shell commands.
    """

    def config(self):
        self.eta = 10
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        target.s.s.timeout = 360

        target.send("dsaparam 1024 ")
        target.expect("-----BEGIN DSA PARAMETERS-----")
        target.expect("-----END DSA PARAMETERS-----")
        target.wait_prompt()

        target.send("dsaparam 2048 ")
        target.expect("-----BEGIN DSA PARAMETERS-----")
        target.expect("-----END DSA PARAMETERS-----")
        target.wait_prompt()

        target.send("dsaparam -out dsaparam.pem 1024 ")
        target.wait_prompt()

        target.send("dsaparam -in dsaparam.pem -text")
        target.expect("[pP]:")
        target.expect("[qQ]:")
        target.expect("[gG]:")
        target.expect("-----BEGIN DSA PARAMETERS-----")
        target.expect("-----END DSA PARAMETERS-----")
        target.wait_prompt()

        target.send("gendsa dsaparam.pem")
        target.expect(["-----BEGIN DSA PRIVATE KEY-----",
                       "-----BEGIN PRIVATE KEY-----"])
        target.expect(["-----END DSA PRIVATE KEY-----",
                       "-----END PRIVATE KEY-----"])
        target.wait_prompt()

        target.send("gendsa -out dsa_key.pem -des3 dsaparam.pem")
        target.expect("Enter PEM pass phrase:")
        target.send("Mickey")
        target.expect("Verifying - Enter PEM pass phrase:")
        target.send("Mickey")
        target.wait_prompt()

        target.send("cat dsa_key.pem")
        i = target.expect(["-----BEGIN DSA PRIVATE KEY-----",
                           "-----BEGIN PRIVATE KEY-----",
                           "-----BEGIN ENCRYPTED PRIVATE KEY-----"])
        if (i != 2):
            target.expect("DEK-Info: DES-EDE3-CBC")

        target.expect(["-----END DSA PRIVATE KEY-----",
                       "-----END ENCRYPTED PRIVATE KEY-----"])
        target.wait_prompt()

        target.send("dsa -in dsa_key.pem -text")
        target.expect("Enter pass phrase for dsa_key.pem")
        target.send("Mickey")
        target.expect("priv:")
        target.expect("pub:")
        target.expect("P:")
        target.expect("Q:")
        target.expect("G:")
        target.expect(["-----BEGIN DSA PRIVATE KEY-----",
                       "-----BEGIN PRIVATE KEY-----"])
        target.expect(["-----END DSA PRIVATE KEY-----",
                       "-----END PRIVATE KEY-----"])


class dh_cmds:
    """
    Test the dhparam shell command
    """

    def config(self):
        self.eta = 40
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):

        target.s.s.timeout = 900

        target.send("dhparam 1024")
        target.expect("Generating DH parameters, 1024 bit long safe prime")
        while True:
            i = target.expect(["-----BEGIN DH PARAMETERS-----",
                               "[+*]"])
            if i == 0:
                break

        target.expect("-----END DH PARAMETERS-----")
        target.wait_prompt()

        target.send("dhparam 2048")
        target.expect("Generating DH parameters, 2048 bit long safe prime")
        while True:
            i = target.expect(["-----BEGIN DH PARAMETERS-----",
                               "[+*]"])
            if i == 0:
                break

        target.expect("-----END DH PARAMETERS-----")
        target.wait_prompt()

        target.send("dhparam -out dhparam.pem 1024")
        target.expect("Generating DH parameters, 1024 bit long safe prime")
        while True:
            i = target.expect([re.escape(target.s.prompt),
                               "[+*]"])
            if i == 0:
                break

        target.send("dhparam -in dhparam.pem -text")
        target.expect_exact(["Diffie-Hellman-Parameters: (1024 bit)",
                             "DH Parameters: (1024 bit)"])
        target.expect("P:")
        target.expect("G:")
        target.expect("-----BEGIN DH PARAMETERS-----")
        target.expect("-----END DH PARAMETERS-----")
        target.wait_prompt()

        target.send("rm dhparam.pem")
        target.wait_prompt()


class speed_cmd:
    """
    Test the speed shell commands
    """

    def config(self):
        self.eta = 600
        self.hosts = 1
        self.v6 = False

    def test(self, log, target, v6, _):
        return

        target.s.s.timeout = 360

        target.send("speed")
        while True:
            i = target.expect([re.escape(target.s.prompt), \
                               "Doing md2", \
                               "Doing mdc2", \
                               "Doing md4", \
                               "Doing md5", \
                               "Doing hmac (md5)", \
                               "Doing sha1", \
                               "Doing sha256", \
                               "Doing sha512", \
                               "Doing rmd160", \
                               "Doing rc4", \
                               "Doing des cbc", \
                               "Doing des ede3", \
                               "Doing aes-128", \
                               "Doing aes-192", \
                               "Doing aes-256", \
                               "Doing rc2", \
                               "Doing blowfish", \
                               "Doing cast", \
                               "Doing 512 bit private", \
                               "Doing 512 bit private rsa's", \
                               "Doing 512 bit public rsa's", \
                               "Doing 1024 bit private rsa's", \
                               "Doing 1024 bit public rsa's", \
                               "Doing 2048 bit private rsa's", \
                               "Doing 2048 bit public rsa's", \
                               "Doing 4096 bit private rsa's", \
                               "Doing 4096 bit public rsa's", \
                               "Doing 512 bit sign dsa's", \
                               "Doing 512 bit verify dsa's", \
                               "Doing 1024 bit sign dsa's", \
                               "Doing 1024 bit verify dsa's", \
                               "Doing 2048 bit sign dsa's", \
                               "Doing 2048 bit verify dsa's"])
            if i == 0:
                break  # Tests completed

##########################################################################
#                       END OF FILE
###########################################################################
