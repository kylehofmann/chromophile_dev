import copy
import functools
import itertools
import operator

import numpy as np

from . import db, run


SHARED_PARAMETERS = {
    'name': None,
    'optimize': True,
    'display': False,
    'cvd': False,
    'output_parameters': False,
    'output_color_map': False,
    'verbose': False,
    'verbose_optimize': False,
    'verbose_post_process': False,
    'opt_parameters': {'maxiter': 1000, 'tol': 1e-15},
    'post_opt_parameters': {
        'Jp_final_samples': 64,
        'reverse': False,
        'rotate': 0,
        # We don't want to spend time getting a really good sRGB
        # approximation during these searches.
        'sRGB_approximation_maxiter': 1,
        # We need at least two nearby points for the heuristic
        # score to work.
        'sRGB_approximation_nearby_points': 2,
        'sRGB_approximation_proof': False
        },
    }

SEQUENTIAL_PARAMETERS = {
    **SHARED_PARAMETERS,
    'cmap': {
        'chroma': None,
        'final_lightness': 0.2,
        'initial_lightness': 0.8,
        'sequence_data': None,
        },
    'parameters': {
        'Jp_constraint_samples': 1,
        'allowed_gamut_error': 1e-06,
        'center_final_hue': None,
        'center_initial_hue': None,
        'cone': False,
        'constraint_samples_per_sequence': 16,
        'cylinder': False,
        'max_chroma': np.inf,
        'max_final_hue_separation': np.inf,
        'max_final_lightness': 1.0,
        'max_hue_diff': np.inf,
        'max_initial_hue_separation': np.inf,
        'max_initial_lightness': 0.4,
        'max_lightness_diff': 1.0,
        'min_chroma': 1e-10,
        'min_final_hue_separation': -np.inf,
        'min_final_lightness': 0.6,
        'min_hue_diff': -np.inf,
        'min_initial_hue_separation': -np.inf,
        'min_initial_lightness': 0.05,
        'min_lightness_diff': -1.0,
        'num_samples_per_sequence': 256,
        'span_final_hue': np.inf,
        'span_initial_hue': np.inf,
        'uniform_space': 'CAM16UCS',
        'weight_chroma': 0.0,
        'weight_final_lightness': 1.0,
        'weight_hue_diff': 0.0,
        'weight_hue_final_separation': 0.0,
        'weight_hue_initial_separation': 0.0,
        'weight_initial_lightness': -1.0,
        'weight_lightness_diff': 1.0,
        'weight_squared_hue_diff': -0.1,
        },
    'type': 'Multisequential',
    }

DIVERGENT_HILL_PARAMETERS = {
    **SHARED_PARAMETERS,
    'cmap': {
        'chroma': None,
        'final_lightness': 0.2,
        'initial_lightness': 0.8,
        'sequence_data': None,
        'divergence_type': 'hill',
        },
    'parameters': {
        'Jp_constraint_samples': 1,
        'allowed_gamut_error': 1e-06,
        'center_final_hue': None,
        'center_initial_hue': None,
        'cone': False,
        'constraint_samples_per_sequence': 16,
        'cylinder': False,
        'max_chroma': np.inf,
        'max_final_hue_separation': 0.0,
        'max_final_lightness': 1.0,
        'max_hue_diff': np.inf,
        'max_initial_hue_separation': np.inf,
        'max_initial_lightness': 0.4,
        'max_lightness_diff': 1.0,
        'min_chroma': 1e-10,
        'min_final_hue_separation': 0.0,
        'min_final_lightness': 0.6,
        'min_hue_diff': -np.inf,
        'min_initial_hue_separation': -np.inf,
        'min_initial_lightness': 0.05,
        'min_lightness_diff': -1.0,
        'num_samples_per_sequence': 256,
        'span_final_hue': np.inf,
        'span_initial_hue': np.inf,
        'uniform_space': 'CAM16UCS',
        'weight_chroma': 0.0,
        'weight_final_lightness': 1.0,
        'weight_hue_diff': 0.0,
        'weight_hue_final_separation': 0.0,
        'weight_hue_initial_separation': 0.0,
        'weight_initial_lightness': -1.0,
        'weight_lightness_diff': 1.0,
        'weight_squared_hue_diff': -0.1,
        },
    'type': 'Divergent',
    }

DIVERGENT_VALLEY_PARAMETERS = {
    **SHARED_PARAMETERS,
    'cmap': {
        'chroma': None,
        'final_lightness': 0.2,
        'initial_lightness': 0.8,
        'sequence_data': None,
        'divergence_type': 'valley',
        },
    'parameters': {
        'Jp_constraint_samples': 1,
        'allowed_gamut_error': 1e-06,
        'center_final_hue': None,
        'center_initial_hue': None,
        'cone': False,
        'constraint_samples_per_sequence': 16,
        'cylinder': False,
        'max_chroma': np.inf,
        'max_final_hue_separation': np.inf,
        'max_final_lightness': 1.0,
        'max_hue_diff': np.inf,
        'max_initial_hue_separation': np.inf,
        'max_initial_lightness': 0.4,
        'max_lightness_diff': 1.0,
        'min_chroma': 1e-10,
        'min_final_hue_separation': -np.inf,
        'min_final_lightness': 0.6,
        'min_hue_diff': -np.inf,
        'min_initial_hue_separation': -np.inf,
        'min_initial_lightness': 0.05,
        'min_lightness_diff': -1.0,
        'num_samples_per_sequence': 256,
        'span_final_hue': np.inf,
        'span_initial_hue': np.inf,
        'uniform_space': 'CAM16UCS',
        'weight_chroma': 0.0,
        'weight_final_lightness': 1.0,
        'weight_hue_diff': 0.0,
        'weight_hue_final_separation': 0.0,
        'weight_hue_initial_separation': 0.0,
        'weight_initial_lightness': -1.0,
        'weight_lightness_diff': 1.0,
        'weight_squared_hue_diff': -0.1,
        },
    'type': 'Divergent',
    }

CYCLIC_PARAMETERS = {
    **SHARED_PARAMETERS,
    'cmap': {
        'chroma': None,
        'final_lightness': 0.2,
        'initial_lightness': 0.8,
        'sequence_data': None,
        'divergence_type': 'valley',
        },
    'parameters': {
        'Jp_constraint_samples': 1,
        'allowed_gamut_error': 1e-06,
        'center_hue': None,
        'cone': False,
        'constraint_samples_per_sequence': 16,
        'cylinder': False,
        'max_chroma': np.inf,
        'max_final_lightness': 1.0,
        'max_initial_lightness': 0.4,
        'max_lightness_diff': 1.0,
        'min_chroma': 1e-10,
        'min_final_lightness': 0.6,
        'min_initial_lightness': 0.05,
        'min_lightness_diff': -1.0,
        'num_samples_per_sequence': 360,
        'span_hue': np.inf,
        'uniform_space': 'CAM16UCS',
        'weight_chroma': 0.0,
        'weight_final_lightness': 1.0,
        'weight_initial_lightness': -1.0,
        'weight_lightness_diff': 1.0,
        },
    'type': 'Cyclic',
    }

ISOLUM_PARAMETERS = {
    **SHARED_PARAMETERS,
    'cmap': {
        'chroma': 0.2,
        'final_lightness': 0.4,
        'initial_lightness': 0.6,
        'sequence_data': None,
        },
    'parameters': {
        'C_weight': 1.0,
        'Jp_constraint_samples': 4,
        'Jp_weight': 1.0,
        'allowed_gamut_error': 1e-06,
        'center_final_hue': None,
        'center_initial_hue': None,
        'cone': False,
        'constraint_samples_per_sequence': 16,
        'cylinder': True,
        'max_chroma': np.inf,
        'max_final_hue_separation': np.inf,
        'max_final_lightness': 1.0,
        'max_hue_diff': np.inf,
        'max_initial_hue_separation': np.inf,
        'max_initial_lightness': 0.4,
        'max_lightness_diff': 1.0,
        'min_chroma': 1e-10,
        'min_final_hue_separation': -np.inf,
        'min_final_lightness': 0.6,
        'min_hue_diff': 60.0,
        'min_initial_hue_separation': -np.inf,
        'min_initial_lightness': 0.05,
        'min_lightness_diff': 0.5,
        'num_samples_per_sequence': 256,
        'span_final_hue': np.inf,
        'span_initial_hue': np.inf,
        'uniform_space': 'CAM16UCS',
        'weight_chroma': 0.0,
        'weight_final_lightness': 1.0,
        'weight_hue_diff': 0.0,
        'weight_hue_final_separation': 0.0,
        'weight_hue_initial_separation': 0.0,
        'weight_initial_lightness': -1.0,
        'weight_lightness_diff': 1.0,
        'weight_squared_hue_diff': 0.001,
        },
    'type': 'Multisequential',
    }


def intervals(start, stop, step, n):
    """Returns list of intervals between starting and ending points

    This function generates tuples of n intervals, with the
    endpoints of the intervals taken from evenly spaced points
    step apart on the circle between the points start and stop.
    The starting and ending points of an interval may be equal.
    The returned intervals are non-overlapping in the following
    sense: An interval of non-zero length is allowed to overlap
    an interval of zero length on either end; two intervals of
    non-zero length are not allowed to overlap; two intervals of
    zero length are not allowed to overlap; and the zero-length
    interval (stop, stop) is excluded.
    """

    if n == 1:
        for lb in np.arange(start, stop, step):
            for ub in np.arange(lb, stop + 1, step):
                yield ((lb, ub),)
    else:
        for prev_intervals in intervals(start, stop, step, n - 1):
            last_interval_start = prev_intervals[-1][0]
            last_interval_stop = prev_intervals[-1][1]
            if last_interval_start == last_interval_stop:
                next_start = last_interval_stop + step
            else:
                next_start = last_interval_stop
            for new_interval in intervals(next_start, stop, step, 1):
                yield (*prev_intervals, *new_interval)


def arcs_around_circle(step, n):
    yield from intervals(0, 360, step, n)

    for lb in np.arange(-360 + step, 0, step):
        for ub in np.arange(step, lb + 360 + 1, step):
            new_interval = (lb, ub)
            if n == 1:
                yield (new_interval,)
            else:
                for next_intervals in intervals(
                        ub, lb + 360, step, n - 1,
                        ):
                    yield (new_interval, *next_intervals)


def _base_directed_arcs(step, n):
    for arcs in arcs_around_circle(step, n):
        all_signs_it = ((1, -1) if lb != ub else (1,) for lb, ub in arcs)
        for signs in itertools.product(*all_signs_it):
            next_arcs = (*(
                (lb, ub - lb) if s == 1 else (ub, lb - ub)
                for (lb, ub), s in zip(arcs, signs)
                ),)
            yield next_arcs


def directed_arcs(step, n, extra_revolutions):
    if extra_revolutions == 0:
        yield from _base_directed_arcs(step, n)
    else:
        for arcs in _base_directed_arcs(step, n):
            if any(diff == 0 for start, diff in arcs):
                continue
            yield (*(
                (start, diff + 360 * extra_revolutions * np.sign(diff))
                for start, diff in arcs
                ),)


def marked_arcs(step):
    for arcs in arcs_around_circle(step, 1):
        lb, ub = arcs[0]
        for mark in np.arange(lb, ub + 1, step):
            yield (lb, mark, ub)


def _make(
        initial_parameters,
        colorfulness,
        span,
        num_samples,
        lightness_threshold,
        similarity_threshold,
        initial_setup_fn,
        cmap_setup_fn,
        cmap_creation_fn,
        cmap_filter_fn,
        ):
    initial_state = copy.deepcopy(initial_parameters)
    db.initialize_state(initial_state)

    colorfulness = np.array(colorfulness)
    span = np.array(span)

    make_name, cmap_iter = initial_setup_fn(
        initial_state, colorfulness, span, num_samples,
        )

    found_states = []
    for i, cmap_data in enumerate(cmap_iter):
        current_state = copy.deepcopy(initial_state)
        current_state['name'] = make_name(i, cmap_data)

        print(f"Considering {current_state['name']}")

        if not cmap_setup_fn(current_state, cmap_data):
            continue

        cmap_creation_fn(current_state)

        if not cmap_filter_fn(current_state, similarity_threshold):
            continue

        lightness_diff = (
            current_state['cmap']['final_lightness']
            - current_state['cmap']['initial_lightness']
            )

        print(f"Lightness difference is {lightness_diff}.")
        if lightness_diff < lightness_threshold:
            print("Rejecting due to size of lightness difference.")
            continue

        # One way in which optimization can fail is by producing
        # a color map where the chroma is wrong.  We reject the
        # color map if the chroma differs from the target by more
        # than 5%.
        if abs(current_state['cmap']['chroma'] / colorfulness - 1.0) > 0.05:
            print(
                "Rejecting due to colorfulness of"
                f" {current_state['cmap']['chroma']}"
                )
            continue

        # Reject results that are too close to other found states
        for s in found_states:
            if np.all(
                    np.abs(
                        s['cmap']['sequence_data']
                        - current_state['cmap']['sequence_data']
                        )
                    < similarity_threshold
                    ):
                print(
                    "Rejecting because",
                    current_state['cmap']['sequence_data'],
                    "is too similar to",
                    s['cmap']['sequence_data'],
                    " from",
                    s['name'],
                    )
                break
        else:
            print(
                "Accepting.  Sequence data is:",
                current_state['cmap']['sequence_data'],
                )
            found_states.append(current_state)

    return found_states


def _mseq_initial_setup(
        state,
        colorfulness,
        span,
        num_samples,
        num_seqs,
        num_extra_revolutions,
        ):
    state['cmap']['chroma'] = colorfulness
    state['parameters']['min_chroma'] = colorfulness
    state['parameters']['max_chroma'] = colorfulness
    state['parameters']['span_initial_hue'] = span / 2
    state['parameters']['span_final_hue'] = span / 2

    if num_seqs == 1:
        base_name = "cp_seq"
    else:
        base_name = "cp_mseq"

    arc_iter = directed_arcs(
        360 / num_samples, num_seqs, num_extra_revolutions,
        )

    def make_name(i, arcs):
        return (
            f"{base_name}_{i}_"
            + "_".join(
                map(str, map(round, itertools.chain.from_iterable(arcs)))
                )
            )

    return make_name, arc_iter


def _mseq_cmap_setup(state, arcs, max_arc_length, min_arc_length):
    hue_diffs = np.fromiter(
        map(operator.itemgetter(1), arcs),
        dtype=np.float64,
        )
    if np.any(
            (np.abs(hue_diffs) > max_arc_length)
            | (np.abs(hue_diffs) < min_arc_length)
            ):
        return False

    state['cmap']['sequence_data'] = np.fromiter(
        itertools.chain.from_iterable(arcs),
        dtype=np.float64,
        )
    state['parameters']['center_initial_hue'] = np.fromiter(
        map(operator.itemgetter(0), arcs),
        dtype=np.float64,
        )
    state['parameters']['center_final_hue'] = (
        state['parameters']['center_initial_hue']
        + hue_diffs
        )

    return True


def _mseq_cmap_filter(state, similarity_threshold):
    seqs = state['cmap']['sequence_data'].reshape(-1, 2)
    for seq0, seq1 in itertools.combinations(seqs, 2):
        if np.all(np.abs(seq0 - seq1) < similarity_threshold):
            print(f"Rejecting because {seq0} and {seq1} are too similar.")
            return False
    return True


def make_mseq(
        num_samples,
        span,
        lightness_threshold,
        colorfulness,
        similarity_threshold,
        num_seqs,
        max_arc_length,
        min_arc_length,
        num_extra_revolutions,
        ):
    return _make(
        SEQUENTIAL_PARAMETERS,
        colorfulness,
        span,
        num_samples,
        lightness_threshold,
        similarity_threshold,
        functools.partial(
            _mseq_initial_setup,
            num_seqs=num_seqs,
            num_extra_revolutions=num_extra_revolutions,
            ),
        functools.partial(
            _mseq_cmap_setup,
            max_arc_length=max_arc_length,
            min_arc_length=min_arc_length,
            ),
        run.create_multiseq,
        _mseq_cmap_filter,
        )


def _div_initial_setup(
        state,
        colorfulness,
        span,
        num_samples,
        div_type,
        ):
    state['cmap']['chroma'] = colorfulness
    state['parameters']['min_chroma'] = colorfulness
    state['parameters']['max_chroma'] = colorfulness
    state['parameters']['span_initial_hue'] = span / 2
    state['parameters']['span_final_hue'] = span / 2

    if div_type == 'hill':
        state['parameters']['min_final_hue_separation'] = 0.0
        state['parameters']['max_final_hue_separation'] = 0.0
    else:
        state['parameters']['min_initial_hue_separation'] = 0.0
        state['parameters']['max_initial_hue_separation'] = 0.0

    arc_iter = marked_arcs(360 / num_samples)

    def make_name(i, arc):
        return (
            f"cp_div_{i}_"
            + "_".join(map(str, map(round, arc)))
            + f"_{div_type}"
            )

    return make_name, arc_iter


def _div_cmap_setup(state, arc, max_arc_length, min_arc_length, div_type):
    lb, mark, ub = arc
    if not min_arc_length < ub - lb < max_arc_length:
        return False

    if div_type == 'hill':
        state['cmap']['sequence_data'] = np.array(
            [lb, mark - lb, ub, mark - ub]
            )
        state['parameters']['center_initial_hue'] = np.array([lb, ub])
        state['parameters']['center_final_hue'] = np.array([mark, mark])
    else:
        state['cmap']['sequence_data'] = np.array(
            [mark, lb - mark, mark, ub - mark]
            )
        state['parameters']['center_initial_hue'] = np.array([mark, mark])
        state['parameters']['center_final_hue'] = np.array([lb, ub])

    return True


def make_div(
        num_samples,
        span,
        lightness_threshold,
        colorfulness,
        similarity_threshold,
        max_arc_length,
        min_arc_length,
        ):
    return (
        *_make(
            DIVERGENT_HILL_PARAMETERS,
            colorfulness,
            span,
            num_samples,
            lightness_threshold,
            similarity_threshold,
            functools.partial(
                _div_initial_setup,
                div_type='hill',
                ),
            functools.partial(
                _div_cmap_setup,
                max_arc_length=max_arc_length,
                min_arc_length=min_arc_length,
                div_type='hill',
                ),
            run.create_multiseq,
            _mseq_cmap_filter,
            ),
        *_make(
            DIVERGENT_VALLEY_PARAMETERS,
            colorfulness,
            span,
            num_samples,
            lightness_threshold,
            similarity_threshold,
            functools.partial(
                _div_initial_setup,
                div_type='valley',
                ),
            functools.partial(
                _div_cmap_setup,
                max_arc_length=max_arc_length,
                min_arc_length=min_arc_length,
                div_type='valley',
                ),
            run.create_multiseq,
            _mseq_cmap_filter,
            ),
        )


def _cyc_initial_setup(state, colorfulness, span, num_samples):
    state['cmap']['chroma'] = colorfulness
    state['parameters']['min_chroma'] = colorfulness
    state['parameters']['max_chroma'] = colorfulness
    state['parameters']['span_hue'] = span / 2

    angle_iter = np.linspace(0, 360, num_samples, dtype=np.float64)

    def make_name(i, angle):
        return f"cp_cyc_{i}_{round(angle)}"

    return make_name, angle_iter


def _cyc_cmap_setup(state, angle):
    state['cmap']['sequence_data'] = np.array(angle)
    state['parameters']['center_hue'] = angle
    return True


def _cyc_cmap_filter(state, similarity_threshold):
    return True


def make_cyc(
        num_samples,
        span,
        lightness_threshold,
        colorfulness,
        similarity_threshold,
        ):
    return _make(
        CYCLIC_PARAMETERS,
        colorfulness,
        span,
        num_samples,
        lightness_threshold,
        similarity_threshold,
        _cyc_initial_setup,
        _cyc_cmap_setup,
        run.create_cyclic,
        _cyc_cmap_filter,
        )


def _isolum_initial_setup(state, colorfulness, span, num_samples):
    state['cmap']['chroma'] = colorfulness
    state['parameters']['min_chroma'] = colorfulness
    state['parameters']['max_chroma'] = colorfulness
    state['parameters']['span_initial_hue'] = span / 2
    state['parameters']['span_final_hue'] = span / 2

    arc_iter = arcs_around_circle(360 / num_samples, 1)

    def make_name(i, arcs):
        return (
            f"cp_isolum_{i}_"
            + "_".join(
                map(str, map(round, itertools.chain.from_iterable(arcs)))
                )
            )

    return make_name, arc_iter


def _isolum_cmap_setup(state, angle):
    state['cmap']['sequence_data'] = np.array(angle)
    state['parameters']['center_hue'] = angle
    return True


def _isolum_cmap_filter(state, similarity_threshold):
    return True


def make_isolum(
        num_samples,
        span,
        colorfulness,
        similarity_threshold,
        max_arc_length,
        min_arc_length,
        ):
    return _make(
        ISOLUM_PARAMETERS,
        colorfulness,
        span,
        num_samples,
        0.0,
        similarity_threshold,
        _isolum_initial_setup,
        functools.partial(
            _mseq_cmap_setup,
            max_arc_length=max_arc_length,
            min_arc_length=min_arc_length,
            ),
        run.create_multiseq,
        _isolum_cmap_filter,
        )
