from __future__ import print_function

import socket
import uuid

from .io_handler import KarotzIOHandler
from .Voos_message_pb2 import InteractiveMode, OK, Tts, VoosMsg


class KarotzClient(object):

    def __init__(self, host, button_callback=None, rfid_callback=None, timeout=None):
        '''
        Create a Karotz client instance.
        :param host: the color in hexadecimal RGB notation (i.e. 'c01oA0'),
            'str'
        :param button_callback: (optional), a callback function
            which gets invoked when the button is pressed
            and must have one argument: the button callback type_
            which an be one of the following values:
            'SIMPLE', 'DOUBLE', 'TRIPLE', 'MULTIPLE', 'LONG_START', 'LONG_STOP'
        :param rfid_callback: (optional), a callback function
            which gets invoked when a RFID tag is hold in front of the device
            and must have two arguments: the rfid identifier (str) and the color (str)
        '''
        self._button_callback = button_callback
        self._rfid_callback = rfid_callback
        self._timeout = timeout
        self._interactive_id = None

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(1)
        self._socket.connect((host, 9123))

        self._io_handler = KarotzIOHandler(self._socket, event_callback=self._event_callback)
        self._io_handler.start()

    def _event_callback(self, msg):
        if msg.buttonCallback.IsInitialized():
            if self._button_callback:
                type_descriptor = msg.buttonCallback.DESCRIPTOR.enum_types_by_name['Type']
                type_ = type_descriptor.values_by_number[msg.buttonCallback.type].name
                self._button_callback(type_)
        elif msg.rfidCallback.IsInitialized():
            if self._rfid_callback:
                color_descriptor = msg.rfidCallback.DESCRIPTOR.enum_types_by_name['Col']
                color = color_descriptor.values_by_number[msg.rfidCallback.color].name
                self._rfid_callback(msg.rfidCallback.id, color)

    def start_interactive_mode(self):
        '''
        Start the interactive mode.

        This must be called before any other method on this instance.

        :returns: True if the interactive was started successful, else False
        '''
        print('start_interactive_mode()')
        interactive_id = self._generate_uuid()
        msg = VoosMsg()
        msg.id = self._generate_uuid()
        msg.interactiveMode.action = InteractiveMode.START
        msg.interactiveMode.interactiveId = interactive_id
        response = self._io_handler.send_synchronous(msg, self._timeout)
        #print('  response:', self._io_handler._msg_to_print(response))
        if response and response.response.code == OK:
            self._interactive_id = interactive_id
            #print('start_interactive_mode() done with interactive id:', self._interactive_id)
            return True
        else:
            #print('start_interactive_mode() failed')
            return False

    def set_led(self, color, fade_time=None, pulse_time=None):
        '''
        Set the color of the LED.
        :param color: the color in hexadecimal RGB notation (i.e. 'c01oA0'),
            'str'
        :param fade_time: (optional), if set the duration to fade from the
            current color to the passes color in seconds, ``float``
        :param pulse_time: (optional), if set the duration to repeat fading
            from the color to the passes color, from the passed color back to
            the current color and so on in seconds, if set to -1 the pulse
            will continue unlimited, ``float``
        :returns: True if setting the LED color was successful, else False
        '''
        print('set_led(%s, fade_time=%s, pulse_time=%s)' % (color, fade_time, pulse_time))
        msg = VoosMsg()
        msg.id = self._generate_uuid()
        msg.interactiveId = self._interactive_id
        if fade_time is None and pulse_time is None:
            msg.led.light.color = color
        else:
            if fade_time is None:
                fade_time = 0
            if pulse_time is None:
                msg.led.fade.color = color
                msg.led.fade.period = int(fade_time * 1000)
            else:
                msg.led.pulse.color = color
                msg.led.pulse.period = int(fade_time * 1000)
                msg.led.pulse.pulse = int(pulse_time * 1000)
        response = self._io_handler.send_synchronous(msg, self._timeout)
        return response and response.response.code == OK

    def move_ears(self, left_ear, right_ear, relative=False):
        '''
        Move the ears.

        The position is specified in radians, where zero is defined
        when the ear are nearly straight up (a little bit tilted to the front)
        and the rotation direction is forward.

        :param left_ear: the position of the left ear, ``float``
        :param right_ear: the position of the right ear, ``float``
        :param relative: (optional), the flag if the movement should be relative
            instead of absolute, ``bool``
        :returns: True if moving the ears was triggered successful, else False
        '''
        print('move_ears(%d, %d) %s' % (left_ear, right_ear, 'relative' if relative else 'absolute'))
        msg = VoosMsg()
        msg.id = self._generate_uuid()
        msg.interactiveId = self._interactive_id
        msg.ears.relative = relative
        msg.ears.left = left_ear
        msg.ears.right = right_ear
        response = self._io_handler.send_synchronous(msg, self._timeout)
        return response and response.response.code == OK

    def reset_ears(self):
        '''
        Reset the ears.

        Seems to be the same as move_ears(0, 0, relative=False).

        :returns: True if resetting the ears was triggered successful, else False
        '''
        print('reset_ears()')
        msg = VoosMsg()
        msg.id = self._generate_uuid()
        msg.interactiveId = self._interactive_id
        msg.ears.reset = True
        response = self._io_handler.send_synchronous(msg, self._timeout)
        return response and response.response.code == OK

    def text_to_speech(self, text, lang):
        '''
        Synthesize speech.

        :param text: the text to speech, ``str``
        :param lang: the language of of the text,
            currently supported languages are:
            'fr-FR', 'en-GB', 'en-US', 'de-DE' and 'es-ES', ``str``
        :returns: True if the synthesis was triggered successful, else False
        '''
        print('text_to_speech()')
        langs = ['fr-FR', 'en-GB', 'en-US', 'de-DE', 'es-ES']
        if lang not in langs:
            raise RuntimeError('Unsupported langs')
        msg = VoosMsg()
        msg.id = self._generate_uuid()
        msg.interactiveId = self._interactive_id
        msg.tts.action = Tts.START
        msg.tts.lang = lang
        msg.tts.text = text
        response = self._io_handler.send_synchronous(msg, self._timeout)
        return response and response.response.code == OK

    def _generate_uuid(self):
        return str(uuid.uuid4())
