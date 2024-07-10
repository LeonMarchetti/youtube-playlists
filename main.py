# pylint: disable=line-too-long
""" Main """
import argparse
from os import getenv, path
import sys
from time import strftime

from dotenv import load_dotenv
import pandas as pd
import playlists
import youtube
from utils import Color


load_dotenv(dotenv_path=path.dirname(__file__) + "/.env")


MSG_SOLO_EXCEL = "Videos que están en Calc pero no en YouTube"
MSG_SOLO_YT = "Videos que están en YouTube pero no en Calc"
MSG_DF_IGUALES = Color.verde('Los datasets son iguales.')


def cargar_df(playlist_id: str, cache: str | None = None):
    """ Carga el dataframe tanto de un archivo ya guardado en el sistema de
    archivos o desde la API de Youtube
    """
    # Si la variable CACHE no está o está comentada en .env entonces da
    # None y paso a llamar a la API
    if cache:
        return pd.read_csv(cache, index_col=0)

    api_key = getenv('API_KEY')
    if not api_key:
        print("No se cargó la API key (API_KEY)", file=sys.stderr)
        sys.exit(1)

    videos = youtube.get_playlist(playlist_id, api_key)
    videos_df = youtube.make_df(videos)
    return videos_df


def guardar_df(df_videos: pd.DataFrame, output_name: str | None):
    """ Guarda el dataframe con la playlist a un archivo CSV, con un timestamp en el nombre del
    archivo
    """
    fecha = strftime('%Y%m%d-%H%M%S')
    df_videos.to_csv(f"{output_name}.{fecha}.csv")


def procesar_playlists(label: str, df_videos: pd.DataFrame, pl_conf):
    """ Procesa el dataframe de la playlist """
    print(Color.amarillo(f'Playlist: {label}'))

    df_videos["No"] = df_videos.index
    df_videos = df_videos.set_index("ID")

    df_excel: pd.DataFrame = pd.read_excel(pl_conf['io'],
                                           sheet_name=pl_conf['sheet_name'],
                                           header=pl_conf['header'],
                                           names=['No', 'Fecha', 'Canal', 'ID', 'Nombre'],
                                           index_col=pl_conf['index_col'],
                                           usecols=pl_conf['usecols'],
                                           skiprows=pl_conf.get('skiprows', []),
                                           parse_dates=pl_conf['parse_dates'])

    # Borrar filas vacías y sin número de índice
    df_excel = df_excel.loc[df_excel.index.dropna()]
    df_excel = df_excel[pd.notna(df_excel["No"])]

    # Videos que están en Excel pero no en YouTube
    df_solo_excel = df_excel.loc[df_excel.index.difference(df_videos.index), :]
    # Videos que están en YouTube pero no en Excel
    df_solo_yt = df_videos.loc[df_videos.index.difference(df_excel.index), :]

    # if df_videos.index.equals(df_excel.index) and df_excel.index.equals(df_videos.index):
    if df_solo_excel.empty and df_solo_yt.empty:
        print(MSG_DF_IGUALES)
        return

    print()
    playlists.procesar_dataframe(df_excel, df_solo_excel, MSG_SOLO_EXCEL)
    playlists.procesar_dataframe(df_videos, df_solo_yt, MSG_SOLO_YT)

    timestamp = strftime("%Y-%m-%dT%H:%M:%S")
    csv_prefix = f"{(getenv('OUTPUT_PREFIX') or '')}/{label}.{timestamp}"
    if df_solo_excel.shape[0] > 0:
        df_solo_excel.to_csv(f"{csv_prefix}.solo_excel.csv")
    if df_solo_yt.shape[0] > 0:
        df_solo_yt.to_csv(f"{csv_prefix}.solo_yt.csv")


def process_args():
    """ Procesa los argumentos de la linea de comandos """
    parser = argparse.ArgumentParser()
    parser.add_argument("playlist", action="append", nargs="?", help="Lista de claves a procesar, ninguna=todas")
    parser.add_argument("--cache", type=str, help="Usa una lista preprocesada desde un archivo")
    parser.add_argument("--csv", action="store", help="Procesar con lista descargada en archivo CSV (requiere atributo 'csv')")
    parser.add_argument("--youtube", action="store_true", help="Procesar con API de Youtube (requiere atributo 'playlist')")
    return parser.parse_args()


def process_youtube(keys: list[str], playlists_conf: dict):
    """ Processes playlist from Youtube Data API """
    for key in keys:
        pl_conf: dict = playlists_conf['playlists'][key]

        if not 'enabled' in pl_conf or not pl_conf['enabled']:
            continue

        if not 'playlist' in pl_conf or not pl_conf['playlist']:
            print(f'Salteando "{key}" por no tener configurada la playlist de Youtube...')
            continue

        df_videos = cargar_df(pl_conf['playlist'])
        procesar_playlists(key, df_videos, pl_conf)

    return 0


def process_csv(csv_input_file: str, keys: list[str], playlists_conf: dict):
    """ Processes playlist from CSV file """
    df_csv = pd.read_csv(csv_input_file, sep=';', header=0, index_col=1)
    # Agregar columna de número de fila al primer dataset
    df_csv = df_csv.assign(No=range(1, len(df_csv)+1, 1))

    for key in keys:
        pl_conf: dict = playlists_conf['playlists'][key]
        df_excel: pd.DataFrame = pd.read_excel(pl_conf['io'],
                                               sheet_name=pl_conf['sheet_name'],
                                               header=pl_conf['header'],
                                               names=['No', 'Fecha', 'Canal', 'ID', 'Nombre'],
                                               index_col=pl_conf['index_col'],
                                               usecols=pl_conf['usecols'],
                                               skiprows=pl_conf.get('skiprows', []),
                                               parse_dates=pl_conf['parse_dates'],
                                               date_format=pd.to_datetime)  # type: ignore

        # Borrar filas vacías
        df_excel = df_excel.loc[df_excel.index.dropna()]

        if df_csv.index.equals(df_excel.index) and df_excel.index.equals(df_csv.index):
            print(Color.verde('Los datasets son iguales.'))
            continue

        # Videos que están en Calc pero no en YouTube
        df3 = df_excel.loc[df_excel.index.difference(df_csv.index), :]
        # Videos que están en YouTube pero no en Calc
        df4 = df_csv.loc[df_csv.index.difference(df_excel.index), :]

        print()
        playlists.procesar_dataframe(df_excel, df3, 'Videos que están en Calc pero no en YouTube')
        playlists.procesar_dataframe(df_csv, df4, 'Videos que están en YouTube pero no en Calc')

    return 0


def main():
    """ Función principal """
    args = process_args()

    playlists_conf = playlists.cargar_playlists_conf(getenv('PLAYLIST_SETTINGS') or 'settings.yml')
    keys: list[str] = list(playlists_conf['playlists'].keys()) if args.playlist == [None] else args.playlist

    if args.csv and args.youtube:
        print("No hay que usar los parámetros \"csv\" y \"youtube\" al mismo tiempo", file=sys.stderr)
        sys.exit(1)

    if args.csv:
        ret = process_csv(args.csv, keys, playlists_conf)
        sys.exit(ret)

    if args.youtube:
        ret = process_youtube(keys, playlists_conf)
        sys.exit(ret)


if __name__ == '__main__':
    main()
