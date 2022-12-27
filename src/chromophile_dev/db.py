import collections.abc
import importlib.resources
import json
import pathlib
import re

import numpy as np

from . import conversion


PERSISTENT_STATE_KEYS = (
    'name',
    'type',
    'cmap',
    'parameters',
    'opt_parameters',
    'post_opt_parameters',
    )

DATA_PACKAGE = f"{__package__}.data"


def initialize_state(state):
    sRGB_to_uniform, uniform_to_sRGB = conversion.uniform_space_conversions(
        state['parameters']['uniform_space']
        )

    state['conversions'] = {
        'sRGB_to_uniform': sRGB_to_uniform,
        'uniform_to_sRGB': uniform_to_sRGB,
        }

    for v in state.values():
        if not isinstance(v, dict):
            continue

        for k1, v1 in v.items():
            if isinstance(v1, str):
                continue
            if isinstance(v1, (collections.abc.Sequence, float)):
                v[k1] = np.array(v1)


def serialize(state):
    persistent_data = {}
    for k in PERSISTENT_STATE_KEYS:
        v = state[k]
        if isinstance(v, dict):
            for k1, v1 in v.items():
                if isinstance(v1, np.ndarray):
                    if v1.size == 1:
                        v1 = v1.item()
                    else:
                        v1 = (*map(float, v1),)
                v[k1] = v1
        persistent_data[k] = v

    persistent_data = {k: state[k] for k in PERSISTENT_STATE_KEYS}
    return json.dumps(persistent_data, indent=4)


def deserialize(data):
    state = json.loads(data)
    initialize_state(state)
    return state


def lookup(name):
    if not name.endswith('.json'):
        name += '.json'

    with importlib.resources.open_text(DATA_PACKAGE, name) as file_handle:
        data = file_handle.read()

    state = deserialize(data)
    return state


def lookup_regexp(regexp):
    for resource in importlib.resources.files(DATA_PACKAGE).iterdir():
        res_name = pathlib.Path(str(resource)).stem
        if res_name.startswith('__') and res_name.endswith('__'):
            continue
        if re.search(regexp, res_name):
            with resource.open(encoding='utf8') as file_handle:
                data = file_handle.read()

            state = deserialize(data)
            yield state


def write_state(filename, state):
    data = serialize(state)

    with open(filename.with_suffix('.json'), 'w') as file_handle:
        print(data, file=file_handle)


def write_cmap(filename, cmap_sRGB256):
    with open(filename.with_suffix('.dat'), 'wb') as file_handle:
        file_handle.write(cmap_sRGB256.tobytes())


def read_cmap(filename):
    with open(filename, 'rb') as file_handle:
        return file_handle.read()


def read_cmap_dir(directory):
    cmaps = []
    for filename in directory.iterdir():
        if filename.suffix != '.dat':
            continue
        cmaps.append((filename.stem, read_cmap(filename)))

    return cmaps


def _convert_with_function(state, func):
    for v in state.values():
        if isinstance(v, dict):
            for k1, v1 in v.items():
                if (
                        k1 == 'sequence_data'
                        or ('hue' in k1 and 'weight' not in k1)
                        ):
                    v[k1] = func(v1)


def convert_to_radians(state):
    _convert_with_function(state, np.deg2rad)


def convert_to_degrees(state):
    _convert_with_function(state, np.rad2deg)
