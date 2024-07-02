# Magicwand: Hand Landmarks to Mouse

# How to use

Make sure you got [Python](https://www.python.org/downloads/) installed on your computer first. Then just type the below lines into your terminal:

```Bash
pip install -r requirements.txt

python Loop.py

```

I haven't tried this on a fresh environment yet, so the requirements.txt might not cover all dependencies. If you are experiencing errors, feel free to open an issue or ping me.

# Short brief

This approach introduce an event manager for keeping track of finger taps. Therefore, you can use the relative distance of any joint to convert to mouse taps.

In addition, an event history is tracked, therefore you can expand the code to support double tap, triple tap or any combination of gestures between fingers.

The mouse is moved per frame based on a drag vector. The origin of the drag vector is the latest touch down event recorded while the destination is the current thumb tip coordinate.
