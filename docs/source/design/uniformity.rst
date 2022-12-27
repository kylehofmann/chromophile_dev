.. _uniformity:

Uniformity
==========

Perceived colors
----------------

The human eye contains only three types of cone cells, so the
physical aspect of a color can be unambiguously specified using
three measurements.  However, these measurements do not
completely describe how a color appears because colors are not
perceived in isolation.  Color appearance depends on ambient
lighting, the background against which the color is viewed, and
the chromatic adaptation of the observer.  (For a thorough
treatment of color appearance, see :cite:p:`Fairchild`.)
High-quality color maps for continuous data are often designed
around the principle of "perceptual uniformity," meaning
perceived differences in colors should be proportional to
differences in data values.  This principle has a long history
:cite:p:`BTSWRA` and is supported by both experience and
experiment :cite:p:`Brewer` :cite:p:`SKR` :cite:p:`Ware`.

Perceived colors are quantified using color appearance models.
Most color appearance models define six parameters, called
"correlates," that represent distinct facets of color
perception.  The absolute amounts of light and color perceived to
come from an object are called brightness and colorfulness,
respectively.  Hue distinguishes colors of equal brightness and
colorfulness.  The other three correlates are proportions.
Saturation is the ratio of an object's colorfulness to its
brightness.  Lightness and chroma are the ratios of an object's
brightness and colorfulness to the brightness of a similarly
illuminated white object.

The correlates most relevant to color map design are lightness,
chroma, and hue.  If the color map is viewed under controlled
conditions, then these three correlates determine a unique color,
and unlike brightness, colorfulness, and saturation, they are
under the direct control of the color map designer.  However, the
relation between perceived color differences and measured values
of these correlates is indirect.  When designing color maps, it
is helpful to parametrize colors so that perceived color
difference is proportional to coordinate distance.  Such a
parametrization is called a uniform color space
:cite:p:`CIE:eILV`.

Uniform color spaces are only suitable for color map design when
the color map is used on data that is suited to a linear scale.
We will tacitly assume this throughout.  Other data should be
transformed first.


Perceptual uniformity
---------------------

Mathematically, a color map is a function :math:`\cc` that
chooses, for each data value :math:`x`, a color :math:`\cc(x)`.
We will always assume that we have chosen a uniform color space
to work in and that :math:`\cc(x)` is represented using
coordinates in that space.  When we need to discuss the rate at
which correlates change, we will assume that the tangent vector
:math:`\cc'(x)` exists.

When interpreted strictly, perceptual uniformity is an extremely
restrictive condition on a color map.  If the color map is
perceptually uniform, then the values of :math:`\cc(x)` make a
line.  To understand why, consider three data values,
:math:`x_1`, :math:`x_2`, and :math:`x_3`.  Perceptual uniformity
means that the distances between :math:`x_1` and :math:`x_2`,
:math:`x_2` and :math:`x_3`, and :math:`x_1` and :math:`x_3` are
proportional to the distances between :math:`\cc(x_1)` and
:math:`\cc(x_2)`, :math:`\cc(x_2)` and :math:`\cc(x_3)`, and
:math:`\cc(x_1)` and :math:`\cc(x_3)`, respectively.  The
distance between :math:`x_1` and :math:`x_3` is the sum of the
distances between :math:`x_1` and :math:`x_2` and between
:math:`x_2` and :math:`x_3`, so the distance between
:math:`\cc(x_1)` and :math:`\cc(x_3)` must be the sum of the
distances between :math:`\cc(x_1)` and :math:`\cc(x_2)` and
between :math:`\cc(x_2)` and :math:`\cc(x_3)`.  Elementary
geometry therefore implies that :math:`\cc(x_1)`,
:math:`\cc(x_2)`, and :math:`\cc(x_3)` are all on a line.  Since
this is true of any three data values, a perceptually uniform
color map is a line in a uniform color space.

However, a line in a uniform color space may be a terrible color
map.  For example, the following color map is a
line in the uniform color space CAM16-UCS :cite:p:`Li`, so it is
perceptually uniform:

.. image:: /image/offset_line.png
   :width: 90%
   :height: 3em
   :alt: Offset line in CAM16-UCS
   :align: center

This color map has a short magenta region, an achromatic region,
and a long green region.  Because this color map is asymmetric,
it tends to color data green.  It makes even pure noise appear
mostly green.  This preponderance of one color gives the viewer
the false impression that the data is skewed.

A different problem with lines in a uniform color space is
illustrated by the following color map:

.. image:: /image/centered_line.png
   :width: 90%
   :height: 3em
   :alt: Centered line in CAM16-UCS
   :align: center

The ends of this color map are distractingly colorful, and there
is evidence that this makes the color map harder to use.  This
color map is similar to the bipolar color map tested by
:cite:p:`SKR`.  In their experiments, subjects performing
identification tasks were slower and less accurate when using a
bipolar color map than when using a color map that varied only in
lightness or that varied linearly in hue, lightness, and chroma.

Every color map made from a line in a uniform color space
suffers, to some extent, from the same problems as the color maps
above.  The failures of these two color maps suggest that
perceptual uniformity does not adequately describe every
desirable quality of a color map.  This is perhaps one reason why
none of the high-quality color maps cited in the introduction are
lines in a uniform color space.

Other types of uniformity
-------------------------

Color maps that are advertised as being perceptually uniform are
usually uniform only in their lightness component.  Their
lightness increases (or decreases) at a constant rate, a property
we will call *lightness uniformity*.  When data is presented
using a lightness-uniform color map, viewers who can accurately
perceive lightness can accurately gauge the magnitude of data.

But as :cite:p:`Ware` observed, an optical illusion called the
simultaneous contrast effect makes it difficult to judge
lightness.  This effect makes the same gray patch appear light
when against a dark background and dark when against a light
background.  In Ware's experiments, subjects attempted to match a
region in a high-contrast test image to a key.  The subjects
performed poorly when the test image was grayscale.  They made
fewer errors when the same data was colored with a large number
of identifiable hues.  Ware recommended that color maps use
lightness to convey form information (level sets or contour
lines) and hue to convey metric information (data values).  Other
suggestions that lightness plays an important part in form
perception have come from experiments with isoluminant (constant
lightness) variants of optical illusions :cite:p:`Gregory`.

Studies of human contrast sensitivity suggest a physical basis
for Ware's recommendations.  Human vision is sensitive in
different ways to low-frequency and high-frequency contrasts.
Achromatic sinusoidal lightness patterns are visible until they
oscillate at more than 60 cycles per degree of visual field,
after which moiré patterns appear :cite:p:`Williams`.  Sinusoidal
chromatic patterns are only visible up to a maximum of around 10
cyc/deg (the exact maximum depends on the colors involved)
:cite:p:`AMH` :cite:p:`KRHM` :cite:p:`Mullen` :cite:p:`SC`
:cite:p:`Switkes`.  But at frequencies below about 0.5 cyc/deg,
contrasts in chromatic sinusoids are more visible than contrasts
in achromatic ones :cite:p:`KRHM` :cite:p:`Mullen`.
High-frequency information, therefore, is best displayed using
lightness contrasts, while low-frequency information is best
displayed using chromatic contrasts.  This offers an explanation
for the importance of lightness uniformity: Lightness uniformity
ensures that a color map displays high-frequency information
well, regardless of where the oscillations appear in the data's
range.  It also suggests that, to display low-frequency
information well, a good color map should have some kind of
uniform chromatic variation.

There are several senses in which a color map might be
chromatically uniform.  We propose calling a color map
*hue-uniform* if its hues change at a constant rate and
*chroma-uniform* if its chroma changes at a constant rate.

Here are three examples.  The first example is isoluminant,
constant hue, and chroma-uniform.  It follows the line in
CAM16-UCS from (67, 0, 0) to (67, 40, −19):

.. image:: /image/constant_hue.png
   :width: 90%
   :height: 3em
   :alt: Isoluminant, constant hue, and chroma-uniform color map
   :align: center

The second example is isoluminant, hue-uniform, and constant
chroma.  This color map follows the circular arc in CAM16-UCS
from (71, 25, −11) to (71, −2, −27).  In polar coordinates, it
begins at −24°, travels 288° counterclockwise, and ends at −96°:

.. image:: /image/constant_chroma.png
   :width: 90%
   :height: 3em
   :alt: Isoluminant, hue-uniform, and constant chroma color map
   :align: center

The third example is isoluminant, hue-uniform, and
chroma-uniform, and it has varying hue and chroma.  This color
map follows a spiral in CAM16-UCS from (59, 0, 0) to (59, 41,
21).  In polar coordinates, it begins at 104°, travels 283°
counterclockwise, and ends at 27°:

.. image:: /image/spiral.png
   :width: 90%
   :height: 3em
   :alt: Isoluminant, hue-uniform, and chroma-uniform color map
   :align: center

Being hue-uniform and chroma-uniform are not enough to guarantee
that a color map accurately presents data.  The spiral color map,
for example, has the undesirable feature that colors near the
beginning are closely spaced while those near the end are far
apart.  To understand the perceptual impact, take evenly spaced
samples from the color map:

.. image:: /image/spiral_samples.png
   :width: 90%
   :height: 3em
   :alt: Samples from an isoluminant, hue-uniform, and
         chroma-uniform color map
   :align: center

These swatches represent equally spaced data values.  However,
the two leftmost swatches are much closer in CAM16-UCS than the
two rightmost swatches.  This deceives the viewer into thinking
that lower data values are closer together than higher data
values.

The spacing of colors is controlled by :math:`\norm{\cc'(x)}`,
the length of the tangent vector.  Variation in
:math:`\norm{\cc'(x)}` causes variation in color spacing.  We say
that a color map has *constant velocity* when
:math:`\norm{\cc'(x)}` is constant.  In constant velocity color
maps, perceived distances between nearby colors are approximately
proportional to perceived distances between nearby data values,
and the constant of proportionality does not depend on the data
values themselves.  A perceptually uniform color map has constant
velocity, but not vice versa, because constant velocity color
maps do not guarantee anything about data values that are far
apart.

Adjusting the spiral color map to have constant velocity yields
the following:

.. image:: /image/spiral_const_velocity.png
   :width: 90%
   :height: 3em
   :alt: Isoluminant and constant velocity color map
   :align: center

But changing the velocity in this way also changes the rate at
which the hue and chroma change.  The following figures plot the
hue and chroma of the above constant velocity spiral.  The
horizontal axis is distance from the left edge of the color map
on a scale from zero to one.  Hue angles were normalized to be
between −270° and 90°:

.. image:: /image/spiral_const_velocity_data.svg
   :width: 90%
   :alt: Chroma and hue of constant velocity spiral
   :align: center

Both the hue and chroma increase much faster near the left end of
the color map than the right end, so changing the spiral to have
constant velocity has also made it neither hue-uniform nor
chroma-uniform.

Criteria for a good color map
-----------------------------

We believe that a high-quality color map should satisfy all of
the following conditions:

#. The color map should be lightness-uniform, hue-uniform, and
   chroma-uniform.
#. The color map should have constant velocity.
#. There should be a large lightness difference between the ends
   of the color map.
#. There should be either a large hue difference, a large chroma
   difference, or both, between the ends of the color map.

These conditions ensure that the color map clearly displays low-
and high-frequency variations in the data and accurately
communicates distances between nearby data values.  Some, though
not all, of them have an extensive history :cite:p:`BTSWRA`.
However, they are also difficult to satisfy.

Most uniform color spaces are parametrized by a lightness
coordinate and two chromaticity coordinates.  Suppose that the
color map is the function :math:`\cc(x) = (J(x), a(x), b(x))`,
where :math:`J` is the lightness coordinate and :math:`a` and
:math:`b` are the chromaticity coordinates.  Convert the
chromaticity coordinates to polar coordinates by setting
:math:`r(x) = \sqrt{a(x)^2 + b(x)^2}` and :math:`\theta(x) =
\atantwo(b(x), a(x))`.  Hue uniformity means that
:math:`\theta(x) = \alpha x + \beta` for some :math:`\alpha` and
:math:`\beta`, while chroma uniformity means that :math:`r(x) =
\gamma x + \delta` for some :math:`\gamma` and :math:`\delta`.
These conditions imply:

.. math::
   :nowrap:

   \begin{align*}
    a(x) &= (\gamma x + \delta)\cos(\alpha x + \beta), \\
    b(x) &= (\gamma x + \delta)\sin(\alpha x + \beta).
   \end{align*}

This curve is called an Archimedean spiral.  Elementary calculus
implies that the length of the tangent vector is:

.. math::

   \norm{(a'(x), b'(x))}
   = \sqrt{\gamma^2 + \alpha^2(\gamma x + \delta)^2}.

It is obvious that if :math:`\alpha \neq 0` and :math:`\gamma
\neq 0`, then the velocity changes as :math:`x` does.
Consequently the only way that a color map can be simultaneously
hue-uniform, chroma-uniform, and constant velocity is if it has
either constant hue or constant chroma.

A constant hue color map has the advantage of being perceptually
uniform.  Such color maps meet every uniformity criterion one
could imagine.  But constant chroma color maps, despite being
perceptually non-uniform, are probably easier to read.  The
subjects in :cite:p:`Ware` made more errors with color maps that
were nearly constant hue than they did with color maps that had a
wide spectrum of hues.  For that reason, we focused our attention
on constant chroma color maps.
