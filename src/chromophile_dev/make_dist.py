import importlib.metadata
import importlib.resources
import json
import operator
import pathlib
import shutil

from jinja2 import Environment

from . import conversion


DEFAULT_ALIASES = (
    ('cp_isolum_cyc_dark', 'cp_cyc_isolum_dark'),
    ('cp_isolum_cyc_light', 'cp_cyc_isolum_light'),
    ('cp_isolum_cyc_wide', 'cp_cyc_isolum_wide'),
    ('cp_blue', 'cp_seq_blue_cyan_cw'),
    ('cp_purple', 'cp_seq_blue_pink_ccw1'),
    ('cp_dawn', 'cp_seq_blue_yellow_ccw'),
    ('cp_peacock', 'cp_seq_blue_yellow_cw'),
    ('cp_gray', 'cp_seq_gray'),
    ('cp_grey', 'cp_seq_gray'),
    ('cp_seq_grey', 'cp_seq_gray'),
    ('cp_teal', 'cp_seq_green_cyan_ccw'),
    ('cp_green', 'cp_seq_green_green_cw'),
    ('cp_lemon_lime', 'cp_seq_green_yellow_cw'),
    ('cp_red', 'cp_seq_red_pink_cw1'),
    ('cp_orange', 'cp_seq_red_yellow_ccw'),
    )

JINJA_ENV = Environment(autoescape=False, keep_trailing_newline=True)

DISTRIBUTIONS = json.loads(
    (
        importlib.resources.files(__package__)
        / 'distributions'
        / 'distributions.json'
    ).read_text()
    )
ALL_DISTRIBUTIONS = list(DISTRIBUTIONS.keys())


def collate_cmap_data(cmaps):
    raw_data = b"".join(map(operator.itemgetter(1), cmaps))
    return raw_data


def make_cmap_index(cmaps):
    return [
        (cmap_name, len(cmap_data) // 3) for cmap_name, cmap_data in cmaps
        ]


def _context_version():
    version = importlib.metadata.version(__package__)
    return {
        'version': version,
        'py_version': repr(version),
        }


def _context_py_index(cmap_index):
    header = "_INDEX = ("
    footer = "    )"
    lines = []
    for cmap_name, cmap_len in cmap_index:
        lines.append(f"    ({cmap_name!r}, {cmap_len}),")
    return '\n'.join([header] + lines + [footer])


def _context_py_aliases(aliases):
    lines = []
    lines.append("_ALIASES = (")
    for cmap_alias, cmap_name in sorted(aliases, key=lambda x: x[1]):
        lines.append(f"    ({cmap_alias!r}, {cmap_name!r}),")
    lines.append("    )")
    return '\n'.join(lines)


def _context_py_cp_peacock_example(cmaps, aliases):
    for cmap_alias, cp_peacock_unaliased in aliases:
        if cmap_alias == 'cp_peacock':
            break
    else:
        raise RuntimeError("Unable to find cp_peacock alias")

    for cmap_name, cmap_data in cmaps:
        if cmap_name == cp_peacock_unaliased:
            break
    else:
        raise RuntimeError("Unable to find cp_peacock data")

    colors = [cmap_data[3*i:3*(i+1)] for i in range(4)]
    color_strs = [f'#{c.hex()}' for c in colors]
    return f"({', '.join(map(repr, color_strs))}, ...)"


def _context_python(cmaps, aliases, cmap_index):
    return {
        'py_data_path': DISTRIBUTIONS['python']['data_path'],
        'py_index': _context_py_index(cmap_index),
        'py_aliases': _context_py_aliases(aliases),
        'py_cp_peacock_example': _context_py_cp_peacock_example(
            cmaps, aliases,
            ),
        }


def prepare_context(cmaps):
    cmap_index = make_cmap_index(cmaps)

    context = {}
    context.update(_context_version())
    context.update(_context_python(cmaps, DEFAULT_ALIASES, cmap_index))
    return context


def find_distribution_files(input_directory, output_directory):
    files_to_copy = []
    templates_to_render = []
    unprocessed = [(input_directory, output_directory)]
    while unprocessed:
        traversable, path = unprocessed.pop()
        if traversable.is_dir():
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            for child in traversable.iterdir():
                unprocessed.append(
                    (child, path / pathlib.Path(child).name)
                    )
        elif traversable.is_file():
            if traversable.name.endswith('.jinja'):
                templates_to_render.append(
                    (traversable, pathlib.Path(path).with_suffix(''))
                    )
            else:
                files_to_copy.append((traversable, path))
        else:
            raise RuntimeError(
                "Traversable {traversable} has unrecognized type"
                )

    return files_to_copy, templates_to_render


def make_distribution(
        name,
        template_context,
        raw_cmap_data,
        input_directory,
        output_directory,
        ):
    files_to_copy, templates_to_render = find_distribution_files(
        input_directory, output_directory,
        )

    for template_path, output_path in templates_to_render:
        template_str = template_path.read_text()
        template = JINJA_ENV.from_string(template_str)
        rendered = template.render(template_context)
        with open(output_path, 'w') as handle:
            handle.write(rendered)

    data_path = DISTRIBUTIONS[name].get('data_path')
    if data_path is not None:
        with open(output_directory / data_path, 'wb') as handle:
            handle.write(raw_cmap_data)

    for src_path, dst_path in files_to_copy:
        shutil.copyfile(src_path, dst_path)


def make_distributions(names, all_cmaps, output_directory):
    dist_directory = (
        importlib.resources.files(__package__) / 'distributions'
        )

    all_cmaps = sorted(all_cmaps)
    raw_cmap_data = collate_cmap_data(all_cmaps)
    template_context = prepare_context(all_cmaps)
    for name in names:
        current_dist_directory = dist_directory / name
        current_output_directory = output_directory / name

        make_distribution(
            name,
            template_context,
            raw_cmap_data,
            current_dist_directory,
            current_output_directory,
            )
