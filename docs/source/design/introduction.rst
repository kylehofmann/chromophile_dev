.. _design_introduction:

Introduction
============

The human vision system is a powerful tool for communicating
data.  One method for doing so is color.  A good color map brings
features of the data into focus without distorting them or
creating artifacts.  However, the complexity of the human visual
system makes these difficult to design.  Many previous authors
have nevertheless constructed high-quality general purpose color
maps for this type of data :cite:p:`Brewer` :cite:p:`CSH`
:cite:p:`Kovesi` :cite:p:`Moreland` :cite:p:`NAR` :cite:p:`SvdW`
:cite:p:`TGHZD`.  The Chromophile color maps are descendents of
their work.  The driving principle behind the Chromophile color
maps is fidelity to the original data.  They may be an adequate
starting point for artistic visualizations, but that is not their
primary purpose.

The first part of this document describes what it means for a
color map to be faithful to the original data.  The second
details an approximation algorithm used to construct the color
maps.  This section is relatively technical, and the details
should be skipped on a first reading.  The third and longest
section describes the color maps themselves.  The final two
sections, which are much shorter, list some known limitations and
make some remarks on the implementation.
