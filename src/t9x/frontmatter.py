'''YAML front matter parsing that preserves unknown fields.

The spec requires that fields t9x does not understand survive a round trip.
We load the full mapping, mutate only the keys we own, and dump everything
back in original insertion order. Lists render inline ([qx3, f2m]) and
mappings render as blocks, matching the spec's examples.
'''
import datetime

import yaml


class FrontMatterDumper(yaml.SafeDumper):
    pass


FrontMatterDumper.add_representer(
    list,
    lambda d, v: d.represent_sequence('tag:yaml.org,2002:seq', v, flow_style=True),
)
FrontMatterDumper.add_representer(
    datetime.datetime,
    lambda d, v: d.represent_scalar(
        'tag:yaml.org,2002:timestamp', v.isoformat(timespec='seconds')
    ),
)


def parse(text):
    '''Split file text into (meta, body). meta is None if no front matter.'''
    if text.startswith('---\n'):
        end = text.find('\n---\n', 3)
        if end != -1:
            meta = yaml.safe_load(text[4:end + 1])
            if isinstance(meta, dict):
                return meta, text[end + 5:]
    return None, text


def dump(meta, body):
    '''Render meta + body back into file text.'''
    front = yaml.dump(
        meta,
        Dumper=FrontMatterDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1000,
    )
    return f'---\n{front}---\n{body}'
