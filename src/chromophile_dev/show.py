import collections
import importlib
import importlib.util
import itertools
import pathlib
import re
import sys

import PIL
import bokeh.io
import bokeh.layouts
import bokeh.plotting
import click
import matplotlib.pyplot as plt
import numpy as np

from . import conversion


def search_cmap_names(cp, regexp, include_aliases):
    if include_aliases:
        cmaps = cp._cmaps
    else:
        cmaps = cp._parsed_cmap_data

    cmap_names = [name for name, _ in cmaps if re.search(regexp, name)]
    parsed_cmap_names = []
    for name in cmap_names:
        _, cmap_type, remainder = name.split('_', 2)
        if cmap_type == 'div':
            remainder, div_type = remainder.rsplit('_', 1)
            parsed_cmap_names.append(((cmap_type, div_type, remainder), name))
        else:
            parsed_cmap_names.append(((cmap_type, remainder), name))

    parsed_cmap_names.sort()
    sorted_cmap_names = [name for _, name in parsed_cmap_names]
    return sorted_cmap_names


@click.group()
@click.option(
    '--chromophile',
    '-c',
    type=click.Path(exists=True, path_type=pathlib.Path),
    help="Path to Chromophile module",
    )
@click.option(
    '--file',
    '-f',
    type=click.File('rb'),
    multiple=True,
    help="Color map file to show",
    )
@click.option(
    '--include-aliases/--exclude-aliases',
    default=False,
    help="Whether color map aliases should be included during regexp search",
    )
@click.option(
    '--regexp',
    '-r',
    help="Regular expression for Chromophile color maps to show",
    )
@click.option(
    '--output',
    '-o',
    type=click.Path(path_type=pathlib.Path),
    help="Directory or file to output color bars to",
    )
@click.option(
    '--display/--no-display',
    '-d',
    default=False,
    help="Display color bars",
    )
@click.pass_context
def show(ctx, chromophile, include_aliases, file, regexp, output, display):
    """Show a color map as a color bar"""

    ctx.ensure_object(dict)
    obj = ctx.obj

    if chromophile is not None:
        if chromophile.name == 'chromophile':
            sys.path.insert(0, str(chromophile.parent))
        else:
            sys.path.insert(0, str(chromophile))

    chromophile_mod = importlib.import_module('chromophile')

    if regexp is not None:
        cmap_names = search_cmap_names(
            chromophile_mod, regexp, include_aliases,
            )
        if not cmap_names:
            ctx.fail("No color maps found")
    else:
        cmap_names = []

    cmap_file = {}
    for f in file:
        cmap_file[pathlib.Path(f.name).stem] = f.read()

    obj['chromophile'] = chromophile_mod
    obj['cmap_names'] = cmap_names
    obj['cmap_file'] = cmap_file
    obj['output'] = output
    obj['display'] = display


@show.command("pillow")
@click.pass_obj
def cmd_pillow(obj):
    all_bytes = {}

    cmap_dict = dict(obj['chromophile']._cmaps)
    for name in obj['cmap_names']:
        cmap_list = cmap_dict[name]
        cmap_bytes = b''.join(map(bytes, cmap_list))
        all_bytes[name] = cmap_bytes

    all_bytes.update(obj['cmap_file'])

    for name, cmap_bytes in all_bytes.items():
        im = PIL.Image.frombytes('RGB', (len(cmap_bytes) // 3, 1), cmap_bytes)
        if obj['output']:
            im.save((obj['output'] / name).with_suffix('.png'))
        if obj['display']:
            im.show()


@show.command("mpl")
@click.pass_obj
def cmd_mpl(obj):
    all_cmaps = {}

    for name, cmap_bytes in obj['cmap_file'].items():
        cmap_ints = np.frombuffer(cmap_bytes, dtype=np.uint8)
        all_cmaps[name] = conversion.sRGB256_to_mpl(
            cmap_ints.reshape((len(cmap_bytes) // 3, 3))
            )

    all_cmaps.update(
        {name: obj['chromophile'].cmap[name] for name in obj['cmap_names']}
        )

    title_height = 0.4
    cmap_height = 0.4
    total_height = title_height + cmap_height * len(all_cmaps)

    cbar_top = 1. - title_height / total_height

    fig, axs = plt.subplots(nrows=len(all_cmaps), figsize=(8.0, total_height))
    if len(all_cmaps) == 1:
        axs = (axs,)

    fig.subplots_adjust(
        top=cbar_top, bottom=0.01, left=0.28, right=0.99, wspace=0.05,
        )
    fig.suptitle(
        'Chromophile color maps',
        fontsize=14,
        x=0.5, y=cbar_top + 0.7 * title_height / total_height,
        )

    for ax, (name, cmap) in zip(axs, all_cmaps.items()):
        cbar_im = np.linspace(0., 1., cmap.colors.shape[0])[None, :]
        ax.imshow(cbar_im, aspect='auto', cmap=cmap)
        im_left, im_bottom, im_width, im_height = ax.get_position().bounds
        text_pos_x = im_left - 0.01
        text_pos_y = im_bottom + im_height / 2.
        fig.text(
            text_pos_x, text_pos_y, name, va='center', ha='right', fontsize=10,
            )

        ax.set_axis_off()

    if obj['output']:
        fig.savefig(obj['output'])
    if obj['display']:
        plt.show()


@show.command("bokeh")
@click.pass_obj
def cmd_bokeh(obj):
    all_palettes = {}

    for name, cmap_bytes in obj['cmap_file'].items():
        cmap_ints = np.frombuffer(cmap_bytes, dtype=np.uint8)
        all_palettes[name] = (
            *itertools.starmap(
                "#{0:02x}{1:02x}{2:02x}".format,
                cmap_ints.reshape((len(cmap_bytes) // 3, 3))
                ),
            )

    all_palettes.update(
        {name: obj['chromophile'].palette[name] for name in obj['cmap_names']}
        )

    im = np.empty((8, 256), dtype=np.float64)
    im[:] = np.arange(256)[None, :]

    figures = []
    for name, pal in all_palettes.items():
        p = bokeh.plotting.figure(
            title=name, height=100, width=600, toolbar_location=None,
            )

        p.x_range.range_padding = 0
        p.y_range.range_padding = 0
        p.xaxis.major_tick_line_color = None
        p.xaxis.minor_tick_line_color = None
        p.yaxis.major_tick_line_color = None
        p.yaxis.minor_tick_line_color = None
        p.xaxis.major_label_text_font_size = '0pt'
        p.yaxis.major_label_text_font_size = '0pt'

        p.image(image=[im], x=0, y=0, dw=255, dh=1, palette=pal)
        figures.append(p)

    fig_layout = bokeh.layouts.layout(figures)

    if obj['output']:
        bokeh.io.output_file(obj['output'], title="Chromophile color maps")
        bokeh.io.save(fig_layout, filename=obj['output'])
    if obj['display']:
        bokeh.io.show(fig_layout)


@show.command("rst-table")
@click.pass_obj
def cmd_rst_table(obj):
    if 'cmap_bytes' in obj:
        raise NotImplementedError(
            "RST table output not supported for file input"
            )

    cmap_to_aliases = collections.defaultdict(list)
    for alias, cmap_name in obj['chromophile']._expanded_aliases:
        cmap_to_aliases[cmap_name].append(alias)

    print(
        ".. list-table::",
        "   :stub-columns: 1",
        "",
        sep='\n',
        )

    for name in obj['cmap_names']:
        print(f"   * - | :code:`{name}`")
        for alias in cmap_to_aliases[name]:
            print(f"       | :code:`{alias}`")

        print(
            f"     - .. image:: /image/{name}.png",
            "          :height: 4ex",
            "          :width: 100%",
            f"          :alt: {name}",
            "          :align: center",
            sep='\n',
            )
