""" Youtube API Test

PlayListItems: list: https://developers.google.com/youtube/v3/docs/playlistItems/list?hl=es-419
"""
import pandas as pd
import googleapiclient.discovery


def get_playlist(playlist_id: str, api_key: str):
    """ Obtains video playlist from YouTube API """
    api = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    api = api.playlistItems()
    videos = []
    page_token: str = ""
    while True:
        req = api.list(part="snippet,status",
                       playlistId=playlist_id,
                       maxResults="50",
                       pageToken=page_token)
        res = req.execute()
        videos.extend(res["items"])

        if "nextPageToken" in res:
            page_token = res["nextPageToken"]
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
