# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT
from secrets import secrets
import socketpool
import wifi
import board
from digitalio import DigitalInOut, Pull

from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.response import HTTPResponse

PORT = 8080
LED_PIN = board.LED
BUTTON_PIN = board.GP0

led = DigitalInOut(LED_PIN)
led.switch_to_output(False)

button = DigitalInOut(BUTTON_PIN)
button.pull = Pull.UP

ssid = secrets["ssid"]
wifi.radio.connect(ssid, secrets["password"])

print(f"Listening on http://{wifi.radio.ipv4_address}:{PORT}")
pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)

index_html = """<!DOCTYPE html>
<html>
<head> <title>Pico W</title> </head>
<body> <h1>Pico W HTTP Server</h1>
<p>Hello, World!</p>
<p>{body}</p>
<p><a href="?led=on">LED ON</a> - <a href="?led=off">LED OFF</a></p>
</body>
</html>
"""

@server.route("/")
def base(request):
    # read the query parameters
    if 'led' in request.query_params:
        if request.query_params['led'] == "on":
            led.value = True
        elif request.query_params['led'] == "off":
            led.value = False
    # prepare the report of the LED status
    if led.value:
        led_state = "LED is ON"
    else:
        led_state = "LED is OFF"
    # prepare the report of the button status
    if button.value:
        button_state = "Button is NOT pressed"
    else:
        button_state = "Button is pressed"
    # put all of that in a page
    page_output = index_html.format(
        body=f"{led_state} and {button_state}"
    )
    # send
    return HTTPResponse(body=page_output, content_type="html")

# startup the server
server.start(str(wifi.radio.ipv4_address), PORT)

while True:
    try:
        # process any waiting requests
        server.poll()
    except OSError:
        continue
