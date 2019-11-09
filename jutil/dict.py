import re
from collections import OrderedDict

from django.utils.text import capfirst


def sorted_dict(d: dict):
    """
    Returns OrderedDict sorted by ascending key
    :param d: dict
    :return: OrderedDict
    """
    return OrderedDict(sorted(d.items()))


def choices_label(choices: tuple, value) -> str:
    """
    Iterates (value,label) list and returns label matching the choice
    :param choices: [(choice1, label1), (choice2, label2), ...]
    :param value: Value to find
    :return: label or None
    """
    for key, label in choices:
        if key == value:
            return label
    return ''


def _dict_to_html_format_key(k: str):
    if k.startswith('@'):
        k = k[1:]
    k = k.replace('_', ' ')
    k = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', k)
    parts = k.split(' ')
    out = [capfirst(parts[0].strip())]
    for p in parts[1:]:
        p2 = p.strip().lower()
        if p2:
            out.append(p2)
    return ' '.join(out)


def _dict_to_html_r(data: dict, margin: str = '') -> str:
    if not isinstance(data, dict):
        return '{}{}\n'.format(margin, data)
    out = ''
    for k, v in sorted_dict(data).items():
        if isinstance(v, dict):
            out += '{}{}:\n'.format(margin, _dict_to_html_format_key(k))
            out += _dict_to_html_r(v, margin + '    ')
            out += '\n'
        elif isinstance(v, list):
            for v2 in v:
                out += '{}{}:\n'.format(margin, _dict_to_html_format_key(k))
                out += _dict_to_html_r(v2, margin + '    ')
            out += '\n'
        else:
            out += '{}{}: {}\n'.format(margin, _dict_to_html_format_key(k), v)
    return out


def dict_to_html(data: dict) -> str:
    """
    Formats dict to simple pre-formatted html (<pre> tag).
    :param data: dict
    :return: str (html)
    """
    return '<pre>' + _dict_to_html_r(data) + '</pre>'
