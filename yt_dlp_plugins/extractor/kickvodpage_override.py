import re
import json

from yt_dlp.extractor.kick import KickIE

from yt_dlp.utils import (
    float_or_none,
    int_or_none,
    parse_iso8601,
    str_or_none,
    traverse_obj,
    url_or_none,
)

class _KickOverridePluginIE(KickIE, plugin_name='kickvodpage'):
    def _create_format(self, video_id):
        response = self._call_api(f'v1/video/{video_id}', video_id)
        
        return {
            'id': video_id,
            'formats': self._extract_m3u8_formats(response['source'], video_id, 'mp4'),
            **traverse_obj(response, {
                'title': ('livestream', ('session_title', 'slug'), {str}, any),
                'description': ('livestream', 'channel', 'user', 'bio', {str}),
                'channel': ('livestream', 'channel', 'slug', {str}),
                'channel_id': ('livestream', 'channel', 'id', {int}, {str_or_none}),
                'uploader': ('livestream', 'channel', 'user', 'username', {str}),
                'uploader_id': ('livestream', 'channel', 'user_id', {int}, {str_or_none}),
                'timestamp': ('created_at', {parse_iso8601}),
                'duration': ('livestream', 'duration', {float_or_none(scale=1000)}),
                'thumbnail': ('livestream', 'thumbnail', {url_or_none}),
                'categories': ('livestream', 'categories', ..., 'name', {str}),
                'view_count': ('views', {int_or_none}),
                'age_limit': ('livestream', 'is_mature', {bool}, {lambda x: 18 if x else 0}),
            }),
        }
    
    def _real_extract(self, url):
        url_regex = re.compile(r'https?://(?:www\.)?kick\.com/(?P<channel_name>[\w-]+)/videos/?$')
        match = url_regex.match(url)
        
        if not match:
            return super()._real_extract(url)
        
        channel_name = match.groupdict()["channel_name"]
        response = self._call_api(f'v2/channels/{channel_name}/videos', None)
        
        if self._configuration_arg('only_latest_stream', ['false', 'true'], ie_key='KickVodPage')[0] == 'true':
            return self._create_format( response[0]['video']['uuid'] )

        # the v2/channels response is missing a lot of data that's in the v1
        # response, but it notably includes the real video id (the uuid used in
        # urls), so we combine the two (in the sense that the entire v2 response
        # is discarded except for only the uuid)
        
        # techincally, the response already answers in new->old sorting, but i
        # don't want to take any chances
        channel_videos = sorted(
            [self._create_format(x['video']['uuid']) for x in response],
            key=lambda x: x['timestamp'],
            reverse=True
        )
        
        return self.playlist_result(
            entries=channel_videos,
            playlist_id=channel_name,
            playlist_title=f'{channel_name} - Videos'
        )
