A Python client for Karotz
==========================

The `Karotz <http://en.wikipedia.org/wiki/Nabaztag>`_ (formerly named Nabaztag) is a programmable device in the shape of a white rabbit.

What is different from other clients?
-------------------------------------

Instead of using the `Rest API <http://dev.karotz.com/api/>`_ which depends on the servers provided by the company selling the Karotz this Python client communicates with the Karotz directly via TCP.
Therefore the Karotz can be controlled without any Internet connectivity (i.e. inside a local network) and without relying on the availability of any external servers.

How does it work?
-----------------

The interface of the Karotz over TCP is only `sparsely <http://wiki.karotz.com/index.php/TCP>`_ documented.
Basically it uses messages exchanged over a TCP connection on port 9123.
The message format is specified in a `ProtoBuf <http://code.google.com/p/protobuf/>`_ file (see `src/karotz/Voos-message.proto <http://wiki.karotz.com/index.php/Voos-message.proto>`_).
Each of the messages is prefixed with a 4 byte long header containing the byte length of the message.

What commands are supported?
----------------------------

 * set the LED color and fade / pulse over time
 * rotate the ears
 * text-to-speech
 * getting notified on button events
 * getting notified for detected RFID tags

More commands should be easy to integrate.

How to run the demo?
--------------------

Call the demo script with the IP address of the Karotz::

  ./scripts/karotz_demo.py 192.168.1.23  # replace the example IP

The Karotz will perform a sequence of actions to show all supported commands.
While the demo runs events for pushing the button or holding RFID tags (called Flatnanoz) in front of the Karotz are indicated on the console.
