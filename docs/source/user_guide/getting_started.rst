.. _getting-started:

Getting started
===============

Installation
------------

The Chromophile color maps are distributed as a Python package.
To install it, open a terminal and execute:

.. code-block:: bash

   pip install chromophile

Or, in IPython or Jupyter, use the :code:`%pip` magic command:

.. code-block:: ipython

   %pip install chromophile

The :mod:`chromophile` package has no required dependencies.  To
use the Chromophile color maps with `Matplotlib
<https://matplotlib.org/>`_, the :mod:`matplotlib` package must
be available at the time the :mod:`chromophile` package is
imported.

The tools used to develop the Chromophile color maps are in a
separate package called `chromophile-dev
<https://github.com/kylehofmann/chromophile_dev/>`_.  Most users
will not need this package.

Usage
-----

To use the color maps, import the Chromophile package:

>>> import chromophile as cp

The Chromophile color maps are stored in two formats:

* Matplotlib :class:`Colormap <matplotlib.colors.Colormap>`
  objects are stored in :data:`cp.cmap <chromophile.cmap>`.  If
  Matplotlib is not available, :data:`cmap <chromophile.cmap>`
  will equal :data:`None`.  The color maps are also added to
  Matplotlib's color map registry.  

* `Bokeh <https://bokeh.org/>`_ palettes are stored in
  :data:`cp.palette <chromophile.palette>`.

Individual color maps can be accessed either as dictionary items
or as attributes of these objects.  For example:

>>> cp.cmap.cp_dawn
<matplotlib.colors.ListedColormap object at ...>
>>> cp.palette['cp_peacock']
('#06003c', '#06013d', '#06023e', '#07043e', ...)

The same color map is returned regardless of how it is accessed:

>>> cp.cmap.cp_lemon_lime is cp.cmap['cp_lemon_lime']
True
>>> cp.palette.cp_blue is cp.palette['cp_blue']
True

Most IDEs should support autocompletion for
:data:`cmap <chromophile.cmap>` and
:data:`palette <chromophile.palette>`.

The available color maps can be listed using the :meth:`.keys()
<dict.keys>` method of :data:`cmap <chromophile.cmap>` or
:data:`palette <chromophile.palette>` or by calling :func:`dir()`
on either of these objects.  They are also displayed in
the :ref:`list-of-color-maps`.
