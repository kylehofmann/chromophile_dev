.. _approximation:

Approximation by sRGB colors
============================

Problems caused by approximation
--------------------------------

In the previous section, we described color maps as curves in a
uniform color space.  The most common standard for computer
displays, however, is sRGB :cite:p:`sRGB`, which is not a uniform
color space.  Because sRGB is intended as a standard for hardware
capabilities, it is not appropriate for designing color maps.
Displaying a color map on a computer requires converting from a
uniform color space to sRGB, but this introduces several
complications.

The first complication is the limited color palette.  sRGB
expresses colors in terms of red, green, and blue stimuli.  The
standard specifies that :math:`2^8 = 256` intensities of
each stimulus are available, indexed by integers between 0 and
255 inclusive.  The intensities of the three stimuli together
require 24 bits to store, so this bit depth is often referred to
as "24-bit color."  sRGB output devices are not required to
support fractional intensities, so sRGB can express
:math:`(2^8)^3 = 16,777,216` colors and no others.

It is not straightforward to approximate even a single color by
an sRGB color because the colors expressible by sRGB are not
evenly distributed in a uniform color space.  As an example,
consider the :math:`J' = 10` cross-section of CAM16-UCS:

.. image:: /image/CAM16-UCS-10-with-sRGB.svg
   :width: 90%
   :alt: The J' = 10 cross-section of CAM16-UCS with sRGB colors marked
   :align: center

The colors in the picture were sampled on a grid with 65,536
points in each direction.  Each color was converted to sRGB, and
colors requiring a stimulus value below 0 or above 255 were
removed.  The nearest sRGB color to each (measured in CAM16-UCS)
was found; there were 6,069 distinct sRGB colors.  We placed a
circle at the :math:`(a', b')` coordinates of each of these
colors.  The color of each circle is the corresponding sRGB
color, but lightened for visual clarity.  Lightening was done by
translating and linearly rescaling the :math:`J'` values of the
sRGB colors so that they spanned the range from 30 and 90.  The
actual range of :math:`J'` values was 9.568 to 10.498, and the
median :math:`J'` value was 10.008.

As a specific example of a difficult color, consider the color
with CAM16-UCS coordinates :math:`(J', a', b') = (82.0, -23.9,
-15.1)`.  In sRGB coordinates, this color is (9.6, 221.5, 249.1)
(when sRGB coordinates are on a scale of 0 to 255).  The most
obvious possibility is to round this to (10, 222, 249).  The
rounded color has CAM16-UCS coordinates (82.13, -23.99, -14.96),
putting it 0.2088 away from the original color.  But the sRGB
color (1, 222, 250) is 12.3\% better.  When this color is
converted to CAM16-UCS, it has coordinates (82.13, -23.95,
-15.22), which is only 0.1830 away from the original color.

For some colors, the perceived difference between the nearest
sRGB color and the color found by rounding in sRGB coordinates is
even more extreme.  The color with CAM16-UCS coordinates
(2.3, 5.7, 2.2), for example, converts to the sRGB color
(4.281, 0.504, 0.498).  This rounds to (4, 1, 0),
which is (2.48, 2.99, 4.49) in CAM16-UCS.  But the sRGB
color (6, 1, 1) converts to (2.94, 5.72, 2.09),
which is 5.47 times closer to the original color!

This problem can be avoided by transforming all :math:`2^{24}`
sRGB colors into the uniform color space and storing them in a
:math:`k`-d tree :cite:p:`Bentley`.  This data structure allows
us to efficiently list the closest sRGB points to any color in
the uniform color space we choose.  We used the :math:`k`-d tree
implementation in SciPy :cite:p:`2020SciPy-NMeth`.

There are three other issues with sRGB approximation that are
specific to color map construction.

#. Two or more distinct colors in the uniform color space may
   have the same sRGB color as their best approximation.  This is
   called *posterization* or *banding*, and it decreases the
   amount of information communicated by the color map.
#. Successive colors may be intended to have increasing values of
   :math:`J'`, but their best sRGB approximations may have
   decreasing values of :math:`J'` instead (or vice versa).  Such
   reversals cause unwanted high-frequency artifacts in the final
   visualization.
#. Similarly, successive colors may be intended to have
   increasing hue angles, but their best sRGB approximations may
   have decreasing hue angles instead (or vice versa).

Because hue mostly communicates low-frequency information, we did
not believe that slightly misordered hue angles would cause
problems for viewers.  For that reason, we directed our efforts
towards only the first two of the above problems.

An approximation algorithm
--------------------------

Our solution to these problems is an application of the
:math:`A^*`-algorithm :cite:p:`RN`.  Each step of the algorithm
begins with an approximation to some of the colors in the color
map, extends it by finding approximations to one of the remaining
colors, and inserts the newly extended approximations into a
priority queue.  The algorithm discards any color map with
posterization or misordered lightnesses.

Here is a description of our algorithm in Python-like pseudocode.
The description uses a function :code:`sRGB_nearest_neighbors`
whose arguments are a color :code:`c` and a positive integer
:code:`n` and which returns a list of the :code:`n` nearest sRGB
colors to :code:`c`.  (In practice this was implemented with a
:math:`k`-d tree.)  By replacing this function, the algorithm
could be used to approximate a color map by a gamut other than
sRGB.

.. code:: python

  def approximate_color_map(colors, max_neighbors):
      H = PriorityQueue()
      H.insert(empty_color_map(), key=0)      # This key does not matter

      while H.nonempty():
          partial_color_map = H.pop()
          t = len(partial_color_map)
          if t == len(colors):
              return partial_color_map

          if t > 0 and colors[t].is_lighter_than(colors[t-1]):
              s = 1
          elif t > 0 and colors[t].is_darker_than(colors[t-1]):
              s = -1
          else:
              s = 0

          for y in sRGB_nearest_neighbors(colors[t], max_neighbors[t]):
              if y in partial_color_map:
                  continue
              if s > 0 and y.is_darker_than(partial_color_map[t-1]):
                  continue
              if s < 0 and y.is_lighter_than(partial_color_map[t-1]):
                  continue

              extended_partial_color_map = partial_color_map.append(y)
              score = heuristic_score(colors, extended_partial_color_map)
              H.insert(extended_partial_color_map, key=score)

      # No sRGB approximation satisfying the desired conditions exists
      return None


  def heuristic_score(colors, extended_partial_color_map):
      heuristic_color_map = extended_partial_color_map.copy()
      for i in range(len(extended_partial_color_map), len(colors)):
          heuristic_color_map.append(sRGB_nearest_neighbors(colors[i], 1)[0])
      return squared_distance(colors, heuristic_color_map)

It is easy to verify that this algorithm does what it is supposed
to:

.. topic:: Theorem

   If the return value of :code:`approximate_color_map` is not
   :code:`None`, then it is a color map
   :code:`sRGB_approximation` with the following properties:

   #. The colors in :code:`sRGB_approximation` are distinct sRGB
      colors.

   #. :code:`sRGB_approximation[i]` is one of the
      :code:`max_neighbors[i]` nearest sRGB approximations to
      :code:`colors[i]`.

   #. For every :code:`i > 0`, if :code:`colors[i]` is lighter
      than :code:`colors[i-1]`, then
      :code:`sRGB_approximation[i]` is lighter than
      :code:`sRGB_approximation[i-1]`; and vice versa if
      :code:`colors[i]` is darker than :code:`colors[i-1]`.

   Furthermore, the root mean square error in the approximation
   of :code:`colors` by :code:`sRGB_approximation` is as small as
   possible among all sequences of sRGB colors with the above
   properties.

   If the return value of :code:`approximate_color_map` is
   :code:`None`, then there is no sequence of sRGB colors with
   the above properties.

.. topic:: Proof

   Because :code:`approximate_color_map` is an instance of the
   :math:`A^*`-algorithm, and because :code:`heuristic_score` is
   a consistent heuristic for the square error, the result is
   either :const:`None` or has the minimum possible square error.
   The root mean square error is a monotonic function of the
   square error, so it is minimized if and only if the square
   error is.

   The algorithm returns an entry of :code:`H`.  Every entry
   added to :code:`H` satisfies the conclusions of the theorem
   (for those :code:`i` where the entry has chosen an
   approximation to :code:`colors[i]`), so the final color map
   does, too.

Improvements to the approximation algorithm
-------------------------------------------

While :code:`sRGB_nearest_neighbors` is already useful in
practice, it can be improved in several ways.

Coalescence
'''''''''''

Call each entry of :code:`H` a "partial color map approximation."
When late colors in the input color map are far away from early
colors, two partial color map approximations may coalesce: They
may differ in their first few entries but not in their later
entries.  When :code:`sRGB_nearest_neighbors` tries to extend
these partial color map approximations, it extends them in the
same way, producing more pairs of color maps that differ only in
their early entries.  This is wasted effort, because one of these
two partial color map approximations was a better approximation
of the early colors in :code:`colors`, and that partial color map
is the only one worth further attention.

To make the :code:`sRGB_nearest_neighbors` appreciate this, it
can be augmented with an associative array :code:`A` that maps
sets of colors to lightnesses.  The array is initialized to empty
at the time :code:`H` is created.  After determining :code:`s`,
the algorithm tests for coalescence as follows.  It creates a set
containing, for all :code:`i` greater than :code:`t`, the
:code:`max_neighbors[i]` nearest sRGB colors to
:code:`colors[i]`, omitting those colors already in
:code:`partial_color_map`.  This set :code:`k` is used as the key
for :code:`A`.  If :code:`k` is present in :code:`A`, then the
algorithm looks up the corresponding value and tests :code:`s`.
If :code:`s == 1` and :code:`partial_color_map[t]` is lighter
than the stored lightness, or if :code:`s == -1` and
:code:`partial_color_map[t]` is darker than the stored lightness,
or if :code:`s == 0`, then the algorithm skips
:code:`partial_color_map`  and returns to the beginning of the
loop.  Otherwise, the algorithm modifies :code:`A` so that
:code:`k` is associated to the lightness of
:code:`partial_color_map[t]`.  (For the empty color map, the
value is a placeholder such as zero.)

Scoring
'''''''

Another way to improve :code:`sRGB_nearest_neighbors` is to
improve :code:`heuristic_score`.  A better (but still consistent)
score is the same as a tighter lower bound on the minimum error
for a completion of :code:`extended_partial_color_map` to an
approximation of all of :code:`colors` satisfying the conclusions
of the theorem.

One way to create better lower bounds is to enforce more
constraints on the colors used to extend the partial color map.
For instance, the final color map consists of distinct colors, so
ideally :code:`heuristic_color_map` should also consist of
distinct colors.  For simplicity, we did not actually try to make
all the colors in :code:`heuristic_color_map` distinct.  Instead,
after creating :code:`heuristic_color_map`, we tested it for
duplicate entries.  If there were indices :code:`i1` through
:code:`ik` such that :code:`heuristic_color_map[i1]` through
:code:`heuristic_color_map[ik]` were the same color, then we
replaced all but one of them by a worse sRGB approximation.
Specifically, if one of these entries was part of
:code:`extended_partial_color_map`, then that entry was left
unchanged, while the others were switched to the second-best sRGB
approximations of the corresponding entries in :code:`colors`;
otherwise, the entry corresponding to the color with the largest
distance between its best and second-best sRGB approximations was
left at the best sRGB approximation, while the others were
switched to second-best approximations.

More elaborate consistent heuristics are possible.  For example,
if three or more colors in :code:`colors` share the same best
sRGB approximation, then we could use a small instance of the
:math:`A^*`-algorithm to find the minimum error way of assigning
distinct sRGB approximations to just these colors.  We could also
try to force :code:`heuristic_color_map` to satisfy, or come
closer to satisfying, the lightness consistency requirement.  We
have not pursued these possibilities.

Multiple passes
'''''''''''''''

Since there are millions of sRGB colors, testing every possible
approximation of every color in :code:`colors` quickly runs out
of memory.  There is little harm in having a bound such as
:code:`max_neighbors` because each color in :code:`colors` has
only a small number of reasonable sRGB approximations.  Unless
:code:`max_neighbors` contains extremely small entries, the final
color map is suboptimal only if making an especially bad
approximation to one color mysteriously improves the
approximations of the other colors.  This should never happen in
any realistic situation.  However, it is not easy to rule it out
with absolute certainty, which makes the presence of
:code:`max_neighbors` a little irksome.

One possible solution to this is to run the algorithm twice in a
branch-and-bound fashion.  The first time, :code:`max_neighbors`
is taken to be fairly small, enough to guarantee that there are
only a few approximations to each color.  If the output is
:const:`None`, :code:`max_neighbors` is increased and the
algorithm is run again.  Once the algorithm outputs a color map,
that color map determines an upper bound on the square error of
the best approximation.  It is not necessary to consider an sRGB
approximation to a color if it, when combined with the nearest
sRGB approximations to the other colors, would produce more
approximation error than the bound.  This allows us to set
:code:`max_neighbors[i]` so that we produce a minimum error
approximation without considering every possible sRGB color.
(There is one complication to this claim, namely the presence of
floating-point approximation errors.  A provably correct
computation would need to use interval arithmetic.  We did not
attempt this.)

We tried this branch-and-bound method on the Chromophile color
maps.  The color maps had three distinct behaviors.  It was
possible for the first pass to produce a color map with so little
error that there was no need to run the second pass.  This
happened when the upper bound resulting from the first pass was
so tight that the second pass would never have considered more
colors than the first pass.  In these cases,
:code:`max_neighbors` could have been reduced.  The second
behavior was that the second pass considered more colors than the
first pass but arrived at the same final result.  The final
behavior was that our methods were not powerful enough for the
second pass to finish in a reasonable amount of time.  Usually,
these were color maps where the first pass had a large square
error (such as :code:`cp_seq_gray`) or which had a large number
of colors (such as :code:`cp_mseq_orange_green_blue_purple`).
There were no cases where the second pass terminated with
different output from the first pass.
