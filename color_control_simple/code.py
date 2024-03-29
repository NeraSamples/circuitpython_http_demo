# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT
"""Use a color picker to change the LEDs"""
import board
import json
import socketpool
import wifi
import os

from adafruit_httpserver import Server, Response

PORT = 8000
ROOT = "/www"
NUM_PIXELS = 1

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

pixels.fill(0)

############################################################################
# server routes and app logic
############################################################################

# set the current color from the web page
@server.route("/receive", methods="POST")
def base(request):
    # receive values in the body
    body = json.loads(request.body)
    ########################################################
    # extract the color field
    color = body.get("color", None)
    if color:
        print(f"{color=}")
        try:
            pixels.fill(int(color, 16))
        except ValueError:
            print("Color invalid")
    ########################################################
    # respond ok
    return Response(request, "ok")

############################################################################
# start and loop
############################################################################

IP_ADDRESS = wifi.radio.ipv4_address or wifi.radio.ipv4_address_ap
server.serve_forever(host=str(IP_ADDRESS), port=PORT)
