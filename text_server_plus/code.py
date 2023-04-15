# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT
"""Show text from the web page on a display"""
import board
import json
import mdns
import microcontroller
import socketpool
import time
import traceback
import wifi
import os

from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.status import CommonHTTPStatus

PORT = 8000
ROOT = "/www"

############################################################################
# Display
############################################################################

import displayio
SCALE = 1

if hasattr(board, "DISPLAY"):
    display = board.DISPLAY
else:
    # setup an external display in the display variable.
    raise OSError("Please setup an external display for this demo")

display.auto_refresh = False

############################################################################
# Interface on the display
############################################################################

import terminalio
from adafruit_display_text.label import Label
from adafruit_display_text import wrap_text_to_lines

FONT = terminalio.FONT

box = FONT.get_bounding_box()

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

splash = displayio.Group()

text_area = Label(
    FONT,
    scale=SCALE,
    text="Ready to\nreceive.",
    color=0xFFFF00,
    anchored_position=(display.width // 2, 2),
    anchor_point=(0.5, 0),
)

splash.append(text_area)
display.show(splash)
display.refresh()

def wrap_the_text(text):
    LINE_WRAP = display.width // (box[0] * text_area.scale)
    return wrap_text_to_lines(text, LINE_WRAP)

############################################################################
# wifi
############################################################################

wifi.radio.connect(
    os.getenv("CIRCUITPY_WIFI_SSID"),
    os.getenv("CIRCUITPY_WIFI_PASSWORD")
)
print(f"Listening on http://{wifi.radio.ipv4_address}:{PORT}")

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)

############################################################################
# server routes and app logic
############################################################################

ERROR400 = CommonHTTPStatus.BAD_REQUEST_400

@server.route("/receive", method="POST")
def base(request):
    try:
        # receive a text in the body
        body = json.loads(request.body)
        ########################################################
        # extract the size field
        size = body.get("size", None)
        # change the scale
        if size:
            try:
                text_area.scale = size
            except ValueError:
                print("Size invalid")
        ########################################################
        # extract the text field
        the_text = body.get("text", "")
        # prepare the message for the screen
        message = "\n".join(wrap_the_text(the_text))
        # show the message
        text_area.text = message
        print(f"Received:", message)
        ########################################################
        # refresh the display after all the changes
        display.refresh()
        # respond ok
        with HTTPResponse(request) as response:
            response.send("ok")
    except (ValueError, AttributeError) as err:
        # show the error if something went wrong
        traceback.print_exception(err)
        with HTTPResponse(request, status=ERROR400) as response:
            response.send("error")

############################################################################
# start and loop
############################################################################

IP_ADDRESS = wifi.radio.ipv4_address or wifi.radio.ipv4_address_ap
server.start(host=str(IP_ADDRESS), port=PORT, root_path=ROOT)

while True:
    server.poll()
    time.sleep(0.01)
