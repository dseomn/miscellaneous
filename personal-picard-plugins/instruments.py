PLUGIN_NAME = _(u'Instruments')
PLUGIN_AUTHOR = u'David Mandelberg'
PLUGIN_DESCRIPTION = u'''\
Adds a multi-valued tag of all the instruments, for use in scripts.
'''
PLUGIN_VERSION = '0.1'
PLUGIN_API_VERSIONS = ['1.3.0']


from picard.metadata import register_track_metadata_processor
from picard.plugin import PluginPriority


def iterate_instruments(instrument_list):
    """Iterate over components of strings like "A, B and C"
    """

    remaining = instrument_list
    while remaining:
        instrument, sep, remaining = remaining.partition(', ')
        if not remaining:
            instrument, sep, remaining = instrument.partition(' and ')
            if ' and ' in remaining:
                raise ValueError(
                    'Instrument list contains multiple \'and\'s: ' +
                    instrument_list)

            yield instrument

def strip_instrument_prefixes(instrument):
    instrument_prefixes = {
        'additional',
        'guest',
        'solo',
        }

    remaining = instrument
    while remaining:
        prefix, sep, remaining = remaining.partition(' ')
        if prefix not in instrument_prefixes:
            return ''.join((prefix, sep, remaining))

    # At this point, the instrument was all prefixes. This can happen with a
    # relationship like "guest performer" which has no instrument.
    return None

def add_instruments(tagger, metadata, *args):
    key_prefix = 'performer:'

    for key, values in metadata.rawitems():
        if not key.startswith(key_prefix):
            continue

        for instrument in iterate_instruments(key[len(key_prefix):]):
            instrument = strip_instrument_prefixes(instrument)
            if instrument:
                metadata.add_unique('~instrument', instrument)

register_track_metadata_processor(
    add_instruments,
    priority=PluginPriority.HIGH,
    )
