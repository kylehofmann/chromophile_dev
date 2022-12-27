.. _chromophile:

The color maps
==============

We constructed the Chromophile color maps using the principles
described in the previous sections.  These color maps are
lightness-uniform, hue-uniform, constant chroma, and constant
velocity.  Hue uniformity and constant chroma are, as far as we
are aware, unique to our color maps.  (:cite:p:`Kovesi` mentions
this possibility in the context of cyclic color maps, but his
design criteria ultimately lead him elsewhere.)  The unique
treatment of chroma inspired the name "Chromophile."

The Chromophile color maps were designed in CAM16-UCS.  When
CAM16-UCS is transformed to cylindrical coordinates, the radial
coordinate is denoted :math:`M'`, the angular coordinate is
:math:`h`, and the height coordinate is :math:`J'`.  We call
:math:`M'` the uniformized colorfulness and :math:`J'` the
uniformized lightness.  We write :math:`\Delta J'` for the
difference between the greatest and least values of :math:`J'` in
the color map.

Except for the isoluminant color maps, all the Chromophile color
maps contain pairs of colors with large lightness differences.
However, some of the color maps do not contain pairs with large
hue differences.  Some, such as :code:`cp_seq_red_pink_cw1`, have
only modest hue differences, and a few, such as
:code:`cp_seq_green_green_cw`, have a nearly constant hue.  These
are for visualizations with other constraints on the color map,
such as legibility against a colored background.  In most
circumstances, we recommend color maps with large hue
differences.

The Chromophile color maps had one additional perceptual
constraint, legibility for people with color vision deficiency.
Illegible color maps are bad color maps, and there is no reason
to use, let alone design, a bad color map.  Using the model of
:cite:p:`MOF` (as implemented in :cite:p:`colour-science`) we
evaluated the suitability of each color map for color vision
deficient viewers and, if necessary, adjusted it to make its
colors distinct for those viewers.  Apart from a few instances
described later, we discarded color maps where this could not be
done.  Viewers in whom one type of cone cell is unusual
(anomalous trichromacy) or absent or non-functional (dichromacy)
will perceive the Chromophile color maps differently from
non-anomalous trichromats, but they should not have difficulty
reading them.  (Users who need a color map specifically optimized
for color vision deficient viewers should see :cite:p:`NAR`.)

Each of the Chromophile color maps is defined by a small number
of parameters.  For instance, our sequential color maps are
determined by the initial and final lightnesses, the chroma, the
initial hue angle, and the change in hue angle.  The small number
of parameters made it possible to automatically generate and
optimize color maps.  With a few exceptions, the Chromophile
color maps were optimized by fixing the colorfulness and varying
the hue angles to maximize the difference in lightness between
their endpoints.  Color map optimization was done using
:func:`scipy.optimize.minimize` with the :code:`method` parameter
set to :code:`trust-constr`.  While optimization is never a
substitute for visual evaluation, it is much easier than
hand-tuning.

All the Chromophile color maps are designed for continuous data.
They are not meant for categorical features such as
distinguishing different lines on a shared line plot.

The gray color map
------------------

The standard sRGB grayscale color map is comprised of the colors
with sRGB coordinates (0, 0, 0), (1, 1, 1), …, (255, 255, 255).
This simplicity is deceptive, for the :math:`J'` values of this
color map are not linear in CAM16-UCS:

.. image:: /image/sRGB_gray_Jp.svg
   :width: 90%
   :alt: CAM16-UCS J' coordinate of the standard sRGB grayscale color map
   :align: center

A secondary problem is that, as the lightness increases, the
color map steadily gains a slight cyan tint.
:code:`cp_seq_gray` fixes both these issues.  The difference
between the sRGB grayscale (top) and :code:`cp_seq_gray`
(bottom) is small, but visible:

.. image:: /image/sRGB_gray.png
   :width: 90%
   :height: 3em
   :alt: The standard sRGB grayscale color map
   :align: center

.. raw:: html

   <p style="margin-bottom: 1em;"></p>

.. image:: /image/cp_seq_gray.png
   :width: 90%
   :height: 3em
   :alt: cp_seq_gray
   :align: center

Sequential color maps
---------------------

Sequential color maps are used when the data consists of real
numbers.  There are fifteen sequential Chromophile color maps
(excluding order-reversed variants and :code:`cp_seq_gray`).
They have systematic names of the form:

   :samp:`cp_seq_{<starting color>}_{<ending color>}_{<direction>}{<optional number>}`

The possible directions were :code:`cw` and :code:`ccw`
(referring to clockwise and counterclockwise directions in the
chromaticity coordinates of CAM16-UCS).  Most color maps do not
have an optional number.  For the ones that do, the number is
:code:`1` if the color map's hues are confined to a small
sector and :code:`2` if the hues span more than one but less
than two full circles.

All of the sequential color maps have 256 colors, :math:`M' =
20`, and :math:`\Delta J' \ge 80`.  Because the sequential
Chromophile color maps have a steady increase in lightness, they
should be legible (though not optimal) for people with any type
of color vision deficiency, even full monochromacy.  The 
parameters of these color maps are:

.. list-table::
   :header-rows: 1
   :class: table-col-2-r table-col-3-r table-col-4-r table-col-5-r table-col-6-r table-col-7-r

   * - Name
     - :math:`J_0'`
     - :math:`J_1'`
     - :math:`\Delta J'`
     - :math:`h_0`
     - :math:`h_1`
     - :math:`\Delta h`
   * - :code:`cp_seq_blue_cyan_ccw`
     - 7.38
     - 94.90
     - 87.52
     - −77.15°
     - 197.44°
     - 274.59°
   * - :code:`cp_seq_blue_cyan_cw`
     - 7.38
     - 94.90
     - 87.52
     - −77.15°
     - −162.56°
     - −85.41°
   * - :code:`cp_seq_blue_pink_ccw1`
     - 7.38
     - 89.64
     - 82.26
     - −77.15°
     - −32.01°
     - 45.14°
   * - :code:`cp_seq_blue_pink_ccw2`
     - 7.38
     - 89.57
     - 82.18
     - −77.15°
     - −31.70°
     - 405.45°
   * - :code:`cp_seq_blue_yellow_ccw`
     - 7.38
     - 98.15
     - 90.77
     - −77.15°
     - 111.96°
     - 189.11°
   * - :code:`cp_seq_blue_yellow_cw`
     - 7.85
     - 98.15
     - 90.31
     - −71.99°
     - −248.04°
     - −176.05°
   * - :code:`cp_seq_green_cyan_ccw`
     - 14.58
     - 94.90
     - 80.33
     - 142.36°
     - 197.44°
     - 55.08°
   * - :code:`cp_seq_green_green_cw`
     - 14.58
     - 95.71
     - 81.13
     - 142.36°
     - 137.36°
     - −5.00°
   * - :code:`cp_seq_green_yellow_cw`
     - 14.58
     - 98.15
     - 83.58
     - 142.36°
     - 111.96°
     - −30.39°
   * - :code:`cp_seq_red_cyan_ccw`
     - 9.61
     - 94.90
     - 85.30
     - 17.26°
     - 197.44°
     - 180.18°
   * - :code:`cp_seq_red_cyan_cw`
     - 8.70
     - 94.90
     - 86.21
     - 27.25°
     - −162.56°
     - −189.81°
   * - :code:`cp_seq_red_pink_cw1`
     - 8.70
     - 89.64
     - 80.95
     - 27.25°
     - −32.01°
     - −59.25°
   * - :code:`cp_seq_red_pink_cw2`
     - 8.70
     - 89.24
     - 80.54
     - 27.25°
     - −33.49°
     - −420.73°
   * - :code:`cp_seq_red_yellow_ccw`
     - 8.70
     - 98.15
     - 89.46
     - 27.25°
     - 111.96°
     - 84.72°
   * - :code:`cp_seq_red_yellow_cw`
     - 8.70
     - 98.15
     - 89.46
     - 27.25°
     - −248.04°
     - −275.28°

Here, :math:`J_0'` and :math:`J_1'` are the uniformized
lightnesses of the initial and final colors, :math:`\Delta J'` is
their difference, :math:`h_0` and :math:`h_1` are the hue angles
of the initial and final colors, and :math:`\Delta h` is the
change in hue angle along the color map.

The sequential color maps were found using a systematic search of
directed arcs on a circle.  The endpoints of each arc were used
as the chromaticity coordinates of the endpoints of a color map.
The initial lightness was set to :math:`J' = 20` and the final
lightness to :math:`J' = 80`.  The color map was optimized to
maximize :math:`\Delta J'` under the constraint that the hue
angles of the endpoints were near their starting points.

Among color maps whose hues made one or less full winding around
the circle, there were 78 combinations of starting color, ending
color, and direction.  However, these led to only thirteen
Chromophile color maps.  The remaining color maps had too small a
value of :math:`\Delta J'` or were duplicates (exact or near) of
the others.  In every case, when a color map's :math:`\Delta J'`
was too small, it was because the dark endpoint was not dark
enough, and ultimately, that was because sRGB does not contain
very dark browns and azures.  There is little flexibility in the
Chromophile color maps; a color map that goes clockwise from
green to pink, for example, necessarily passes through brown.  If
the initial lightness is low, then those browns are so dark that
they are not in sRGB, but increasing the initial lightness makes
:math:`\Delta J'` too small.  This explains the small number of
color maps starting at green: Any color map starting at green
must avoid brown, so it cannot travel clockwise very far, and it
must avoid azure, so it cannot travel counterclockwise very far,
either.  The only Chromophile color maps containing dark green
have similar starting and ending hues, and their darkest colors
are lighter than the darkest colors of the other Chromophile
color maps.

Multi-sequential color maps
---------------------------

Multi-sequential color maps are used for data consisting of a
real variable and a categorical variable.  The categorical
variable is used to select a sequential color map, and the real
variable selects a color from that color map.  Multi-sequential
color maps are not often needed in practice, but an example can
be seen in Figure 3h of :cite:p:`TGHZD`.

Each sequence in each of the multi-sequential Chromophile color
maps has 256 colors, so the full color map has between 512 and
1024 colors.  Their names follow the pattern:

   :samp:`cp_mseq_{<first color>}_{<second color>}{_<optional third color>}{_<optional fourth color>}`

Their parameters are:

.. list-table::
   :header-rows: 1
   :class: table-col-2-r table-col-3-r table-col-4-r table-col-5-r table-col-6-r table-col-7-r

   * - Name
     - :math:`J_0'`
     - :math:`J_1'`
     - :math:`\Delta J'`
     - :math:`h_0`
     - :math:`h_1`
     - :math:`\Delta h`
   * - :code:`cp_mseq_green_blue`
     - 14.58
     - 94.90
     - 80.33
     - 142.36°
     - 142.36°
     - 0.00°
   * -
     -
     -
     -
     - −89.66°
     - −162.56°
     - −72.90°
   * - :code:`cp_mseq_green_purple`
     - 11.22
     - 91.22
     - 80.00
     - 142.36°
     - 142.36°
     - 0.00°
   * -
     -
     -
     -
     - −32.81°
     - −32.81°
     - 0.00°
   * - :code:`cp_mseq_green_red`
     - 11.22
     - 91.22
     - 80.00
     - 142.36°
     - 142.36°
     - 0.00°
   * -
     -
     -
     -
     - 25.00°
     - −32.81°
     - −57.81°
   * - :code:`cp_mseq_orange_blue`
     - 8.70
     - 94.90
     - 86.21
     - 27.25°
     - 102.83°
     - 75.59°
   * -
     -
     -
     -
     - −79.67°
     - −162.56°
     - −82.90°
   * - :code:`cp_mseq_orange_teal`
     - 14.58
     - 94.90
     - 80.33
     - 36.67°
     - 102.83°
     - 66.16°
   * -
     -
     -
     -
     - 142.36°
     - 197.44°
     - 55.08°
   * - :code:`cp_mseq_purple_orange`
     - 8.83
     - 89.64
     - 80.82
     - −60.00°
     - −32.01°
     - 27.99°
   * -
     -
     -
     -
     - 27.47°
     - 86.82°
     - 59.35°
   * - :code:`cp_mseq_red_blue`
     - 7.14
     - 87.14
     - 80.00
     - 27.24°
     - −14.85°
     - −42.09°
   * -
     -
     -
     -
     - −79.90°
     - −120.00°
     - −40.10°
   * - :code:`cp_mseq_teal_purple`
     - 11.22
     - 91.22
     - 80.00
     - 142.36°
     - 180.00°
     - 37.64°
   * -
     -
     -
     -
     - −32.81°
     - −32.81°
     - 0.00°
   * - :code:`cp_mseq_orange_blue_purple`
     - 8.88
     - 89.64
     - 80.76
     - 27.57°
     - 86.82°
     - 59.24°
   * -
     -
     -
     -
     - −80.01°
     - −142.99°
     - −62.98°
   * -
     -
     -
     -
     - −59.22°
     - −32.01°
     - 27.21°
   * - :code:`cp_mseq_orange_green_blue`
     - 14.58
     - 94.90
     - 80.33
     - 36.67°
     - 102.83°
     - 66.16°
   * -
     -
     -
     -
     - 142.36°
     - 142.36°
     - 0.00°
   * -
     -
     -
     -
     - −89.66°
     - −162.56°
     - −72.90°
   * - :code:`cp_mseq_orange_green_blue_purple`
     - 11.22
     - 91.22
     - 80.00
     - 36.62°
     - 88.11°
     - 51.50°
   * -
     -
     -
     -
     - 142.36°
     - 142.36°
     - 0.00°
   * -
     -
     -
     -
     - −87.57°
     - −143.19°
     - −55.62°
   * -
     -
     -
     -
     - −32.81°
     - −32.81°
     - 0.00°

To find multi-sequential color maps containing two sequences, we
performed a systematic search, similar to the one for sequential
color maps, of pairs of directed arcs on a circle.  This search
used :math:`M' = 20`, and we kept only color maps that achieved
:math:`\Delta J' \ge 80`.  There was one exception,
:code:`cp_mseq_red_blue`.  The red and blue multisequential
color map that resulted from the search had colors that could not
be distinguished by some dichromats, and there seemed to be no
way to remove this ambiguity while meeting our other
requirements.  Red and blue are such a popular pairing that we
kept this color map anyway.  We re-optimized, this time
restricting the endpoints to ensure legibility for color vision
deficient viewers, requiring :math:`\Delta J'` to be at least
80, and aiming to make :math:`M'` as large as possible.
The final :math:`M'` was 18.15.

A similar search of triples of directed arcs found
:code:`cp_mseq_orange_blue_purple` and
:code:`cp_mseq_orange_green_blue`.  Searching quadruples
resulted in no color maps that achieved :math:`M' = 20` and
:math:`\Delta J' \ge 80`.
:code:`cp_mseq_orange_green_blue_purple` was produced by
imposing the constraint :math:`\Delta J' \ge 80` and maximizing
:math:`M'`.  The result was :math:`M' = 17.65`.

The multi-sequential Chromophile color maps with two sequences
should be legible for dichromats.  Those with three or four
sequences should be legible for anomalous trichromats but are
probably not legible for dichromats.  It is possible to design a
color map with three or four sequences of colors that all appear
distinct to a dichromat.  Two of the sequences would appear very
colorful and the others would have the same colors but appear
more gray.  However, it seems difficult, maybe impossible, to do
this simultaneously for all the different types of dichromats
while meeting the other criteria for Chromophile color maps.

Divergent color maps
--------------------

Divergent color maps, sometimes called bipolar color maps, are a
type of multi-sequential color map.  They are used when the data
consists of real numbers, one of those numbers is the boundary
between two qualitatively different categories, and the
visualization should communicate distance from the boundary.
This situation often arises when plotting differences.

Divergent color maps are not a substitute for contour lines.  If
the boundary value has no special meaning, then divergent color
maps are unnecessary and may even be deceptive.

Some divergent color maps can also be used as sequential color
maps (for example, :cite:p:`Moreland` was designed with that goal
in mind).  The divergent Chromophile color maps were not intended
for this and should not be used for sequential data.

Each divergent Chromophile color map consists of two sequential
color maps of 256 colors each, for a total of 512 colors.  There
are two types of divergent Chromophile color maps.  One type has
a sharp transition at the boundary.  These color maps are just
rearrangements of two-sequence multi-sequential color maps, so
they will not be discussed further.  The other type makes a
smooth transition at the boundary.  There are five divergent
Chromophile color maps of this type.  Their names have the form:

   :samp:`cp_div_{<first color>}_{<second color>}_{<divergence type>}`

The divergence type is "hill" or "valley" according to whether
the transition between the two categories happens at a light or a
dark color.  The parameters for these color maps are:

.. list-table::
   :header-rows: 1
   :class: table-col-2-r table-col-3-r table-col-4-r table-col-5-r table-col-6-r table-col-7-r

   * - Name
     - :math:`J_0'`
     - :math:`J_1'`
     - :math:`\Delta J'`
     - :math:`h_0`
     - :math:`h_1`
     - :math:`\Delta h`
   * - :code:`cp_div_blue_orange_valley`
     - 10.34
     - 94.90
     - 84.57
     - 4.90°
     - −162.56°
     - −167.46°
   * -
     -
     -
     -
     - 5.10°
     - 102.83°
     - 97.73°
   * - :code:`cp_div_green_blue_hill`
     - 14.79
     - 94.79
     - 80.00
     - 142.62°
     - 194.16°
     - 51.55°
   * -
     -
     -
     -
     - −90.00°
     - −164.84°
     - −74.84°
   * - :code:`cp_div_green_cyan_valley`
     - 14.61
     - 94.90
     - 80.29
     - 142.30°
     - 132.30°
     - −10.00°
   * -
     -
     -
     -
     - 142.40°
     - 197.44°
     - 55.04°
   * - :code:`cp_div_orange_blue_hill`
     - 9.18
     - 94.47
     - 85.29
     - 22.34°
     - 180.00°
     - 157.66°
   * -
     -
     -
     -
     - −80.55°
     - −177.00°
     - −96.45°
   * - :code:`cp_div_pink_orange_valley`
     - 9.91
     - 89.91
     - 80.00
     - 5.00°
     - −32.13°
     - −37.13°
   * -
     -
     -
     -
     - 5.10°
     - 87.03°
     - 81.93°

Hill and valley color maps are equally usable but are good for
different purposes.  Imagine, for example, that you are comparing
a model to experimental data, and the plot shows the amount and
direction of residual error.  If the residual is displayed
against a dark background, then light colors will draw a viewer's
attention.  A hill map will focus attention on where the model is
correct: "Look at how good my model is!" A valley map will focus
attention on where the model is incorrect: "Look at how bad their
model is!"

There are fewer divergent Chromophile color maps than sequential
or even multisequential color maps because it was difficult to
make these color maps legible for viewers with color vision
deficiency.  We chose the central hue so that viewers with red or
green cone cell abnormalities see a color transition there.
These color maps should also be legible for viewers with blue
cone cell abnormalities.

The color map :code:`cp_div_pink_orange_valley` is very slightly
lower quality than the others.  After the central hue was
adjusted to make the color map legible for viewers with red and
green cone cell deficiencies, the color map had :math:`\Delta J'
= 79.31`.  This was so close to :math:`\Delta J' = 80`, and there
were so few divergent color maps, that we compromised.  We
required :math:`\Delta J' \ge 80` and maximized :math:`M'`,
getting a color map with :math:`M' = 19.61`.  

We made but rejected four other divergent color maps.  Three
would have been valley color maps:
:code:`cp_div_blue_purple_valley`,
:code:`cp_div_green_purple_valley`, and
:code:`cp_div_orange_green_valley`.  One would have been a
hill color map, :code:`cp_div_orange_green_hill`.  All of
these were acceptable for non-anomalous trichromats and viewers
with blue cone cell abnormalities.  However, there was no way to
make them legible for viewers with red or green cone cell
abnormalities.

Isoluminant color maps
----------------------

Isoluminant color maps may be appropriate when used to display
secondary or tertiary properties of the data and when a color's
lightness is dictated by other considerations.  For example, in
three-dimensional renderings, isoluminant color maps are the only
color maps that do not interact with the scene's lighting.  In
principle, they should be ideal for such renderings.  However, as
explained earlier in :ref:`uniformity`, they make details so
difficult to discern that resulting visualizations are often
worthless (this was noted by :cite:p:`Moreland`).  They should be
used cautiously if at all.  

For those cases where isoluminant color maps are appropriate,
there are nine isoluminant Chromophile color maps.  They come in
three families of three color maps each.  One of these families
consists of cyclic color maps and will be discussed later.  The
others are sequential color maps whose names have the form:

   :samp:`cp_isolum_{<first color>}_{<second color>}_{<style>}`

The parameters for these color maps are:

.. list-table::
   :header-rows: 1
   :class: table-col-2-r table-col-3-r table-col-4-r table-col-5-r table-col-6-r table-col-7-r

   * - Name
     - :math:`M'`
     - :math:`J'`
     - :math:`h_0`
     - :math:`h_1`
     - :math:`\Delta h`
   * - :code:`cp_isolum_purple_orange_dark`
     - 18.65
     - 32.01
     - −74.00°
     - 80.00°
     - 154.00°
   * - :code:`cp_isolum_purple_orange_light`
     - 18.65
     - 82.01
     - −74.00°
     - 80.00°
     - 154.00°
   * - :code:`cp_isolum_yellow_blue_dark`
     - 18.11
     - 34.95
     - 98.00°
     - 266.00°
     - 168.00°
   * - :code:`cp_isolum_yellow_blue_light`
     - 18.11
     - 84.95
     - 98.00°
     - 266.00°
     - 168.00°
   * - :code:`cp_isolum_purple_orange_wide`
     - 32.71
     - 67.63
     - −49.00°
     - 51.00°
     - 100.00°
   * - :code:`cp_isolum_yellow_blue_wide`
     - 26.34
     - 72.87
     - 97.00°
     - 262.00°
     - 165.00°

:code:`cp_isolum_purple_orange_dark` and
:code:`cp_isolum_purple_orange_light` have the same hues in the
same order; the only difference between these color maps is their
lightnesses.  The same is true of
:code:`cp_isolum_yellow_blue_dark` and
:code:`cp_isolum_yellow_blue_light`.  This makes both pairs
appropriate for the following situation (among others): Suppose
each observation consists of a pair of values, say :math:`(A,
B)`.  The first value, :math:`A`, is used to select a lightness,
and the second value, :math:`B`, is used to select a hue.
Observations achieving the maximum value of :math:`A` are colored
by using :math:`B` to select a color from the light color map;
observations achieving the minimum value of :math:`A` are colored
by using :math:`B` to select a color from the dark color map;
values of :math:`A` between the minimum and maximum are colored
by linearly interpolating between the light and dark color maps.
For both of these pairs of color maps, linearly interpolating in
CAM16-UCS between the dark and light version of each hue stays
within the sRGB gamut.

Isoluminant color maps are hard to use even for people with
normal trichromatic vision, but for dichromats, they are nearly
illegible.  For a dichromat, every color in an isoluminant color
map is a blend of the two most extreme colors in the color map,
and the best isoluminant color map would steadily go from one
extreme to the other.  However, which colors are perceived as
most extreme depends on the type of color vision deficiency.  A
color map that is good for someone with one type of color vision
deficiency is often illegible for someone with a different type.

While our optimization found many color maps with similar values
of :math:`J'` and :math:`M'`, we were unable to find isoluminant
color maps that were legible for all viewers and that met our
other criteria.  The only color maps that had a similar
appearance for every type of dichromacy had :math:`\Delta h` so
small that the color map was equally useless for everyone.  In
the end, we decided to make the color maps legible for as many
people as possible.  We believe the final color maps are
acceptable for viewers with protanomaly, protanopia,
deuteranomaly, and deuteranopia.  These viewers should perceive
the endpoints of the color maps as the most colorful, and they
should see a color change near the center of the color maps.  We
extend our apologies to tritanomalous and tritanopic viewers.  

The :code:`wide` variants were constructed by searching for
arcs with constant :math:`J'` and large values of :math:`M'`.
The :code:`dark` and :code:`light` color maps were found
by searching for pairs of arcs in CAM16-UCS which had the same
:math:`(a', b')` coordinates, were in the sRGB gamut for both
small and large values of :math:`J'`, and whose hue angles we
believed were acceptable.  The resulting :math:`\Delta J'` was 40
for the yellow--blue color maps and 44 for the purple--orange
color maps.  To increase :math:`\Delta J'`, we decreased
:math:`M'`.  The cost was making the colors closer to gray and
therefore less distinct (a particularly troublesome trade-off in
an isoluminant color map).  We thought a good compromise was to
require :math:`\Delta J' \ge 50` and maximize :math:`M'`.

Cyclic color maps
-----------------

A cyclic color map is one that makes a smooth progression of
colors when wrapped around a circle.  These color maps are used
for angular data.  All the cyclic Chromophile color maps have 360
colors.

Some data needs conversion before a cyclic color map can be used.
Points on a circle can be converted to angles using the
two-argument arctangent function :math:`\atantwo`.  Some angular
data does not distinguish between antipodal points on the circle;
for example, this is the case if the data consists of pairs of
directions such as "north–south" or "east–west."  In this case,
all the angles should be doubled (and wrapped around the circle)
before colors are assigned.  (Mathematically, this kind of data
consists of points on the real projective line
:math:`\mathbf{RP}^1`, and doubling angles is a function from the
real projective line to the unit circle.)

Cyclic color maps are difficult to design because they must start
and end at the same lightness.  Lightness is not cyclic, so if
the color map's lightness changes somewhere in the middle, then
it must change back somewhere else.  Since those changes happen
in opposite directions, the color map's lightness cannot change
at a constant rate unless the color map is isoluminant.  (This is
a consequence of the Mean Value Theorem from differential
calculus.)  An isoluminant cyclic Chromophile-style color map is
completely specified by :math:`J'` and :math:`M'`.

There are three isoluminant cyclic Chromophile color maps.  Their
names follow the scheme:

   :samp:`cp_cyc_isolum_{<style>}`

For convenience, they also available under the aliases
:code:`cp_isolum_cyc_`\<*style*>.

:code:`cp_cyc_isolum_light` and
:code:`cp_cyc_isolum_dark` use the same hues in the same
order, just like the other :code:`light` and :code:`dark`
pairs of isoluminant color maps.  These color maps have the
largest :math:`M'` for which :math:`\Delta J'` was at least 50.
:code:`cp_cyc_isolum_wide` is the most colorful isoluminant
circle in CAM16-UCS that is centered on gray and fits in the sRGB
gamut.  Linearly interpolating in CAM16-UCS between any point on
this circle and black does not leave the sRGB gamut, so it is
appropriate for displaying complex numbers or two-dimensional
real vectors.

The lack of contrast in isoluminant color maps means they are not
very good for purely angular data.  For that reason there is
another cyclic Chromophile color map.  This color map is intended
for angular data in which one angle is more important than the
others.  One of the angles, :math:`\theta_0`, will be dark, while
its antipode, :math:`\theta_1`, will be light.  In between,
:math:`J'` varies linearly with the angle.  If :math:`J'_0` and
:math:`J'_1` are the uniformized lightnesses at :math:`\theta_0`
and :math:`\theta_1`, and if :math:`\theta` is any angle, then
the :math:`J'` coordinate at angle :math:`\theta` is

.. math::

   J'_0 + (J'_1 - J'_0)\frac{d(\theta, \theta_0)}{180^\circ},

where :math:`d(\theta, \theta_0)` is the angular distance
:math:`\min_{k \in \ZZ} \abs{\theta - \theta_0 + k \cdot
360^\circ}`.  The name of this color map follows the format

   :samp:`cp_cyc_{<dark color>}_{<light color>}_{<variant>}`

The "valley" variant begins with its darkest color (in the
valley, so to speak).  It is lightest halfway through and returns
to dark colors at the end.  The "hill" variant begins and ends
light and is darkest in the middle.  The names "hill" and
"valley" are meant to evoke the behavior of the color maps at 0°
under the assumption that the angles being colored are between 0°
and 360°.  The names, however, are imperfect; if the angles being
colored are between −180° and 180°, then the behavior is
reversed.  In any case, before the angles being displayed are
mapped to colors, they should be rotated so that the viewer's
attention is drawn to the angles of greatest interest.  

The parameters of the cyclic Chromophile color maps are:

.. list-table::
   :header-rows: 1
   :class: table-col-2-r table-col-3-r table-col-4-r table-col-5-r table-col-6-r table-col-7-r

   * - Name
     - :math:`M'`
     - :math:`J_0'`
     - :math:`J_1'`
     - :math:`\Delta J'`
     - :math:`h_0`
     - :math:`h_1`
   * - :code:`cp_cyc_isolum_dark`
     - 17.62
     - 33.01
     - 33.01
     - 0.00
     - 0.00°
     - 180.00°
   * - :code:`cp_cyc_isolum_light`
     - 17.62
     - 83.01
     - 83.01
     - 0.00
     - 0.00°
     - 180.00°
   * - :code:`cp_cyc_isolum_wide`
     - 26.25
     - 72.43
     - 72.43
     - 0.00
     - 0.00°
     - 180.00°
   * - :code:`cp_cyc_red_cyan_valley`
     - 20.00
     - 10.42
     - 94.98
     - 84.56
     - -30.35°
     - 149.65°

Isoluminant cyclic color maps are even more hostile to color
vision deficient viewers than other isoluminant color maps.
These color maps will always be unsuitable for dichromats because
every color represents two different angles.  We do not know of
any way to improve the usability of these color maps for
dichromat viewers.

:code:`cp_cyc_red_cyan_valley` is kinder to everyone, but it is
not especially kind to those with color vision deficiency.  A
data angle's distance from the angle being highlighted is visible
from its lightness, but there are two possible data angles at
each distance, and they can be distinguished only by color.
Trichromats will always be able to tell the two possibilities
apart, but dichromats might not.  Our initial search found two
cyclic color maps with large :math:`\Delta J'`, which we called
:code:`cp_cyc_red_cyan_valley` and
:code:`cp_cyc_blue_yellow_valley`.  The former was acceptable for
viewers with protanopia and deuteranopia but poor for those with
tritanopia; the latter turned out the other way.  We considered
trying to split the difference.  The compromise color map, which
would have been :code:`cp_cyc_purple_green_valley`, still had a
large :math:`\Delta J'`, but it was not really acceptable for
viewers with any type of color vision deficiency.  As with the
isoluminant Chromophile color maps, it seemed best to provide
color maps which met the needs of as many viewers as possible, so
we included :code:`cp_cyc_red_cyan_valley` and omitted the
others.
