import copy
import warnings

import numpy as np
import matplotlib.pyplot as plt

from . import cmap, conversion, db, display, fmt, opt


# viscm seems to rely on old QT bindings which have been removed
# in Matplotlib 3.5.
try:
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        import viscm
except ImportError:
    VISCM_AVAILABLE = False
else:
    VISCM_AVAILABLE = True


def _final_cone_check(state, cmap_cone):
    if not state['verbose_post_process']:
        return

    cmap_cone_sRGB = state['conversions']['uniform_to_sRGB'](cmap_cone)

    allowed_gamut_error = state['parameters']['allowed_gamut_error']

    sRGB_lower_bound = -allowed_gamut_error
    sRGB_upper_bound = 1. + allowed_gamut_error

    too_low = np.any(cmap_cone_sRGB < sRGB_lower_bound, axis=-1)
    too_high = np.any(cmap_cone_sRGB > sRGB_upper_bound, axis=-1)

    failures = np.vstack((np.argwhere(too_low), np.argwhere(too_high)))

    if failures.size == 0:
        print("Passed cone check.")
        return

    out_of_gamut_colors = []
    for idx in failures:
        idx = (*idx,)
        if len(idx) == 1:
            idx = idx[0]
        out_of_gamut_colors.append(
            (
                f"Cone sample {idx}",
                cmap_cone[idx],
                None,
                cmap_cone_sRGB[idx],
            ),
            )

    print("Cone check failed for:")
    print(fmt.colors(*out_of_gamut_colors))


def _post_optimization(cmap_uniform, state, old_cmap):
    cmap_uniform = cmap.post_process(
        cmap_uniform,
        state['post_opt_parameters'],
        )

    cmap_sRGB256, cmap_obj = conversion.color_maps_from_uniform(
        cmap_uniform,
        state['name'],
        state['parameters'],
        state['post_opt_parameters'],
        state['conversions'],
        state['verbose_post_process'],
        )

    if state['verbose_post_process'] and old_cmap is not None:
        had_change = []
        for k, v in state['cmap'].items():
            if isinstance(v, (float, np.ndarray)):
                if not np.all(np.isclose(v, old_cmap[k])):
                    had_change.append(k)
            elif v != old_cmap[k]:
                had_change.append(k)

        if not had_change:
            print("No changes to color map.")
        else:
            print(
                "Color map had changes to:",
                ", ".join(had_change)
                )

    db.convert_to_degrees(state)

    if state['verbose_post_process']:
        print(db.serialize(state))
    if state['output_parameters']:
        db.write_state(state['output_parameters'], state)
    if state['output_color_map']:
        if state['parameters']['cylinder']:
            output_path = state['output_color_map']
            dark_path = output_path.with_name(output_path.name + '_dark')
            light_path = output_path.with_name(output_path.name + '_light')
            db.write_cmap(dark_path, cmap_sRGB256[0])
            db.write_cmap(light_path, cmap_sRGB256[1])
        else:
            db.write_cmap(state['output_color_map'], cmap_sRGB256)

    return cmap_sRGB256, cmap_obj


def _mseq_like_sequence_data(cmap_uniform, cmap_sRGB256, state):
    if not state['verbose_post_process']:
        return

    for idx in np.ndindex(cmap_uniform.shape[:-2]):
        cmap_uniform_idx = cmap_uniform[idx]
        cmap_sRGB256_idx = cmap_sRGB256[idx]

        print(display.mseq_endpoints(
            state['parameters']['num_samples_per_sequence'],
            cmap_uniform_idx,
            cmap_sRGB256_idx,
            ))
        print(display.mseq_lightness_differences(
            state['parameters']['num_samples_per_sequence'],
            cmap_uniform_idx,
            cmap_sRGB256_idx,
            state['conversions'],
            ))


def _cyclic_sequence_data(cmap_uniform, cmap_sRGB256, state):
    if not state['verbose_post_process']:
        return

    for idx in np.ndindex(cmap_uniform.shape[:-2]):
        cmap_uniform_idx = cmap_uniform[idx]
        cmap_sRGB256_idx = cmap_sRGB256[idx]

        print(display.cyclic_quarters(
            cmap_uniform_idx,
            cmap_sRGB256_idx,
            ))

        if not np.isclose(
                state['cmap']['initial_lightness'],
                state['cmap']['final_lightness'],
                ):
            print(display.cyclic_lightness_differences(
                cmap_uniform_idx,
                cmap_sRGB256_idx,
                state['conversions'],
                ))


def _display_cvd(plot_func, cmap_obj, cvd, state):
    cmap_uniform_cvd, cmap_sRGB256_cvd, cmap_obj_cvd = conversion.cvd_cmap(
        cmap_obj, cvd, state['cvd_severity'], state['conversions'],
        )

    plot_func(
        cmap_uniform_cvd,
        cmap_sRGB256_cvd,
        cmap_obj_cvd,
        state['parameters'],
        state['conversions'],
        )


def _display_with_plot_type(
        plot_func,
        cmap_uniform,
        cmap_sRGB256,
        cmap_obj,
        state,
        ):
    if state['display']:
        plot_func(
            cmap_uniform,
            cmap_sRGB256,
            cmap_obj,
            state['parameters'],
            state['conversions'],
            )

        if state['cvd']:
            _display_cvd(plot_func, cmap_obj, 'Protanomaly', state)
            _display_cvd(plot_func, cmap_obj, 'Deuteranomaly', state)
            _display_cvd(plot_func, cmap_obj, 'Tritanomaly', state)

        if VISCM_AVAILABLE:
            viscm.viscm(cmap_obj)

        plt.show()


def create_multiseq(state):
    db.convert_to_radians(state)

    old_cmap = copy.deepcopy(state['cmap'])

    if state['optimize']:
        (
            state['cmap']['initial_lightness'],
            state['cmap']['final_lightness'],
            state['cmap']['chroma'],
            state['cmap']['sequence_data'],
        ) = opt.mseq_optimize(state)

    if state['parameters']['cylinder']:
        cmap_uniform = cmap.cylinder(
            state['parameters']['num_samples_per_sequence'],
            state['cmap']['initial_lightness'],
            state['cmap']['final_lightness'],
            state['cmap']['chroma'],
            state['cmap']['sequence_data'][::2],
            state['cmap']['sequence_data'][1::2],
            True,
            2
            )
    else:
        cmap_uniform = cmap.multisequential(
            state['parameters']['num_samples_per_sequence'],
            state['cmap']['initial_lightness'],
            state['cmap']['final_lightness'],
            state['cmap']['chroma'],
            state['cmap']['sequence_data'][::2],
            state['cmap']['sequence_data'][1::2],
            True,
            )

    if state['parameters']['cone']:
        cmap_cone = cmap.cone(
            state['parameters']['num_samples_per_sequence'],
            state['cmap']['initial_lightness'],
            state['cmap']['final_lightness'],
            state['cmap']['chroma'],
            state['cmap']['sequence_data'][::2],
            state['cmap']['sequence_data'][1::2],
            True,
            state['post_opt_parameters']['Jp_final_samples'],
            )
        _final_cone_check(state, cmap_cone)

    cmap_sRGB256, cmap_obj = _post_optimization(cmap_uniform, state, old_cmap)

    _mseq_like_sequence_data(cmap_uniform, cmap_sRGB256, state)
    _display_with_plot_type(
        display.multiseq_plot,
        cmap_uniform,
        cmap_sRGB256,
        cmap_obj,
        state,
        )

    return cmap_uniform, cmap_sRGB256, cmap_obj


def create_divergent(state):
    db.convert_to_radians(state)

    old_cmap = copy.deepcopy(state['cmap'])

    if state['optimize']:
        (
            state['cmap']['initial_lightness'],
            state['cmap']['final_lightness'],
            state['cmap']['chroma'],
            state['cmap']['sequence_data'],
        ) = opt.mseq_optimize(state)

    cmap_uniform = cmap.divergent(
        state['parameters']['num_samples_per_sequence'],
        state['cmap']['initial_lightness'],
        state['cmap']['final_lightness'],
        state['cmap']['chroma'],
        state['cmap']['sequence_data'][::2],
        state['cmap']['sequence_data'][1::2],
        True,
        state['cmap']['divergence_type'],
        )

    cmap_sRGB256, cmap_obj = _post_optimization(cmap_uniform, state, old_cmap)

    _mseq_like_sequence_data(cmap_uniform, cmap_sRGB256, state)
    _display_with_plot_type(
        display.divergent_plot,
        cmap_uniform,
        cmap_sRGB256,
        cmap_obj,
        state,
        )

    return cmap_uniform, cmap_sRGB256, cmap_obj


def create_cyclic(state):
    db.convert_to_radians(state)

    old_cmap = copy.deepcopy(state['cmap'])

    if state['optimize']:
        (
            state['cmap']['initial_lightness'],
            state['cmap']['final_lightness'],
            state['cmap']['chroma'],
            state['cmap']['sequence_data'],
        ) = opt.cyclic_optimize(state)

    if state['parameters']['cylinder']:
        cmap_uniform_dark = cmap.cyclic(
            state['parameters']['num_samples_per_sequence'],
            state['cmap']['initial_lightness'],
            state['cmap']['initial_lightness'],
            state['cmap']['chroma'],
            state['cmap']['sequence_data'],
            )
        cmap_uniform_light = cmap.cyclic(
            state['parameters']['num_samples_per_sequence'],
            state['cmap']['final_lightness'],
            state['cmap']['final_lightness'],
            state['cmap']['chroma'],
            state['cmap']['sequence_data'],
            )
        cmap_uniform = np.stack((cmap_uniform_dark, cmap_uniform_light))
    else:
        cmap_uniform = cmap.cyclic(
            state['parameters']['num_samples_per_sequence'],
            state['cmap']['initial_lightness'],
            state['cmap']['final_lightness'],
            state['cmap']['chroma'],
            state['cmap']['sequence_data'],
            )

    cmap_sRGB256, cmap_obj = _post_optimization(cmap_uniform, state, old_cmap)
    _cyclic_sequence_data(cmap_uniform, cmap_sRGB256, state)

    if state['parameters']['cylinder']:
        _display_with_plot_type(
            display.cyclic_cylinder_plot,
            cmap_uniform,
            cmap_sRGB256,
            cmap_obj,
            state,
            )
    else:
        _display_with_plot_type(
            display.cyclic_plot,
            cmap_uniform,
            cmap_sRGB256,
            cmap_obj,
            state,
            )

    return cmap_uniform, cmap_sRGB256, cmap_obj


def create_gray(state):
    cmap_uniform = cmap.gray(
        state['parameters']['num_samples_per_sequence'],
        state['cmap']['initial_lightness'],
        state['cmap']['final_lightness'],
        )

    cmap_sRGB256, cmap_obj = _post_optimization(cmap_uniform, state, None)
    _mseq_like_sequence_data(cmap_uniform, cmap_sRGB256, state)

    _display_with_plot_type(
        display.multiseq_plot,
        cmap_uniform,
        cmap_sRGB256,
        cmap_obj,
        state,
        )

    return cmap_uniform, cmap_sRGB256, cmap_obj
