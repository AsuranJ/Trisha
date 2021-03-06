# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..utils import (
    try_get,
    ExtractorError,
)
from ..compat import (
    compat_str,
)


class WhoWatchIE(InfoExtractor):
    IE_NAME = 'whowatch'
    _VALID_URL = r'https?://whowatch\.tv/viewer/(?P<id>\d+)/?'
    META_API_URL = 'https://api.whowatch.tv/lives/%s'
    LIVE_API_URL = 'https://api.whowatch.tv/lives/%s/play'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        self._download_webpage(url, video_id)
        metadata = self._download_json(self.META_API_URL % video_id, video_id)
        live_data = self._download_json(self.LIVE_API_URL % video_id, video_id)

        title = try_get(None, (
            lambda x: live_data['share_info']['live_title'][1:-1],
            lambda x: metadata['live']['title'],
        ), compat_str)

        hls_url = live_data.get('hls_url')
        if not hls_url:
            raise ExtractorError('The live is offline.', expected=True)
        formats = self._extract_m3u8_formats(
            hls_url, video_id, ext='mp4', entry_protocol='m3u8_native',
            m3u8_id='hls')
        self._sort_formats(formats)

        uploader_id = try_get(metadata, lambda x: x['live']['user']['user_path'], compat_str)
        uploader_id_internal = try_get(metadata, lambda x: x['live']['user']['id'], int)
        uploader = try_get(metadata, lambda x: x['live']['user']['name'], compat_str)

        return {
            'id': video_id,
            'title': title,
            'uploader_id': uploader_id,
            'uploader_id_internal': uploader_id_internal,
            'uploader': uploader,
            'formats': formats,
            'is_live': True,
        }
