.. _caveats:

Caveats
=======

The Chromophile color maps are imperfect.  This section lists
some known deficiencies.

One aspect of optimization that could be improved is the sRGB
gamut constraints.  The optimization would be faster if the
gradient of the constraint function was available.  It might also
be more reliable; it is possible to find choices of parameters
where the way in which NumPy was compiled affects the
optimization result.  But evaluating the constraint function
requires converting from CAM16-UCS to sRGB, and this is
complicated.  We relied on the Colour package
:cite:p:`colour-science` to do this conversion, but it does not
include the gradient of the conversion (it is unlikely anyone has
wanted it before).

The optimization is intended to make the color maps better, but
attempting to optimize a color map does not necessarily improve
it :cite:p:`LH`.  The objective function did not account for some
physical phenomena, such as chromatic abberation in the lens of
the eye.  It put very little weight on chromatic variation
because, even though it is known to have an effect on the
smallest features that an observer can resolve :cite:p:`WTBSSR`,
we did not know how to quantify the trade-off between chromatic
variation and lightness variation.  A better objective function
would, of course, produce better color maps.

The Chromophile color maps have few highly chromatic colors, and
this makes them less aesthetically pleasing than some
alternatives.  Highly chromatic colors in sRGB are limited to a
narrow range of lightnesses.  Because of this, the only way for a
constant chroma color map to have a large lightness difference is
to avoid highly chromatic colors.

Data with naturally or conventionally associated colors should be
mapped using those colors :cite:p:`TGHZD`, but it is not always
possible to do this and satisfy the uniformity constraints of the
Chromophile color maps.  For example, one popular type of color
map simulates the appearance of black body radiation at
increasing temperatures by starting at black and progressing
through red, orange, yellow, and finally white.  Just like an
actual black body, color maps of this type become more colorful
during the transition from black to red and less colorful during
the transition from yellow to white.  No Chromophile color map
has a similar sequence of colors.  The closest,
:code:`cp_seq_red_yellow_ccw`, has a very different appearance.

The Chromophile color maps were designed for typical computer
displays, not for print.  In print, the available gamut depends
on the inks, the paper, and the printing equipment, and it can be
very different from a computer screen.  There are print setups
that easily exceed the sRGB gamut.  Others have a smaller gamut
than, or a quite different gamut from, sRGB.  If you must be
certain that a Chromophile color map will print accurately,
consult a print professional.

The Chromophile color maps do not take advantage of the gamuts
available in Ultra HD televisions and in movie projectors.  These
gamuts allow colors with greater chroma, a larger lightness
difference between the endpoints, or both.  They also have a
larger bit depth, so they would also provide smoother gradients.
As of this writing, most computers are not equipped with such
displays, so designing such color maps did not seem worthwhile.
This may change some day.
