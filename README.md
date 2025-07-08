Plugin that allows entry of URLs like `kick.com/<username/videos` to download an entire channel's VODs. This should be easily extensible to clips as well, but I don't feel like doing that right now.

Install by dropping this folder (KickVodPage) into `$XDG_CONFIG_DIR/yt-dlp/plugins` (where $XDG_CONFIG_DIR is usually `~/.config`) or `%APPDATA%/yt-dlp/plugins`. These directories might not exist if you've never done this before, so you'll have to create them.
