""" Youtube API Test

PlayListItems: list: https://developers.google.com/youtube/v3/docs/playlistItems/list?hl=es-419
"""
import json
import requests
import pandas as pd


def make_url(playlist_id: str | None, api_key: str | None, max_results: str | None, token=""):
    """ Creates the URL string for fetching the playlist videos """
    return "https://www.googleapis.com/youtube/v3/playlistItems?" \
        + "part=snippet,status" \
        + f"&playlistId={playlist_id}" \
        + f"&key={api_key}" \
        + f"&maxResults={max_results}" \
        + (f"&pageToken={token}" if token else "")


def get_playlist(url: str, make_url_func):
    """ Obtains video playlist from YouTube API """
    videos = []
    while True:
        # request = requests.get(url, timeout=10, headers={"Authorization": "Bearer "})
        request = requests.get(url, timeout=10)
        data: dict = json.loads(request.text)
        videos.extend(data["items"])

        if "nextPageToken" in data:
            url = make_url_func(data["nextPageToken"])
        else:
            break
    return videos


def is_public(video) -> bool:
    """ Check if video is public and thus listed in the playlist """
    return video["status"]["privacyStatus"] == "public"


def make_df(videos: list):
    """ Saves the video list into a dataframe.

    At the moment ignores deleted/blocked videos.
    """
    videos_df = pd.DataFrame(columns=["Canal", "ID", "Nombre"])
    for video in videos:
        if "videoOwnerChannelTitle" in video["snippet"] and is_public(video):
            videos_df = pd.concat([
                videos_df,
                pd.DataFrame([[
                    video["snippet"]["videoOwnerChannelTitle"],
                    video["snippet"]["resourceId"]["videoId"],
                    video["snippet"]["title"]
                ]], columns=videos_df.columns)
            ], ignore_index=True)
    videos_df.index += 1
    videos_df.rename(columns={"Unnamed: 0": "No"})
    return videos_df
