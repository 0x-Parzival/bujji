#!/bin/bash

# Wait for the window to appear
sleep 2

# Keep trying to set the window to stay on top
while true; do
    # Find the Kalki window and set it to stay on top
    wmctrl -r "python3" -b add,above || true
    sleep 2
done 