PLUGIN_NAME = _(u'Instruments')
PLUGIN_AUTHOR = u'David Mandelberg'
PLUGIN_DESCRIPTION = u'''\
Adds a multi-valued tag of all the instruments, for use in scripts.
'''
PLUGIN_VERSION = '0.1'
PLUGIN_API_VERSIONS = ['1.3.0']


from picard.metadata import register_track_metadata_processor
from picard.plugin import PluginPriority


def add_instruments(tagger, metadata, *args):
    key_prefix = 'performer:'
    for key, values in metadata.rawitems():
        if not key.startswith(key_prefix):
            continue
        instrument = key[len(key_prefix):]
        metadata.add_unique('~instrument', instrument)

register_track_metadata_processor(
    add_instruments,
    priority=PluginPriority.HIGH,
    )
