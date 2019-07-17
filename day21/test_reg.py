import re
import os
def get_throughput(log):
    frame_data = []
    tcp_through_data = []
    udp_through_data = []
    pat = re.compile(r'iperf3.*-l\s(\d+)')
    with open(log, 'r') as f:
        for line in f:
            m = pat.search(line)
            if m is not None:
                frame_data.append(m.group(1))
            if re.search("receiver", line):
                # print(line.split()[-3])
                tcp_through_data.append(line.split()[-3])
            if re.search('\d+%', line):
                # print(line.split()[-6])
                udp_through_data.append(line.split()[-6])
        else:
            final_data = tcp_through_data + udp_through_data
            # print(final_data)
    return list(zip(frame_data, final_data))

log = r"F:\xiaozhan_git\study_20190608\day21\test_data.txt"
res = get_throughput(log)
print(res)     # [('64', '247'), ('1024', '1082'), ('1400', '6241')]