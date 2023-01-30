# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT
from math import ceil
from adafruit_led_animation.animation import Animation
from adafruit_led_animation.color import BLACK, calculate_intensity


class CometsChase(Animation):
    """
    Chase pixels in one direction in a single color, like a theater marquee sign.
    But with comets.

    :param pixel_object: The initialised LED object.
    :param float speed: Animation speed rate in seconds, e.g. ``0.1``.
    :param color: Animation color in ``(r, g, b)`` tuple, or ``0x000000`` hex format.
    :param size: Number of pixels to turn on in a row.
    :param spacing: Number of pixels to turn off in a row.
    :param reverse: Reverse direction of movement.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        pixel_object,
        speed,
        color,
        size=0,
        spacing=0,
        reverse=False,
        name=None
    ):
        if size == 0:
            size = len(pixel_object) // 4

        self._size = size
        self._spacing = spacing
        self._repeat_width = size + spacing
        self._num_repeats = ceil(len(pixel_object) / self._repeat_width)
        self._overflow = len(pixel_object) % self._repeat_width
        self._direction = 1 if not reverse else -1
        self._reverse = reverse
        self._offset = 0

        self._color_step = 0.95 / size
        self._comet_colors = None
        self._computed_color = color

        self._num_pixels = len(pixel_object)

        def _resetter():
            self._offset = 0
            self._reverse = reverse
            self._direction = 1 if not reverse else -1

        self._reset = _resetter

        super().__init__(pixel_object, speed, color, name=name)

    on_cycle_complete_supported = True

    @property
    def reverse(self):
        """
        Whether the animation is reversed
        """
        return self._reverse

    @reverse.setter
    def reverse(self, value):
        self._reverse = value
        self._direction = -1 if self._reverse else 1

    def _set_color(self, color):
        self._comet_colors = []
        for n in range(self._size):
            self._comet_colors.append(
                calculate_intensity(color, (n * self._color_step) ** 2 + 0.05)
            )
        for n in range(self._spacing):
            self._comet_colors.append(BLACK)
        self._computed_color = color

    def draw(self):
        colors = self._comet_colors
        if self.reverse:
            colors = list(reversed(colors))
        
        cc = colors[self._repeat_width - self._offset:]
        while len(cc) < len(self.pixel_object):
            cc += colors
        self.pixel_object[:] = cc[:len(self.pixel_object)]

        self._offset = (self._offset + self._direction) % self._repeat_width

    def reset(self):
        self._reset()
