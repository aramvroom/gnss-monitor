import itertools
import time
from itertools import cycle

from rpi_ws281x import PixelStrip, Color

from gnss_monitor.config import LEDs

def strip_type_to_int(strip_type: str):
    strip_dictionary = {"SK6812_STRIP_RGBW": 0x18100800,
                        "SK6812_STRIP_RBGW": 0x18100008,
                        "SK6812_STRIP_GRBW": 0x18081000,
                        "SK6812_STRIP_GBRW": 0x18080010,
                        "SK6812_STRIP_BRGW": 0x18001008,
                        "SK6812_STRIP_BGRW": 0x18000810,
                        "SK6812_SHIFT_WMASK": 0xf0000000,
                        "WS2811_STRIP_RGB": 0x00100800,
                        "WS2811_STRIP_RBG": 0x00100008,
                        "WS2811_STRIP_GRB": 0x00081000,
                        "WS2811_STRIP_GBR": 0x00080010,
                        "WS2811_STRIP_BRG": 0x00001008,
                        "WS2811_STRIP_BGR": 0x00000810,
                        "WS2812_STRIP": 0x00081000,
                        "SK6812_STRIP": 0x00081000,
                        "SK6812W_STRIP": 0x18081000}
    return strip_dictionary[strip_type]

def rotate_list(l, n):
    return l[n:] + l[:n]


class LedController(object):
    def __init__(self, max_sats, ephemeris, azelev, led_config: LEDs):
        self.max_sats = max_sats
        self.ephemeris = ephemeris
        self.azelev = azelev
        self.config = led_config

        # Create dictionary to map PRN to LED indices
        self.prn_to_led_map = {led_config.satellites.map_prns[i]: led_config.satellites.map_leds[i] for i in range(len(led_config.satellites.map_prns))}

        # Create LED strip
        strip = PixelStrip(led_config.general.led_count, led_config.general.gpio_pin,
                           led_config.general.led_freq_hz, led_config.general.dma_channel,
                           led_config.general.invert_signal, led_config.general.led_max_brightness,
                           led_config.general.channel, strip_type_to_int(led_config.general.led_strip_type))
        strip.begin()
        self.ledstrip = strip

    def get_led_idx(self, sat_idx):
        sat_prn = sat_idx + 1
        try:
            led_idx = self.prn_to_led_map[sat_prn]
        except KeyError:
            led_idx = -1
        return led_idx

    def get_brightness(self, sat_idx):
        elev = self.azelev[sat_idx][1]

        a = (self.config.satellites.max_elev_brightness -  self.config.satellites.min_elev_brightness) / \
            (self.config.satellites.max_elev - self.config.satellites.min_elev)
        b = self.config.satellites.min_elev_brightness

        brightness = a * elev + b
        if brightness < 0:
            brightness = 0
        return brightness

    def set_sat_led(self, sat_idx, signal_health):
        if self.azelev[sat_idx][1] < self.config.satellites.min_elev:
            led_color = [0, 0, 0]
        elif signal_health == 0:
            led_color = self.config.satellites.color_healthy
        elif signal_health == -1:
            led_color = self.config.satellites.color_unknown
        else:
            led_color = self.config.satellites.color_unhealthy

        brightness = self.get_brightness(sat_idx) / self.config.general.led_max_brightness
        led_color_with_elev = [round(i * brightness) for i in led_color]
        color = Color(*led_color_with_elev)
        led_idx = self.get_led_idx(sat_idx)
        # Catch the case where the led index is not found
        if led_idx >= 0:
            self.ledstrip.setPixelColor(led_idx, color)


    def show_plane(self, led_indices):
        # Only keep the LED indices which are not already satellites
        led_indices =  [x for x in led_indices if x not in self.config.satellites.map_leds]

        mid_color = Color(*self.config.satellites.color_plane)
        color_with_brightness = [round(i * self.config.satellites.brightness_early_late_plane) for i in self.config.satellites.color_plane]
        early_late_color = Color(*color_with_brightness)
        reset_color = Color(0, 0, 0)

        very_early_cycle_plane = cycle(led_indices)
        early_cycle_plane = cycle(rotate_list(led_indices, 1))
        prompt_cycle_plane = cycle(rotate_list(led_indices, 2))
        late_cycle_plane = cycle(rotate_list(led_indices, 3))
        very_late_cycle_plane = cycle(rotate_list(led_indices, 4))

        for _ in itertools.count():
            self.ledstrip.setPixelColor(next(very_early_cycle_plane), reset_color)
            self.ledstrip.setPixelColor(next(early_cycle_plane), early_late_color)
            self.ledstrip.setPixelColor(next(prompt_cycle_plane), mid_color)
            self.ledstrip.setPixelColor(next(late_cycle_plane), early_late_color)
            self.ledstrip.setPixelColor(next(very_late_cycle_plane), reset_color)
            time.sleep(self.config.general.plane_interval)

    def update_leds(self):
        for _ in itertools.count():
            for satIdx in range(self.max_sats):
                if len(self.azelev[satIdx]):
                    self.set_sat_led(satIdx, self.ephemeris[satIdx].signalHealth)
            self.ledstrip.show()
            time.sleep(self.config.general.update_interval)
