"""
Print formatted color information
"""

import decimal
import itertools
import math

import numpy as np


def q(x, _quantization_param=decimal.Decimal('1e-10')):
    return f"{decimal.Decimal(x).quantize(_quantization_param):15f}"


def table(entry_strs, spacing=3, columns=160):
    max_len = max(max(map(len, entry)) for entry in entry_strs)
    intercolumn_space = max_len + spacing
    max_entries_per_row = columns // intercolumn_space

    num_entries = len(entry_strs)
    num_rows = math.ceil(num_entries / max_entries_per_row)

    row_strs = [[] for i in range(num_rows)]
    for entry, row in zip(entry_strs, itertools.cycle(row_strs)):
        row.append(entry)

    final_strs = []
    for row in row_strs:
        for row_entry in itertools.zip_longest(*row, fillvalue=""):
            padded_strs = []
            for s in row_entry:
                padded_strs.append(s + " " * (intercolumn_space - len(s)))
            final_strs.append("".join(padded_strs))
        final_strs.append("")

    return "\n".join(final_strs)


def color(c_uniform):
    return '  '.join(map(q, c_uniform))


def color_long(c_uniform=None, c_sRGB256=None, c_sRGB1=None):
    if c_uniform is not None:
        chroma = np.hypot(*c_uniform[1:3])
        hue = np.arctan2(c_uniform[2], c_uniform[1]) * 180. / np.pi
        unif_strs = (
            f"Lightness:      {q(c_uniform[0])}",
            f"Chromaticity 0: {q(c_uniform[1])}",
            f"Chromaticity 1: {q(c_uniform[2])}",
            f"Chroma:         {q(chroma)}",
            f"Hue:            {q(hue)}",
            )
    else:
        unif_strs = ()

    if c_sRGB256 is not None:
        sRGB256_strs = (
            f"sRGB256:          "
            f"{c_sRGB256[0]:3}, {c_sRGB256[1]:3}, {c_sRGB256[2]:3}",
            )
    else:
        sRGB256_strs = ()

    if c_sRGB1 is not None:
        sRGB1_strs = (
            f"sRGB 1 R:       {q(c_sRGB1[0])}",
            f"sRGB 1 G:       {q(c_sRGB1[1])}",
            f"sRGB 1 B:       {q(c_sRGB1[2])}",
            )
    else:
        sRGB1_strs = ()

    return unif_strs + sRGB256_strs + sRGB1_strs


def colors(*name_color_tuples):
    color_strs = []
    for name, *color_data in name_color_tuples:
        entry_strs = color_long(*color_data)
        entry_strs = (name, *(f"  {s}" for s in entry_strs))
        color_strs.append(entry_strs)

    return table(color_strs)


def _format_angles(h0, delta_h):
    h0 = ((h0 + 180) % 360) - 180
    h1 = h0 + delta_h

    if delta_h > 360 or delta_h < -360:
        h1 = ((h1 + 180) % 360) - 180
    else:
        if h1 > 180 and h0 > 180:
            h0 -= 360
            h1 -= 360
        if h1 < -180 and h0 < -180:
            h0 += 360
            h1 += 360

    # Prevent "-0.00"
    if abs(h0) < 0.005:
        h0 = 0.0
    if abs(h1) < 0.005:
        h1 = 0.0
    if abs(delta_h) < 0.005:
        delta_h = 0.0

    return h0, h1, delta_h


def format_angles_tex(h0, delta_h):
    h0, h1, delta_h = _format_angles(h0, delta_h)

    return (*(rf"${x:.02f}^\circ$" for x in (h0, h1, delta_h)),)


def format_angles_rst(h0, delta_h):
    h0, h1, delta_h = _format_angles(h0, delta_h)

    return (
        *(
            f"{x:.02f}\N{DEGREE SIGN}".replace("-", "\N{MINUS SIGN}")
            for x in (h0, h1, delta_h)
        ),
        )


def format_params_tex(state):
    cm = state['cmap']

    if state['type'] == 'Gray':
        pass
    elif state['type'] == 'Multisequential':
        if 'isolum' not in state['name']:
            print(r" \cmap{" f"{state['name']}" "}", end="")
            print(f" & ${100 * cm['initial_lightness']:.02f}$", end="")
            print(f" & ${100 * cm['final_lightness']:.02f}$", end="")
            Jp_diff = 100 * (
                cm['final_lightness'] - cm['initial_lightness']
                )
            print(f" & ${Jp_diff:.02f}$", end="")
            for angle_str in format_angles_tex(
                    cm['sequence_data'][0], cm['sequence_data'][1]
                    ):
                print(f" & {angle_str}", end="")
            print(r" \\")
            num_seqs = len(cm['sequence_data']) // 2
            for seq_num in range(1, num_seqs):
                print(" & & &", end="")
                for angle_str in format_angles_tex(
                        cm['sequence_data'][2 * seq_num],
                        cm['sequence_data'][2 * seq_num + 1],
                        ):
                    print(f" & {angle_str}", end="")
                print(r" \\")
        elif state['parameters']['cylinder']:
            print(fr" \cmap{{{state['name']}_dark}}", end="")
            print(f" & ${100 * cm['chroma']:.02f}$", end="")
            print(f" & ${100 * cm['initial_lightness']:.02f}$", end="")
            for angle_str in format_angles_tex(
                    cm['sequence_data'][0], cm['sequence_data'][1]
                    ):
                print(f" & {angle_str}", end="")
            print(r" \\")
            print(fr" \cmap{{{state['name']}_light}}", end="")
            print(f" & ${100 * cm['chroma']:.02f}$", end="")
            print(f" & ${100 * cm['final_lightness']:.02f}$", end="")
            for angle_str in format_angles_tex(
                    cm['sequence_data'][0], cm['sequence_data'][1]
                    ):
                print(f" & {angle_str}", end="")
            print(r" \\")
        else:
            print(fr" \cmap{{{state['name']}}}", end="")
            print(f" & ${100 * cm['chroma']:.02f}$", end="")
            print(f" & ${100 * cm['initial_lightness']:.02f}$", end="")
            for angle_str in format_angles_tex(
                    cm['sequence_data'][0], cm['sequence_data'][1]
                    ):
                print(f" & {angle_str}", end="")
            print(r" \\")
    elif state['type'] == 'Divergent':
        print(r" \cmap{" f"{state['name']}" "}", end="")
        print(f" & ${100 * cm['initial_lightness']:.02f}$", end="")
        print(f" & ${100 * cm['final_lightness']:.02f}$", end="")
        Jp_diff = 100 * (cm['final_lightness'] - cm['initial_lightness'])
        print(f" & ${Jp_diff:.02f}$", end="")
        for angle_str in format_angles_tex(
                cm['sequence_data'][0], cm['sequence_data'][1]
                ):
            print(f" & {angle_str}", end="")
        print(r" \\")
        print(" & & &", end="")
        for angle_str in format_angles_tex(
                cm['sequence_data'][2], cm['sequence_data'][3]
                ):
            print(f" & {angle_str}", end="")
        print(r" \\")
    elif state['type'] == 'Cyclic':
        if state['parameters']['cylinder']:
            print(r" \cmap{" f"{state['name']}" "_dark}", end="")
            print(f" & ${100 * cm['chroma']:.02f}$", end="")
            print(f" & ${100 * cm['initial_lightness']:.02f}$", end="")
            print(f" & ${100 * cm['initial_lightness']:.02f}$", end="")
            print(" & $0.00$ & $0.00^\\circ$ & $180.00^\\circ$", end="")
            print(r" \\")
            print(r" \cmap{" f"{state['name']}" "_light}", end="")
            print(f" & ${100 * cm['chroma']:.02f}$", end="")
            print(f" & ${100 * cm['final_lightness']:.02f}$", end="")
            print(f" & ${100 * cm['final_lightness']:.02f}$", end="")
            print(" & $0.00$ & $0.00^\\circ$ & $180.00^\\circ$", end="")
            print(r" \\")
        else:
            print(r" \cmap{" f"{state['name']}" "}", end="")
            print(f" & ${100 * cm['chroma']:.02f}$", end="")
            print(f" & ${100 * cm['initial_lightness']:.02f}$", end="")
            print(f" & ${100 * cm['final_lightness']:.02f}$", end="")
            Jp_diff = 100 * (
                cm['final_lightness'] - cm['initial_lightness']
                )
            print(f" & ${Jp_diff:.02f}$", end="")
            angle = ((cm['sequence_data'] + 180) % 360) - 180
            print(f" & ${angle:.02f}^\\circ$", end="")
            antipodal_angle = (cm['sequence_data'] % 360) - 180
            print(f" & ${antipodal_angle:.02f}^\\circ$", end="")
            print(r" \\")


def format_params_rst(state):
    cm = state['cmap']

    if state['type'] == 'Gray':
        pass
    elif state['type'] == 'Multisequential':
        if 'isolum' not in state['name']:
            print(f"   * - :code:`{state['name']}`")
            print(f"     - {100 * cm['initial_lightness']:.02f}")
            print(f"     - {100 * cm['final_lightness']:.02f}")
            Jp_diff = 100 * (
                cm['final_lightness'] - cm['initial_lightness']
                )
            print(f"     - {Jp_diff:.02f}")
            for angle_str in format_angles_rst(
                    cm['sequence_data'][0], cm['sequence_data'][1]
                    ):
                print(f"     - {angle_str}")
            num_seqs = len(cm['sequence_data']) // 2
            for seq_num in range(1, num_seqs):
                print(f"   * -")
                print(f"     -")
                print(f"     -")
                print(f"     -")
                for angle_str in format_angles_rst(
                        cm['sequence_data'][2 * seq_num],
                        cm['sequence_data'][2 * seq_num + 1],
                        ):
                    print(f"     - {angle_str}")
        elif state['parameters']['cylinder']:
            print(f"   * - :code:`{state['name']}_dark`")
            print(f"     - {100 * cm['chroma']:.02f}")
            print(f"     - {100 * cm['initial_lightness']:.02f}")
            for angle_str in format_angles_rst(
                    cm['sequence_data'][0], cm['sequence_data'][1]
                    ):
                print(f"     - {angle_str}")
            print(f"   * - :code:`{state['name']}_light`")
            print(f"     - {100 * cm['chroma']:.02f}")
            print(f"     - {100 * cm['final_lightness']:.02f}")
            for angle_str in format_angles_rst(
                    cm['sequence_data'][0], cm['sequence_data'][1]
                    ):
                print(f"     - {angle_str}")
        else:
            print(f"   * - :code:`{state['name']}`")
            print(f"     - {100 * cm['chroma']:.02f}")
            print(f"     - {100 * cm['initial_lightness']:.02f}")
            for angle_str in format_angles_rst(
                    cm['sequence_data'][0], cm['sequence_data'][1]
                    ):
                print(f"     - {angle_str}")
    elif state['type'] == 'Divergent':
        print(f"   * - :code:`{state['name']}`")
        print(f"     - {100 * cm['initial_lightness']:.02f}")
        print(f"     - {100 * cm['final_lightness']:.02f}")
        Jp_diff = 100 * (
            cm['final_lightness'] - cm['initial_lightness']
            )
        print(f"     - {Jp_diff:.02f}")
        for angle_str in format_angles_rst(
                cm['sequence_data'][0], cm['sequence_data'][1]
                ):
            print(f"     - {angle_str}")
        print(f"   * -")
        print(f"     -")
        print(f"     -")
        print(f"     -")
        for angle_str in format_angles_rst(
                cm['sequence_data'][2], cm['sequence_data'][3],
                ):
            print(f"     - {angle_str}")
    elif state['type'] == 'Cyclic':
        if state['parameters']['cylinder']:
            print(f"   * - :code:`{state['name']}_dark`")
            print(f"     - {100 * cm['chroma']:.02f}")
            print(f"     - {100 * cm['initial_lightness']:.02f}")
            print(f"     - {100 * cm['initial_lightness']:.02f}")
            print(f"     - 0.00")
            print(f"     - 0.00\N{DEGREE SIGN}")
            print(f"     - 180.00\N{DEGREE SIGN}")
            print(f"   * - :code:`{state['name']}_light`")
            print(f"     - {100 * cm['chroma']:.02f}")
            print(f"     - {100 * cm['final_lightness']:.02f}")
            print(f"     - {100 * cm['final_lightness']:.02f}")
            print(f"     - 0.00")
            print(f"     - 0.00\N{DEGREE SIGN}")
            print(f"     - 180.00\N{DEGREE SIGN}")
        else:
            print(f"   * - :code:`{state['name']}`")
            print(f"     - {100 * cm['chroma']:.02f}")
            print(f"     - {100 * cm['initial_lightness']:.02f}")
            print(f"     - {100 * cm['final_lightness']:.02f}")
            Jp_diff = 100 * (
                cm['final_lightness'] - cm['initial_lightness']
                )
            print(f"     - {Jp_diff:.02f}")
            angle = ((cm['sequence_data'] + 180) % 360) - 180
            print(f"     - {angle:.02f}\N{DEGREE SIGN}")
            antipodal_angle = (cm['sequence_data'] % 360) - 180
            print(f"     - {antipodal_angle:.02f}\N{DEGREE SIGN}")
