"""
Linux candump 标准格式（用 # 分隔）

这是最常见的开源格式，特征是 ID 和数据之间用一个 # 号连接，例如：
can0  12F#1122334455667788 （有时前面还带有时间戳 (1689243001.123) can0 12F#1122334455667788）

"""


def parse_line(log_line: str):
    log_line = log_line.strip()
    if not log_line:
        return None

    try:
        # 以 Linux candump 格式为例的安全写法
        parts = log_line.split()
        if not parts:
            return None

        can_packet = parts[-1]
        if '#' not in can_packet:
            return None  # 格式不对，没有#号就跳过

        can_id, payload = can_packet.split('#')
        return can_id, payload

    except (IndexError, ValueError) as e:
        # 记录错误行，但不崩溃
        print(f"解析失败的行: {log_line}，错误原因: {e}")
        return None


def parse_vector(log_line):
    log_line = log_line.strip()
    if not log_line:
        return None

    try:
        parts = log_line.split()
        if not parts:
            return None

        can_id = parts[3]
        payload_list = parts[5:]  # 拿到 ['11', '22', '33', '44', '55', '66', '77', '88']
        payload = "".join(payload_list)
        # print(f"CAN ID: {can_id}")  # 输出: 12F
        # print(f"Payload: {payload}")  # 输出: 1122334455667788
        return can_id, payload

    except (IndexError, ValueError) as e:
        # 记录错误行，但不崩溃
        print(f"解析失败的行: {log_line}，错误原因: {e}")
        return None


if __name__ == "__main__":
    ret = parse_line('can0  12F#1122334455667788')
    print(ret)

    ret = parse_vector('1 0.001 RX 12F 8 11 22 33 44')
    print(ret)
