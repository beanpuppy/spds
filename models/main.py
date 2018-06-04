import datetime
from peewee import *
from config import Config
import math

database = Config.DATABASE

# monkey patch the DateTimeField to add support for the isoformt which is what
# peewee exports as from DataSet
DateTimeField.formats.append('%Y-%m-%dT%H:%M:%S')
DateField.formats.append('%Y-%m-%dT%H:%M:%S')

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    # Example usage
    #       doc = AdminDocument.create()
    #       doc.apply(request.form)
    #       doc.apply(request.json)
    #       doc.apply(request.json, required=['filename'], dates=['uploaddate'])
    def apply_request(self, source, ignore = None, required = None, dates = None):

        for field in self._meta.get_sorted_fields():
            data = source.get(field)
            if field == "id": continue
            if field in ignore: continue
            # Verify in required_fields
            if field in required and data == None:
                return {'error': 'Empty required field'}
            if field in dates:
                data = "" # strp==]===
            if data is None or data == "": continue
            self.__dict__[field] = data

        return ""

    class Meta:
        database = database

class Playlist(BaseModel):
    id=AutoField(column_name='id', null=False)
    playlist_id=CharField(column_name='playlist_id', null=False)
    name=CharField(column_name='name', null=False)
    author=CharField(column_name='author', null=False)
    date=DateTimeField(column_name='date', null=False)
    score=IntegerField(column_name='score', null=False)

    class Meta:
        table_name = 'Playlists'

class Track(BaseModel):
    id=AutoField(column_name='id', null=False)
    spotify_id=CharField(column_name='spotify_id', null=False)
    genius_id=CharField(column_name='genius_id', null=False)
    name=CharField(column_name='name', null=False)
    score=IntegerField(column_name='score', null=False)
    imcomplete=CharField(column_name='incomplete', null=False)

    class Meta:
        table_name = 'Tracks'

class Artist(BaseModel):
    id=AutoField(column_name='id', null=False)
    artist_id=CharField(column_name='artist_id', null=False)
    name=CharField(column_name='name', null=False)

    class Meta:
        table_name = 'Artists'

class PlaylistTrack(BaseModel):
    playlist_id=ForeignKeyField(Playlist, backref='tracks')
    track_id=ForeignKeyField(Track, backref='playlists')

    class Meta:
        table_name = 'LinkPlaylistsToTracks'

class TrackArtist(BaseModel):
    track_id=ForeignKeyField(Playlist, backref='artists')
    artist_id=ForeignKeyField(Track, backref='tracks')

    class Meta:
        table_name = 'LinkTracksToArtists'
