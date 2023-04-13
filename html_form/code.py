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
import re

from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.status import CommonHTTPStatus

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
# form helper
# Reads the form data and converts it into a dictionary according to the
# content type used byt the web page.
############################################################################

def get_form_data(request):
    ctype = request.headers['Content-Type'].lower()
    if ctype.startswith("text/plain"):
        # lines as name=value
        data = request.body.decode()
        form = dict(
            line.split("=",1) for line in data.split("\r\n") if "=" in line
        )
    elif ctype.startswith("application/x-www-form-urlencoded"):
        # no URL decoding implemented
        data = request.body.decode().replace("%20"," ")
        form = dict(
            line.split("=",1) for line in data.split("&") if "=" in line
        )
    elif ctype.startswith("multipart/form-data"):
        # multipart data, a little more complex of a format
        pos = ctype.find("boundary=")
        sep = ("--" + ctype[pos+9:])
        data = request.body.decode().split(sep)
        form = {}
        for bloc in data:
            parts = bloc.split("\r\n\r\n")
            mm1 = re.search('.*name="(.*)"', parts[0])
            if mm1:
                key = mm1.group(1)
                mm2 = re.search('(.*)\r\n-*', parts[1])
                if mm2:
                    value = mm2.group(1)
                    form[key] = value
    elif ctype.startswith("application/json"):
        # a custom POST request using a json body, not a regular FORM
        form = json.loads(request.body)
    else:
        return None
    return form

############################################################################
# server routes and app logic
############################################################################

ERROR400 = CommonHTTPStatus.BAD_REQUEST_400

@server.route("/", method="POST")
def index_form_handler(request):
    """Receive data in the body of a POST request."""
    try:
        # get the data from the form
        form = get_form_data(request)

        # debug print
        if form is None:
            raise ValueError("Bad Input")
        print(repr(form))

        ##################################################################
        # Your application code
        # this is where you decide what to do with the form data

        # example: print the message field to the console
        if "message" in form:
            the_text = form["message"]
            print("Message was:", the_text)

        ##################################################################

        # then, send the form again
        with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
            response.send_file(f"{ROOT}/index.html")

    except (ValueError, AttributeError) as err:
        fm = traceback.format_exception(err, err, err.__traceback__)
        fm = "".join("> "+x.replace("\n", "\n> ") for x in fm)
        print(fm)
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
