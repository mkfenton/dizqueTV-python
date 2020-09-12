import json
import logging
from xml.etree import ElementTree
from typing import List, Union

import m3u8
from requests import Response
from plexapi.video import Video, Movie, Episode
from plexapi.server import PlexServer as PServer

import dizqueTV.requests as requests
from dizqueTV.settings import XMLTVSettings, PlexSettings, FFMPEGSettings, HDHomeRunSettings
from dizqueTV.channels import Channel, Program, Filler
from dizqueTV.plex_server import PlexServer
from dizqueTV.templates import PLEX_SERVER_SETTINGS_TEMPLATE, CHANNEL_SETTINGS_TEMPLATE, CHANNEL_SETTINGS_DEFAULT
import dizqueTV.helpers as helpers
from dizqueTV.exceptions import MissingParametersError, ChannelCreationError


def convert_plex_item_to_program(plex_item: Union[Video, Movie, Episode], plex_server: PServer) -> Program:
    """
    Convert a PlexAPI Video, Movie or Episode object into a Program
    :param plex_item: plexapi.video.Video, plexapi.video.Movie or plexapi.video.Episode object
    :param plex_server: plexapi.server.PlexServer object
    :return: Program object
    """
    data = helpers._make_program_dict_from_plex_item(plex_item=plex_item, plex_server=plex_server)
    return Program(data=data, dizque_instance=None, channel_instance=None)


def convert_plex_item_to_filler(plex_item: Union[Video, Movie, Episode], plex_server: PServer) -> Filler:
    """
    Convert a PlexAPI Video, Movie or Episode object into a Filler
    :param plex_item: plexapi.video.Video, plexapi.video.Movie or plexapi.video.Episode object
    :param plex_server: plexapi.server.PlexServer object
    :return: Program object
    """
    data = helpers._make_filler_dict_from_plex_item(plex_item=plex_item, plex_server=plex_server)
    return Filler(data=data, dizque_instance=None, channel_instance=None)


def convert_plex_server_to_dizque_plex_server(plex_server: PServer) -> PlexServer:
    data = helpers._make_server_dict_from_plex_server(plex_server=plex_server)
    return PlexServer(data=data, dizque_instance=None)


class API:
    def __init__(self, url: str, verbose: bool = False):
        self.url = url.rstrip('/')
        self.verbose = verbose
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                            level=(logging.INFO if verbose else logging.ERROR))

    def _get(self, endpoint: str, params: dict = None, headers: dict = None, timeout: int = 2) -> Union[Response, None]:
        if not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
        url = f"{self.url}/api{endpoint}"
        return requests.get(url=url,
                            params=params,
                            headers=headers,
                            timeout=timeout,
                            log='info')

    def _post(self, endpoint: str, params: dict = None, headers: dict = None, data: dict = None, timeout: int = 2) -> \
            Union[Response, None]:
        if not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
        url = f"{self.url}/api{endpoint}"
        return requests.post(url=url,
                             params=params,
                             data=data,
                             headers=headers,
                             timeout=timeout,
                             log='info')

    def _put(self, endpoint: str, params: dict = None, headers: dict = None, data: dict = None, timeout: int = 2) -> \
            Union[Response, None]:
        if not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
        url = f"{self.url}/api{endpoint}"
        return requests.put(url=url,
                            params=params,
                            data=data,
                            headers=headers,
                            timeout=timeout,
                            log='info')

    def _delete(self, endpoint: str, params: dict = None, data: dict = None, timeout: int = 2) -> Union[Response, None]:
        if not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
        url = f"{self.url}/api{endpoint}"
        return requests.delete(url=url,
                               params=params,
                               data=data,
                               timeout=timeout,
                               log='info')

    def _get_json(self, endpoint: str, params: dict = None, headers: dict = None, timeout: int = 2) -> json:
        response = self._get(endpoint=endpoint, params=params, headers=headers, timeout=timeout)
        if response:
            return response.json()
        return {}

    # Versions
    @property
    def dizquetv_version(self) -> str:
        """
        Get dizqueTV version number
        :return: dizqueTV version number
        """
        return self._get_json(endpoint='/version').get('dizquetv')

    @property
    def ffmpeg_version(self) -> str:
        """
        Get FFMPEG version number
        :return: ffmpeg version number
        """
        return self._get_json(endpoint='/version').get('ffmpeg')

    # Plex Servers
    @property
    def plex_servers(self) -> List[PlexServer]:
        """
        Get the Plex Media Servers connected to dizqueTV
        :return: List of PlexServer objects
        """
        json_data = self._get_json(endpoint='/plex-servers')
        return [PlexServer(data=server, dizque_instance=self) for server in json_data]

    def plex_server_status(self, server_name: str) -> bool:
        """
        Check if a Plex Media Server is accessible
        :param server_name: Name of Plex Server
        :return: True if active, False if not active
        """
        if self._post(endpoint='/plex-servers/status', data={'name': server_name}):
            return True
        return False

    def plex_server_foreign_status(self, server_name: str) -> bool:
        """

        :param server_name: Name of Plex Server
        :return: True if active, False if not active
        """
        if self._post(endpoint='/plex-servers/foreignstatus', data={'name': server_name}):
            return True
        return False

    def get_plex_server(self, server_name: str) -> Union[PlexServer, None]:
        """
        Get a specific Plex Media Server
        :param server_name: Name of Plex Server
        :return: PlexServer object or None
        """
        for server in self.plex_servers:
            if server.name == server_name:
                return server
        return None

    def add_plex_server(self, **kwargs) -> Union[PlexServer, None]:
        """
        Add a Plex Media Server to dizqueTV
        :param kwargs: keyword arguments of setting names and values
        :return: PlexServer object or None
        """
        if helpers._settings_are_complete(new_settings_dict=kwargs,
                                          template_settings_dict=PLEX_SERVER_SETTINGS_TEMPLATE,
                                          ignore_id=True) \
                and self._put(endpoint='/plex-servers', data=kwargs):
            return self.get_plex_server(server_name=kwargs['name'])
        return None

    def add_plex_server_from_plexapi(self, plex_server: PServer) -> Union[PlexServer, None]:
        """
        Convert and add a plexapi.PlexServer as a Plex Media Server to dizqueTV
        :param plex_server: plexapi.PlexServer object to add to dizqueTV
        :return: PlexServer object or None
        """
        current_servers = self.plex_servers
        index = 0
        index_available = False
        while not index_available:
            if index in [ps.index for ps in current_servers]:
                index += 1
            else:
                index_available = True
        server_settings = {
            'name': plex_server.friendlyName,
            'uri': helpers.get_plex_indirect_uri(plex_server=plex_server),
            'accessToken': helpers.get_plex_access_token(plex_server=plex_server),
            'index': index,
            'arChannels': True,
            'arGuide': True
        }
        return self.add_plex_server(**server_settings)

    def update_plex_server(self, server_name: str, **kwargs) -> bool:
        """
        Edit a Plex Media Server on dizqueTV
        :param server_name: name of Plex Media Server to update
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        server = self.get_plex_server(server_name=server_name)
        if server:
            old_settings = server._data
            new_settings = helpers._combine_settings(new_settings_dict=kwargs, old_settings_dict=old_settings)
            if self._post(endpoint='/plex-servers', data=new_settings):
                return True
        return False

    def delete_plex_server(self, server_name: str) -> bool:
        """
        Remove a Plex Media Server from dizqueTV
        :param server_name: Name of Plex Server
        :return: True if successful, False if unsuccessful
        """
        if self._delete(endpoint='/plex-servers', data={'name': server_name}):
            return True
        return False

    # Channels
    @property
    def channels(self) -> List[Channel]:
        """
        Get all dizqueTV channels
        :return: List of Channel objects
        """
        json_data = self._get_json(endpoint='/channels', timeout=5)  # large JSON may take longer, so bigger timeout
        return [Channel(data=channel, dizque_instance=self) for channel in json_data]

    def get_channel(self, channel_number: int) -> Union[Channel, None]:
        """
        Get a specific dizqueTV channel
        :param channel_number: Number of channel
        :return: Channel object or None
        """
        channel_data = self._get_json(endpoint=f'/channel/{channel_number}')
        if channel_data:
            return Channel(data=channel_data, dizque_instance=self)
        return None

    def get_channel_info(self, channel_number: int) -> json:
        """
        Get the name, number and icon for a dizqueTV channel
        :param channel_number: Number of channel
        :return: JSON data with channel name, number and icon path
        """
        return self._get_json(endpoint=f'/channel/description/{channel_number}')

    @property
    def channel_numbers(self) -> List[int]:
        """
        Get all dizqueTV channel numbers
        :return: List of channel numbers
        """
        data = self._get_json(endpoint='/channelNumbers')
        if data:
            return data
        return []

    def _fill_in_default_channel_settings(self, settings_dict: dict, handle_errors: bool = False) -> dict:
        """
        Set some dynamic default values, such as channel number, start time and image URLs
        :param settings_dict: Dictionary of new settings for channel
        :return: Dictionary of settings with defaults filled in
        """
        if not settings_dict.get('programs'):  # empty or doesn't exist
            if handle_errors:
                settings_dict['programs'] = [{
                    "duration": 600000,
                    "isOffline": True
                }]
            else:
                raise ChannelCreationError("You must include at least one program when creating a channel.")
        if settings_dict.get('number') in self.channel_numbers:
            if handle_errors:
                settings_dict.pop('number')  # remove 'number' key, will be caught down below
            else:
                raise ChannelCreationError(f"Channel #{settings_dict.get('number')} already exists.")
        if 'number' not in settings_dict.keys():
            settings_dict['number'] = max(self.channel_numbers) + 1
        if 'name' not in settings_dict.keys():
            settings_dict['name'] = f"Channel {settings_dict['number']}"
        if 'startTime' not in settings_dict.keys():
            settings_dict['startTime'] = helpers.get_nearest_30_minute_mark()
        if 'icon' not in settings_dict.keys():
            settings_dict['icon'] = f"{self.url}/images/dizquetv.png"
        if 'offlinePicture' not in settings_dict.keys():
            settings_dict['offlinePicture'] = f"{self.url}/images/generic-offline-screen.png"
        # override duration regardless of user input
        settings_dict['duration'] = sum(program['duration'] for program in settings_dict['programs'])
        return helpers._combine_settings(new_settings_dict=settings_dict, old_settings_dict=CHANNEL_SETTINGS_DEFAULT)

    def add_channel(self,
                    programs: List[Union[Program, Video, Movie, Episode]],
                    plex_server: PServer = None,
                    handle_errors: bool = False,
                    **kwargs) -> Union[Channel, None]:
        """
        Add a channel to dizqueTV
        Must include at least one program to create
        :param programs: At least one Program or PlexAPI Video, Movie or Episode to add to the new channel
        :param plex_server: plexapi.server.PlexServer (optional, required if adding PlexAPI Video, Movie or Episode)
        :param kwargs: keyword arguments of setting names and values
        :param handle_errors: Suppress error if they arise
        (ex. alter invalid channel number, add redirect if no program is included)
        :return: new Channel object or None
        """
        kwargs['programs'] = []
        for program in programs:
            if type(program) == Program:
                kwargs['programs'].append(program)
            else:
                if not plex_server:
                    raise ChannelCreationError("You must include a plex_server if you are adding PlexAPI Video, "
                                               "Movie or Episodes as programs")
                kwargs['programs'].append(
                    convert_plex_item_to_program(plex_item=program, plex_server=plex_server)._data)
        kwargs = self._fill_in_default_channel_settings(settings_dict=kwargs, handle_errors=handle_errors)
        if helpers._settings_are_complete(new_settings_dict=kwargs,
                                          template_settings_dict=CHANNEL_SETTINGS_TEMPLATE,
                                          ignore_id=True) \
                and self._put(endpoint="/channel", data=kwargs):
            return self.get_channel(channel_number=kwargs['number'])
        return None

    def update_channel(self, channel_number: int, **kwargs) -> bool:
        """
        Edit a dizqueTV channel
        :param channel_number: Number of channel to update
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        channel = self.get_channel(channel_number=channel_number)
        if channel:
            old_settings = channel._data
            new_settings = helpers._combine_settings(new_settings_dict=kwargs, old_settings_dict=old_settings)
            if self._post(endpoint="/channel", data=new_settings):
                return True
        return False

    def delete_channel(self, channel_number: int) -> bool:
        """
        Delete a dizqueTV channel
        :return: True if successful, False if unsuccessful
        """
        if self._delete(endpoint="/channel", data={'number': channel_number}):
            return True
        return False

    # FFMPEG Settings
    @property
    def ffmpeg_settings(self) -> Union[FFMPEGSettings, None]:
        """
        Get dizqueTV's FFMPEG settings
        :return: FFMPEGSettings object or None
        """
        json_data = self._get_json(endpoint='/ffmpeg-settings')
        if json_data:
            return FFMPEGSettings(data=json_data, dizque_instance=self)
        return None

    def update_ffmpeg_settings(self, **kwargs) -> bool:
        """
        Edit dizqueTV's FFMPEG settings
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.ffmpeg_settings._data
        new_settings = helpers._combine_settings(new_settings_dict=kwargs, old_settings_dict=old_settings)
        if self._put(endpoint='/ffmpeg-settings', data=new_settings):
            return True
        return False

    def reset_ffmpeg_settings(self) -> bool:
        """
        Reset dizqueTV's FFMPEG settings to default
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.ffmpeg_settings._data
        if self._post(endpoint='/ffmpeg-settings', data={'_id': old_settings['_id']}):
            return True
        return False

    # Plex settings
    @property
    def plex_settings(self) -> Union[PlexSettings, None]:
        """
        Get dizqueTV's Plex settings
        :return: PlexSettings object or None
        """
        json_data = self._get_json(endpoint='/plex-settings')
        if json_data:
            return PlexSettings(data=json_data, dizque_instance=self)
        return None

    def update_plex_settings(self, **kwargs) -> bool:
        """
        Edit dizqueTV's Plex settings
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.plex_settings._data
        new_settings = helpers._combine_settings(new_settings_dict=kwargs, old_settings_dict=old_settings)
        if self._put(endpoint='/plex-settings', data=new_settings):
            return True
        return False

    def reset_plex_settings(self) -> bool:
        """
        Reset dizqueTV's Plex settings to default
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.plex_settings._data
        if self._post(endpoint='/plex-settings', data={'_id': old_settings['_id']}):
            return True
        return False

    # XML Refresh Time
    @property
    def last_xmltv_refresh(self) -> str:
        """
        Get the last time the XMLTV file was refreshed
        :return: Timestamp of last refresh
        """
        return self._get_json(endpoint='/xmltv-last-refresh')

    # XMLTV Settings
    @property
    def xmltv_settings(self) -> Union[XMLTVSettings, None]:
        """
        Get dizqueTV's XMLTV settings
        :return: XMLTVSettings object or None
        """
        json_data = self._get_json(endpoint='/xmltv-settings')
        if json_data:
            return XMLTVSettings(data=json_data, dizque_instance=self)
        return None

    def update_xmltv_settings(self, **kwargs) -> bool:
        """
        Edit dizqueTV's XMLTV settings
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.xmltv_settings._data
        new_settings = helpers._combine_settings(new_settings_dict=kwargs, old_settings_dict=old_settings)
        if self._put(endpoint='/xmltv-settings', data=new_settings):
            return True
        return False

    def reset_xmltv_settings(self) -> bool:
        """
        Reset dizqueTV's XMLTV settings to default
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.xmltv_settings._data
        if self._post(endpoint='/xmltv-settings', data={'_id': old_settings['_id']}):
            return True
        return False

    # HDHomeRun Settings
    @property
    def hdhr_settings(self) -> Union[HDHomeRunSettings, None]:
        """
        Get dizqueTV's HDHomeRun settings
        :return: HDHomeRunSettings object or None
        """
        json_data = self._get_json(endpoint='/hdhr-settings')
        if json_data:
            return HDHomeRunSettings(data=json_data, dizque_instance=self)
        return None

    def update_hdhr_settings(self, **kwargs) -> bool:
        """
        Edit dizqueTV's HDHomeRun settings
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.hdhr_settings._data
        new_settings = helpers._combine_settings(new_settings_dict=kwargs, old_settings_dict=old_settings)
        if self._put(endpoint='/hdhr-settings', data=new_settings):
            return True
        return False

    def reset_hdhr_settings(self) -> bool:
        """
        Reset dizqueTV's HDHomeRun settings to default
        :return: True if successful, False if unsuccessful
        """
        old_settings = self.hdhr_settings._data
        if self._post(endpoint='/hdhr-settings', data={'_id': old_settings['_id']}):
            return True
        return False

    # XMLTV.XML
    def refresh_xml(self) -> bool:
        """
        Force the server to update the xmltv.xml file
        :return: True if successful, False if unsuccessful
        """
        # updating the xmltv_settings causes the server to reload the xmltv.xml file
        return self.update_xmltv_settings()

    @property
    def xmltv_xml(self) -> Union[ElementTree.Element, None]:
        """
        Get dizqueTV's XMLTV data
        :return: xml.etree.ElementTree.Element object or None
        """
        self.refresh_xml()
        response = self._get(endpoint='/xmltv.xml')
        if response:
            return ElementTree.fromstring(response.content)
        return None

    @property
    def m3u(self) -> m3u8:
        """
        Get dizqueTV's m3u playlist
        Without m3u8, this method currently produces an error.
        :return: m3u8 object
        """
        return m3u8.load(f"{self.url}/api/channels.m3u")

    # Other Functions
    def convert_plex_item_to_program(self, plex_item: Union[Video, Movie, Episode], plex_server: PServer) -> Program:
        """
        Convert a PlexAPI Video, Movie or Episode object into a Program
        :param plex_item: plexapi.video.Video, plexapi.video.Movie or plexapi.video.Episode object
        :param plex_server: plexapi.server.PlexServer object
        :return: Program object
        """
        return convert_plex_item_to_program(plex_item=plex_item, plex_server=plex_server)

    def convert_plex_item_to_filler(self, plex_item: Union[Video, Movie, Episode], plex_server: PServer) -> Filler:
        """
        Convert a PlexAPI Video, Movie or Episode object into a Filler
        :param plex_item: plexapi.video.Video, plexapi.video.Movie or plexapi.video.Episode object
        :param plex_server: plexapi.server.PlexServer object
        :return: Program object
        """
        return convert_plex_item_to_filler(plex_item=plex_item, plex_server=plex_server)

    def add_programs_to_channels(self, programs: List[Program],
                                 channels: List[Channel] = None,
                                 channel_numbers: List[int] = None) -> bool:
        """
        Add multiple programs to multiple channels
        :param programs: List of Program objects
        :param channels: List of Channel objects (optional)
        :param channel_numbers: List of channel numbers
        :return: True if successful, False if unsuccessful (Channel objects reload in place)
        """
        if not channels and not channel_numbers:
            raise MissingParametersError(
                "Please include either a list of Channel objects or a list of channel numbers.")
        if channel_numbers:
            channels = []
            for number in channel_numbers:
                channels.append(self.get_channel(channel_number=number))
        for channel in channels:
            if not channel.add_programs(programs=programs):
                return False
        return True

    def add_fillers_to_channels(self, fillers: List[Filler],
                                channels: List[Channel] = None,
                                channel_numbers: List[int] = None) -> bool:
        """
        Add multiple filler items to multiple channels
        :param fillers: List of Filler objects
        :param channels: List of Channel objects (optional)
        :param channel_numbers: List of channel numbers
        :return: True if successful, False if unsuccessful (Channel objects reload in place)
        """
        if not channels and not channel_numbers:
            raise MissingParametersError(
                "Please include either a list of Channel objects or a list of channel numbers.")
        if channel_numbers:
            channels = []
            for number in channel_numbers:
                channels.append(self.get_channel(channel_number=number))
        for channel in channels:
            if not channel.add_fillers(fillers=fillers):
                return False
        return True
