import json

import dizqueTV.helpers as helpers


class XMLTVSettings:
    def __init__(self, data: json, dizque_instance):
        self._data = data
        self._dizque_instance = dizque_instance
        self.cache = data.get('cache')
        self.refresh = data.get('refresh')
        self.file = data.get('file')
        self._id = data.get('_id')

    @helpers.check_for_dizque_instance
    def reload(self):
        """
        Reload current XMLTVSettings object
        """
        temp_settings = self._dizque_instance.xmltv_settings
        if temp_settings:
            json_data = temp_settings._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_settings

    @helpers.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit these XMLTV settings
        Automatically refreshes current XMLTVSettings object
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        if self._dizque_instance.update_xmltv_settings(**kwargs):
            self.reload()
            return True
        return False

    @helpers.check_for_dizque_instance
    def reset(self) -> bool:
        """
        Reset these XMLTV settings
        Automatically refreshes current XMLTVSettings object
        :return: True if successful, False if unsuccessful
        """
        if self._dizque_instance.reset_xmltv_settings():
            self.reload()
            return True
        return False


class HDHomeRunSettings:
    def __init__(self, data: json, dizque_instance):
        self._data = data
        self._dizque_instance = dizque_instance
        self.tunerCount = data.get('tunerCount')
        self.autoDiscovery = data.get('autoDiscovery')
        self._id = data.get('_id')

    @helpers.check_for_dizque_instance
    def refresh(self):
        """
        Reload current HDHomeRunSettings object
        """
        temp_settings = self._dizque_instance.hdhr_settings
        if temp_settings:
            json_data = temp_settings._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_settings

    @helpers.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit these HDHomeRun settings
        Automatically refreshes current HDHomeRunSettings object
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        if self._dizque_instance.update_hdhr_settings(**kwargs):
            self.refresh()
            return True
        return False

    @helpers.check_for_dizque_instance
    def reset(self) -> bool:
        """
        Reset these HDHomeRun settings
        Automatically refreshes current HDHomeRunSettings object
        :return: True if successful, False if unsuccessful
        """
        if self._dizque_instance.reset_hdhr_settings():
            self.refresh()
            return True
        return False


class FFMPEGSettings:
    def __init__(self, data: json, dizque_instance):
        self._data = data
        self._dizque_instance = dizque_instance
        self.configVersion = data.get('configVersion')
        self.ffmpegPath = data.get('ffmpegPath')
        self.threads = data.get('threads')
        self.concatMuxDelay = data.get('concatMuxDelay')
        self.logFfmpeg = data.get('logFfmpeg')
        self.enableFFMPEGTranscoding = data.get('enableFFMPEGTranscoding')
        self.audioVolumePercent = data.get('audioVolumePercent')
        self.videoEncoder = data.get('videoEncoder')
        self.audioEncoder = data.get('audioEncoder')
        self.targetResolution = data.get('targetResolution')
        self.videoBitrate = data.get('videoBitrate')
        self.videoBufSize = data.get('videoBufSize')
        self.audioBitrate = data.get('audioBitrate')
        self.audioBufSize = data.get('audioBufSize')
        self.audioSampleRate = data.get('audioSampleRate')
        self.audioChannels = data.get('audioChannels')
        self.errorScreen = data.get('errorScreen')
        self.errorAudio = data.get('errorAudio')
        self.normalizeVideoCodec = data.get('normalizeVideoCodec')
        self.normalizeAudioCodec = data.get('normalizeAudioCodec')
        self.normalizeResolution = data.get('normalizeResolution')
        self.normalizeAudio = data.get('normalizeAudio')
        self._id = data.get('_id')

    @helpers.check_for_dizque_instance
    def refresh(self):
        """
        Reload current FFMPEGSettings object
        """
        temp_settings = self._dizque_instance.ffmpeg_settings
        if temp_settings:
            json_data = temp_settings._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_settings

    @helpers.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit these FFMPEG settings
        Automatically refreshes current FFMPEGSettings object
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        if self._dizque_instance.update_ffmpeg_settings(**kwargs):
            self.refresh()
            return True
        return False

    @helpers.check_for_dizque_instance
    def reset(self) -> bool:
        """
        Reset these FFMPEG settings
        Automatically refreshes current FFMPEGSettings object
        :return: True if successful, False if unsuccessful
        """
        if self._dizque_instance.reset_ffmpeg_settings():
            self.refresh()
            return True
        return False


class PlexSettings:
    def __init__(self, data: json, dizque_instance):
        self._data = data
        self._dizque_instance = dizque_instance
        self.streamPath = data.get('streamPath')
        self.debugLogging = data.get('debugLogging')
        self.transcodeBitrate = data.get('transcodeBitrate')
        self.mediaBufferSize = data.get('mediaBufferSize')
        self.transcodeMediaBufferSize = data.get('transcodeMediaBufferSize')
        self.maxPlayableResolution = data.get('maxPlayableResolution')
        self.maxTranscodeResolution = data.get('maxTranscodeResolution')
        self.videoCodecs = data.get('videoCodecs')
        self.audioCodecs = data.get('audioCodecs')
        self.maxAudioChannels = data.get('maxAudioChannels')
        self.audioBoost = data.get('audioBoost')
        self.enableSubtitles = data.get('enableSubtitles')
        self.subtitleSize = data.get('subtitleSize')
        self.updatePlayStatus = data.get('updatePlayStatus')
        self.streamProtocol = data.get('streamProtocol')
        self.forceDirectPlay = data.get('forceDirectPlay')
        self.pathReplace = data.get('pathReplace')
        self.pathReplaceWith = data.get('pathReplaceWith')
        self._id = data.get('_id')

    @helpers.check_for_dizque_instance
    def refresh(self):
        """
        Reload current PlexSettings object
        """
        temp_settings = self._dizque_instance.plex_settings
        if temp_settings:
            json_data = temp_settings._data
            self.__init__(data=json_data, dizque_instance=self._dizque_instance)
            del temp_settings

    @helpers.check_for_dizque_instance
    def update(self, **kwargs) -> bool:
        """
        Edit these Plex settings
        Automatically refreshes current PlexSettings object
        :param kwargs: keyword arguments of setting names and values
        :return: True if successful, False if unsuccessful
        """
        if self._dizque_instance.update_plex_settings(**kwargs):
            self.refresh()
            return True
        return False

    @helpers.check_for_dizque_instance
    def reset(self) -> bool:
        """
        Reset these Plex settings
        Automatically refreshes current PlexSettings object
        :return: True if successful, False if unsuccessful
        """
        if self._dizque_instance.reset_plex_settings():
            self.refresh()
            return True
        return False
