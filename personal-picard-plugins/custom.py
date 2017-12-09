PLUGIN_NAME = _(u'David\'s Custom Plugin')
PLUGIN_AUTHOR = u'David Mandelberg'
PLUGIN_VERSION = '0.1'
PLUGIN_API_VERSIONS = ['1.3.0']


from picard.metadata import register_track_metadata_processor
from picard.plugin import PluginPriority


def genre_normalize(tagger, metadata, *args):
    if 'genre' not in metadata:
        return

    metadata['genre'] = sorted({
        genre.lower().replace(' ', '-')
        for genre in metadata.getall('genre')})

register_track_metadata_processor(
    genre_normalize,
    priority=PluginPriority.LOW,
    )


def genre_normalize_added(tagger, metadata, *args):
    genres = metadata.getall('genre')
    for i, genre in enumerate(genres):
        genre_parts = genre.split('/')
        if len(genre_parts) >= 2 and genre_parts[0].lower() == 'added':
            genres[i] = '/'.join(genre_parts[:2])

register_track_metadata_processor(
    genre_normalize_added,
    )


def genre_from_instruments(tagger, metadata, *args):
    genres = []
    for instrument in metadata.getall('~instrument'):
        instrument = instrument.replace('/', '_')
        if 'vocals' in instrument:
            genres.append('performance/vocal')
            if instrument != 'vocals':
                genres.append('performance/vocal/' + instrument)
        else:
            genres.append('performance/instrument')
            genres.append('performance/instrument/' + instrument)

    for genre in genres:
        metadata.add_unique('genre', genre)

register_track_metadata_processor(
    genre_from_instruments,
    )


def genre_from_releasetype(tagger, metadata, *args):
    if 'soundtrack' in metadata.getall('~secondaryreleasetype'):
        metadata.add_unique('genre', 'context/soundtrack')

register_track_metadata_processor(
    genre_from_releasetype,
    )


def genre_meta(tagger, metadata, *args):
    genres = metadata.getall('genre')

    if not any((genre.lower().startswith('added/') for genre in genres)):
        genres.append('meta/missing-added')

    metadata['genre'] = genres

register_track_metadata_processor(
    genre_meta,
    )
