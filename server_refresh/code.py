# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT
"""
Show the state of buttons, as toggles.
Press once to add the button to the list, press again to remove.
The html retrieves the buttons state every 5 seconds.
"""
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

MDNS_NAME = "buttons-responder"
PORT = 8000
ROOT = "/www"

############################################################################
# Buttons
############################################################################

import keypad
buttons = keypad.Keys(
    (board.BUTTON_UP, board.BUTTON_SELECT, board.BUTTON_DOWN),
    value_when_pressed=True,
)
btn_names = ["BUP", "BSEL", "BDOWN"]
pressed_state = [False, False, False]

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

@server.route("/buttons", method="GET")
def buttons_get(request):
    try:
        # receive a text in the body
        body = json.dumps([
            btn_names[i]
            for i in range(len(btn_names))
            if pressed_state[i] is True
        ])
        with HTTPResponse(request) as response:
            response.send(body)
    except Exception as err:
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
    if event := buttons.events.get():
        if event.pressed:
            pressed_state[event.key_number] = not pressed_state[event.key_number]
