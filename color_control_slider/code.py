# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT
"""Use a color picker to change the LEDs"""
import board
import json
import socketpool
import time
import wifi
import os

from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.status import CommonHTTPStatus

PORT = 8000
ROOT = "/www"
NUM_PIXELS = 1

# retrieve color from NVM: see library lights
current_color = 0x0D010D
current_brightness = 1.0

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
server = HTTPServer(pool, root_path=ROOT)

############################################################################
# some output for demo (neopixel)
############################################################################

from rainbowio import colorwheel

# change this code with your own color leds setup
if hasattr(board, "NEOPIXEL"):
    import neopixel
    pixels = neopixel.NeoPixel(board.NEOPIXEL, NUM_PIXELS)
elif hasattr(board, "DOTSTAR_CLOCK"):
    import adafruit_dotstar
    pixels = adafruit_dotstar.DotStar(board.DOTSTAR_CLOCK, board.DOTSTAR_DATA, NUM_PIXELS)
else:
    raise RuntimeError("This demo requires some RGB pixels connected")

pixels.fill(current_color)

############################################################################
# server routes and app logic
############################################################################

ERROR400 = CommonHTTPStatus.BAD_REQUEST_400

# set the current color from the web page
@server.route("/receive", method="POST")
def base(request):
    global current_color
    try:
        # receive values in the body
        body = json.loads(request.body)
        ########################################################
        # extract the color field
        color = body.get("color", None)
        if color:
            print(f"{color=}")
            try:
                pixels.fill(int(color, 16))
                current_color = int(color, 16)
            except ValueError:
                print("Color invalid")
        ########################################################
        # extract the brightness field
        brightness = body.get("brightness", None)
        if brightness is not None:
            print(f"{brightness=}%")
            try:
                pixels.brightness = brightness / 100
                current_brightness = brightness / 100
            except ValueError:
                print("Color invalid")
        ########################################################
        # respond ok
        with HTTPResponse(request) as response:
            response.send("ok")
    except (ValueError, AttributeError) as err:
        # show the error if something went wrong
        traceback.print_exception(err)
        with HTTPResponse(request, status=ERROR400) as response:
            response.send("error")

# read the current color from the web page
@server.route("/getcolor")
def base(request):
    with HTTPResponse(request, content_type=MIMEType.TYPE_JSON) as response:
        brightness = min(100, max(0, round(100 * current_brightness)))
        out_data = json.dumps({
            "brightness": brightness,
            "color": f"#{current_color:06X}",
        })
        response.send(out_data)

############################################################################
# start and loop
############################################################################

IP_ADDRESS = wifi.radio.ipv4_address or wifi.radio.ipv4_address_ap
server.serve_forever(host=str(IP_ADDRESS), port=PORT)
