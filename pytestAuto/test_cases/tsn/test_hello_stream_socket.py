#!/usr/bin/env python3
# encoding=utf-8
# @Author = xiaozhan Li
# @Time = 10/31/2022 12:49 PM
# @Email = lxz_20081025@163.com
# @Name = test_hello_stream_socket.py
import allure
import pytest
import pandas as pd
import sys

from utils.vlmTarget import boot_target_16278, boot_target_18290


class TestSuiteStreamSocket(object):
    def setup_class(self):
        self.tgt1 = boot_target_16278()
        self.tgt2 = boot_target_18290()

        with allure.step('Run ipAttach and ifconfig on IA target 16278'):
            self.tgt1.sendAndExpect('ipAttach 5,"gei"', 'value = 0 = 0x0', timeout=30)
            self.tgt1.sendAndExpect('ifconfig "gei5 10.10.10.3/24 up"', 'value = 0 = 0x0', timeout=30)

        with allure.step('Run ipAttach and ifconfig on IA target 18290'):
            self.tgt2.sendAndExpect('ipAttach 5,"gei"', 'value = 0 = 0x0', timeout=30)
            self.tgt2.sendAndExpect('ifconfig "gei5 10.10.10.4/24 up"', 'value = 0 = 0x0', timeout=30)

        with allure.step('Check connection between 16278 and 18290'):
            rets = self.tgt2.sendAndReturnAll('ping "10.10.10.3"', 'value = 0 = 0x0', timeout=30)
            res = '\n'.join(rets)

        with allure.step('Assert interface and connection on target 18290'):
            assert '0% packet loss' in res

    def teardown_class(self):
        with allure.step('close telnet session'):
            self.tgt1.connClose()
            self.tgt2.connClose()

    @allure.title('hello stream socket---tsn')
    def test_hello_stream_socket(self):
        with allure.step('Set tsn sender on target 16278--sender'):
            self.tgt1.sendAndExpect('ptpdAdd "gei5",4,2,0,0,200,0,0', 'value = 0 = 0x0', timeout=60)
            self.tgt1.sendAndExpect('ptpdStart', 'value = 1 = 0x1', timeout=60)
            self.tgt1.sendAndExpect('demoStreamCommonInit "flow1", 6, "gei",5, 0,1000000, 100000, 3000,7, '
                               '"a0:36:9f:97:a0:13"', 'value = 0 = 0x0', timeout=60)
            self.tgt1.sendAndExpect('demoHelloStreamSocketTx "flow1","10.10.10.4",5001,0', 'bind ok',
                               timeout=60)

        with allure.step('Set tsn receiver on target 18290--receiver'):
            self.tgt2.sendAndExpect('ptpdAdd "gei5",4,2,0,0,200,0,0', 'value = 0 = 0x0', timeout=30)
            self.tgt2.sendAndExpect('ptpdStart', 'value = 1 = 0x1', timeout=30)
            self.tgt2.sendAndExpect('demoStreamCommonInit "flow1", 6, "gei",5, 0,1000000, 100000, 3000,7, '
                               '"a0:36:9f:97:a0:13"', 'value = 0 = 0x0', timeout=30)
            rets = self.tgt2.sendAndReturnAllByTimeout('demoHelloStreamSocketRx "gei",5,"a0:36:9f:97:a0:13",5001', 120)

        with allure.step('Turn off the stream on 16278--sender'):
            self.tgt1.sendAndExpect('demoHelloStreamSocketTxStop', 'value = 0 = 0x0', timeout=30)
        with allure.step('Turn off the stream on 18290---receiver'):
            self.tgt2.sendAndExpect('demoHelloStreamSocketRxStop', 'value = 0 = 0x0', timeout=30)

        with allure.step('Use pandas to process data'):
            rets = [i.rstrip(' !\n') for i in rets]
            rets = rets[5:]
            print('rets\n', rets)
            df = pd.DataFrame(rets, columns=['value'])
            new_colnames = ['sequence', 'tx-time', 'rx-time', 'tx-rx-cost', 'tx-rx-jitter']
            df_new = df['value'].str.split(';', expand=True)
            df_new.columns = new_colnames
            df_new['tx-rx-jitter'] = df_new['tx-rx-jitter'].apply(lambda x: x.split(':')[1]).apply(
                lambda x: x.split(' ')[0])
            df_new['tx-rx-jitter'] = df_new['tx-rx-jitter'].astype(int)
            print(df_new['tx-rx-jitter'].head(3))
            last_jitter = df_new['tx-rx-jitter'].tail(1).values[0]

        with allure.step(f'Assert last jitter {last_jitter} on target receiver--target 18290'):
            assert -200 < last_jitter < 200



