"""
Color conversion
"""

import collections
import functools
import heapq
import itertools
import operator
import pathlib
import pickle
import time
import warnings

import colour
import matplotlib as mpl
import numpy as np
import platformdirs
import scipy.spatial


# Fix a scale; don't guess.
colour.set_domain_range_scale(1)


def sRGB_nearest_neighbors_cache_path(space):
    cache_dir = pathlib.Path(
        platformdirs.user_cache_dir('chromophile_dev', appauthor=False)
        )
    cache_filename = (
        f"{space.lower()}_kdtree"
        f"_scipy-{scipy.__version__}"
        ".pickle"
        )
    cache_path = cache_dir / cache_filename

    return cache_path


@functools.cache
def sRGB_nearest_neighbors_get_cached(space, verbose):
    cache_path = sRGB_nearest_neighbors_cache_path(space)

    if verbose:
        print(
            "Looking for cached nearest neighbors data structure at",
            cache_path,
            )

    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, 'rb') as handle:
            kd_tree = pickle.load(handle)
    except (OSError, pickle.PickleError):
        return None
    else:
        return kd_tree


def sRGB_nearest_neighbors_store_cached(space, kd_tree):
    cache_path = sRGB_nearest_neighbors_cache_path(space)

    with open(cache_path, 'wb') as handle:
        pickle.dump(kd_tree, handle)


def sRGB_nearest_neighbors_generate(conversions, verbose):
    if verbose:
        print("Generating sRGB nearest neighbors data structure")

    start_time = time.monotonic()

    sRGB256_range = np.arange(256, dtype=np.uint8)
    rr, gg, bb = np.meshgrid(
        sRGB256_range, sRGB256_range, sRGB256_range, indexing='ij',
        )
    all_sRGB256 = np.c_[rr.ravel(), gg.ravel(), bb.ravel()]
    all_uniform = conversions['sRGB_to_uniform'](sRGB256_to_sRGB1(all_sRGB256))

    kd_tree = scipy.spatial.KDTree(all_uniform)

    end_time = time.monotonic()

    if verbose:
        print(f"Generation time was {end_time - start_time} seconds.")

    return kd_tree


def sRGB_nearest_neighbors_structure(
        space, conversions, verbose,
        ):
    kd_tree = sRGB_nearest_neighbors_get_cached(space, verbose)
    if kd_tree is None:
        kd_tree = sRGB_nearest_neighbors_generate(conversions, verbose)
        sRGB_nearest_neighbors_store_cached(space, kd_tree)

    return kd_tree


def unpack_sRGB_indices(packed):
    unpacked = np.empty((*packed.shape, 3), dtype=np.uint8)
    unpacked[..., 2] = packed & 255
    unpacked[..., 1] = (packed >> 8) & 255
    unpacked[..., 0] = (packed >> 16) & 255
    return unpacked


def uniform_space_conversions(space):
    space = space.lower()

    # The following function is undocumented, but it's precisely
    # what we need.
    conversion_path = colour.graph.conversion._conversion_path

    sRGB_to_uniform_path = conversion_path('srgb', space)
    uniform_to_sRGB_path = conversion_path(space, 'srgb')

    # Use linear sRGB space

    def sRGB_to_uniform(v):
        with np.errstate(all='ignore'):
            for fn in sRGB_to_uniform_path:
                v = fn(v)
        return v

    def uniform_to_sRGB(v):
        with np.errstate(all='ignore'):
            for fn in uniform_to_sRGB_path:
                v = fn(v)
        return v

    return sRGB_to_uniform, uniform_to_sRGB


def sRGB1_validity(x):
    """Returns booleans indicating where x defines valid sRGB1 points

    Since sRGB is quantized, we assume that x is valid until it's
    closer to where the next quantized value would be, if
    quantized values could extend below 0 or above 255.  That is,
    our limits are -1/(2*255) and 1 + 1/(2*255).
    """

    valid_entries = x >= -1 / (2 * 255)
    valid_entries &= x <= 1 + 1 / (2 * 255)
    valid_entries &= np.isfinite(x)
    return np.all(valid_entries, axis=-1)


def sRGB1_to_sRGB256(x):
    """
    Convert sRGB floats to bytes

    The input is assumed to consist of triples of floating-point
    numbers in gamma-corrected sRGB space with coordinates in [0,
    1].  This function quantizes to integers between 0 and 255.
    """

    y = x * 255.
    np.round(y, out=y)
    np.clip(y, 0., 255., out=y)
    return y.astype(np.uint8)


def sRGB256_to_sRGB1(x):
    """Convert sRGB bytes to floats"""

    return x.astype(np.float64) / 255.0


def sRGB256_to_sRGB1_epsilon(x):
    """Convert sRGB bytes to floats, adding epsilon

    This is the same as sRGB256_to_sRGB1, except we add a tiny
    amount.  This is because some software works with
    floating-point RGB values in [0, 1], but what ultimately gets
    displayed on the screen must be bytes.  Matplotlib, and
    probably other software too, multiplies by 255 and casts to a
    byte, that is, it takes a floor.  So [0, 1/255) is sent to
    zero, [1/255, 2/255) is sent to one, and so on.  The only way
    to get an output of 255 is to use the number 1, since the
    rest of the interval [255/255, 256/255) is outside of the
    gamut.

    To ensure we get the results we want, we need to send a byte
    value of x to something in the range [x/255, (x+1)/255).  We
    do this by sending x to x/255 + 1/(4*255).  The addition is
    to ensure that we don't accidentally round down, and we
    choose 1/(4*255) because this should always be small enough
    that we never accidentally round up.  We clip to ensure that
    we don't exceed 1, since that can cause out-of-gamut
    warnings.
    """

    sRGB1_colors = x / 255 + 1 / (4 * 255)
    np.clip(sRGB1_colors, 0.0, 1.0, out=sRGB1_colors)
    return sRGB1_colors


def sRGB256_to_mpl(cmap, name=None):
    """Converts sRGB byte values to a Matplotlib color map"""

    mpl_colors = sRGB256_to_sRGB1_epsilon(cmap)
    return mpl.colors.ListedColormap(mpl_colors, name=name)


def _sRGB_heuristic_score_ndarray(nearby_idxs, square_distances, neighbors):
    cmap_len = len(neighbors)

    score = np.sum(np.choose(neighbors, square_distances[:cmap_len].T))
    current_cmap_color_idxs = set(
        np.choose(neighbors, nearby_idxs[:cmap_len].T)
        )

    extended_cmap_idxs = nearby_idxs[cmap_len:, 0]
    collisions = collections.defaultdict(list)
    for color_num, color_idx in enumerate(extended_cmap_idxs, start=cmap_len):
        collisions[color_idx].append(color_num)

    for colliding_color, collision_idxs in collisions.items():
        if colliding_color in current_cmap_color_idxs:
            # All colliding indices are replaced by second best
            # sRGB approximations
            score += np.sum(square_distances[collision_idxs, 1])
        elif len(collision_idxs) == 1:
            # Special code path for the most common case.  The
            # general path below is correct in this case, but
            # this path is faster and more numerically accurate.
            score += square_distances[collision_idxs[0], 0]
        else:
            # Find biggest gap between best and second best sRGB
            # approximations; use the best approximation for the
            # color with the biggest gap and the second best for
            # the others.
            collision_sq_dists = square_distances[collision_idxs, 0:2]
            score += np.sum(collision_sq_dists[:, 1])
            score -= np.max(
                collision_sq_dists[:, 1] - collision_sq_dists[:, 0]
                )

    return score


def _sRGB_heuristic_score_list(nearby_idxs, square_distances, neighbors):
    cmap_len = len(neighbors)

    score = sum(
        itertools.starmap(
            operator.getitem,
            zip(square_distances[:cmap_len], neighbors),
            )
        )
    current_cmap_color_idxs = set(
        itertools.starmap(
            operator.getitem,
            zip(nearby_idxs[:cmap_len], neighbors),
            )
        )

    extended_cmap_idxs = map(operator.itemgetter(0), nearby_idxs[cmap_len:])
    collisions = collections.defaultdict(list)
    for color_num, color_idx in enumerate(extended_cmap_idxs, start=cmap_len):
        collisions[color_idx].append(color_num)

    for colliding_color, collision_idxs in collisions.items():
        if colliding_color in current_cmap_color_idxs:
            # All colliding indices are replaced by second best
            # sRGB approximations
            for idx in collision_idxs:
                sq_dists = square_distances[idx]
                if len(sq_dists) <= 1:
                    return np.inf
                score += square_distances[idx][1]
        elif len(collision_idxs) == 1:
            # Common case with a fast path
            score += square_distances[collision_idxs[0]][0]
        else:
            # Find biggest gap between best and second best
            # sRGB approximations; use the best approximation
            # for the color with the biggest gap and the
            # second best for the others.
            max_diff = np.float64(0.0)
            for idx in collision_idxs:
                sq_dists = square_distances[idx]
                if len(sq_dists) == 1:
                    if max_diff == np.inf:
                        # Two colors have only a single
                        # approximation available, and those
                        # approximations collide.
                        return np.inf
                    score += sq_dists[0]
                    max_diff = np.inf
                else:
                    score += sq_dists[1]
                    diff = sq_dists[1] - sq_dists[0]
                    if diff > max_diff:
                        max_diff = diff
            if max_diff != np.inf:
                score -= max_diff

    return score


def sRGB_heuristic_score(nearby_idxs, square_distances, neighbors):
    """Find a heuristic score for a partial sRGB approximation

    We extend `nearby_idxs` to an approximation of the entire
    color map by taking the nearest sRGB approximation to all the
    remaining colors.  Then we partition the indices of the
    entries of `nearby_idxs` by value, that is, we determine
    which entries of `nearby_idxs` collide.  When a set has only
    a single entry, then the square distance for that entry
    contributes to the score as-is.  When a set has several
    entries, we improve the heuristic score by resolving some of
    the collisions.  We know that only one of the entries in the
    set can retain its present value.  If one of the entires was
    already in `nearby_idxs`, then it is the one to retain its
    value, and the others are switched to the second-best sRGB
    approximations of the colors they are trying to approximate.
    Otherwise, all but one are switched; the unswitched color is
    chosen to minimize the total error of the set.  This is
    equivalent to choosing it to be the color where the gap
    between the best and second best sRGB approximations is
    as large as possible.
    """

    if isinstance(square_distances, np.ndarray):
        return _sRGB_heuristic_score_ndarray(
            nearby_idxs, square_distances, neighbors,
            )
    else:
        return _sRGB_heuristic_score_list(
            nearby_idxs, square_distances, neighbors,
            )


def find_sRGB_approximation(
        cmap_uniform,
        sRGB_points,
        nearby_idxs,
        square_distances,
        bound,
        max_iters,
        verbose,
        ):
    """
    Find an sRGB approximation to a color map

    This function finds an sRGB approximation of cmap_uniform.
    The points it uses for this approximation are in nearby_idxs;
    this is a sequence whose i'th entry is a list of all points
    which can be used to approximate cmap_uniform[i].  The
    squared distances from these points to cmap_uniform[i] are in
    square_distances.  The function returns the best
    approximation (measured using squared L^2 distance) that is
    less than the given bound, together with that approximation's
    squared L^2 distance.  It returns None and infinity if it
    failed to find an approximation.

    The function uses the A* algorithm to find its approximation.
    The underlying dynamic program builds the color map one color
    at a time starting at the first color.  At each step, the
    dynamic program has a partial color map (an assignment of
    some colors in cmap_uniform to nearby sRGB points), and it
    extends that assignment by a single step.  The A* heuristic
    simply predicts that every color in the color map for which
    we have not yet chosen an sRGB point will be assigned its
    nearest sRGB point.  This function also removes partial color
    maps when they coalesce: If it can guarantee that two partial
    color maps will be completed in the same way, then it prunes
    the one with the worse score.

    This function may be called twice.  It's called once with
    nearby_idxs containing a fixed number of sRGB approximations
    per color map point.  Then we optionally call it a second
    time with nearby_idxs containing all sRGB approximations
    within a certain radius.  The first call is used to produce a
    good approximate answer.  The second call is done to prove
    that we have the best color map (except for issues with
    floating point precision; that would require interval
    arithmetic).
    """

    initial_score = sRGB_heuristic_score(
        nearby_idxs, square_distances, np.array((), dtype=np.intp),
        )
    if initial_score > bound:
        # It's impossible to satisfy the bound
        return None, np.inf

    # The set of seen color sets is used to avoid doing
    # duplicative work.  At each step of the dynamic program, we
    # consider a new partial color map.  By the nature of the
    # dynamic program, that partial color map is the best way to
    # use that set of colors to fill out the beginning portion of
    # the final color map.  We hope to find the best way to
    # complete this partial color map to a full color map.  That
    # best completion depends only on which colors remain to be
    # approximated and which colors are still available for that
    # purpose.  If we ever come across another partial color map
    # which needs to approximate the same uniform space colors
    # with the same set of available sRGB colors, then the two
    # color maps have coalesced; we're guaranteed that the second
    # color map will ultimately be completed in the same way as
    # the first.  Since the second color map will still have a
    # higher score, there's no point in working on both, so we
    # prune it immediately.
    #
    # However, there's one other restriction that comes into play
    # here.  It's not quite true that the color maps will always
    # be completed the same way.  Remember that we require that
    # the sign of the change in J' is the same for the
    # approximations as it is for the pre-approximation points.
    # Because of this, the J' of the most recently chosen point
    # affects the possible ways of completing the color map.  It
    # can happen that the nearest approximation has a somewhat
    # larger value of J' than a further neighbor, and this can
    # cause us to have fewer possible ways of completing the
    # color map if we select the nearest neighbor instead of the
    # less near one.  The solution we adopt is to refine our
    # criterion for detecting duplicates slightly.  We say that
    # two partial color maps are duplicates if they have selected
    # approximations for the same colors, if their set of
    # possible remaining colors are the same, and the value of J'
    # in the last color is larger in the color map which is the
    # worse approximation (if the sign of the change in J' is
    # positive; otherwise, we change the direction of the
    # inequality).  If the current color map has the same key but
    # a smaller value of J', then we allow it to produce color
    # maps as long as the newly added colors are those that would
    # not have been allowed under the larger value of J'.
    remaining_color_sets = {}

    best_solution = None
    states = [(initial_score, np.array((), dtype=np.intp))]

    iter_num = 0
    while states:
        iter_num += 1
        if iter_num == max_iters:
            break

        current_score, current_neighbors = heapq.heappop(states)

        idx = len(current_neighbors)
        if idx == cmap_uniform.shape[0]:
            best_solution = current_neighbors
            break

        # This is the color map so far, but each color is stored
        # as a single 24-bit integer instead of as three 8-bit
        # integers.
        if isinstance(square_distances, list):
            cmap_so_far = (
                *itertools.starmap(
                    operator.getitem,
                    zip(nearby_idxs[:idx], current_neighbors),
                    ),
                )
        else:
            cmap_so_far = np.choose(current_neighbors, nearby_idxs[:idx].T)

        # Determine desired sign of change in J'
        if idx > 0:
            Jp_delta = cmap_uniform[idx][0] - cmap_uniform[idx - 1][0]
            if np.abs(Jp_delta) < 1e-10:
                Jp_sign = 0
            elif Jp_delta > 0:
                Jp_sign = 1
            else:
                Jp_sign = -1
            current_Jp = sRGB_points[cmap_so_far[idx - 1], 0]
        else:
            Jp_sign = 0
            # Placeholder.  Since Jp_sign = 0 in this case, the
            # actual value doesn't matter.
            current_Jp = 0.0

        # Test whether this partial color map should be pruned.
        remaining_color_set = set(
            itertools.chain.from_iterable(nearby_idxs[idx:])
            )
        remaining_color_set.difference_update(cmap_so_far)
        remaining_color_key = (idx, frozenset(remaining_color_set))

        # If Jp_sign is nonzero, the pruning tests need to
        # account for the sign; otherwise, they don't.
        if Jp_sign:
            # If we've observed this remaining color set before,
            # then we need to test whether we should prune.  But
            # if we haven't, then we won't prune.
            last_Jp = remaining_color_sets.get(remaining_color_key)

            # If Jp_sign is 1, we should prune if current_Jp >=
            # last_Jp; if it's -1, we should prune if current_Jp
            # <= last_Jp.  But we ought to be careful about
            # precision and not prune if the difference between
            # current_Jp and last_Jp is small enough to be
            # potentially due to numerical error during the
            # conversion from sRGB to the uniform color space.
            if last_Jp is not None and Jp_sign * (current_Jp - last_Jp) > 1e-10 * last_Jp:
                # Prune this color map.
                continue

            remaining_color_sets[remaining_color_key] = current_Jp
        else:
            if remaining_color_key in remaining_color_sets:
                continue

            # Since we're using a dictionary we need a value, but
            # in this case that value doesn't matter.
            remaining_color_sets[remaining_color_key] = 0.0

        # Add new states
        for i in range(len(nearby_idxs[idx])):
            next_pt = nearby_idxs[idx][i]
            # Check for collisions
            if np.any(next_pt == cmap_so_far):
                continue
            # Check sign of change in J'.  If Jp_sign = 0, then
            # we haven't previously considered any color maps
            # that will be completed like this one, so we're not
            # going to prune here.
            if Jp_sign and (
                    # Check whether the sign of the change in J'
                    # is what we want.  If Jp_sign = 1, the test
                    # passes if next_pt's J' is larger than the
                    # previous point's Jp.  If Jp_sign = -1, then
                    # it's the same except next_pt's J' must be
                    # smaller.
                    Jp_sign * (sRGB_points[next_pt, 0] - current_Jp) <= 0.0
                    # Check whether we've already created a color
                    # map whose completion will be better.  The
                    # test passes if, the last time we considered
                    # a color map that would be completed like
                    # this one, we would have rejected next_pt.
                    or (
                        last_Jp is not None
                        and Jp_sign * (sRGB_points[next_pt, 0] - last_Jp) > 0.0
                        )
                    ):
                continue

            new_neighbors = np.r_[current_neighbors, i]
            new_score = sRGB_heuristic_score(
                nearby_idxs, square_distances, new_neighbors,
                )
            if new_score > bound:
                continue

            heapq.heappush(states, (new_score, new_neighbors))

    if best_solution is None:
        return None, np.inf

    if verbose:
        print("Neighbor numbers of best solution were:")
        print(best_solution)

    best_cmap = np.fromiter(
        (idxs[nbs] for idxs, nbs in zip(nearby_idxs, best_solution)),
        dtype=np.int32,
        )

    cmap_sRGB256 = unpack_sRGB_indices(best_cmap)

    return cmap_sRGB256, current_score


def round_color_map_to_sRGB(
        cmap_uniform, parameters, post_opt_parameters, conversions, verbose,
        ):
    """
    Convert uniform color map to rounded sRGB

    This function carefully converts from a uniform color space
    to sRGB256.  It uses a k-d tree to look up the nearest (in
    uniform space) sRGB points to the points in the color map.
    On its first pass, it looks up only a fixed number of
    neighbors; it uses the result from that pass to get an upper
    bound on the distance of the neighbors it needs to consider.
    On its second pass, it produces a provably optimal
    approximation.  This is a simple kind of branch-and-bound.

    The color maps returned by this function have all their
    colors distinct.  The approximations also respect the input
    color maps direction of changes in J'; that is, any pair of
    successive colors for which J' is increasing in the input
    color map will have approximations which also have increasing
    J', and similarly for decreasing J'.
    """

    # Get or create nearest neighbors data structure
    kd_tree = sRGB_nearest_neighbors_structure(
        parameters['uniform_space'], conversions, verbose,
        )
    sRGB_points = kd_tree.data

    # On the first pass, find lots of nearest neighbors
    num_nearby_points = post_opt_parameters['sRGB_approximation_nearby_points']
    max_iters = post_opt_parameters['sRGB_approximation_maxiter']

    first_nearby_distances, first_nearby_idxs = kd_tree.query(
        cmap_uniform, num_nearby_points,
        )
    if num_nearby_points == 1:
        first_nearby_distances = first_nearby_distances[..., None]
        first_nearby_idxs = first_nearby_idxs[..., None]

    first_square_distances = np.square(first_nearby_distances)

    first_cmap_sRGB256, first_score = (
        find_sRGB_approximation(
            cmap_uniform,
            sRGB_points,
            first_nearby_idxs,
            first_square_distances,
            np.inf,
            max_iters,
            verbose,
            )
        )

    if verbose:
        print(f"Color map score was {first_score}")

    if first_cmap_sRGB256 is None:
        print(
            "Warning: Failed to find valid sRGB approximation. "
            " Returning nearest neighbor approximation."
            )
        cmap_naive_packed = np.take_along_axis(
            first_nearby_idxs,
            np.zeros(first_nearby_idxs.shape[0], dtype=np.intp)[..., None],
            axis=1,
            )[..., 0]
        cmap_naive = unpack_sRGB_indices(cmap_naive_packed)

        return cmap_naive

    if not post_opt_parameters['sRGB_approximation_proof']:
        return first_cmap_sRGB256

    # Now we know that there's some color map whose score is
    # first_score.  From this, we want an upper bounds on the
    # furthest approximations we have to consider.  An easy upper
    # bound on the furthest distance from point i comes from
    # assuming that every point except point i ends up with its
    # nearest neighbor; clearly we can't do better than that with
    # the other points.  The maximum squared distance we have to
    # consider for point i is the difference between first_score
    # and the sum of the squared distances of the other points to
    # their nearest neighbors.
    nn_bounds = np.sqrt(
        first_score - (
            np.sum(first_square_distances[..., 0])
            - first_square_distances[..., 0]
            )
        )

    second_nearby_idxs = kd_tree.query_ball_point(cmap_uniform, nn_bounds)

    second_square_distances = []
    for i, cur_idxs in enumerate(second_nearby_idxs):
        cur_square_distances = np.sum(
            np.square(kd_tree.data[cur_idxs] - cmap_uniform[i]),
            axis=-1,
            )

        sorter = np.argsort(cur_square_distances)
        cur_square_distances = cur_square_distances[sorter]
        second_nearby_idxs[i] = np.array(second_nearby_idxs[i])[sorter]

        second_square_distances.append(cur_square_distances)

    new_max_neighbor = max(map(len, second_nearby_idxs))
    if new_max_neighbor <= num_nearby_points:
        if verbose:
            print(
                "Found optimal color map on first pass. "
                f" {new_max_neighbor=}."
                )
        second_cmap_sRGB256 = first_cmap_sRGB256
        second_score = first_score
    elif new_max_neighbor > 1000:
        if verbose:
            print(
                "WARNING: Too many nearby neighbors! "
                " Not attempting to prove optimality!"
                )
        second_cmap_sRGB256 = first_cmap_sRGB256
        second_score = first_score
    else:
        second_cmap_sRGB256, second_score = find_sRGB_approximation(
            cmap_uniform,
            sRGB_points,
            second_nearby_idxs,
            second_square_distances,
            # Scale just a little so that numerical precision
            # issues don't throw us off
            first_score * (1.0 + 1e-12),
            max_iters,
            verbose,
            )

        # Check to see if we failed the second time around.  This
        # will happen if we reach the iteration limit.
        if second_cmap_sRGB256 is None:
            second_cmap_sRGB256 = first_cmap_sRGB256
            second_score = first_score

    if verbose:
        print(f"Second pass score was {second_score}")

    if second_score > first_score:
        print(
            f"WARNING: Second pass score of {second_score}"
            f" was larger than first pass score of {first_score}!"
            )

    return second_cmap_sRGB256


def color_maps_from_uniform(
        cmap_uniform,
        name,
        parameters,
        post_opt_parameters,
        conversions,
        verbose,
        ):
    """Generates color maps from initial uniform color map"""

    cmap_sRGB256 = np.empty_like(cmap_uniform, dtype=np.uint8)
    for idx in np.ndindex(cmap_uniform.shape[:-2]):
        current_cmap_uniform = cmap_uniform[idx]
        cmap_sRGB256[idx] = round_color_map_to_sRGB(
            current_cmap_uniform,
            parameters,
            post_opt_parameters,
            conversions,
            verbose,
            )

    cmap_obj = sRGB256_to_mpl(cmap_sRGB256.reshape((-1, 3)), name=name)
    return cmap_sRGB256, cmap_obj


def cvd_simulation(data, cvd, severity):
    """Color vision deficiency simulation"""

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        M_a = colour.matrix_cvd_Machado2009(cvd, severity)

    data = np.einsum('...ij,...j->...i', M_a, data)
    np.clip(data, 0.0, 1.0, out=data)

    return data


def cvd_cmap(cmap_obj, cvd, cvd_severity, conversions):
    """Color vision deficiency simulation"""

    decoded_colors = colour.cctf_decoding(cmap_obj.colors)
    cvd_colors = cvd_simulation(decoded_colors, cvd, cvd_severity)

    cmap_uniform_cvd = conversions['sRGB_to_uniform'](cvd_colors)
    cmap_sRGB256_cvd = sRGB1_to_sRGB256(cvd_colors)

    encoded_cvd_colors = colour.cctf_encoding(cvd_colors)
    cmap_obj_cvd = mpl.colors.ListedColormap(
        encoded_cvd_colors, name=cmap_obj.name,
        )

    return cmap_uniform_cvd, cmap_sRGB256_cvd, cmap_obj_cvd
