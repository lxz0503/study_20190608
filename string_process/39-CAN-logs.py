#!/usr/bin/env python3
# encoding=utf-8
"""
@Time    : 2026/10/28 21:57
@Author  : sam
@File    : 39-CAN-logs.py
@Description: CAN logs statistics
"""


class CANLogAnalyzer(object):
    def __init__(self, logs):
        self.logs = logs

    def aggregate_traffic(self):
        can_summary = {}   # use dictionary for statistics
        for log in self.logs:
            if not log.strip():  # if log is empty string
                continue

            parts = log.split()
            if len(parts) != 3:  # length must be 3
                continue

            raw_timestamp, can_id, payload = parts  # unpack list
            time_stamp = int(raw_timestamp)  # change to int to compare

            if can_id not in can_summary:  # can_id occurs for the first time
                can_summary[can_id] = {
                    'count': 1,
                    'last_timestamp': time_stamp,
                    'payload': payload
                }
            else:
                can_summary[can_id]['count'] += 1
                if time_stamp > can_summary[can_id]['last_timestamp']:
                    can_summary[can_id]['last_timestamp'] = time_stamp
                    can_summary[can_id]['payload'] = payload

        for can_id in can_summary:
            del can_summary[can_id]['last_timestamp']

        return can_summary


if __name__ == '__main__':
    logs = [
        '13456 0x1A0 00FF12AB',
        '23456 0x1AB 00BB34HH',
        '27456 0x2AB 00AB34HH',
        '22456 0x3AB 00CB34HH'
    ]
    run = CANLogAnalyzer(logs)
    print(run.aggregate_traffic())
