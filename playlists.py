''' Compara dos listas de videos convertidas en tablas para buscar videos faltantes
en cada lista. '''
from datetime import date
import pandas as pd
import yaml
from utils import Color


pd.set_option('display.max_colwidth', None)


def cargar_playlists_conf(filename: str) -> dict:
    ''' Carga la configuración desde un archivo '''
    with open(filename, encoding='utf8') as settings_file:
        return yaml.load(settings_file, yaml.Loader)


def procesar_dataframe(df_orig: pd.DataFrame, df_filt: pd.DataFrame, title: str):
    ''' Imprime los videos faltantes más los videos contiguos como referencia

    Imprime los videos borrados en rojo y los videos contiguos a estos en blanco
    '''

    if not df_filt.empty:
        print(Color.amarillo(title))
        for _, row in df_filt.sort_values(by='No').iterrows():
            # Fila anterior
            if (row['No'] - 1 not in df_filt['No'].values
                    and row['No'] - 1 in df_orig['No'].values):
                prev_row = df_orig[df_orig['No'] == row['No'] - 1].iloc[0]
                print(f'  {prev_row["No"]:4}\t{prev_row["Canal"]}, "{prev_row["Nombre"]}"')

            print(Color.rojo(f'⬤ {row["No"]:4}\t{row["Canal"]}, "{row["Nombre"]}"'))

            # Fila siguiente
            if (row['No'] + 1 not in df_filt['No'].values
                    and row['No'] + 1 in df_orig['No'].values):
                next_row = df_orig[df_orig['No'] == row['No'] + 1].iloc[0]
                print(f'  {next_row["No"]:4}\t{next_row["Canal"]}, "{next_row["Nombre"]}"')

        print()
        mostrar_faltantes(df_filt)

        print()


def mostrar_faltantes(dataframe: pd.DataFrame):
    ''' Imprime los videos borrados en formato CSV para pegar en Calc '''
    if not dataframe.empty:
        print(Color.verde('Salida:'))
        print()

        # dataframe = dataframe.assign(Fecha_el=date.today().strftime('%d/%m/%y'))
        dataframe["Fecha_el"] = date.today().strftime('%d/%m/%y')
        dataframe.sort_values(by='No', inplace=True)

        if 'Fecha' not in dataframe:
            dataframe["Fecha"] = ""

        dataframe = dataframe.reset_index()[['Fecha_el', 'Fecha', 'Canal', 'ID', 'Nombre']]

        print(dataframe.to_csv(index=False, date_format='%d/%m/%y'))
