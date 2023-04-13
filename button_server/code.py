# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT
"""Press a button on the web page to cycle the colors"""
import board
import mdns
import microcontroller
import socketpool
import time
import wifi
import os

from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.mime_type import MIMEType

PORT = 8000
ROOT = "/www"

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
# some output for demo (neopixel)
############################################################################

from rainbowio import colorwheel

if hasattr(board, "NEOPIXEL"):
    import neopixel
    pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
elif hasattr(board, "DOTSTAR_CLOCK"):
    import adafruit_dotstar
    pixels = adafruit_dotstar.DotStar(board.DOTSTAR_CLOCK, board.DOTSTAR_DATA, 1)
elif hasattr(board, "LED"):
    # must work on pico W
    import digitalio
    pixels = None
    led = digitalio.DigitalInOut(board.LED)
    led.switch_to_output(False)

colors = [colorwheel(24 * x) for x in range(10)]
color_num = 0

if pixels:
    def next_color(color=None):
        """Cycle between colors or set the current color index"""
        global color_num
        if color is not None:
            color_num = color
        else:
            color_num = (color_num + 1) % len(colors)
        pixels.fill(colors[color_num])

    pixels.fill(colors[0])
else:
    def next_color(color=None):
        """For picow, sets the blink speed"""
        global color_num
        if color is not None:
            color_num = color
        else:
            color_num = (color_num + 1) % len(colors)

############################################################################
# server routes and app logic
############################################################################

@server.route("/button")
def base(request):
    # read the button parameter, default to "A" if absent
    button = request.query_params.get("button", "A")
    # trigger example function
    if button == "B":
        next_color(0)
    else:
        next_color()
    # respond ok to the page
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send("ok")

############################################################################
# start and loop
############################################################################

IP_ADDRESS = wifi.radio.ipv4_address or wifi.radio.ipv4_address_ap
server.start(host=str(IP_ADDRESS), port=PORT, root_path=ROOT)

brights = (
    [x**2 / 2500 for x in range(50)]
    + [x**2 / 2500 for x in reversed(range(50))]
)

while True:
    for pb in brights:
        server.poll()
        if pixels:
            pixels.brightness = pb
        else:
            bright = ((10 * pb * (color_num + 1)) % 10)
            led.value = bright > 5
        time.sleep(0.02)
