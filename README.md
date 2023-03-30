# circuitpython_http_demo
A collection of python and html/javascript code to control a board from a self-hosted web page.

The adafruit_httpserver library and other dependencies have to be [installed from the Bundle](https://circuitpython.org/libraries).

## [Button Server](button_server/)

Press a button to make the board do something.

In this case, cycle between colors on the status LED.

## Sending Text To The Board

Three examples for sending text to a board, to display on a screen

### [Using a standard html form.](text_form)

This example encompasses multiple form encodings and extracts the values from each of them. There is no urldecode() function, so avoid using url encoding.

### [Send text with javascript](text_server)

Uses javascript to send the content of a field asynchronously while staying in the page.

### [Send text with javascript extended](text_server_plus)

A more elaborate version of the javascript field with a loading icon and some CSS.

## [Server Refresh Buttons State](server_refresh)

Show the state of buttons, as toggles.

Press once to add a button to the list, press again to remove. The html retrieves the buttons state every 5 seconds.

This example is written for the Adafruit Fun House, but you can change the button pins to what you need.

## [My Library Lights](my_library_lights)

A web server for controlling a strip of Neopixel LEDs.

This code also uses an analog proximity sensor to increase the light for a short period of time when someone comes in front. That way you can have a nice LED animation around your library, and it will help you see what you are doing when you get close to retrieve something from it.
