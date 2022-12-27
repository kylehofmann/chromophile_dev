"""
Optimization functions
"""

import itertools

import numpy as np
import scipy.optimize

from . import cmap


def _extend_parameter(num_seqs, parameters, key):
    param = np.array(parameters.get(key))
    if param.size == 1:
        param = param.repeat(num_seqs)
    return param


def Jp_C_bounds(parameters):
    lower_bounds = np.r_[
        parameters['min_initial_lightness'],
        parameters['min_final_lightness'],
        parameters['min_chroma'],
        ]
    upper_bounds = np.r_[
        parameters['max_initial_lightness'],
        parameters['max_final_lightness'],
        parameters['max_chroma'],
        ]

    return lower_bounds, upper_bounds


def mseq_hue_bounds(num_seqs, parameters):
    center_initial_hue = _extend_parameter(
        num_seqs, parameters, 'center_initial_hue',
        )
    span_initial_hue = _extend_parameter(
        num_seqs, parameters, 'span_initial_hue',
        )
    min_hue_diff = _extend_parameter(num_seqs, parameters, 'min_hue_diff')
    max_hue_diff = _extend_parameter(num_seqs, parameters, 'max_hue_diff')

    initial_hue_lower_bounds = center_initial_hue - span_initial_hue
    initial_hue_upper_bounds = center_initial_hue + span_initial_hue

    lower_bounds = np.c_[initial_hue_lower_bounds, min_hue_diff].ravel()
    upper_bounds = np.c_[initial_hue_upper_bounds, max_hue_diff].ravel()

    return lower_bounds, upper_bounds


def mseq_bounds(num_seqs, parameters):
    Jp_C_lb, Jp_C_ub = Jp_C_bounds(parameters)
    initial_hue_lb, initial_hue_ub = mseq_hue_bounds(num_seqs, parameters)

    lower_bounds = np.hstack((Jp_C_lb, initial_hue_lb))
    upper_bounds = np.hstack((Jp_C_ub, initial_hue_ub))

    return scipy.optimize.Bounds(lower_bounds, upper_bounds)


def cyclic_hue_bounds(parameters):
    center_hue = parameters.get('center_hue', 0.0)
    span_hue = parameters.get('span_hue', 0.0)

    hue_lower_bound = center_hue - span_hue
    hue_upper_bound = center_hue + span_hue

    return hue_lower_bound, hue_upper_bound


def cyclic_bounds(parameters):
    Jp_C_lb, Jp_C_ub = Jp_C_bounds(parameters)
    hue_lb, hue_ub = cyclic_hue_bounds(parameters)

    lower_bounds = np.hstack((Jp_C_lb, hue_lb))
    upper_bounds = np.hstack((Jp_C_ub, hue_ub))

    return scipy.optimize.Bounds(lower_bounds, upper_bounds)


def lightness_diff_constraint(parameters):
    functional = np.array([-1., 1., 0.])
    lower_bound = np.array(parameters['min_lightness_diff'])
    upper_bound = np.array(parameters['max_lightness_diff'])

    return functional, lower_bound, upper_bound


def mseq_final_hue_constraints(num_seqs, parameters):
    final_hue_functionals = (
        np.eye(num_seqs).ravel().repeat(2).reshape((num_seqs, -1))
        )

    center_final_hue = _extend_parameter(
        num_seqs, parameters, 'center_final_hue',
        )
    span_final_hue = _extend_parameter(num_seqs, parameters, 'span_final_hue')

    final_hue_lower_bounds = center_final_hue - span_final_hue
    final_hue_upper_bounds = center_final_hue + span_final_hue

    return (
        final_hue_functionals, final_hue_lower_bounds, final_hue_upper_bounds,
        )


def mseq_hue_separation_constraints(num_seqs, parameters):
    num_pairs = num_seqs * (num_seqs - 1) // 2

    initial_hue_sep_functionals = np.zeros(
        (num_pairs, 2 * num_seqs), dtype=np.float64,
        )
    final_hue_sep_functionals = np.zeros(
        (num_pairs, 2 * num_seqs), dtype=np.float64,
        )

    for i, (j, k) in enumerate(itertools.combinations(range(num_seqs), 2)):
        initial_hue_sep_functionals[i, 2 * j] = 1
        initial_hue_sep_functionals[i, 2 * k] = -1
        final_hue_sep_functionals[i, 2 * j] = 1
        final_hue_sep_functionals[i, 2 * j + 1] = 1
        final_hue_sep_functionals[i, 2 * k] = -1
        final_hue_sep_functionals[i, 2 * k + 1] = -1

    initial_hue_sep_lb = np.array(parameters['min_initial_hue_separation'])
    if initial_hue_sep_lb.size == 1:
        initial_hue_sep_lb = initial_hue_sep_lb.repeat(num_pairs)

    initial_hue_sep_ub = np.array(parameters['max_initial_hue_separation'])
    if initial_hue_sep_ub.size == 1:
        initial_hue_sep_ub = initial_hue_sep_ub.repeat(num_pairs)

    final_hue_sep_lb = np.array(parameters['min_final_hue_separation'])
    if final_hue_sep_lb.size == 1:
        final_hue_sep_lb = final_hue_sep_lb.repeat(num_pairs)

    final_hue_sep_ub = np.array(parameters['max_final_hue_separation'])
    if final_hue_sep_ub.size == 1:
        final_hue_sep_ub = final_hue_sep_ub.repeat(num_pairs)

    functionals = np.vstack(
        (initial_hue_sep_functionals, final_hue_sep_functionals),
        )

    lower_bounds = np.hstack((initial_hue_sep_lb, final_hue_sep_lb))
    upper_bounds = np.hstack((initial_hue_sep_ub, final_hue_sep_ub))

    return functionals, lower_bounds, upper_bounds


def mseq_linear_constraints(num_seqs, parameters):
    Jp_diff_func, Jp_diff_lb, Jp_diff_ub = lightness_diff_constraint(
        parameters,
    )
    final_hue_func, final_hue_lb, final_hue_ub = mseq_final_hue_constraints(
        num_seqs, parameters,
    )
    hue_sep_func, hue_sep_lb, hue_sep_ub = mseq_hue_separation_constraints(
        num_seqs, parameters,
    )

    hue_funcs = np.vstack((final_hue_func, hue_sep_func))

    functionals = np.block(
        [
            [Jp_diff_func, np.zeros(2 * num_seqs)],
            [np.zeros((hue_funcs.shape[0], 3)), hue_funcs],
        ]
        )

    lower_bounds = np.hstack((Jp_diff_lb, final_hue_lb, hue_sep_lb))
    upper_bounds = np.hstack((Jp_diff_ub, final_hue_ub, hue_sep_ub))

    return scipy.optimize.LinearConstraint(
        functionals, lower_bounds, upper_bounds,
        )


def cyclic_linear_constraints(parameters):
    Jp_diff_func, Jp_diff_lb, Jp_diff_ub = lightness_diff_constraint(
        parameters,
        )

    functionals = np.r_[Jp_diff_func, 0.]
    lower_bounds = Jp_diff_lb
    upper_bounds = Jp_diff_ub

    return scipy.optimize.LinearConstraint(
        functionals, lower_bounds, upper_bounds,
        )


def sRGB_cmap_constraint(
        cmap_fn, num_samples, conversions, allowed_gamut_error,
        ):
    sRGB_lower_bound = -allowed_gamut_error
    sRGB_upper_bound = 1. + allowed_gamut_error
    lower_bounds = (sRGB_lower_bound,) * (3 * num_samples)
    upper_bounds = (sRGB_upper_bound,) * (3 * num_samples)

    uniform_to_sRGB = conversions['uniform_to_sRGB']

    def constraint_fn(v):
        cmap_uniform = cmap_fn(v)
        cmap_sRGB = uniform_to_sRGB(cmap_uniform)
        return cmap_sRGB.ravel()

    return scipy.optimize.NonlinearConstraint(
        constraint_fn, lower_bounds, upper_bounds, jac='3-point',
        )


def mseq_sRGB_cmap_constraint(cmap_fn, num_seqs, parameters, conversions):
    num_samples = num_seqs * parameters['constraint_samples_per_sequence']
    if parameters['cone'] or parameters['cylinder']:
        num_samples *= parameters['Jp_constraint_samples']

    return sRGB_cmap_constraint(
        cmap_fn, num_samples, conversions, parameters['allowed_gamut_error'],
        )


def cyclic_sRGB_cmap_constraint(cmap_fn, parameters, conversions):
    num_samples = parameters['constraint_samples_per_sequence']
    if parameters['cone'] or parameters['cylinder']:
        num_samples *= parameters['Jp_constraint_samples']

    return sRGB_cmap_constraint(
        cmap_fn, num_samples, conversions, parameters['allowed_gamut_error'],
        )


def mseq_parse_initial(cm):
    v = np.array(
        [
            cm['initial_lightness'],
            cm['final_lightness'],
            cm['chroma'],
            *cm['sequence_data'],
        ],
        )
    return v


def mseq_parse_result(v):
    initial_lightness, final_lightness, chroma, *sequence_data = v
    sequence_data = np.rad2deg(sequence_data)
    return initial_lightness, final_lightness, chroma, sequence_data


def mseq_cmap_function(parameters):
    num_samples_per_sequence = parameters['constraint_samples_per_sequence']

    def cmap_func(v):
        return cmap.multisequential(
            num_samples_per_sequence,
            v[0],
            v[1],
            v[2],
            v[3::2],
            v[4::2],
            True,
            )

    return cmap_func


def mseq_cylinder_cmap_function(parameters):
    num_samples_per_sequence = parameters['constraint_samples_per_sequence']
    num_cylinder_samples = parameters['Jp_constraint_samples']

    def cmap_func(v):
        return cmap.cylinder(
            num_samples_per_sequence,
            v[0],
            v[1],
            v[2],
            v[3::2],
            v[4::2],
            True,
            num_cylinder_samples,
            ).reshape(-1, 3)

    return cmap_func


def mseq_cone_cmap_function(parameters):
    num_samples_per_sequence = parameters['constraint_samples_per_sequence']
    num_cone_samples = parameters['Jp_constraint_samples']

    def cmap_func(v):
        return cmap.cone(
            num_samples_per_sequence,
            v[0],
            v[1],
            v[2],
            v[3::2],
            v[4::2],
            True,
            num_cone_samples,
            ).reshape(-1, 3)

    return cmap_func


def mseq_objective(parameters):
    linear_weights = np.array([
        parameters['weight_initial_lightness'],
        parameters['weight_final_lightness'],
        parameters['weight_chroma'],
        ])

    weight_lightness_diff = parameters['weight_lightness_diff']
    weight_hue_initial_separation = parameters['weight_hue_initial_separation']
    weight_hue_final_separation = parameters['weight_hue_final_separation']
    weight_hue_diff = parameters['weight_hue_diff']
    weight_squared_hue_diff = parameters['weight_squared_hue_diff']

    # Normalize.  Angles are between -pi and pi, but after
    # rescaling this way, they're effectively between -1 and 1
    # like lightness differences.
    #
    # Some of these may be arrays, so we make sure not to do this
    # in-place in case it modifies the originals.
    weight_hue_initial_separation = weight_hue_initial_separation / np.pi
    weight_hue_final_separation = weight_hue_final_separation / np.pi
    weight_hue_diff = weight_hue_diff / np.pi
    weight_squared_hue_diff = weight_squared_hue_diff / np.pi

    linear_score_slice = np.s_[0:3]
    seq_initial_hues_slice = np.s_[3::2]
    seq_hue_diffs_slice = np.s_[4::2]
    seq_hues_and_diffs_slice = np.s_[3:]

    def objective(v):
        linear_score = np.inner(linear_weights, v[linear_score_slice])

        initial_seq_hues = v[seq_initial_hues_slice]
        seq_hue_diffs = v[seq_hue_diffs_slice]

        hue_diff_score = (
            np.sum(weight_hue_diff * seq_hue_diffs)
            + np.sum(weight_squared_hue_diff * seq_hue_diffs**2)
            )

        lightness_diff = v[1] - v[0]
        lightness_diff_score = weight_lightness_diff * lightness_diff**2

        initial_hue_seps = (
            initial_seq_hues[None, :] - initial_seq_hues[:, None]
            )

        initial_hue_seps += np.pi
        initial_hue_seps %= 2. * np.pi
        initial_hue_seps -= np.pi
        initial_hue_seps_score = (
            weight_hue_initial_separation * np.sum(initial_hue_seps**2)
            )

        final_seq_hues = initial_seq_hues + seq_hue_diffs
        final_hue_seps = final_seq_hues[None, :] - final_seq_hues[:, None]
        final_hue_seps += np.pi
        final_hue_seps %= 2. * np.pi
        final_hue_seps -= np.pi
        final_hue_seps_score = (
            weight_hue_final_separation * np.sum(final_hue_seps**2)
            )
        score = (
            linear_score
            + hue_diff_score
            + lightness_diff_score
            + initial_hue_seps_score
            + final_hue_seps_score
            )

        jac = np.zeros_like(v)
        jac[:3] = linear_weights
        jac[0] += weight_lightness_diff * -2. * lightness_diff
        jac[1] += weight_lightness_diff * 2. * lightness_diff
        jac[seq_initial_hues_slice] = (
            weight_hue_initial_separation
            * -4.
            * np.sum(initial_hue_seps, axis=1)
            )
        jac[seq_hue_diffs_slice] = (
            weight_hue_diff
            + weight_squared_hue_diff * 2. * v[seq_hue_diffs_slice]
            )

        final_hue_jac = (
            weight_hue_final_separation * 4. * np.sum(final_hue_seps, axis=1)
            )
        jac[seq_initial_hues_slice] -= final_hue_jac
        jac[seq_hue_diffs_slice] -= final_hue_jac

        return (-score, -jac)

    def hessian(v):
        n = v.size
        hess = np.zeros((n, n), dtype=np.float64)

        # Lightness diff
        hess[0, 0] = 2 * weight_lightness_diff
        hess[0, 1] = -2 * weight_lightness_diff
        hess[1, 0] = -2 * weight_lightness_diff
        hess[1, 1] = 2 * weight_lightness_diff

        # Squared hue diffs
        h_hue_diff = hess[seq_hue_diffs_slice, seq_hue_diffs_slice]
        np.fill_diagonal(h_hue_diff, 2. * weight_squared_hue_diff)

        # Hue separation
        h_hues = hess[seq_initial_hues_slice, seq_initial_hues_slice]
        h_hues[:] = -4. * weight_hue_initial_separation
        np.fill_diagonal(
            h_hues,
            4. * (n-3) / 2 * weight_hue_initial_separation,
            )

        # Final hue separation
        h_hues_and_diffs = hess[
            seq_hues_and_diffs_slice, seq_hues_and_diffs_slice
            ]
        h_hues_and_diffs[:] += weight_hue_final_separation * (
            np.kron(
                np.eye((n-3) // 2, dtype=np.int64),
                np.full((2, 2), 4. * (n-3) / 2),
                ) - 4
            )

        return -hess

    return objective, hessian


def mseq_opt_setup(state, cmap_func):
    num_seqs = len(state['cmap']['sequence_data']) // 2

    initial = mseq_parse_initial(state['cmap'])
    objective, hessian = mseq_objective(state['parameters'])

    bounds = mseq_bounds(num_seqs, state['parameters'])
    constraints = [
        mseq_linear_constraints(num_seqs, state['parameters']),
        mseq_sRGB_cmap_constraint(
            cmap_func, num_seqs, state['parameters'], state['conversions'],
            ),
        ]

    args = (objective, initial)
    kwargs = {
        'bounds': bounds,
        'constraints': constraints,
        'jac': True,
        'hess': hessian,
        }
    return args, kwargs


def cyclic_parse_initial(cm):
    v = np.array(
        [
            cm['initial_lightness'],
            cm['final_lightness'],
            cm['chroma'],
            cm['sequence_data'],
        ],
        )
    return v


def cyclic_parse_result(v):
    initial_lightness, final_lightness, chroma, hue = v
    hue = np.rad2deg(hue)
    return initial_lightness, final_lightness, chroma, hue


def cyclic_cmap_function(parameters):
    num_samples = parameters['constraint_samples_per_sequence']

    def cmap_func(v):
        return cmap.cyclic(
            num_samples,
            v[0],
            v[1],
            v[2],
            v[3],
            )

    return cmap_func


def cyclic_cylinder_cmap_function(parameters):
    num_samples = parameters['constraint_samples_per_sequence']
    num_samples_per_sequence = num_samples // 2
    num_cylinder_samples = parameters['Jp_constraint_samples']

    def cmap_func(v):
        return cmap.cylinder(
            num_samples_per_sequence,
            v[0],
            v[1],
            v[2],
            np.array((v[3], v[3] + np.pi)),
            np.array((np.pi, np.pi)),
            False,
            num_cylinder_samples,
            )

    return cmap_func


def cyclic_cone_cmap_function(parameters):
    num_samples = parameters['constraint_samples_per_sequence']
    num_samples_per_sequence = num_samples // 2
    num_cone_samples = parameters['Jp_constraint_samples']

    def cmap_func(v):
        return cmap.cone(
            num_samples_per_sequence,
            v[0],
            v[1],
            v[2],
            np.array((v[3], v[3] + np.pi)),
            np.array((np.pi, np.pi)),
            False,
            num_cone_samples,
            )

    return cmap_func


def cyclic_objective(parameters):
    linear_weights = np.array([
        parameters['weight_initial_lightness'],
        parameters['weight_final_lightness'],
        parameters['weight_chroma'],
        ])

    weight_lightness_diff = parameters['weight_lightness_diff']

    linear_score_slice = np.s_[0:3]

    def objective(v):
        linear_score = np.inner(linear_weights, v[linear_score_slice])

        lightness_diff = v[1] - v[0]
        lightness_diff_score = weight_lightness_diff * lightness_diff**2

        score = linear_score + lightness_diff_score

        jac = np.zeros_like(v)
        jac[:3] = linear_weights
        jac[0] += weight_lightness_diff * -2. * lightness_diff
        jac[1] += weight_lightness_diff * 2. * lightness_diff

        return (-score, -jac)

    def hessian(v):
        n = v.size
        hess = np.zeros((n, n), dtype=np.float64)

        # Lightness diff
        hess[0, 0] = 2 * weight_lightness_diff
        hess[0, 1] = -2 * weight_lightness_diff
        hess[1, 0] = -2 * weight_lightness_diff
        hess[1, 1] = 2 * weight_lightness_diff

        return -hess

    return objective, hessian


def cyclic_opt_setup(state, cmap_func):
    initial = cyclic_parse_initial(state['cmap'])
    objective, hessian = cyclic_objective(state['parameters'])

    bounds = cyclic_bounds(state['parameters'])
    constraints = [
        cyclic_linear_constraints(state['parameters']),
        cyclic_sRGB_cmap_constraint(
            cmap_func,
            state['parameters'],
            state['conversions'],
            ),
        ]

    args = (objective, initial)
    kwargs = {
        'bounds': bounds,
        'constraints': constraints,
        'jac': True,
        'hess': hessian,
        }
    return args, kwargs


def optimization_setup(opt_parameters, verbose):
    options = {
        'maxiter': opt_parameters['maxiter'],
        'verbose': verbose,
        }

    kwargs = {
        'method': 'trust-constr',
        'options': options,
        'tol': opt_parameters['tol'],
        }

    return kwargs


def _optimize(opt_args, opt_kwargs, state):
    if state['verbose_optimize']:
        print("Beginning optimization.")

    result = scipy.optimize.minimize(*opt_args, **opt_kwargs)

    if state['verbose_optimize'] == 1:
        print(f"Final score: {-result.fun}")
        print(result.message)
    elif state['verbose_optimize'] > 1:
        print(result)

    return result.x


def mseq_optimize(state):
    if state['parameters']['cone']:
        cmap_func = mseq_cone_cmap_function(state['parameters'])
    elif state['parameters']['cylinder']:
        cmap_func = mseq_cylinder_cmap_function(state['parameters'])
    else:
        cmap_func = mseq_cmap_function(state['parameters'])

    opt_kwargs = optimization_setup(
        state['opt_parameters'], state['verbose_optimize'],
        )

    opt_args, opt_mseq_kwargs = mseq_opt_setup(state, cmap_func)
    opt_kwargs.update(opt_mseq_kwargs)

    result = _optimize(opt_args, opt_kwargs, state)
    return result[0], result[1], result[2], result[3:]


def cyclic_optimize(state):
    if state['parameters']['cone']:
        cmap_func = cyclic_cone_cmap_function(state['parameters'])
    elif state['parameters']['cylinder']:
        cmap_func = cyclic_cylinder_cmap_function(state['parameters'])
    else:
        cmap_func = cyclic_cmap_function(state['parameters'])

    opt_kwargs = optimization_setup(
        state['opt_parameters'], state['verbose_optimize'],
        )

    opt_args, opt_mseq_kwargs = cyclic_opt_setup(state, cmap_func)
    opt_kwargs.update(opt_mseq_kwargs)

    result = _optimize(opt_args, opt_kwargs, state)
    return result[0], result[1], result[2], result[3]
