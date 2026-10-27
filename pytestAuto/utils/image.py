#!/usr/bin/env python3
# encoding=utf-8
import os
import sys


def image_type(target):
    if target == 'IA':
        if os.path.isfile('/folk/xli3/tsn_trial/IA_Image/vxWorks'):
            return target

    elif target == 'XL710':
        if os.path.isfile('/folk/xli3/40G_image/vxWorks'):
            return target

    elif target == 'ZCU102':
        if os.path.isfile('/folk/xli3/tsn_trial/ZCU102_Image/uVxWorks') and \
                os.path.isfile('/folk/xli3/tsn_trial/ZCU102_Image/xlnx-zcu102.dtb'):
            return target
    elif target == 'LS1028':
        if os.path.isfile('/folk/xli3/tsn_trial/LS1028_Image/uVxWorks') and \
                os.path.isfile('/folk/xli3/tsn_trial/LS1028_Image/LS1028.dtb'):
            return target
    else:
        print('target not supported')
        sys.exit(1)


if __name__ == "__main__":
    targets = ['IA', 'XL710', 'PPC', 'ZCU102', 'LS1028']
    for target in targets:
        image_type(target)
