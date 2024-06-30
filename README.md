# Magicwand: Hand Landmarks to Mouse

# Short brief

This approach introduce an event manager for keeping track of finger taps. Therefore, you can use the relative distance of any joint to convert to mouse taps.

In addition, an event history is tracked, therefore you can expand the code to support double tap, triple tap or any combination of gestures between fingers.

The mouse is moved per frame based on a drag vector. The origin of the drag vector is the latest touch down event recorded while the destination is the current thumb tip coordinate.
