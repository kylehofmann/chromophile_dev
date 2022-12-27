import itertools
import warnings

import numpy as np
import matplotlib as mpl
import matplotlib.cm
import matplotlib.colors
import matplotlib.pyplot as plt

from . import conversion, fmt


def mseq_endpoints(
        num_samples_per_seq,
        cmap_uniform,
        cmap_sRGB256,
        ):
    initial_colors_uniform = cmap_uniform[::num_samples_per_seq]
    initial_colors_sRGB256 = cmap_sRGB256[::num_samples_per_seq]
    final_colors_uniform = cmap_uniform[
        num_samples_per_seq - 1::num_samples_per_seq
        ]
    final_colors_sRGB256 = cmap_sRGB256[
        num_samples_per_seq - 1::num_samples_per_seq
        ]

    initial_color_data = []
    for i, (c_unif, c_sRGB256) in enumerate(
            zip(initial_colors_uniform, initial_colors_sRGB256),
            ):
        initial_color_data.append((f'Initial color {i}', c_unif, c_sRGB256))

    final_color_data = []
    for i, (c_unif, c_sRGB256) in enumerate(
            zip(final_colors_uniform, final_colors_sRGB256),
            ):
        final_color_data.append((f'Final color {i}', c_unif, c_sRGB256))

    color_data = itertools.chain.from_iterable(
        zip(initial_color_data, final_color_data)
        )

    return fmt.colors(*color_data)


def mseq_lightness_differences(
        num_samples_per_seq,
        cmap_uniform,
        cmap_sRGB256,
        conversions,
        ):
    num_seqs = cmap_uniform.shape[0] // num_samples_per_seq

    cmap_sRGB256_uniform = conversions['sRGB_to_uniform'](
        conversion.sRGB256_to_sRGB1(cmap_sRGB256)
        )
    cmap_sRGB256_uniform_Jp = cmap_sRGB256_uniform[:, 0]

    lightness_diff_strs = []
    for i in range(num_seqs):
        current_seq_Jp = cmap_sRGB256_uniform_Jp[
            num_samples_per_seq * i:num_samples_per_seq * (i + 1)
            ]
        current_seq_Jp_diff = current_seq_Jp[1:] - current_seq_Jp[:-1]

        min_diff = np.min(current_seq_Jp_diff)
        max_diff = np.max(current_seq_Jp_diff)

        seq_strs = (
           f"Sequence {i}",
           f"  Min J' diff: {fmt.q(min_diff)}",
           f"  Max J' diff: {fmt.q(max_diff)}",
           )

        if min_diff < 0 < max_diff:
            seq_strs += ("  WARNING: Inconsistent sign!",)

        lightness_diff_strs.append(seq_strs)

    return fmt.table(lightness_diff_strs)


def cyclic_quarters(
        cmap_uniform,
        cmap_sRGB256,
        ):
    num_samples = cmap_uniform.shape[-2]
    num_samples_per_quarter = num_samples // 4
    quarters_uniform = cmap_uniform[::num_samples_per_quarter]
    quarters_sRGB256 = cmap_sRGB256[::num_samples_per_quarter]

    color_data = []
    for i, (c_unif, c_sRGB256) in enumerate(
            zip(quarters_uniform, quarters_sRGB256),
            ):
        if i == 0:
            text = "at start of circle"
        elif i == 2:
            text = "1/2 around the circle"
        else:
            text = f"{i}/4 around the circle"

        color_data.append((f'Color {text}', c_unif, c_sRGB256))

    return fmt.colors(*color_data)


def cyclic_lightness_differences(
        cmap_uniform,
        cmap_sRGB256,
        conversions,
        ):
    num_samples_per_half = cmap_uniform.shape[0] // 2

    cmap_sRGB256_uniform = conversions['sRGB_to_uniform'](
        conversion.sRGB256_to_sRGB1(cmap_sRGB256)
        )
    cmap_sRGB256_uniform_Jp = cmap_sRGB256_uniform[:, 0]

    lightness_diff_strs = []
    for i in range(2):
        current_seq_Jp = cmap_sRGB256_uniform_Jp[
            num_samples_per_half * i:num_samples_per_half * (i + 1)
            ]
        current_seq_Jp_diff = current_seq_Jp[1:] - current_seq_Jp[:-1]

        min_diff = np.min(current_seq_Jp_diff)
        max_diff = np.max(current_seq_Jp_diff)

        seq_strs = (
           f"Sequence {i}",
           f"  Min J' diff: {fmt.q(min_diff)}",
           f"  Max J' diff: {fmt.q(max_diff)}",
           )

        if min_diff < 0 < max_diff:
            seq_strs += ("  WARNING: Inconsistent sign!",)

        lightness_diff_strs.append(seq_strs)

    return fmt.table(lightness_diff_strs)


def colorbar(ax, cmap_obj):
    ax.set_xlim((0., 1.))
    ax.set_ylim((0., 1.))

    cbar_im = np.linspace(0., 1., 1024)[None, :]
    ax.imshow(
        cbar_im,
        cmap=cmap_obj,
        aspect='auto',
        extent=(0., 1., 0., 1.),
        )


def test_image(
        max_x=20.0,
        x_samples=2048,
        y_samples=1024,
        ):
    """Construct a test image

    This test image is essentially a continuously varying
    sinusoidal grating.  The frequency of the sinusoid varies
    from lowest at the left to highest at the right, while the
    amplitude varies from largest at the bottom to smallest at
    the top.

    More precisely, the image is a plot of the function

        (1 - y) * sin(x^2)

    for 0 <= x <= max_x and 0 <= y <= 1.  The point is that the
    derivative in the x direction is 2x cos(x^2); and if we just
    look at the peaks, we find that the derivative is basically
    increasing linearly.

    A remark on resolution: If we want to be able to observe each
    cycle clearly, then we need to have a pretty fine resolution
    near the right edge of the plot (and hence everywhere).  In
    addition to that, we are hampered by Matplotlib here because
    it really does not want to reproduce images with
    pixel-for-pixel accuracy (essentially because it wants to
    always be able to zoom); the easiest workaround is to just
    increase the resolution, since that helps get pixel values
    right on average.  These factors together are why, by
    default, we produce the test image at a pretty large scale.
    """

    xs = np.linspace(0.0, max_x, x_samples)
    ys = np.linspace(0.0, 1.0, y_samples)

    xs **= 2
    np.sin(xs, out=xs)

    im = xs[None, :] * ys[:, None]
    return im


def show_test_image(ax, cmap_obj):
    ax.set_xlim((0., 1.))
    ax.set_ylim((0., 1.))

    im = test_image()
    ax.imshow(
        im,
        cmap=cmap_obj,
        aspect='auto',
        extent=(0., 1., 0., 1.),
        )


def color_wheel(ax, cmap_obj):
    azimuths = np.linspace(0., 2.*np.pi, 257)
    zeniths = np.array([0., 1.])
    values = np.linspace(0., 2.*np.pi, 256)[None, :]

    ax.pcolormesh(azimuths, zeniths, values, cmap=cmap_obj)
    ax.set_yticks([])


def swatches(ax, swatches_to_show):
    ax.set_xticks([])
    ax.set_yticks([])
    ax.imshow(swatches_to_show)


def sample_colorspace(
        extent,
        lightness,
        num_colorspace_samples,
        num_batches_per_side=1,
        batch_idx_x=0,
        batch_idx_y=0,
        ):
    num_samples_per_batch = num_colorspace_samples // num_batches_per_side

    (min_x, max_x), (min_y, max_y) = extent
    delta_x = (max_x - min_x) / num_batches_per_side
    delta_y = (max_y - min_y) / num_batches_per_side

    chromaticity0_coords = np.linspace(
        min_x + batch_idx_x * delta_x,
        min_x + (batch_idx_x + 1) * delta_x,
        num_samples_per_batch,
        endpoint=False,
        )
    chromaticity1_coords = np.linspace(
        min_y + batch_idx_y * delta_y,
        min_y + (batch_idx_y + 1) * delta_y,
        num_samples_per_batch,
        endpoint=False,
        )

    samples = np.empty(
        (num_samples_per_batch, num_samples_per_batch, 3),
        dtype=np.float64,
        )
    samples[..., 0] = lightness
    samples[..., 1] = chromaticity0_coords[None, :]
    samples[..., 2] = chromaticity1_coords[:, None]

    return samples


def plot_colorspace(ax, rgb_samples, extent, num_colorspace_samples):
    half_step0 = (
        (extent[0][1] - extent[0][0]) / (2 * num_colorspace_samples)
        )
    half_step1 = (
        (extent[1][1] - extent[0][0]) / (2 * num_colorspace_samples)
        )

    ax.imshow(
        rgb_samples,
        origin='lower',
        extent=(
            extent[0][0] - half_step0,
            extent[0][1] - half_step0,
            extent[1][0] - half_step1,
            extent[1][1] - half_step1,
            ),
        )


def find_colorspace_sRGB_points(rgb_samples, uniform_space, conversions):
    kd_tree = conversion.sRGB_nearest_neighbors_structure(
        uniform_space, conversions, False,
        )

    _, nearby_packed = kd_tree.query(rgb_samples, 1)
    nearby_unpacked = conversion.unpack_sRGB_indices(nearby_packed)
    return nearby_unpacked


def colorspace_with_cmap(
        ax, cmap_uniform, lightness, conversions, num_colorspace_samples=256,
        ):
    min_chromaticity0 = np.min(cmap_uniform[..., 1])
    max_chromaticity0 = np.max(cmap_uniform[..., 1])
    min_chromaticity1 = np.min(cmap_uniform[..., 2])
    max_chromaticity1 = np.max(cmap_uniform[..., 2])

    min_chromaticity0 = np.floor(min_chromaticity0 * 20. - .5) / 20.
    min_chromaticity1 = np.floor(min_chromaticity1 * 20. - .5) / 20.
    max_chromaticity0 = np.ceil(max_chromaticity0 * 20. + .5) / 20.
    max_chromaticity1 = np.ceil(max_chromaticity1 * 20. + .5) / 20.

    extent = (
        (min_chromaticity0, max_chromaticity0),
        (min_chromaticity1, max_chromaticity1),
        )

    uniform_samples = sample_colorspace(
        extent, lightness, num_colorspace_samples,
        )

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        rgb_samples = conversions['uniform_to_sRGB'](uniform_samples)

    valid_idx = conversion.sRGB1_validity(rgb_samples)
    rgb_samples[~valid_idx] = 1.0

    plot_colorspace(ax, rgb_samples, extent, num_colorspace_samples)

    grays_uniform = cmap_uniform.copy()
    grays_uniform[..., 1:3] = 0.
    grays_sRGB = conversions['uniform_to_sRGB'](grays_uniform)
    np.clip(grays_sRGB, 0., 1., out=grays_sRGB)

    coords = cmap_uniform[..., 1:3]
    for idx in np.ndindex(cmap_uniform.shape[:-1]):
        pt = coords[idx]
        c = grays_sRGB[idx]
        ax.add_patch(plt.Circle(pt, .001, color=c))

    ax.set_xlim((min_chromaticity0, max_chromaticity0))
    ax.set_ylim((min_chromaticity1, max_chromaticity1))


def correlates(ax_lightness, ax_chroma, ax_hue, cmap_uniform):
    cmap_uniform = cmap_uniform.reshape(-1, 3)

    x_coords = np.arange(cmap_uniform.shape[0])

    uniform_hues = np.rad2deg(
        np.arctan2(cmap_uniform[:, 2], cmap_uniform[:, 1])
        )

    ax_lightness.plot(x_coords, cmap_uniform[:, 0])
    ax_chroma.plot(x_coords, np.hypot(cmap_uniform[:, 1], cmap_uniform[:, 2]))
    ax_hue.plot(x_coords, uniform_hues)

    ax_lightness.set_ylabel('Target lightness')
    ax_chroma.set_ylabel('Target chroma')
    ax_hue.set_ylabel('Target hue angle')


def correlate_diffs(
        ax_lightness_true,
        ax_chroma_true,
        ax_hue_true,
        ax_lightness_diff,
        ax_chroma_diff,
        ax_hue_diff,
        cmap_uniform,
        cmap_sRGB256,
        conversions,
        ):
    cmap_uniform = cmap_uniform.reshape(-1, 3)
    cmap_sRGB256 = cmap_sRGB256.reshape(-1, 3)

    x_coords = np.arange(cmap_uniform.shape[0])

    cmap_sRGB_uniform = conversions['sRGB_to_uniform'](
        conversion.sRGB256_to_sRGB1(cmap_sRGB256)
        )
    diffs = cmap_sRGB_uniform - cmap_uniform

    uniform_hues = np.rad2deg(
        np.arctan2(cmap_uniform[:, 2], cmap_uniform[:, 1])
        )
    quantized_hues = np.rad2deg(
        np.arctan2(cmap_sRGB_uniform[:, 2], cmap_sRGB_uniform[:, 1])
        )
    hue_diffs = (quantized_hues - uniform_hues + np.pi) % (2*np.pi) - np.pi

    ax_lightness_true.plot(x_coords, cmap_sRGB_uniform[:, 0])
    ax_chroma_true.plot(
        x_coords,
        np.hypot(cmap_sRGB_uniform[:, 1], cmap_sRGB_uniform[:, 2]),
        )
    ax_hue_true.plot(x_coords, quantized_hues)

    ax_lightness_diff.plot(x_coords, diffs[:, 0])
    ax_chroma_diff.plot(x_coords, np.hypot(diffs[:, 1], diffs[:, 2]))
    ax_hue_diff.plot(x_coords, hue_diffs)

    ax_lightness_true.set_ylabel('Actual lightness')
    ax_chroma_true.set_ylabel('Actual chroma')
    ax_hue_true.set_ylabel('Actual hue angle')
    ax_lightness_diff.set_ylabel('Lightness errors')
    ax_chroma_diff.set_ylabel('Chroma errors')
    ax_hue_diff.set_ylabel('Hue angle errors')


def _core_plot(cmap_uniform, cmap_sRGB256, cmap_obj, conversions):
    fig = plt.figure(figsize=(18, 9), constrained_layout=True)
    fig.canvas.manager.set_window_title(cmap_obj.name)

    gs = mpl.gridspec.GridSpec(3, 5, figure=fig)

    ax_cbar = fig.add_subplot(gs[0, 0:2])
    ax_test_image = fig.add_subplot(gs[1, 0:2])

    colorspace_axs = []
    colorspace_axs.append(fig.add_subplot(gs[2, 0]))
    colorspace_axs.append(fig.add_subplot(gs[2, 1]))

    min_cspace_lightness = np.min(cmap_uniform[..., 0])
    max_cspace_lightness = np.max(cmap_uniform[..., 0])
    colorspace_lightnesses = np.linspace(
        min_cspace_lightness, max_cspace_lightness, 2,
        )

    ax_lightness = fig.add_subplot(gs[0, 2])
    ax_chroma = fig.add_subplot(gs[1, 2])
    ax_hue = fig.add_subplot(gs[2, 2])
    ax_lightness_true = fig.add_subplot(gs[0, 3])
    ax_chroma_true = fig.add_subplot(gs[1, 3])
    ax_hue_true = fig.add_subplot(gs[2, 3])
    ax_lightness_diff = fig.add_subplot(gs[0, 4])
    ax_chroma_diff = fig.add_subplot(gs[1, 4])
    ax_hue_diff = fig.add_subplot(gs[2, 4])

    for ax, lightness in zip(colorspace_axs, colorspace_lightnesses):
        colorspace_with_cmap(ax, cmap_uniform, lightness, conversions)

    colorbar(ax_cbar, cmap_obj)
    show_test_image(ax_test_image, cmap_obj)

    correlates(
        ax_lightness,
        ax_chroma,
        ax_hue,
        cmap_uniform,
        )
    correlate_diffs(
        ax_lightness_true,
        ax_chroma_true,
        ax_hue_true,
        ax_lightness_diff,
        ax_chroma_diff,
        ax_hue_diff,
        cmap_uniform,
        cmap_sRGB256,
        conversions,
        )

    return fig


def _multiseq_like_plot(
        cmap_uniform,
        cmap_sRGB256,
        cmap_obj,
        conversions,
        ):
    fig = _core_plot(
        cmap_uniform, cmap_sRGB256, cmap_obj, conversions,
        )
    return fig


def multiseq_plot(
        cmap_uniform,
        cmap_sRGB256,
        cmap_obj,
        parameters,
        conversions,
        ):
    return _multiseq_like_plot(
        cmap_uniform,
        cmap_sRGB256,
        cmap_obj,
        conversions,
        )


def divergent_plot(
        cmap_uniform,
        cmap_sRGB256,
        cmap_obj,
        parameters,
        conversions,
        ):
    return _multiseq_like_plot(
        cmap_uniform,
        cmap_sRGB256,
        cmap_obj,
        conversions,
        )


def cyclic_plot(
        cmap_uniform,
        cmap_sRGB256,
        cmap_obj,
        parameters,
        conversions,
        ):
    fig = _core_plot(
        cmap_uniform, cmap_sRGB256, cmap_obj, conversions,
        )
    return fig


def cyclic_cylinder_plot(
        cmap_uniform,
        cmap_sRGB256,
        cmap_obj,
        parameters,
        conversions,
        ):
    fig = _core_plot(
        cmap_uniform, cmap_sRGB256, cmap_obj, conversions,
        )
    return fig


def colorspace_plot(
        uniform_space,
        num_colorspace_samples,
        num_batches_per_side,
        downscale,
        J_prime,
        extent,
        scale,
        sRGB_points,
        output,
        ):
    fig, ax = plt.subplots()

    if output is not None:
        fig.tight_layout(pad=0)

    sRGB_to_uniform, uniform_to_sRGB = conversion.uniform_space_conversions(
        uniform_space,
        )
    conversions = {
        'sRGB_to_uniform': sRGB_to_uniform,
        'uniform_to_sRGB': uniform_to_sRGB,
        }

    extent = ((extent[0], extent[1]), (extent[2], extent[3]))

    num_downscaled_samples_per_batch = (
        num_colorspace_samples // (num_batches_per_side * downscale)
        )
    num_samples_per_batch = num_downscaled_samples_per_batch * downscale
    num_downscaled_samples = (
        num_downscaled_samples_per_batch * num_batches_per_side
        )
    num_colorspace_samples = (
        num_samples_per_batch * num_batches_per_side
        )

    downscaled_samples = np.zeros(
        (num_downscaled_samples, num_downscaled_samples, 3),
        dtype=np.float64,
        )

    if sRGB_points:
        nearest_sRGB256_dedupe = set()

    for batch_idx_x in range(num_batches_per_side):
        for batch_idx_y in range(num_batches_per_side):
            uniform_samples = sample_colorspace(
                extent,
                J_prime,
                num_colorspace_samples,
                num_batches_per_side,
                batch_idx_x,
                batch_idx_y,
                )

            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                rgb_samples = conversions['uniform_to_sRGB'](uniform_samples)

            valid_idx = conversion.sRGB1_validity(rgb_samples)
            rgb_samples[~valid_idx] = 1.0
            np.clip(rgb_samples, 0.0, 1.0, out=rgb_samples)

            downscaled_start_x = batch_idx_x * num_downscaled_samples_per_batch
            downscaled_stop_x = (
                downscaled_start_x + num_downscaled_samples_per_batch
                )

            downscaled_start_y = batch_idx_y * num_downscaled_samples_per_batch
            downscaled_stop_y = (
                downscaled_start_y + num_downscaled_samples_per_batch
                )

            # When we display the final image, the first
            # coordinate is the vertical coordinate and the
            # second coordinate is the horizontal coordinate.
            downscaled_batch = downscaled_samples[
                downscaled_start_y:downscaled_stop_y,
                downscaled_start_x:downscaled_stop_x,
                ]

            for x_offset in range(downscale):
                for y_offset in range(downscale):
                    downscaled_batch += rgb_samples[
                        x_offset::downscale,
                        y_offset::downscale,
                        ]

            if sRGB_points:
                valid_uniform_samples = (
                    uniform_samples[valid_idx].reshape(-1, 3)
                    )
                nearest_sRGB256 = find_colorspace_sRGB_points(
                    valid_uniform_samples, uniform_space, conversions,
                    )
                nearest_sRGB256_dedupe.update(
                    map(tuple, nearest_sRGB256),
                    )

    downscaled_samples /= downscale * downscale

    if scale:
        extent = (
            (extent[0][0] * 100, extent[0][1] * 100),
            (extent[1][0] * 100, extent[1][1] * 100),
            )

    plot_colorspace(
        ax, downscaled_samples, extent, num_downscaled_samples,
        )

    if sRGB_points:
        # Here, we give ourselves an extra chance to find sRGB
        # points that should be included but that we missed
        # because we didn't use enough samples.  We do this by
        # projecting every point in sRGB down to the lightness of
        # interest, testing whether it's in the sRGB gamut, and
        # if so, finding its nearest neighbor.  This will find
        # many of the nearest sRGB points to the lightness slice.
        # It's not guaranteed to find them all because it's
        # possible (at least in theory) that the sRGB point is
        # closest to some points on the slice but that the
        # projection isn't one of those points (this can happen
        # when the projection is closer to an sRGB point whose
        # lightness is closer to the lightness of the slice).
        # However, this technique gets almost all the sRGB points
        # on its own, and if we sample with a high enough
        # resolution, we'll have all or nearly all of them.
        kd_tree = conversion.sRGB_nearest_neighbors_structure(
            uniform_space, conversions, False,
            )
        extra_points = kd_tree.data.copy()
        extra_points[:, 0] = J_prime

        valid_idx = conversion.sRGB1_validity(
            conversions['uniform_to_sRGB'](extra_points)
            )
        valid_extra_points = extra_points[(valid_idx,)]
        nearest_sRGB256 = find_colorspace_sRGB_points(
            valid_extra_points, uniform_space, conversions,
            )

        nearest_sRGB256_dedupe.update(map(tuple, nearest_sRGB256))

        print(
            "  Final number of distinct sRGB points is:",
            len(nearest_sRGB256_dedupe),
            )

        nearest_sRGB256_dedupe_arr = np.array((*nearest_sRGB256_dedupe,))
        nearest_sRGB1 = (
            conversion.sRGB256_to_sRGB1(nearest_sRGB256_dedupe_arr)
            )
        nearest_uniform = conversions['sRGB_to_uniform'](nearest_sRGB1)
        nearest_locations = nearest_uniform[..., 1:3]

        nearest_min_Jp = np.min(nearest_uniform[..., 0])
        nearest_max_Jp = np.max(nearest_uniform[..., 0])
        scaled_nearest_uniform = nearest_uniform.copy()
        scaled_nearest_uniform[:, 0] -= nearest_min_Jp
        scaled_nearest_uniform[:, 0] *= (
            0.6 / (nearest_max_Jp - nearest_min_Jp)
            )
        scaled_nearest_uniform[:, 0] += 0.3

        print(f"Minimum J': {nearest_min_Jp}")
        print(f"Maximum J': {nearest_max_Jp}")
        print(f"Median J': {np.median(nearest_uniform[..., 0])}")

        scaled_nearest_sRGB256 = find_colorspace_sRGB_points(
            scaled_nearest_uniform, uniform_space, conversions,
            )
        scaled_nearest_sRGB = conversion.sRGB256_to_sRGB1(
            scaled_nearest_sRGB256,
            )

        radius = 0.001
        if scale:
            nearest_locations *= 100
            radius *= 100

        for pt, col in zip(nearest_locations, scaled_nearest_sRGB):
            ax.add_patch(plt.Circle(pt, radius, color=col))

    if not output:
        plt.show()
    else:
        plt.savefig(output, bbox_inches='tight')


def colormap_plot(uniform_space, cmap_name):
    sRGB_to_uniform, uniform_to_sRGB = (
        conversion.uniform_space_conversions(uniform_space)
        )
    conversions = {
        'sRGB_to_uniform': sRGB_to_uniform,
        'uniform_to_sRGB': uniform_to_sRGB,
        }

    cmap_obj = mpl.cm.get_cmap(cmap_name)
    if isinstance(cmap_obj, mpl.colors.ListedColormap):
        cmap_sRGB = np.array(cmap_obj.colors)
    else:
        values = np.linspace(0.0, 1.0, 256)
        cmap_sRGB = cmap_obj(values)

    cmap_uniform = sRGB_to_uniform(cmap_sRGB[:, :3])

    fig = plt.figure(figsize=(9, 9), constrained_layout=True)
    fig.canvas.manager.set_window_title(cmap_obj.name)

    gs = mpl.gridspec.GridSpec(3, 3, figure=fig)

    ax_cbar = fig.add_subplot(gs[0, 0:2])
    ax_test_image = fig.add_subplot(gs[1, 0:2])

    colorspace_axs = []
    colorspace_axs.append(fig.add_subplot(gs[2, 0]))
    colorspace_axs.append(fig.add_subplot(gs[2, 1]))

    min_cspace_lightness = np.min(cmap_uniform[..., 0])
    max_cspace_lightness = np.max(cmap_uniform[..., 0])
    colorspace_lightnesses = np.linspace(
        min_cspace_lightness, max_cspace_lightness, 2,
        )

    ax_lightness = fig.add_subplot(gs[0, 2])
    ax_chroma = fig.add_subplot(gs[1, 2])
    ax_hue = fig.add_subplot(gs[2, 2])

    for ax, lightness in zip(colorspace_axs, colorspace_lightnesses):
        colorspace_with_cmap(ax, cmap_uniform, lightness, conversions)

    colorbar(ax_cbar, cmap_obj)
    show_test_image(ax_test_image, cmap_obj)

    correlates(
            ax_lightness,
            ax_chroma,
            ax_hue,
            cmap_uniform,
            )

    plt.show()
