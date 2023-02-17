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

MDNS_NAME = "text-setter"
PORT = 8080
ROOT = "/www"

# setup I2C display
I2C_ADDRESS = 0x3D
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64

SCALE = 1

############################################################################
# Display
############################################################################

import displayio

if hasattr(board, "DISPLAY"):
    display = board.DISPLAY
else:
    from adafruit_displayio_ssd1306 import SSD1306
    displayio.release_displays()
    try:
        i2c = board.I2C()
    except RuntimeError:
        i2c = board.STEMMA_I2C()

    display_bus = displayio.I2CDisplay(i2c, device_address=I2C_ADDRESS)
    display = SSD1306(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)

############################################################################
# Interface on the display
############################################################################

import terminalio
from adafruit_display_text.label import Label
from adafruit_display_text import wrap_text_to_lines

FONT = terminalio.FONT

box = FONT.get_bounding_box()
LINE_WRAP = display.width // (box[0] * SCALE)

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

############################################################################
# MDNS
############################################################################

mdnserv =  mdns.Server(wifi.radio)
mdnserv.hostname = MDNS_NAME
mdnserv.advertise_service(service_type="_http", protocol="_tcp", port=PORT)

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

@server.route("/text", method="POST")
def base(request):
    # receive a text in the body
    body = json.loads(request.body)
    try:
        the_text = body.get("the_text", "")
        message = "\n".join(wrap_text_to_lines(the_text, LINE_WRAP))
        text_area.text = message
        print(f"Received:", message)
        with HTTPResponse(request) as response:
            response.send("ok")
    except (ValueError, AttributeError) as err:
        traceback.print_exception(err, err, err.__traceback__)
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
