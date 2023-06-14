# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT
"""Show text from the web page on a display"""
import board
import json
import socketpool
import time
import traceback
import wifi
import os

from adafruit_httpserver import Server, Response, MIMETypes

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

if not wifi.radio.connected:
    wifi.radio.connect(
        os.getenv("WIFI_SSID"),
        os.getenv("WIFI_PASSWORD")
    )
print(f"Listening on http://{wifi.radio.ipv4_address}:{PORT}")

pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, root_path=ROOT, debug=True)

############################################################################
# server routes and app logic
############################################################################

@server.route("/receive", methods="POST")
def base(request):
    # receive a text in the body
    body = json.loads(request.body)

    ########################################################
    # extract the size field
    size = body.get("size", None)
    # change the scale
    if size:
        try:
            text_area.scale = size
            print(f"Size: {size}")
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
    return Response(request, "ok")

############################################################################
# start and loop
############################################################################

IP_ADDRESS = wifi.radio.ipv4_address or wifi.radio.ipv4_address_ap
server.start(host=str(IP_ADDRESS), port=PORT)

while True:
    server.poll()
    # do something else
    time.sleep(0.01)
