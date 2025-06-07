# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Quote board matrix display
# uses AdafruitIO to serve up a quote text feed and color feed
# random quotes are displayed, updates periodically to look for new quotes
# avoids repeating the same quote twice in a row

import time
import random
import board
import json
import terminalio  # type: ignore
import displayio
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_display_text import label

# === Setup ===
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=True)
display = matrixportal.graphics.display

# --- Load quotes ---
def load_and_update_quotes(filename="quotes.json"):
    with open(filename, "r") as file:
        return json.load(file)

quotes = load_and_update_quotes()

def get_day_of_week():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[time.localtime().tm_wday]

# --- Rain setup ---
bitmap = displayio.Bitmap(64, 32, 2)
palette = displayio.Palette(2)
palette[0] = 0x000000
palette[1] = 0xD3D3D3
    # light gray for border
rain_grid = displayio.TileGrid(bitmap, pixel_shader=palette)

# --- Text setup ---
quote_text = quotes.get(get_day_of_week(), "No quote today")
text_label = label.Label(terminalio.FONT, text=quote_text, color=0xFFFFFF)
text_label.y = 15
text_label.x = display.width  # start offscreen to the right


# --- Display group ---
group = displayio.Group()
group.append(rain_grid)
group.append(text_label)
display.root_group = group

# --- Rain state ---
drops = [random.randint(0, 31) for _ in range(64)]

# --- Timing controls ---
last_rain = time.monotonic()
last_scroll = time.monotonic()
RAIN_DELAY = 0.005      # faster rain
SCROLL_DELAY = 0.01     # slower scrolling

# --- Main loop ---
while True:
    now = time.monotonic()

    # --- Animate rain ---
    if now - last_rain > RAIN_DELAY:
        for x in range(64):
            for y in range(32):
                bitmap[x, y] = 0
        for x in range(64):
            y = drops[x]
            bitmap[x, y] = 1
            drops[x] = (y + 1) % 32
            if random.random() < 0.01:
                drops[x] = 0
        last_rain = now

    # --- Animate scroll ---
    if now - last_scroll > SCROLL_DELAY:
        text_label.x -= 1
        if text_label.x < -text_label.bounding_box[2]:  # fully scrolled off
            text_label.x = display.width
        last_scroll = now