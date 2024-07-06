# Youtube

Compares a Youtube playlist's state to a saved list on a Excel/Calc file.

## Usage

1. Compare a Youtube playlist using the Youtube Data API:

```sh
python main.py --youtube "playlist-name"
```

The playlist is obtained using a Google Cloud API key and the playlist's ID.

2. Compare a Youtube playlist downloaded to a CSV file:

```sh
python main.py --csv "playlist.csv" "playlist-name"
```

In both cases it compares the videos' IDs.

## Settings

Playlist settings stored in YAML format, loaded from file at the environment variable `PLAYLIST_SETTINGS`. All configured playlists are listed under the top `playlists` object.

- `io`: Excel/Calc filename.
- `sheet_name`: Sheet name
- `header`: Header row
- `index_col`: Column index with the videos' ids.
- `usecols`: Columns with videos' properties.
- `skiprows`: Rows indexes to skip.
- `parse_dates`: Column name to parse dates.
- `enabled`: If the playlist is processed during execution.

Set `API_KEY` with key obtained from the Google Cloud Console to use the Youtube Data API.