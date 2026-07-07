Matrixia Plasma 6 wallpaper — 1.0.2

Install:
  ./install.sh

Configuration:
  ~/.config/matrixia.conf

The configuration is re-read once per second. Source-code edits to main.qml
require the current wallpaper object to be recreated. The simplest method is:
  systemctl --user restart plasma-plasmashell.service

This release fixes:
  - invalid matrixia.conf URL (file://file:///...)
  - stale trails after changing mode or colour
  - excessively persistent exponential after-images
  - Context2D silently keeping its default 10px font when a quoted family
    name was rejected; the font size now applies and falls back to monospace
