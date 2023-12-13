import importlib
import pathlib

import click
import numpy as np

from . import db, display, fmt, make_dist, run, search


class AngleParamType(click.ParamType):
    name = "angle"

    def convert(self, value, param, ctx):
        try:
            return np.float64(value)
        except ValueError:
            self.fail(f"{value!r} is not a floating-point number")


class FloatSequenceParamType(click.ParamType):
    name = "float sequence"

    def get_metavar(self, param):
        return "FLOAT[,FLOAT,...]"

    def convert(self, value, param, ctx):
        if isinstance(value, (int, float)):
            return np.float64(value)

        if isinstance(value, str):
            value = value.split(",")

        try:
            return np.array(value, dtype=np.float64)
        except ValueError:
            self.fail(f"{value!r} is not a sequence of floats")


class AngleSequenceParamType(click.ParamType):
    name = "angle sequence"

    def get_metavar(self, param):
        return "ANGLE[,ANGLE,...]"

    def convert(self, value, param, ctx):
        if isinstance(value, (int, float)):
            return np.deg2rad(np.float64(value))

        if isinstance(value, str):
            value = value.split(",")

        try:
            return np.deg2rad(value)
        except ValueError:
            self.fail(f"{value!r} is not a sequence of floats")


ANGLE = AngleParamType()
FLOAT_SEQUENCE = FloatSequenceParamType()
ANGLE_SEQUENCE = AngleSequenceParamType()


def validate_sequence_data(ctx, param, value):
    if len(value) % 2 == 1:
        raise click.BadParameter(
            "Sequence data must have an even number of entries"
            )

    if len(value) == 0:
        raise click.BadParameter("Must have at least one sequence")

    return value


@click.command()
@click.option(
    '--output-color-map', '-O',
    type=click.Path(
        exists=True,
        file_okay=False,
        writable=True,
        path_type=pathlib.Path,
        ),
    help="Output color map bytes to the given directory",
    )
@click.option(
    '--output-parameters', '-o',
    type=click.Path(
        exists=True,
        file_okay=False,
        writable=True,
        path_type=pathlib.Path,
        ),
    help="Output color map parameters to the given directory",
    )
@click.option(
    '--cvd/--no-cvd',
    default=False,
    help="Display color vision deficiency simulations",
    )
@click.option(
    '--cvd-severity',
    type=float,
    default=1.0,
    help="Severity of color vision deficiency simulation",
    )
@click.option(
    '--optimize/--no-optimize',
    default=True,
    help="Whether to optimize the color map"
    )
@click.option(
    '--display/--no-display', '-d',
    default=False,
    help="Display color map",
    )
@click.option(
    '--verbose-optimize',
    count=True,
    help="Print more optimization information",
    )
@click.option(
    '--verbose-post-process',
    count=True,
    help="Print color map post-processing information",
    )
@click.option(
    '--name',
    '-n',
    type=str,
    multiple=True,
    help="Name of a color map to edit",
    )
@click.option(
    '--regexp',
    '-r',
    type=str,
    multiple=True,
    help="Regular expression for color maps to edit",
    )
@click.option(
    '--file',
    '-f',
    type=click.File('r', encoding='utf8'),
    multiple=True,
    help="File containing color map to edit",
    )
def cmd_edit(name, regexp, file, **kwargs):
    """Re-optimize a color map

    The color maps to optimize should be specified by name, by
    regular expression, or by file.
    """

    states = []
    for n in name:
        states.append(db.lookup(n))
    for r in regexp:
        states.extend(db.lookup_regexp(r))
    for f in file:
        states.append(db.deserialize(f.read()))

    for arg in (
            'cvd',
            'cvd_severity',
            'display',
            'optimize',
            'verbose_optimize',
            'verbose_post_process',
            ):
        for state in states:
            state[arg] = kwargs[arg]

    for arg in (
            'output_color_map',
            'output_parameters',
            ):
        if (val := kwargs[arg]) is not None:
            for state in states:
                state[arg] = val / f'{state["name"]}'
        else:
            for state in states:
                state[arg] = None

    type_lookup_table = {
        'Multisequential': run.create_multiseq,
        'Divergent': run.create_divergent,
        'Cyclic': run.create_cyclic,
        'Gray': run.create_gray,
        }

    for state in states:
        print(f"Processing {state['name']}")
        type_lookup_table[state['type']](state)


@click.command()
@click.option(
    '--name',
    '-n',
    type=str,
    multiple=True,
    help="Name of a color map to print",
    )
@click.option(
    '--regexp',
    '-r',
    type=str,
    multiple=True,
    help="Regular expression for color maps to print",
    )
@click.option(
    '--file',
    '-f',
    type=click.File('r', encoding='utf8'),
    multiple=True,
    help="File containing color map to print",
    )
def cmd_print(name, regexp, file):
    """Print color map parameters as an RST table"""

    states = []
    for n in name:
        states.append(db.lookup(n))
    for r in regexp:
        states.extend(db.lookup_regexp(r))
    for f in file:
        states.append(db.deserialize(f.read()))

    print(".. list-table::")
    print("   :header-rows: 1")
    print("   :class:", end="")
    for col_num in range(2, 8):
        print(f" table-col-{col_num}-r", end="")
    print("\n")

    # Delete the following as needed:
    print("   * - Name")
    print("     - :math:`M'`")
    print("     - :math:`J'`")
    print("     - :math:`J_0'`")
    print("     - :math:`J_1'`")
    print(r"     - :math:`\Delta J'`")
    print("     - :math:`h_0`")
    print("     - :math:`h_1`")
    print(r"     - :math:`\Delta h`")

    for state in sorted(
            states, key=lambda s: (len(s['name'].split('_')), s['name'])
            ):
        fmt.format_params_rst(state)


@click.group()
@click.option(
    '--name',
    type=str,
    default="Unnamed color map",
    help="Name of the color map",
    )
@click.option(
    '--output-color-map', '-O',
    type=click.Path(dir_okay=False, writable=True, path_type=pathlib.Path),
    help="Output color map bytes to the given file",
    )
@click.option(
    '--output-parameters', '-o',
    type=click.Path(
        dir_okay=False,
        writable=True,
        allow_dash=True,
        path_type=pathlib.Path,
        ),
    help="Output color map parameters to the given file",
    )
@click.option(
    '--display/--no-display', '-d',
    default=False,
    help="Display color map",
    )
@click.option(
    '--cvd/--no-cvd',
    default=False,
    help="Display color vision deficiency simulations",
    )
@click.option(
    '--cvd-severity',
    type=float,
    default=1.0,
    help="Severity of color vision deficiency simulation",
    )
@click.option(
    '--optimize/--no-optimize',
    default=True,
    help="Whether to optimize the color map"
    )
@click.option(
    '--verbose-optimize',
    count=True,
    help="Print more optimization information",
    )
@click.option(
    '--verbose-post-process',
    count=True,
    help="Print more information about post-processing",
    )
@click.option(
    '--uniform-space',
    type=str,
    default='CAM16UCS',
    help="Uniform color space to use",
    )
@click.option(
    '--maxiter',
    type=int,
    default=1000,
    help="Optimizer maximum iterations",
    )
@click.option(
    '--tol',
    type=float,
    default=1e-15,
    help="Optimizer tolerance",
    )
@click.option(
    '--Jp-constraint-samples',
    type=int,
    default=4,
    help=(
        "Number of samples to use in the J' direction when verifying"
        " constraints for cylinder and cone color maps"
        ),
    )
@click.option(
    '--Jp-final-samples',
    type=int,
    default=64,
    help=(
        "Number of samples in the J' direction to use"
        " for final isoluminant gamut check"
        ),
    )
@click.option(
    '--allowed-gamut-error',
    type=float,
    default=1e-6,
    help="Amount by which color map is allowed to go out-of-gamut",
    )
@click.option(
    '--sRGB-approximation-maxiter',
    type=int,
    default=100000,
    help="Maximum number of iterations of sRGB approximation",
    )
@click.option(
    '--sRGB-approximation-nearby-points',
    type=int,
    default=100000,
    help="Number of nearby points to use during sRGB approximation",
    )
@click.option(
    '--sRGB-approximation-proof/--no-sRGB-approximation-proof',
    default=False,
    help="Whether to attempt to prove optimality of the sRGB approximation",
    )
@click.pass_context
def cmd_create(ctx, **kwargs):
    """Create a new color map

    Not supported.  Use the 'search' command instead.
    """

    ctx.ensure_object(dict)

    state = ctx.obj
    for arg in (
            'name',
            'cvd',
            'cvd_severity',
            'display',
            'optimize',
            'output_color_map',
            'output_parameters',
            'verbose_optimize',
            'verbose_post_process',
            ):
        state[arg] = kwargs.pop(arg, None)

    state['opt_parameters'] = {}
    for arg in ('maxiter', 'tol', 'Jp_constraint_samples'):
        state['opt_parameters'][arg] = kwargs.pop(arg.lower(), None)

    state['post_opt_parameters'] = {}
    for arg in (
            'Jp_final_samples',
            'sRGB_approximation_maxiter',
            'sRGB_approximation_nearby_points',
            'sRGB_approximation_proof',
            ):
        state['post_opt_parameters'][arg] = kwargs.pop(arg.lower(), None)

    state['parameters'] = kwargs


@cmd_create.command("multisequential")
@click.option(
    '--num-samples-per-sequence',
    type=int,
    default=256,
    help="Number of samples per sequence",
    )
@click.option(
    '--constraint-samples-per-sequence',
    type=int,
    default=16,
    help=(
        "Number of samples per sequence to use to check"
        " constraints during optimization"
        ),
    )
@click.option(
    '--weight-initial-lightness',
    type=float,
    default=0.0,
    help="Weight of initial lightness coordinate",
    )
@click.option(
    '--min-initial-lightness',
    type=float,
    default=-np.inf,
    help="Minimum initial lightness coordinate",
    )
@click.option(
    '--max-initial-lightness',
    type=float,
    default=np.inf,
    help="Maximum initial lightness coordinate",
    )
@click.option(
    '--weight-final-lightness',
    type=float,
    default=0.0,
    help="Weight of final lightness coordinate",
    )
@click.option(
    '--min-final-lightness',
    type=float,
    default=-np.inf,
    help="Minimum final lightness coordinate",
    )
@click.option(
    '--max-final-lightness',
    type=float,
    default=np.inf,
    help="Maximum final lightness coordinate",
    )
@click.option(
    '--weight-chroma',
    type=float,
    default=0.0,
    help="Weight of radial coordinate",
    )
@click.option(
    '--min-chroma',
    type=float,
    default=0.0,
    help="Minimum radial coordinate",
    )
@click.option(
    '--max-chroma',
    type=float,
    default=np.inf,
    help="Maximum radial coordinate",
    )
@click.option(
    '--weight-hue-diff',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Weight of starting and ending hue differences",
    )
@click.option(
    '--weight-squared-hue-diff',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Weight of squared starting and ending hue differences",
    )
@click.option(
    '--weight-hue-initial-separation',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Weight of sequence initial hue separation",
    )
@click.option(
    '--weight-hue-final-separation',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Weight of sequence final hue separation",
    )
@click.option(
    '--weight-lightness-diff',
    type=FLOAT_SEQUENCE,
    default=0.0,
    help="Weight of lightness difference",
    )
@click.option(
    '--min-lightness-diff',
    type=FLOAT_SEQUENCE,
    default=-np.inf,
    help="Minimum allowed lightness difference",
    )
@click.option(
    '--max-lightness-diff',
    type=FLOAT_SEQUENCE,
    default=np.inf,
    help="Maximum allowed lightness difference",
    )
@click.option(
    '--min-hue-diff',
    type=ANGLE_SEQUENCE,
    default=-np.inf,
    help="Minimum allowed starting and ending hue differences",
    )
@click.option(
    '--max-hue-diff',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Maximum allowed starting and ending hue differences",
    )
@click.option(
    '--min-initial-hue-separation',
    type=ANGLE_SEQUENCE,
    default=-np.inf,
    help="Minimum allowed separation between sequences' initial hues",
    )
@click.option(
    '--max-initial-hue-separation',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Maximum allowed separation between sequences' initial hues",
    )
@click.option(
    '--min-final-hue-separation',
    type=ANGLE_SEQUENCE,
    default=-np.inf,
    help="Minimum allowed separation between sequences' final hues",
    )
@click.option(
    '--max-final-hue-separation',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Maximum allowed separation between sequences' final hues",
    )
@click.option(
    '--center-initial-hue',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Center of allowed region for initial angle",
    )
@click.option(
    '--span-initial-hue',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Allowed difference from center for initial angle",
    )
@click.option(
    '--center-final-hue',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Center of allowed region for final angle",
    )
@click.option(
    '--span-final-hue',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Allowed difference from center for final angle",
    )
@click.option(
    '--cone/--no-cone',
    default=False,
    help="Require cone from color map to black to be in gamut",
    )
@click.option(
    '--reverse/--forward',
    default=False,
    help="Reverse color map",
    )
@click.option(
    '--rotate',
    type=int,
    default=0,
    help="Rotate color map",
    )
@click.argument('initial_lightness', type=float)
@click.argument('final_lightness', type=float)
@click.argument('chroma', type=float)
@click.argument(
    'sequence_data',
    nargs=-1,
    type=ANGLE,
    callback=validate_sequence_data,
    )
@click.pass_obj
def cmd_multisequential(state, **kwargs):
    state['type'] = "Multisequential"

    state['cmap'] = {}
    for arg in (
            'initial_lightness',
            'final_lightness',
            'chroma',
            'sequence_data',
            ):
        state['cmap'][arg] = kwargs.pop(arg)

    for arg in (
            'reverse',
            'rotate',
            ):
        state['post_opt_parameters'][arg] = kwargs.pop(arg)

    state['parameters'].update(kwargs)

    db.initialize_state(state)
    run.create_multiseq(state)


@cmd_create.command("divergent")
@click.option(
    '--num-samples-per-sequence',
    type=int,
    default=256,
    help="Number of samples per sequence",
    )
@click.option(
    '--constraint-samples-per-sequence',
    type=int,
    default=16,
    help=(
        "Number of samples per sequence to use to check"
        " constraints during optimization"
        ),
    )
@click.option(
    '--weight-initial-lightness',
    type=float,
    default=0.0,
    help="Weight of initial lightness coordinate",
    )
@click.option(
    '--min-initial-lightness',
    type=float,
    default=-np.inf,
    help="Minimum initial lightness coordinate",
    )
@click.option(
    '--max-initial-lightness',
    type=float,
    default=np.inf,
    help="Maximum initial lightness coordinate",
    )
@click.option(
    '--weight-final-lightness',
    type=float,
    default=0.0,
    help="Weight of final lightness coordinate",
    )
@click.option(
    '--min-final-lightness',
    type=float,
    default=-np.inf,
    help="Minimum final lightness coordinate",
    )
@click.option(
    '--max-final-lightness',
    type=float,
    default=np.inf,
    help="Maximum final lightness coordinate",
    )
@click.option(
    '--weight-chroma',
    type=float,
    default=0.0,
    help="Weight of radial coordinate",
    )
@click.option(
    '--min-chroma',
    type=float,
    default=0.0,
    help="Minimum radial coordinate",
    )
@click.option(
    '--max-chroma',
    type=float,
    default=2.0,
    help="Maximum radial coordinate",
    )
@click.option(
    '--weight-hue-diff',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Weight of starting and ending hue differences",
    )
@click.option(
    '--weight-squared-hue-diff',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Weight of squared starting and ending hue differences",
    )
@click.option(
    '--weight-hue-initial-separation',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Weight of sequence initial hue separation",
    )
@click.option(
    '--weight-hue-final-separation',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Weight of sequence final hue separation",
    )
@click.option(
    '--weight-lightness-diff',
    type=FLOAT_SEQUENCE,
    default=0.0,
    help="Weight of lightness difference",
    )
@click.option(
    '--min-lightness-diff',
    type=FLOAT_SEQUENCE,
    default=-np.inf,
    help="Minimum allowed lightness difference",
    )
@click.option(
    '--max-lightness-diff',
    type=FLOAT_SEQUENCE,
    default=np.inf,
    help="Maximum allowed lightness difference",
    )
@click.option(
    '--min-hue-diff',
    type=ANGLE_SEQUENCE,
    default=-np.inf,
    help="Minimum allowed starting and ending hue differences",
    )
@click.option(
    '--max-hue-diff',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Maximum allowed starting and ending hue differences",
    )
@click.option(
    '--min-initial-hue-separation',
    type=ANGLE_SEQUENCE,
    default=-np.inf,
    help="Minimum allowed separation between sequences' initial hues",
    )
@click.option(
    '--max-initial-hue-separation',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Maximum allowed separation between sequences' initial hues",
    )
@click.option(
    '--min-final-hue-separation',
    type=ANGLE_SEQUENCE,
    default=-np.inf,
    help="Minimum allowed separation between sequences' final hues",
    )
@click.option(
    '--max-final-hue-separation',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Maximum allowed separation between sequences' final hues",
    )
@click.option(
    '--center-initial-hue',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Center of allowed region for initial angle",
    )
@click.option(
    '--span-initial-hue',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Allowed difference from center for initial angle",
    )
@click.option(
    '--center-final-hue',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Center of allowed region for final angle",
    )
@click.option(
    '--span-final-hue',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Allowed difference from center for final angle",
    )
@click.option(
    '--reverse/--forward',
    default=False,
    help="Reverse color map",
    )
@click.option(
    '--rotate',
    type=int,
    default=0,
    help="Rotate color map",
    )
@click.argument('initial_lightness', type=float)
@click.argument('final_lightness', type=float)
@click.argument('chroma', type=float)
@click.argument('hue0', type=ANGLE)
@click.argument('hue_diff0', type=ANGLE)
@click.argument('hue1', type=ANGLE)
@click.argument('hue_diff1', type=ANGLE)
@click.argument('divergence_type', type=click.Choice(["hill", "valley"]))
@click.pass_obj
def cmd_divergent(state, **kwargs):
    state['type'] = "Divergent"

    state['cmap'] = {}
    for arg in (
            'initial_lightness',
            'final_lightness',
            'chroma',
            'divergence_type',
            ):
        state['cmap'][arg] = kwargs.pop(arg)

    state['cmap']['sequence_data'] = np.fromiter(
        map(kwargs.pop, ('hue0', 'hue_diff0', 'hue1', 'hue_diff1')),
        dtype=np.float64,
        )

    for arg in (
            'reverse',
            'rotate',
            ):
        state['post_opt_parameters'][arg] = kwargs.pop(arg)

    state['parameters'].update(kwargs)

    db.initialize_state(state)
    run.create_divergent(state)


@cmd_create.command("cyclic")
@click.option(
    '--num-samples-per-sequence',
    type=int,
    default=256,
    help="Number of samples per sequence",
    )
@click.option(
    '--constraint-samples-per-sequence',
    type=int,
    default=16,
    help=(
        "Number of samples per sequence to use to check"
        " constraints during optimization"
        ),
    )
@click.option(
    '--weight-initial-lightness',
    type=float,
    default=0.0,
    help="Weight of initial lightness coordinate",
    )
@click.option(
    '--min-initial-lightness',
    type=float,
    default=-np.inf,
    help="Minimum initial lightness coordinate",
    )
@click.option(
    '--max-initial-lightness',
    type=float,
    default=np.inf,
    help="Maximum initial lightness coordinate",
    )
@click.option(
    '--weight-final-lightness',
    type=float,
    default=0.0,
    help="Weight of final lightness coordinate",
    )
@click.option(
    '--min-final-lightness',
    type=float,
    default=-np.inf,
    help="Minimum final lightness coordinate",
    )
@click.option(
    '--max-final-lightness',
    type=float,
    default=np.inf,
    help="Maximum final lightness coordinate",
    )
@click.option(
    '--weight-chroma',
    type=float,
    default=0.0,
    help="Weight of radial coordinate",
    )
@click.option(
    '--min-chroma',
    type=float,
    default=0.0,
    help="Minimum radial coordinate",
    )
@click.option(
    '--max-chroma',
    type=float,
    default=np.inf,
    help="Maximum radial coordinate",
    )
@click.option(
    '--weight-hue-diff',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Weight of starting and ending hue differences",
    )
@click.option(
    '--weight-squared-hue-diff',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Weight of squared starting and ending hue differences",
    )
@click.option(
    '--weight-hue-initial-separation',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Weight of sequence initial hue separation",
    )
@click.option(
    '--weight-hue-final-separation',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Weight of sequence final hue separation",
    )
@click.option(
    '--weight-lightness-diff',
    type=FLOAT_SEQUENCE,
    default=0.0,
    help="Weight of lightness difference",
    )
@click.option(
    '--min-lightness-diff',
    type=FLOAT_SEQUENCE,
    default=-np.inf,
    help="Minimum allowed lightness difference",
    )
@click.option(
    '--max-lightness-diff',
    type=FLOAT_SEQUENCE,
    default=np.inf,
    help="Maximum allowed lightness difference",
    )
@click.option(
    '--min-hue-diff',
    type=ANGLE_SEQUENCE,
    default=-np.inf,
    help="Minimum allowed starting and ending hue differences",
    )
@click.option(
    '--max-hue-diff',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Maximum allowed starting and ending hue differences",
    )
@click.option(
    '--min-initial-hue-separation',
    type=ANGLE_SEQUENCE,
    default=-np.inf,
    help="Minimum allowed separation between sequences' initial hues",
    )
@click.option(
    '--max-initial-hue-separation',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Maximum allowed separation between sequences' initial hues",
    )
@click.option(
    '--min-final-hue-separation',
    type=ANGLE_SEQUENCE,
    default=-np.inf,
    help="Minimum allowed separation between sequences' final hues",
    )
@click.option(
    '--max-final-hue-separation',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Maximum allowed separation between sequences' final hues",
    )
@click.option(
    '--center-initial-hue',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Center of allowed region for initial angle",
    )
@click.option(
    '--span-initial-hue',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Allowed difference from center for initial angle",
    )
@click.option(
    '--center-final-hue',
    type=ANGLE_SEQUENCE,
    default=0.0,
    help="Center of allowed region for final angle",
    )
@click.option(
    '--span-final-hue',
    type=ANGLE_SEQUENCE,
    default=np.inf,
    help="Allowed difference from center for final angle",
    )
@click.argument('initial_lightness', type=float)
@click.argument('final_lightness', type=float)
@click.argument('chroma', type=float)
@click.argument(
    'sequence_data',
    nargs=-1,
    type=ANGLE,
    callback=validate_sequence_data,
    )
@click.pass_obj
def cmd_cyclic(state, **kwargs):
    state['type'] = "Cyclic"

    state['cmap'] = {}
    for arg in (
            'initial_lightness',
            'final_lightness',
            'chroma',
            'sequence_data',
            ):
        state['cmap'][arg] = kwargs.pop(arg)

    for arg in (
            'reverse',
            'rotate',
            ):
        state['post_opt_parameters'][arg] = kwargs.pop(arg)

    state['parameters'].update(kwargs)

    db.initialize_state(state)
    run.create_cyclic(state)


@cmd_create.command("gray")
@click.option(
    '--num-samples-per-sequence',
    type=int,
    default=256,
    help="Number of samples",
    )
@click.option(
    '--reverse/--forward',
    default=False,
    help="Reverse color map",
    )
@click.argument('initial_lightness', type=float)
@click.argument('final_lightness', type=float)
@click.pass_obj
def cmd_gray(state, **kwargs):
    """Generate a grayscale color map"""

    state['type'] = "Gray"

    state['cmap'] = {}
    for arg in (
            'initial_lightness',
            'final_lightness',
            ):
        state['cmap'][arg] = kwargs.pop(arg)

    state['cmap']['chroma'] = 0.0
    state['cmap']['sequence_data'] = ()

    for arg in ('reverse',):
        state['post_opt_parameters'][arg] = kwargs.pop(arg)
    state['post_opt_parameters']['rotate'] = 0

    state['parameters'].update(kwargs)

    db.initialize_state(state)
    run.create_gray(state)


@click.group()
@click.option(
    '--num-samples',
    default=6,
    type=int,
    help="Number of circle locations at which to try creating a color map",
    )
@click.option(
    '--span',
    default=60.0,
    type=float,
    help="Size in degrees of arc in which the colors are required to stay",
    )
@click.option(
    '--lightness-threshold',
    default=0.75,
    type=float,
    help="Difference in J' below which a result will be discarded",
    )
@click.option(
    '--colorfulness',
    default=0.2,
    type=float,
    help="Uniformized colorfulness to use",
    )
@click.option(
    '--similarity-threshold',
    default=30.0,
    type=float,
    help=(
        "Angular distance below which two sequences"
        " will be considered duplicates"
        ),
    )
@click.option(
    '--output-directory',
    default='.',
    type=click.Path(file_okay=False, path_type=pathlib.Path),
    help="Directory in which to generate output files",
    )
@click.pass_context
def cmd_search(
        ctx,
        num_samples,
        span,
        lightness_threshold,
        colorfulness,
        similarity_threshold,
        output_directory,
        ):
    """Search for new color maps"""

    ctx.ensure_object(dict)

    state = ctx.obj
    state['num_samples'] = num_samples
    state['span'] = span
    state['lightness_threshold'] = lightness_threshold
    state['colorfulness'] = colorfulness
    state['similarity_threshold'] = similarity_threshold
    state['output_directory'] = output_directory


@cmd_search.command("mseq")
@click.option(
    "--max-arc-length",
    type=float,
    default=np.inf,
    help="Maximum arc length to consider."
    )
@click.option(
    "--min-arc-length",
    type=float,
    default=0.0,
    help="Minimum arc length to consider."
    )
@click.option(
    "--num-extra-revolutions",
    type=int,
    default=0,
    help="Add extra revolutions to every directed arc"
    )
@click.argument("num_seqs", type=int)
@click.pass_obj
def cmd_search_mseq(
        obj, num_seqs, max_arc_length, min_arc_length, num_extra_revolutions,
        ):
    results = search.make_mseq(
        obj['num_samples'],
        obj['span'],
        obj['lightness_threshold'],
        obj['colorfulness'],
        obj['similarity_threshold'],
        num_seqs,
        max_arc_length,
        min_arc_length,
        num_extra_revolutions,
        )

    for state in results:
        db.write_state(obj['output_directory'] / state['name'], state)


@cmd_search.command("div")
@click.option(
    "--max-arc-length",
    type=float,
    default=np.inf,
    help="Maximum arc length to consider."
    )
@click.option(
    "--min-arc-length",
    type=float,
    default=0.0,
    help="Minimum arc length to consider."
    )
@click.pass_obj
def cmd_search_div(obj, max_arc_length, min_arc_length):
    results = search.make_div(
        obj['num_samples'],
        obj['span'],
        obj['lightness_threshold'],
        obj['colorfulness'],
        obj['similarity_threshold'],
        max_arc_length,
        min_arc_length,
        )

    for state in results:
        db.write_state(obj['output_directory'] / state['name'], state)


@cmd_search.command("cyc")
@click.pass_obj
def cmd_search_cyc(obj):
    results = search.make_cyc(
        obj['num_samples'],
        obj['span'],
        obj['lightness_threshold'],
        obj['colorfulness'],
        obj['similarity_threshold'],
        )

    for state in results:
        db.write_state(obj['output_directory'] / state['name'], state)


@cmd_search.command("isolum")
@click.option(
    "--max-arc-length",
    type=float,
    default=np.inf,
    help="Maximum arc length to consider."
    )
@click.option(
    "--min-arc-length",
    type=float,
    default=np.inf,
    help="Minimum arc length to consider."
    )
@click.pass_obj
def cmd_search_isolum(obj, max_arc_length, min_arc_length):
    results = search.make_isolum(
        obj['num_samples'],
        obj['span'],
        obj['colorfulness'],
        obj['similarity_threshold'],
        max_arc_length,
        min_arc_length,
        )

    for state in results:
        db.write_state(obj['output_directory'] / state['name'], state)


@click.command()
@click.option(
    '--distribution',
    '-d',
    multiple=True,
    type=click.Choice(make_dist.ALL_DISTRIBUTIONS),
    default=make_dist.ALL_DISTRIBUTIONS,
    help="Only remake this distribution",
    )
@click.argument(
    'cmap_directory',
    type=click.Path(file_okay=False, path_type=pathlib.Path),
    )
@click.argument(
    'output_directory',
    type=click.Path(file_okay=False, path_type=pathlib.Path),
    )
def cmd_make_dist(distribution, cmap_directory, output_directory):
    """Make Chromophile distributions

    The CMAP_DIRECTORY argument should contain the data files
    produced by 'cp_edit -O'.  The final distributions will be
    placed in OUTPUT_DIRECTORY.
    """

    all_cmaps = db.read_cmap_dir(cmap_directory)
    make_dist.make_distributions(distribution, all_cmaps, output_directory)


@click.command()
@click.option(
    '--uniform-space',
    type=str,
    default='CAM16UCS',
    help="Uniform color space to use",
    )
@click.option(
    '--num-samples',
    '-n',
    default=1024,
    type=int,
    help="Number of samples",
    )
@click.option(
    '--batches-per-side',
    '-b',
    default=1,
    type=int,
    help="Number of batches per side",
    )
@click.option(
    '--downscale',
    default=1,
    type=int,
    help="Number of adjacent samples to combine",
    )
@click.option(
    '--extent',
    '-e',
    default=(-1, 1, -1, 1),
    type=float,
    nargs=4,
    help="Display extent",
    )
@click.option(
    '--scale/--no-scale',
    default=False,
    help="Scale coordinates to between 0 and 100",
    )
@click.option(
    '--sRGB-points/--no-sRGB-points',
    default=False,
    help="Display sRGB points",
    )
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help="Save picture to this file",
    )
@click.argument('J_prime', type=float)
def cmd_colorspace(
        uniform_space,
        num_samples,
        batches_per_side,
        downscale,
        extent,
        scale,
        srgb_points,
        output,
        j_prime,
        ):
    """Display an isoluminant slice of a color space

    All coordinates are between -1 and 1.
    """

    display.colorspace_plot(
        uniform_space,
        num_samples,
        batches_per_side,
        downscale,
        j_prime,
        extent,
        scale,
        srgb_points,
        output,
        )


@click.command()
@click.option(
    '--uniform-space',
    type=str,
    default='CAM16UCS',
    help="Uniform color space to use",
    )
@click.option(
    '--module',
    '-m',
    type=str,
    help='Module to load',
    )
@click.argument('name', type=str)
def cmd_colormap(uniform_space, module, name):
    """Display a color map plot

    The color map should be either a Matplotlib installed color map or
    should be provided by an imported module.
    """

    if module is not None:
        importlib.import_module(module)

    display.colormap_plot(uniform_space, name)
