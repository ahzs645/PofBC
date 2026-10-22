# The Best Place on Earth mark, as CorelDRAW artwork

`BC_The_Best_Place_on_Earth.cdr` was supplied on 22 October 2026: a CorelDRAW 9 file of the
stacked mark — the shaded sun and mountains, “British Columbia”, the gold rule and “The Best Place
on Earth”. `BC_The_Best_Place_on_Earth.svg` is its conversion, made with libcdr's `cdr2xhtml`
(libcdr-tools 0.1.7) and taken out of the XHTML wrapper, nothing else changed:

```sh
cdr2xhtml BC_The_Best_Place_on_Earth.cdr > out.xhtml
```

It is held as the original the gallery's `best-place-on-earth` one-off can be checked against. That
one-off is lifted from published artwork (artwork/one-offs/best-place-on-earth.svg), whose sun is
shaded with bitmaps sampled back into radial gradients; this file shades each ray with linear
gradients of its own, which the one-off build does not read, so it is not used to draw anything yet.
