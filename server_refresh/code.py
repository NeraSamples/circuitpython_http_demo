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

from adafruit_httpserver import Server, Response, MIMETypes, BAD_REQUEST_400

PORT = 8000
ROOT = "/www"

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
# server routes and app logic
############################################################################

@server.route("/buttons", methods="GET")
def buttons_get(request):
    # receive a text in the body
    body = json.dumps([
        btn_names[i]
        for i in range(len(btn_names))
        if pressed_state[i] is True
    ])
    return Response(request, body)

############################################################################
# start and loop
############################################################################

IP_ADDRESS = wifi.radio.ipv4_address or wifi.radio.ipv4_address_ap
server.start(host=str(IP_ADDRESS), port=PORT)

while True:
    server.poll()
    time.sleep(0.01)
    if event := buttons.events.get():
        if event.pressed:
            pressed_state[event.key_number] = not pressed_state[event.key_number]
