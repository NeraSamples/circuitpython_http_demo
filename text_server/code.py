# SPDX-FileCopyrightText: 2023 Neradoc
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

MDNS_NAME = "text-setter"
PORT = 8080
ROOT = "/www"

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

@server.route("/text")
def base(request):
    # receive a text
    the_text = request.query_params.get("the_text", "")
    print(f"Received: {the_text}")
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send("ok")

############################################################################
# start and loop
############################################################################

IP_ADDRESS = wifi.radio.ipv4_address or wifi.radio.ipv4_address_ap
server.start(host=str(IP_ADDRESS), port=PORT, root_path=ROOT)

while True:
    server.poll()
    time.sleep(0.01)
