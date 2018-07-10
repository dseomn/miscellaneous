PLUGIN_NAME = _(u'David\'s Custom Plugin')
PLUGIN_AUTHOR = u'David Mandelberg'
PLUGIN_VERSION = '0.1'
PLUGIN_API_VERSIONS = ['1.3.0']


import slugify

from picard.metadata import register_track_metadata_processor
from picard.plugin import PluginPriority


def genre_normalize(tagger, metadata, *args):
    if 'genre' not in metadata:
        return

    metadata['genre'] = sorted({
        slugify.slugify(genre, ok=slugify.SLUG_OK + '/')
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


def genre_from_media(tagger, metadata, *args):
    genres_by_media = {
        '7" Vinyl': [
            'media/phonograph',
            'media/phonograph/by-material/vinyl',
            'media/phonograph/by-shape/disc',
            'media/phonograph/by-size/7in',
            ],
        '10" Vinyl': [
            'media/phonograph',
            'media/phonograph/by-material/vinyl',
            'media/phonograph/by-shape/disc',
            'media/phonograph/by-size/10in',
            ],
        '12" Vinyl': [
            'media/phonograph',
            'media/phonograph/by-material/vinyl',
            'media/phonograph/by-shape/disc',
            'media/phonograph/by-size/12in',
            ],

        'Cassette': [
            'media/tape',
            'media/tape/cassette',
            ],

        'CD': [
            'media/optical',
            'media/optical/cd',
            ],
        'CD-R': [
            'media/optical',
            'media/optical/cd',
            'media/optical/cd/cd-r',
            ],
        'Enhanced CD': [
            'media/optical',
            'media/optical/cd',
            'media/optical/cd/enhanced-cd',
            ],
        'HDCD': [
            'media/optical',
            'media/optical/cd',
            'media/optical/cd/hdcd',
            ],

        'Digital Media': [
            'media/digital',
            ],
        }

    for media in metadata.getall('media'):
        if media in genres_by_media:
            for genre in genres_by_media[media]:
                metadata.add_unique('genre', genre)
        else:
            raise ValueError('No genres for media: ' + media)

register_track_metadata_processor(
    genre_from_media,
    )


def genre_meta(tagger, metadata, *args):
    genres = metadata.getall('genre')

    if not any((genre.lower().startswith('added/') for genre in genres)):
        genres.append('meta/missing-added')

    if not any((genre.lower().startswith('media/') for genre in genres)):
        genres.append('meta/missing-media')

    if any((genre.lower() == 'media/phonograph' for genre in genres)):
        if not any((genre.lower().startswith('media/phonograph/by-size/') for genre in genres)):
            genres.append('meta/missing-phonograph-size')
        if not any((genre.lower().startswith('media/phonograph/by-speed/') for genre in genres)):
            genres.append('meta/missing-phonograph-speed')

    metadata['genre'] = genres

register_track_metadata_processor(
    genre_meta,
    )
