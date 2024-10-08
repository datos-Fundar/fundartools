try:
    import gwrappers
    from gwrappers.googledrive import *

    files_api = googledrive.instance.service.files()
except ImportError:
    raise ImportError("'gwrappers' isn't installed. Get it from github.com/datos-Fundar/gwrappers")