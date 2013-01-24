#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from karotz.client import KarotzClient


# three consecutive clicks will stop the interactive mode, so 'triple' and 'multiple' are not really useful
button_types = ['SIMPLE', 'DOUBLE', 'TRIPLE', 'MULTIPLE', 'LONG_START', 'LONG_STOP']


def button_callback(type_):
    if type_ in button_types:
        print('button:', type_)
    else:
        print('unknown button type:', type_, file=sys.stderr)


# register the Flatnanoz with their id and color
rfids = {
    'D0021A35038C355A': 'RED',  # 1
    'D0021A350392017D': 'BLUE',  # 2
    'D0021A3506198BA8': 'GREEN',  # 3
    'D0021A35038E2269': 'YELLOW',  # 4
    'D0021A3503943127': 'PINK',  # 5
    'D0021A35038D179E': 'BLACK'  # 6
}


def rfid_callback(id_, color):
    if id_ in rfids:
        if color == rfids[id_]:
            print('rfid:', id_, color)
        else:
            print('rfid:', id_, 'but color does not match: ', color, '!=', rfids[id_], file=sys.stderr)
    else:
        print('unknown rfid:', id_, color, file=sys.stderr)


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Demo client to communicate with a Karotz using a direct TCP connection (port 9123) instead of the Rest API.')
    parser.add_argument('host', help='The IP address of the Karotz (i.e. "192.168.1.23")')
    namespace = parser.parse_args(args)

    kc = KarotzClient(namespace.host, button_callback=button_callback, rfid_callback=rfid_callback, timeout=3)
    if not kc.start_interactive_mode():
        raise RuntimeError('starting interactive mode failed')

    if not kc.text_to_speech('Hello. I am a Karotz.', 'en-US'):
        raise RuntimeError('synthesizing speech failed')
    time.sleep(3)

    if not kc.set_led('ff0000'):
        raise RuntimeError('setting led failed')
    time.sleep(1)
    kc.set_led('00ff00')
    time.sleep(1)
    kc.set_led('0000ff')
    time.sleep(1)
    kc.set_led('ffff00', fade_time=1)
    time.sleep(2)
    kc.set_led('00ffff', fade_time=1)
    time.sleep(2)
    kc.set_led('ff00ff', fade_time=1)
    time.sleep(2)
    kc.set_led('000000', fade_time=1, pulse_time=4)
    time.sleep(4)
    kc.set_led('0000ff', fade_time=0.5, pulse_time=2)
    time.sleep(2)

    kc.reset_ears()
    time.sleep(5)
    kc.move_ears(2, 2)
    time.sleep(3)
    kc.move_ears(0, 0)
    time.sleep(3)
    kc.move_ears(2, 2)
    time.sleep(3)
    kc.move_ears(-2, -2, relative=True)
    time.sleep(3)
    kc.move_ears(-2, -2, relative=True)
    time.sleep(3)
    kc.move_ears(-2, -2, relative=True)
    time.sleep(3)
    kc.move_ears(0, 0)
    time.sleep(5)

    kc.text_to_speech('End of demo client.', 'de-DE')
    time.sleep(3)


if __name__ == '__main__':
    main()
