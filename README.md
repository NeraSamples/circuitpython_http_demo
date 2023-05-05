# circuitpython_http_demo

A collection of python and html/javascript code to control a board from a self-hosted web page. The files in each sample directory requires that the code.py file and www directory be placed at the root of the CIRCUITPY drive.

The adafruit_httpserver library and other dependencies have to be [installed from the Bundle](https://circuitpython.org/libraries).

MIT licensed libraries used: [Coloris color selector](https://coloris.js.org/), [Javascript Color Picker](https://github.com/ivanvmat/color-picker).

## Button Server

[Press a button on a page](button_server).

A simple web page that uses javascript to trigger a URL on the board when clicking a button.
Multiple buttons are handled by using a "button" parameter in the URL.
This shows how to handle URL parameters. Note that url decoding of values is not implemented.

Multiple buttons can also be handled by changing the path of the button URL and adding multiple URL handlers.

In this example, the status LED is used to pulse a color. Button A cycles between colors. Button B resets it to red. On a pico W it blinks the on-board LED instead and changes blinking pattern.

## Sending A Form To The Board

[An html page with standard forms](html_form).

This page has multiple forms, sent with `POST`, using different content-types.
A function extracts the values based on the content type into a dictionary.
Choose what format you want to use and write your form, then insert your application code. 

Note that there is pretty much no support for url encoding, so avoid that one.

To change the content of the page based on the applications status (like previous values), instead of sending the html file, it should be loaded and use some string replacement before sending the modified content.

## Send Text With Javascript

[Show a text field on a screen](text_server_plus).

A script that sends text when you press enter. Uses javascript to send the content of the field, encoded using json, while staying in the page. JSON is used here to avoid having to encode and decode url encodings.

Some optional features can be removed to adapt the code to other uses:
- The web page shows a loading icon when the text is being sent.
- The python code shows the text on a builtin display, or external display if setup.

## Server Refresh Buttons State

[Show the state of buttons, as toggles](server_refresh).

Press once to add a button to the list, press again to remove. The html retrieves the buttons state every 5 seconds.

This example is written for the Adafruit Fun House, but you can change the button pins to what you need.

## Color Pickers For LEDs

[Click on a color picker to send color to an LED script](color_control_simple).

This demo controls the color of a LED strip (or single on-board LED by default) from a web page with a simple javascript color selector. Clicking on the selector sends the new color to the board. It sends the value as an entry in a json dictionary to make it easier to extend to more controls.

[A bigger version with another color picker and a brightness slider](color_control_slider).

This version has a choice of 2 color pickers, defaulting to the rainbow wheel. Changing color picker is as simple as switching which init function to call, `init_coloris()` or `init_colorpicker()`.

However, color pickers are not always the best suited to pick LED colors, because low brightness LED colors appear as really dark colors on the computer's screen. So this demo has a separate brightness slider which sets the neopixels brigthness.

This allows selecting the color with the full brightness color wheel, while still managing the LEDs brightness with the slider. In addition, loading the page sets the color in the page to the actual current color.

To remember the color between resets of the board, see the library lights example.


## My Library Lights

[A server controlling a strip of Neopixel LEDs](https://github.com/NeraSamples/circuitpython_http_neopixel_animation).

This code is in another repository.

## Notes

### No favicon

The html files in this repository use this snippet to avoid a request for a favicon from the web browser.

```html
<link rel="icon" href="data:;base64,=">
```

### MDNS entry

It is possible to set the mdns name of the board with the mdns module, so that it can be accessed as `my-server-name.local` on local networks that support it.

```py
import mdns
mdnserv =  mdns.Server(wifi.radio)
mdnserv.hostname = "my-server-name"
mdnserv.advertise_service(service_type="_http", protocol="_tcp", port=PORT)
```

### Each example in its directory

Each example can be left in its directory for tests and imported from a separate code.py file. For that the path to the www directory must be changed, this is one way to do it for the `html_form` code for example. `__name__` is `html_form.code` and shortened to just the directory name.

- in `html_form/code.py`: set ROOT this way: `ROOT = f"/{__name__[:-5]}/www"`
- in the main code.py file of CIRCUITPY, use: `import html_form.code`



