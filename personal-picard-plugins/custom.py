PLUGIN_NAME = _(u'David\'s Custom Plugin')
PLUGIN_AUTHOR = u'David Mandelberg'
PLUGIN_VERSION = '0.1'
PLUGIN_API_VERSIONS = ['1.3.0']


import slugify

from picard.metadata import register_track_metadata_processor
from picard.plugin import PluginPriority


def genre_filter(tagger, metadata, *args):
    def parse_track_num(track_num):
        medium, sep, track = track_num.partition('.')
        try:
            medium = int(medium)
            track = int(track) if track else None
        except ValueError:
            raise ValueError('Invalid medium/track identifer: ' + track_num)
        return medium, track

    def parse_extent(extent):
        for track_range in extent.split('+'):
            first, sep, last = track_range.partition('-')
            if not last:
                last = first

            yield parse_track_num(first), parse_track_num(last)

    this_medium = int(metadata['discnumber']) if 'discnumber' in metadata else None
    this_track = int(metadata['tracknumber']) if 'tracknumber' in metadata else None

    def gte_first(first):
        if this_medium == first[0]:
            return first[1] is None or this_track >= first[1]
        else:
            return this_medium > first[0]

    def lte_last(last):
        if this_medium == last[0]:
            return last[1] is None or this_track <= last[1]
        else:
            return this_medium < last[0]

    filtered_genres = []
    for genre in metadata.getall('genre'):
        genre, sep, extent = genre.partition('@')
        if sep and extent:
            if this_medium is None or this_track is None:
                raise ValueError('Cannot filter genre without medium and track info.')
            for first, last in parse_extent(extent):
                if gte_first(first) and lte_last(last):
                    # The genre matches the extent, so add it.
                    filtered_genres.append(genre)
                    break
        elif sep or extent:
            raise ValueError('Invalid genre: ' + ''.join((genre, sep, extent)))
        else:
            # No filter, so the genre applies to everything.
            filtered_genres.append(genre)
    metadata['genre'] = filtered_genres

register_track_metadata_processor(
    genre_filter,
    priority=PluginPriority.HIGH,
    )

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
            if genre.lower() != 'added/unknown':
                metadata.add_unique('dseomn_added', '-'.join(genre_parts[1:]))

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
        '7" Shellac': [
            'media/phonograph',
            'media/phonograph/by-material/shellac',
            'media/phonograph/by-shape/disc',
            'media/phonograph/by-size/7in',
            ],
        '10" Shellac': [
            'media/phonograph',
            'media/phonograph/by-material/shellac',
            'media/phonograph/by-shape/disc',
            'media/phonograph/by-size/10in',
            ],
        '12" Shellac': [
            'media/phonograph',
            'media/phonograph/by-material/shellac',
            'media/phonograph/by-shape/disc',
            'media/phonograph/by-size/12in',
            ],
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
        'DVD': [
            'media/optical',
            'media/optical/dvd',
            ],
        'DVD-Video': [
            'media/optical',
            'media/optical/dvd',
            'media/optical/dvd/dvd-video',
            ],
        'DVD-Audio': [
            'media/optical',
            'media/optical/dvd',
            'media/optical/dvd/dvd-audio',
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
