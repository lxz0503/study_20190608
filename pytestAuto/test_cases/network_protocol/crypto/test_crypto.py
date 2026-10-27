#!/usr/bin/env python3
# encoding=utf-8
"""
@author:XLi3
@time:2/20/2024 5:43 PM
@file:test_crypto.py
"""
import re
import time

import pytest
import allure
import sys

sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.log_record import log
from utils.case_record import record_result, record_result_expect
from utils.ezTargets import QemuTarget, VxWorksImage


def fips_mode(target, prompt):  # xiaozhan, modify this function-- add ret as return value
    log.info('Check FIPS mode which should not be on')
    ret = target.sendAndReturnAll('fips_ctrl mode show', prompt)
    if 'FIPS mode on' in ret:
        assert False


def import_buf(target, key_id, buf, prompt):  # xiaozhan, add prompt parameter
    try:
        target.send("keydb import buf " + key_id)  # import_buf(target, "kalle", "kallekalle", self.vxprompt)
        target.expect("Enter key:")
        target.send(buf)  # input kallekalle
        target.expect("Re-type key:")
        target.send(buf)  # kallekalle
        target.expect(prompt)
    except:
        log.error('Failed to import buf')
        assert False


def verify_buf_exists(target, key_id,
                      prompt):  # xiaozhan, add prompt parameter     verify_buf_exists(target, "kalle", self.vxprompt)
    try:
        target.send("keydb list buf")
        target.expect(key_id)
        target.expect(prompt)
    except:
        log.error('Failed to verify buf exists')
        assert False


def verify_buf_value(target, key_id, key_value, prompt):  # xiaozhan, add prompt parameter
    try:
        target.send("keydb verify " + key_id)
        target.expect("Enter key:")
        target.send(key_value)
        i = target.expect(["Keys match", "Keys do not match"])
        target.expect(prompt)
    except:
        log.error('Incorrect key value')
        assert False
    else:
        if i == 1:
            log.error('Incorrect key value')
            assert False


def verify_buf_does_not_exist(target, key_id, prompt):
    try:
        target.send("keydb list buf")
        i = target.expect([key_id, prompt])  # xiaozhan, add prompt
    except:
        log.error('key_id ' + key_id + ' exists when it should not')
        assert False
    else:
        if i == 0:
            log.error('key_id ' + key_id + ' exists when it should not')
            assert False


class TestCrypto(object):
    """
    Run openssl Big Number tests
    """

    def setup_class(self):
        # different test suite has different path
        self.image_path = '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu-crypto/vxWorks'
        self.vxprompt = '# '
        self.result = []
        self.pass_num = self.fail_num = 0
        self.module = 'ipcrypto.ipcrypto_test'
        # set up network on qemu
        vximage = VxWorksImage(self.image_path, debug=False)
        self.vx_targets = [QemuTarget('QEMU-Q35-%s' % x, logFile='qemu%s.log' % x) for x in range(1, 2)]
        [x.boot(vximage) for x in self.vx_targets]
        # qemu VxWorks
        self.t1 = self.vx_targets[0]
        # config ipv6 for each qemu vxworks
        self.t1.sendAndExpect('cmd', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet6 add 2000::3 prefixlen 64 up', self.vxprompt)
        self.t1.sendAndExpect('ifconfig eth0 inet add 10.236.1.3 prefixlen 24 up', self.vxprompt)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_bntest(self, version):
        with allure.step('bntest'):
            target = self.t1
            name = 'bntest'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = '\n'.join(target.sendAndReturnAll('bntest', self.vxprompt))
            res = re.search(r'bntest\s+successfully', ret)[0]
            if res not in ret:
                ret = 'FAIL'
                record_result_expect(self.result, ret, case_name)

            log.info(f'run on target {target.board}')
            ret = '\n'.join(target.sendAndReturnAll('exptest', self.vxprompt))
            res = re.search(r'exptest\s+successfully', ret)[0]
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_ectest(self, version):
        with allure.step('Run openssl Elliptic Curve tests'):
            target = self.t1
            name = 'ectest'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = '\n'.join(target.sendAndReturnAll('ectest', self.vxprompt))
            res = re.search(r'ectest\s+successfully', ret)[0]
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_ecdh(self, version):
        with allure.step('Run openssl ECDH tests'):
            target = self.t1
            name = 'ecdh'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = target.sendAndReturnAll('ecdhtest', self.vxprompt)[:-1]
            res = 'ok'
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_ecdsa(self, version):
        with allure.step('Run openssl ECDSA tests'):
            target = self.t1
            name = 'ectest'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = '\n'.join(target.sendAndReturnAll('ecdsatest', self.vxprompt))
            res = re.search(r'ecdsatest\s+successfully', ret)[0]
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_exp(self, version):
        with allure.step('Run openssl exp tests'):
            target = self.t1
            name = 'exp'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = '\n'.join(target.sendAndReturnAll('exptest', self.vxprompt))
            res = re.search(r'exptest\s+successfully', ret)[0]
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    @pytest.mark.skip()
    def test_crypto_md2(self, version):
        with allure.step('Run openssl MD2 tests'):
            target = self.t1

            log.info('====Start Tests Run openssl MD2 tests==\n\n')
            log.info(f'run on target {target.board}\nmd2test')
            ret = '\n'.join(target.sendAndReturnAll('md2test', self.vxprompt))
            assert 'ok' in ret

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_md4(self, version):
        with allure.step('Run openssl MD4 tests'):
            target = self.t1
            name = 'md4'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'run on target {target.board}')

            try:
                fips_mode(target, self.vxprompt)
                ret = target.sendAndReturnAll('md4test', self.vxprompt)[:-1]
                res = 'ok'
            except:
                ret = 'FAIL'
                record_result_expect(self.result, ret, case_name)
            else:
                record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_md5(self, version):
        with allure.step('Run openssl MD5 tests'):
            target = self.t1
            name = 'md5'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'run on target {target.board}')

            try:
                fips_mode(target, self.vxprompt)
                ret = target.sendAndReturnAll('md5test', self.vxprompt)[:-1]
                res = 'ok'
            except:
                ret = 'FAIL'
                record_result_expect(self.result, ret, case_name)
            else:
                record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_hmac(self, version):
        with allure.step('Run openssl hmac tests'):
            target = self.t1
            name = 'hmac'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'run on target {target.board}')

            try:
                fips_mode(target, self.vxprompt)
                ret = '\n'.join(target.sendAndReturnAll('hmactest', self.vxprompt))
                res = re.search(r'hmactest\s+successfully', ret)[0]
            except:
                ret = 'FAIL'
                record_result_expect(self.result, ret, case_name)
            else:
                record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_rc2(self, version):  # xiaozhan, this can not be running on simulator
        with allure.step('Run openssl RC2 tests'):
            target = self.t1
            name = 'rc2'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'run on target {target.board}')

            ret = '\n'.join(target.sendAndReturnAll('rc2test', self.vxprompt))
            res = re.search(r'rc2test\s+successfully', ret)[0]
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_rc4(self, version):
        with allure.step('Run openssl RC4 tests'):
            target = self.t1
            name = 'rc4'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = '\n'.join(target.sendAndReturnAll('rc4test', self.vxprompt))
            res = re.search(r'rc4test\s+successfully', ret)[0]
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    @pytest.mark.skip()
    def test_rc5(self, version):
        with allure.step('Run openssl RC5 tests'):
            target = self.t1
            name = 'rc5'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = '\n'.join(target.sendAndReturnAll('rc5test', self.vxprompt))
            res = re.search(r'rc5test\s+successfully', ret)[0]
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_des(self, version):
        with allure.step('Run openssl DES tests'):
            target = self.t1
            name = 'des'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = '\n'.join(target.sendAndReturnAll('destest', self.vxprompt))
            res = re.search(r'destest\s+successfully', ret)[0]
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    @pytest.mark.skip()
    def test_sha(self, version):
        with allure.step('Run openssl SHA tests'):
            target = self.t1
            name = 'sha'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = target.sendAndReturnAll('shatest', self.vxprompt)[:-1]
            res = 'ok'
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_sha1(self, version):
        with allure.step('Run openssl SHA1 tests'):
            target = self.t1
            name = 'sha1'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = target.sendAndReturnAll('sha1test', self.vxprompt)[:-1]
            res = 'ok'
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_sha256(self, version):
        with allure.step('Run openssl SHA256 tests'):
            target = self.t1
            name = 'sha256'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = target.sendAndReturnAll('sha256test', self.vxprompt)[:-1]
            res = 'passed'
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_sha512(self, version):
        with allure.step('Run openssl SHA512 and SHA384 tests'):
            target = self.t1
            name = 'sha512'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = target.sendAndReturnAll('sha512test', self.vxprompt)[:-1]
            res = 'passed'
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_rmd(self, version):
        with allure.step('Run openssl Ripemd tests'):
            target = self.t1
            name = 'rmd'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = target.sendAndReturnAll('rmdtest', self.vxprompt)[:-1]
            res = 'ok'
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_rand(self, version):
        with allure.step('Run openssl RAND tests'):
            target = self.t1
            name = 'rand'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = target.sendAndReturnAll('randtest', self.vxprompt)[:-1]
            res = 'done'
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_cast(self, version):
        with allure.step('Run openssl CAST tests'):
            target = self.t1
            name = 'cast'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = '\n'.join(target.sendAndReturnAll('casttest', self.vxprompt))
            res = re.search(r'casttest\s+successfully', ret)[0]
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_bf(self, version):
        with allure.step('Run openssl BF tests'):
            target = self.t1
            name = 'bf'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = '\n'.join(target.sendAndReturnAll('bftest', self.vxprompt))
            res = re.search(r'bftest\s+successfully', ret)[0]
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_dsa(self, version):
        with allure.step('Run openssl DSA tests'):
            target = self.t1
            name = 'dsa'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = '\n'.join(target.sendAndReturnAll('dsatest', self.vxprompt))
            res = re.search(r'dsatest\s+successfully', ret)[0]
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_rsa(self, version):
        with allure.step('Run openssl RSA tests'):
            target = self.t1
            name = 'rsa'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'run on target {target.board}')

            try:
                fips_mode(target, self.vxprompt)
                ret = '\n'.join(target.sendAndReturnAll('rsa_test', self.vxprompt))
                res = re.search(r'rsa_test\s+successfully', ret)[0]
            except:
                ret = 'FAIL'
                record_result_expect(self.result, ret, case_name)
            else:
                record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_evp(self, version):
        with allure.step('Run openssl EVP tests'):
            target = self.t1
            name = 'evp'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'Run openssl EVP tests on {target.board}')

            try:
                target.send("fips_ctrl mode show")
                i = target.expect(["FIPS mode on",
                                   "ipcom_shell : Unknown command: 'fips_ctrl'",
                                   "Cmd: 'fips_ctrl' not found"])
                if i == 0:
                    target.send("evp_test /romfs/evptests-fips-140-2.txt")  # xiaozhan, modify to romfs instead of ftp
                else:
                    target.send("evp_test /romfs/evptests.txt")  # xiaozhan, modify to romfs instead of ftp

                target.expect('Subtest: ')
                target.expect('Reading /romfs/evptests.txt')
                target.expect('Completed')
                target.expect(self.vxprompt)  # xiaozhan, do not forget this prompt
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    @pytest.mark.skip()
    def test_aescmac(self, version):
        with allure.step('Verify the AES CMAC algorithm using test vectors'):
            target = self.t1
            name = 'aescmac'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = target.sendAndReturnAll('cmactest', self.vxprompt)[-2]
            res = 'cmactest succeeds'
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_aeskeywrap(self, version):
        with allure.step('Verify the AES Key Wrap algorithm using test vectors'):
            target = self.t1
            name = 'aeskeywrap'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')
            ret = target.sendAndReturnAll('aeskeywraptest', self.vxprompt)[-2]
            res = 'aeskeywraptest succeeds'
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_rsa_cmds(self, version):
        with allure.step('Test the genrsa and rsa shell commands.'):
            target = self.t1
            name = 'rsa_cmds'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'run on target {target.board}')

            try:
                target.send('genrsa 1024')
                target.expect(["-----BEGIN RSA PRIVATE KEY-----", "-----BEGIN PRIVATE KEY-----"])
                target.expect(["-----END RSA PRIVATE KEY-----", "-----END PRIVATE KEY-----"])
                target.expect(self.vxprompt)

                target.send("genrsa 2048 ")
                target.expect(["-----BEGIN RSA PRIVATE KEY-----", "-----BEGIN PRIVATE KEY-----"])
                target.expect(["-----END RSA PRIVATE KEY-----", "-----END PRIVATE KEY-----"])
                target.expect(self.vxprompt)

                target.send('genrsa -aes128 1024')
                target.expect('Enter PEM pass phrase:')
                target.send('Goofy')
                target.expect('Verifying - Enter PEM pass phrase:')
                target.send("Goofy")
                i = target.expect(["-----BEGIN RSA PRIVATE KEY-----", "-----BEGIN ENCRYPTED PRIVATE KEY-----"])
                if i != 1:
                    target.expect("DEK-Info: AES-128-CBC")

                target.expect(["-----END RSA PRIVATE KEY-----", "-----END ENCRYPTED PRIVATE KEY-----"])
                target.expect(self.vxprompt)

                target.sendAndExpect('cd /ram', self.vxprompt)  # xiaozhan, add for qemu
                target.send("genrsa -out rsa_key.pem -aes128 1024")  # debug here
                target.expect("Enter PEM pass phrase:")
                target.send("Goofy")
                target.expect("Verifying - Enter PEM pass phrase:")
                target.sendAndExpect("Goofy", self.vxprompt)

                target.send("cat rsa_key.pem")
                i = target.expect(["-----BEGIN RSA PRIVATE KEY-----", "-----BEGIN ENCRYPTED PRIVATE KEY-----"])
                if i != 1:
                    target.expect("DEK-Info: AES-128-CBC")

                target.expect(["-----END RSA PRIVATE KEY-----", "-----END ENCRYPTED PRIVATE KEY-----"])
                target.expect(self.vxprompt)

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
                target.expect(["-----BEGIN RSA PRIVATE KEY-----", "-----BEGIN PRIVATE KEY-----"])
                target.expect(["-----END RSA PRIVATE KEY-----", "-----END PRIVATE KEY-----"])
                target.expect(self.vxprompt)

                target.sendAndExpect("rm rsa_key.pem", self.vxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_dsa_cmds(self, version):
        with allure.step('Test the dsaparam, gendsa and dsa shell commands'):
            target = self.t1
            name = 'dsa_cmds'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'run on target {target.board}')

            try:
                target.send("dsaparam 1024")
                target.expect("-----BEGIN DSA PARAMETERS-----")
                target.expect("-----END DSA PARAMETERS-----")
                target.expect(self.vxprompt)

                target.send("dsaparam 2048")
                target.expect("-----BEGIN DSA PARAMETERS-----")
                target.expect("-----END DSA PARAMETERS-----")
                target.expect(self.vxprompt)

                target.sendAndExpect('cd /ram', self.vxprompt)  # xiaozhan, add
                target.sendAndExpect("dsaparam -out dsaparam.pem 1024", self.vxprompt)

                target.send("dsaparam -in dsaparam.pem -text")
                target.expect("[pP]:")
                target.expect("[qQ]:")
                target.expect("[gG]:")
                target.expect("-----BEGIN DSA PARAMETERS-----")
                target.expect("-----END DSA PARAMETERS-----")
                target.expect(self.vxprompt)

                target.send("gendsa dsaparam.pem")
                target.expect(["-----BEGIN DSA PRIVATE KEY-----", "-----BEGIN PRIVATE KEY-----"])
                target.expect(["-----END DSA PRIVATE KEY-----", "-----END PRIVATE KEY-----"])
                target.expect(self.vxprompt)

                target.send("gendsa -out dsa_key.pem -des3 dsaparam.pem")
                target.expect("Enter PEM pass phrase:")
                target.send("Mickey")
                target.expect("Verifying - Enter PEM pass phrase:")
                target.send("Mickey")
                target.expect(self.vxprompt)

                target.send("cat dsa_key.pem")
                i = target.expect(["-----BEGIN DSA PRIVATE KEY-----", "-----BEGIN PRIVATE KEY-----",
                                   "-----BEGIN ENCRYPTED PRIVATE KEY-----"])
                if i != 2:
                    target.expect("DEK-Info: DES-EDE3-CBC")

                target.expect(["-----END DSA PRIVATE KEY-----",
                               "-----END ENCRYPTED PRIVATE KEY-----"])
                target.expect(self.vxprompt)

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
                target.expect(self.vxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_dh_cmds(self, version):
        with allure.step('Test the dhparam shell command'):
            target = self.t1
            name = 'dh_cmds'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'run on target {target.board}')

            try:
                target.send("dhparam 1024")
                target.expect("Generating DH parameters, 1024 bit long safe prime")
                target.expect("-----BEGIN DH PARAMETERS-----")
                target.expect("-----END DH PARAMETERS-----")
                target.expect(self.vxprompt)

                target.send("dhparam 2048")
                target.expect("Generating DH parameters, 2048 bit long safe prime")
                target.expect("-----BEGIN DH PARAMETERS-----",
                              timeout=120)  # xiaozhan, this needs a long time more than 20 seconds
                target.expect("-----END DH PARAMETERS-----", timeout=120)
                target.expect(self.vxprompt)

                target.sendAndExpect('cd /ram', self.vxprompt)
                target.send("dhparam -out dhparam.pem 1024")
                target.expect("Generating DH parameters, 1024 bit long safe prime")
                target.expect(self.vxprompt)
                target.send("dhparam -in dhparam.pem -text")
                # remove below two lines, xiaozhan
                # target.expect(["Diffie-Hellman-Parameters: (1024 bit)",
                #                "DH Parameters: (1024 bit)"], timeout=90)   # xiaozhan, add timeout=40
                target.expect("P:")
                target.expect("G:")
                target.expect("-----BEGIN DH PARAMETERS-----")
                target.expect("-----END DH PARAMETERS-----")
                target.expect(self.vxprompt)
                target.sendAndExpect("rm dhparam.pem", self.vxprompt)
            except:
                ret = 'FAIL'
            else:
                ret = 'PASS'
            finally:
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    @pytest.mark.skip('need to debug')
    def test_crypto_speed_cmd(self, version):
        with allure.step('Test the speed shell commands'):
            target = self.t1
            name = 'speed_cmd'
            case_name = self.module + '.' + name + '-' + version

            log.info(f'run on target {target.board}')

            ret = target.sendAndReturnAll('speed', self.vxprompt, timeout=620)[
                  :-1]  # xiaozhan, it needs 600 seconds to finish this case, failed on qemu
            res = 'Doing'
            record_result(self.result, res, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_pkey_import(self, version):
        with allure.step('Verify that public key pairs can be imported into the key database'):
            target = self.t1
            name = 'pkey_import'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'run on target {target.board}')

            try:
                target.send("keydb import key kalle /romfs/rsa_1024.pem")  # xiaozhan, change to /romfs
                i = target.expect([self.vxprompt,
                                   "ipcom_shell : Unknown command: 'keydb'",
                                   "Cmd: 'keydb' not found"])
                if i != 0:  # xiaozhan, modify to new framework
                    log.error('Failed to import key kalle')
                    assert False

                target.send("keydb list key")
                target.expect("kalle")
                target.expect(self.vxprompt)  # xiaozhan, add

                target.send("keydb import key kalle /romfs/dsa_1024.pem")
                target.expect("Failed: already installed")
                target.expect(self.vxprompt)

                target.sendAndExpect("keydb import key nisse /romfs/dsa_1024.pem", self.vxprompt)
                target.send("keydb list key")
                target.expect("nisse")
                target.expect(self.vxprompt)

                target.sendAndExpect("keydb delete key kalle", self.vxprompt)
                ret = target.sendAndReturnAll("keydb list key", self.vxprompt)  # xiaozhan, return a list
                if 'kalle' in ret:
                    log.error('Failed to delete key_id kalle')
                    assert False

                target.sendAndExpect("keydb delete key nisse", self.vxprompt)
                ret = target.sendAndReturnAll("keydb list key", self.vxprompt)  # xiaozhan, return a list
                if 'nisse' in ret:
                    log.error('Failed to delete key_id nisse')
                    assert False
            except:
                ret = 'FAIL'
                record_result_expect(self.result, ret, case_name)
            else:
                ret = 'PASS'
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_pkey_find(self, version):
        with allure.step('Verify that a key can be found matching an X509 certificate'):
            target = self.t1
            name = 'pkey_find'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'run on target {target.board}')

            try:
                # Verify that no key is found when the key of the cert is not installed
                target.send("keydb find /romfs/rsa_1024_cert.pem")  # xiaozhan. modify
                i = target.expect(["Key matching certificate found",
                                   "No matching key found.",
                                   "ipcom_shell : Unknown command: 'keydb'",
                                   "Cmd: 'keydb' not found"])
                if i == 0 or i == 2 or i == 3:
                    log.error('Matching key found, when no key should be found')
                    assert False
                target.expect(self.vxprompt)
                # Verify that a key is found when the key of the cert is installed
                target.sendAndExpect("keydb import key rsa_1024 /romfs/rsa_1024.pem",
                                     self.vxprompt)  # xiaozhan, change to /romfs
                target.send("keydb find /romfs/rsa_1024_cert.pem")
                i = target.expect(["Key matching certificate found. key_id: rsa_1024",
                                   "No matching key found."])
                if i == 1:
                    log.error('Matching key not found for cert rsa_1024')
                    assert False
                target.expect(self.vxprompt)

                # Install a DSA key and verify that the correct key is found for
                # RSA and DSA certs, respectively
                target.sendAndExpect("keydb import key dsa_1024 /romfs/dsa_1024.pem",
                                     self.vxprompt)  # xiaozhan, change to /romfs
                target.send("keydb find /romfs/dsa_1024_cert.pem")
                i = target.expect(["Key matching certificate found. key_id: dsa_1024",
                                   "No matching key found."])
                if i == 1:  # xiaozhan, add
                    log.error('Matching key not found for cert dsa_1024')
                    assert False
                target.expect(self.vxprompt)

                target.send("keydb find /romfs/rsa_1024_cert.pem")
                i = target.expect(["Key matching certificate found. key_id: rsa_1024",
                                   "No matching key found."])
                if i == 1:
                    log.error('Matching key not found for cert rsa_1024')
                    assert False
                target.expect(self.vxprompt)

                # Remove rsa_1024 key, verify that a key for dsa_1024_cert is still found
                target.sendAndExpect("keydb delete key rsa_1024", self.vxprompt)
                target.send("keydb find /romfs/dsa_1024_cert.pem")
                i = target.expect(["Key matching certificate found. key_id: dsa_1024",
                                   "No matching key found."])
                if i == 1:
                    log.error('Matching key not found for cert dsa_1024')
                    assert False
                # Cleanup
                target.sendAndExpect("keydb delete key dsa_1024", self.vxprompt)
            except:
                ret = 'FAIL'
                record_result_expect(self.result, ret, case_name)
            else:
                ret = 'PASS'
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_pkey_print(self, version):
        with allure.step('Verify that public keys can be printed of key pairs stored in the key database'):
            target = self.t1
            name = 'pkey_print'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'run on target {target.board}')

            try:
                target.send("keydb import key rsa_1024 /romfs/rsa_1024.pem")  # xiaozhan, modify to /romfs
                i = target.expect([self.vxprompt,
                                   "ipcom_shell : Unknown command: 'keydb'",
                                   "Cmd: 'keydb' not found"])
                if i != 0:
                    log.error('Failed to import key rsa_1024')
                    assert False

                target.sendAndExpect("keydb import key dsa_1024 /romfs/dsa_1024.pem", self.vxprompt)

                target.send("keydb print rsa_1024")
                # target.expect("Public-Key: (1024 bit)")
                target.expect("Public-Key:")
                target.expect(["Modulus:", "Modulus (1024 bit):"])
                target.expect("Exponent:")
                target.expect(self.vxprompt)

                target.send("keydb print dsa_1024")
                target.expect("Public-Key:")
                target.expect("pub:")
                target.expect("P:")
                target.expect("Q:")
                target.expect("G:")
                target.expect(self.vxprompt)
                # Cleanup
                target.sendAndExpect("keydb delete key dsa_1024", self.vxprompt)
                target.sendAndExpect("keydb delete key rsa_1024", self.vxprompt)
            except:
                ret = 'FAIL'
                record_result_expect(self.result, ret, case_name)
            else:
                ret = 'PASS'
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_buf_import_delete(self, version):
        with allure.step(
                'Verify that pre-shared keys or buffers can be imported into, and deleted from the key database'):
            target = self.t1
            name = 'buf_import_delete'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'run on target {target.board}')

            try:
                target.send("keydb")
                i = target.expect([self.vxprompt,
                                   "ipcom_shell : Unknown command: 'keydb'",
                                   "Cmd: 'keydb' not found"])
                if i != 0:
                    log.error('failed for keydb command')
                    assert False

                # Normal, successful case
                import_buf(target, "kalle", "kallekalle", self.vxprompt)
                verify_buf_exists(target, "kalle", self.vxprompt)

                # Normal, successful case, add 2nd key
                import_buf(target, "nisse", "nissenisse", self.vxprompt)
                verify_buf_exists(target, "nisse", self.vxprompt)

                # Should fail, already installed
                target.send("keydb import buf kalle")
                target.expect("Enter key:")
                target.send("kallekalle")
                target.expect("Re-type key:")
                target.send("kallekalle")
                target.expect("Failed: already installed")
                target.expect(self.vxprompt)

                # Should fail, key mismatch
                target.send("keydb import buf kalle")
                target.expect("Enter key:")
                target.send("kalle")
                target.expect("Re-type key:")
                target.send("ellak")
                target.expect("Failed. Entered keys do not match")
                target.expect(self.vxprompt)

                # Verify that a key can be deleted
                target.sendAndExpect("keydb delete buf kalle", self.vxprompt)
                time.sleep(1)
                verify_buf_does_not_exist(target, "kalle", self.vxprompt)

                # Verify that key be added, after it's been deleted
                import_buf(target, "kalle", "kallekalle", self.vxprompt)
                verify_buf_exists(target, "kalle", self.vxprompt)

                # Delete the key once more
                target.sendAndExpect("keydb delete buf kalle", self.vxprompt)
                verify_buf_does_not_exist(target, "kalle", self.vxprompt)

                # xiaozhan  add
                target.sendAndExpect("keydb delete buf nisse", self.vxprompt)
                verify_buf_does_not_exist(target, "nisse", self.vxprompt)
            except:
                ret = 'FAIL'
                record_result_expect(self.result, ret, case_name)
            else:
                ret = 'PASS'
                record_result_expect(self.result, ret, case_name)

    @pytest.mark.parametrize('version', ['IPv4'])
    def test_crypto_buf_verify(self, version):
        with allure.step('Verify that the value of a buffer key can be verified'):
            target = self.t1
            name = 'buf_verify'
            case_name = self.module + '.' + name + '-' + version
            log.info(f'run on target {target.board}')

            try:
                # Verify that keydb command is available
                target.send("keydb")
                i = target.expect([self.vxprompt,
                                   "ipcom_shell : Unknown command: 'keydb'",
                                   "Cmd: 'keydb' not found"])
                if i != 0:
                    log.error('Failed to run keydb command')
                    assert False

                # Normal case
                import_buf(target, "kalle", "kalle", self.vxprompt)
                verify_buf_value(target, "kalle", "kalle", self.vxprompt)

                # Minimal buffer length
                import_buf(target, "1", "1", self.vxprompt)
                verify_buf_value(target, "1", "1", self.vxprompt)

                # Maximum buffer length, 128
                max_pw_str = "01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567"
                import_buf(target, "max_buf", max_pw_str, self.vxprompt)
                verify_buf_value(target, "max_buf", max_pw_str, self.vxprompt)

                # Exceed Maximum buffer length, 128 + 1
                exceed_buf = max_pw_str + "X"
                target.send("keydb import buf exceeded_buf")
                target.expect("Enter key:")
                target.send(exceed_buf)
                target.expect("Re-type key:")
                target.send(exceed_buf)
                target.expect("Failed: invalid argument")
                target.expect(self.vxprompt)
                verify_buf_does_not_exist(target, "exceeded_buf", self.vxprompt)

                # 1 byte padding
                import_buf(target, "kalle15", "012345678901234", self.vxprompt)
                verify_buf_value(target, "kalle15", "012345678901234", self.vxprompt)

                # 16 byte padding
                import_buf(target, "kalle16", "0123456789012345", self.vxprompt)
                verify_buf_value(target, "kalle16", "0123456789012345", self.vxprompt)

                # 15 byte padding
                import_buf(target, "kalle17", "01234567890123456", self.vxprompt)
                verify_buf_value(target, "kalle17", "01234567890123456", self.vxprompt)

                # This particular key is used by ike in tests
                import_buf(target, "ike", "this_should_be_secret", self.vxprompt)
                verify_buf_value(target, "ike", "this_should_be_secret", self.vxprompt)

                # clean environment
                target.sendAndExpect("keydb delete buf kalle", self.vxprompt)
                target.sendAndExpect("keydb delete buf max_buf", self.vxprompt)
                target.sendAndExpect("keydb delete buf 1", self.vxprompt)
                target.sendAndExpect("keydb delete buf kalle15", self.vxprompt)
                target.sendAndExpect("keydb delete buf kalle16", self.vxprompt)
                target.sendAndExpect("keydb delete buf kalle17", self.vxprompt)
                target.sendAndExpect("keydb delete buf ike", self.vxprompt)
            except:
                ret = 'FAIL'
                record_result_expect(self.result, ret, case_name)
            else:
                ret = 'PASS'
                record_result_expect(self.result, ret, case_name)

    def teardown_class(self):
        # clean up vxworks
        for t in self.vx_targets:
            t.cleanup()
            t.logFile.close()
        # process self.result ----store result,upload to Database or sth like that
        for i in self.result:
            if i[1] == 'PASS':
                self.pass_num += 1
            else:
                self.fail_num += 1
        log.info('----test result statistics for crypto----')
        log.info(self.result)
        log.info(f'total:{len(self.result)}, passed:{self.pass_num}, failed:{self.fail_num}')


if __name__ == "__main__":
    pass
