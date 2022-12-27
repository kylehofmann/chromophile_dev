import numpy as np


def sequential(
        num_samples,
        initial_lightness,
        final_lightness,
        chroma,
        initial_hue,
        hue_diff,
        endpoint,
        ):
    lightnesses = np.linspace(
        initial_lightness,
        final_lightness,
        num_samples,
        axis=-1,
        endpoint=endpoint,
        )
    chromas = np.maximum(chroma, 0.)[..., None]
    hues = np.linspace(
        initial_hue,
        initial_hue + hue_diff,
        num_samples,
        axis=-1,
        endpoint=endpoint,
        )
    a_coords = chromas * np.cos(hues)
    b_coords = chromas * np.sin(hues)
    samples = np.stack(
        np.broadcast_arrays(lightnesses, a_coords, b_coords), axis=-1,
        )
    return samples


def gray(
        num_samples,
        initial_lightness,
        final_lightness,
        ):
    lightnesses = np.linspace(
        initial_lightness,
        final_lightness,
        num_samples,
        axis=-1,
        )
    a_coords = 0.
    b_coords = 0.
    samples = np.stack(
        np.broadcast_arrays(lightnesses, a_coords, b_coords), axis=-1,
        )
    return samples


def multisequential(
        num_samples_per_sequence,
        initial_lightness,
        final_lightness,
        chroma,
        initial_hue,
        hue_diff,
        endpoint,
        ):
    cmaps = sequential(
        num_samples_per_sequence,
        initial_lightness,
        final_lightness,
        chroma,
        initial_hue,
        hue_diff,
        endpoint,
        )

    return np.concatenate(cmaps, axis=0)


def cylinder(
        num_samples_per_sequence,
        initial_lightness,
        final_lightness,
        chroma,
        initial_hue,
        hue_diff,
        endpoint,
        cylinder_samples,
        ):
    lightnesses = np.linspace(
        initial_lightness, final_lightness, cylinder_samples, axis=-1,
        )
    chroma, initial_hue, hue_diff = np.broadcast_arrays(
        chroma, initial_hue, hue_diff,
        )

    lightnesses = np.reshape(
        lightnesses, lightnesses.shape + (1,) * len(chroma.shape)
        )
    chroma = chroma[None, ...]
    initial_hue = initial_hue[None, ...]
    hue_diff = hue_diff[None, ...]

    cmaps = multisequential(
        num_samples_per_sequence,
        lightnesses,
        lightnesses,
        chroma,
        initial_hue,
        hue_diff,
        endpoint,
        )

    return cmaps


def cone(
        num_samples_per_sequence,
        initial_lightness,
        final_lightness,
        chroma,
        initial_hue,
        hue_diff,
        endpoint,
        cone_samples,
        ):
    cone_initial_lightnesses = np.linspace(
        initial_lightness, 0, cone_samples, axis=-1, endpoint=False,
        )
    cone_final_lightnesses = np.linspace(
        final_lightness, 0, cone_samples, axis=-1, endpoint=False,
        )
    cone_chromas = np.linspace(
        chroma, 0, cone_samples, axis=-1, endpoint=False,
        )

    cmaps = multisequential(
        num_samples_per_sequence,
        cone_initial_lightnesses,
        cone_final_lightnesses,
        cone_chromas,
        initial_hue[None, ...],
        hue_diff[None, ...],
        endpoint,
        )

    return cmaps


def divergent(
        num_samples_per_sequence,
        initial_lightness,
        final_lightness,
        chroma,
        initial_hue,
        hue_diff,
        endpoint,
        divergence_type,
        ):
    cm = multisequential(
        num_samples_per_sequence,
        initial_lightness,
        final_lightness,
        chroma,
        initial_hue,
        hue_diff,
        endpoint,
        )

    if divergence_type == 'hill':
        cm = np.r_[
            cm[:num_samples_per_sequence],
            cm[num_samples_per_sequence:][::-1],
            ]
    elif divergence_type == 'valley':
        cm = np.r_[
            cm[:num_samples_per_sequence][::-1],
            cm[num_samples_per_sequence:],
            ]

    return cm


def cyclic(
        num_samples,
        initial_lightness,
        final_lightness,
        chroma,
        initial_hue,
        ):
    cmaps = sequential(
        num_samples // 2,
        np.array((initial_lightness, final_lightness)),
        np.array((final_lightness, initial_lightness)),
        chroma,
        np.array((initial_hue, initial_hue + np.pi)),
        np.pi,
        False,
        )

    return np.concatenate(cmaps, axis=0)


def post_process(
        cmap_uniform,
        post_opt_parameters,
        ):
    if post_opt_parameters['reverse']:
        cmap_uniform = cmap_uniform[::-1]

    if post_opt_parameters['rotate']:
        boundary = (
            post_opt_parameters['num_samples_per_sequence']
            * post_opt_parameters['rotate']
            )
        cmap_uniform = np.r_[cmap_uniform[boundary:], cmap_uniform[:boundary]]

    return cmap_uniform
