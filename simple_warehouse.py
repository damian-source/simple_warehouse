import os
import datetime
import time
import pytz # obsługa stref czasowych
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tksheet
import threading
from pynput.keyboard import Listener, Key # biblioteka do nasłuchiwania klawiatury


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
DOCUMENT_ID  = 'tu wpisz swoj dokument ID'
WAREHOUSE_SHEET = "Magazyn"
LOGS_SHEET = "Logi"
DEFINITION_SHEET = "Definicje"


# Dane aktualnego użytkownika
worker = "nie znane"
localization = "nie znane"
time_zone = "Europe/Warsaw"

# nazwy dla polskiej wersji językowej
new_product_text = "wprowadzenie produktu"
ship_text = "wysyłka"
change_localization_text = "Przemagazynowanie"
return_itme_text = "przyjęcie zwrotu"
input_item_text = "Wprowadzanie"
save_text = "zapisz"
add_text = "dodaj"
barcode_text = "Kod"
brand_text = "Marka"
size_text = "Rozmiar"
name_text = "Nazwa"
price_text = "Cena"
location_text = "Lokalizacja"
color_text = "Kolor"
confirm_text = "Zatwierdź"
add_to_list_text = "Dodaj do listy"
added_to_list_text = "Dodano do listy"
added_do_database_text = "Dodano do bazy danych"
added_do_database_all_text = "Dodano do bazy danych wszystkie proukty"
added_new_difinition_text = "Dodano nową definicję"
hello_text = "Witaj w aplikacji Simple Warehouse"
no_found_id_text = "Nie znaleziono artykułu"
worning_text = "Uwaga!"
ID_exists_text = "Towar o tym numerze ID jest już w bazie lub w arkuszu."
destiny_restorage_text = "Przemagazynuj do"
no_data_to_restorage_text = "Nie podałeś kodu lub celu przemagazynowania"
no_ID_text = "Brak szukanego ID"
no_history_log_text = "Nie znaleziowo w logach produktu"
exists_in_warehouse = "produkt już jest w magazynie"
product_text = "Produkt"
return_to_warehouse = "wrócił do magazynu."
returns_text = "Zwroty"
settings_text = "Ustawienia"
my_localization_text = "Moja lokalizacja"
my_name_text = "Moje imię"
save_txt = "zapisz"
unknown_text = "brak"
remove_text = "Usuwanie"
type_remove_text = "usunięty"
none_text = "brak"

# zmienne globalne
new_barcode_list = []
restorage_values = ''
credentials_ok = False



def credentials():
    global credentials_ok
    creds = None

    # Spróbuj wczytać istniejące poświadczenia
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Sprawdź, czy poświadczenia są ważne, jeśli nie, odśwież lub utwórz nowe
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)

            # Zapisz poświadczenia dla następnego uruchomienia
            with open("token.json", "w") as token:
                token.write(creds.to_json())
                print('Zapis nowych poświadczeń')
            credentials_ok = True
        except Exception as e:
            print(f"Błąd przy odświeżaniu poświadczeń: {e}")
            # Usuń nieprawidłowy token i spróbuj ponownie
            if os.path.exists("token.json"):
                os.remove("token.json")
                print('Usunięcie tokena i onowne pobieranie poświadczeń.')
            return credentials()  # Rekurencyjne ponowne wywołanie funkcji

    return creds


creds = credentials()  # pobierz poświadczenia
service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()

# Funkcje pomocnicze
def get_sheet_id_by_name(sheet_name):
  """Zwraca sheetId dla danego sheet_name w dokumencie Google Sheets."""
  # Pobierz metadane dokumentu, które zawierają informacje o arkuszach.
  sheet_metadata = service.spreadsheets().get(spreadsheetId=DOCUMENT_ID).execute()
  sheets = sheet_metadata.get('sheets', '')
  # Znajdź arkusz o podanej nazwie i zwróć jego sheetId.
  for sheet in sheets:
    if sheet['properties']['title'] == sheet_name:
      return sheet['properties']['sheetId']

  return None  # Jeśli nie znajdzie arkusza o podanej nazwie, zwraca None.

def find_first_empty_row(sheet_name, column):
  # Funkcja do znajdowania pierwszego wolnego wiersza w danym arkuszu.
  column_range = f"{sheet_name}!{column}:{column}"
  column_data = sheet.values().get(
    spreadsheetId=DOCUMENT_ID, range=column_range
  ).execute()
  column_values = column_data.get("values", [])
  return len(column_values) + 1

def day_now():
    timezone = pytz.timezone('Europe/Warsaw')  # Przykład dla strefy czasowej Warszawy
    now = datetime.datetime.now(timezone)
    #return f'{now.day}-{str(now.month).zfill(2)}-{now.year}'
    return now.strftime('%Y-%m-%d')

def time_now():
    timezone = pytz.timezone('Europe/Warsaw')  # Przykład dla strefy czasowej Warszawy
    now = datetime.datetime.now(timezone)
    #return f'{now.hour}:{str(now.minute).zfill(2)}:{str(now.second).zfill(2)}'
    return now.strftime('%H:%M:%S')

def print_user_message(pole, komunikat):
  # Funkcja do dodawania komunikatów dla użytkownika w GUI
    pole.insert(tk.END, komunikat + "\n")
    pole.see(tk.END)  # Przewijanie do najnowszego komunikatu

def save_settings():
    """Funkcja zapisuje ustawienia do pliku"""
    global worker, localization
    name = my_name_entry.get()
    localization = my_localization_combobox.get()

    worker = name


    with open("user_settings.txt", "w") as file:
        file.write(f"Name: {name}\n")
        file.write(f"Localization: {localization}\n")

def load_settings():
    """Funkcja odczytuje ustawienia z pliku (o ile istnieje)
    i przypisuje je do odpowiednich zmiennych"""
    global worker, localization

    try:
        with open("user_settings.txt", "r") as file:
            lines = file.readlines()
            worker = lines[0].strip().split(": ")[1] if len(lines) > 0 else "nie znane"
            localization = lines[1].strip().split(": ")[1] if len(lines) > 1 else "nie znane"
    except FileNotFoundError:
        worker = unknown_text
        localization = unknown_text

    my_name_entry.delete(0, tk.END)  # Usuwa obecną zawartość pola
    my_name_entry.insert(0, worker)  # Wstawia wartość imienia do pola

    my_localization_combobox.set(localization)  # Ustawia wartość lokalizacji w combobox

class AutocompleteCombobox(ttk.Combobox):
    """Klasa służy do generowania combobox z autoumupełnianiem.
    Wpisuje kilka pierwszych liter i działają one jako filtr jeżeli rozwinę
    listę"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._complete_values = self['values']
        self.bind('<KeyRelease>', self._on_keyrelease)

    def _on_keyrelease(self, event):
        # Ignorowanie niektórych klawiszy
        if event.keysym in ("BackSpace", "Left", "Right", "Up", "Down", "Return", "Escape"):
            value = event.widget.get()
            if value == '':
                self['values'] = self._complete_values
                self.event_generate('<Escape>')  # Zamyka rozwijaną listę
            return

        value = event.widget.get()
        if value == '':
            self['values'] = self._complete_values
            self.event_generate('<Escape>')  # Zamyka rozwijaną listę
            return

        new_values = [val for val in self._complete_values if val.lower().startswith(value.lower())]
        self['values'] = new_values



# Funkcje do obsługi bazy danych (Google sheets)
def save_data(ID, Producent, Rozmiar, Nazwa, Kolor, Cena_netto):
  """
  Funkcja zapisuje produkt w arkuszu danych zdefiniowanym jako WAREHOUSE_SHEET
  oraz zapisuje logi w arkuszu LOGS_SHEET

  Parametry:
  ID (str)
  Producent (str)
  Rozmiar (str)
  Nazwa (str)
  Kolor (str)
  Cena_netto (int)

  """

  #creds = credentials()  # pobierz poświadczenia
  #service = build("sheets", "v4", credentials=creds)
  #sheet = service.spreadsheets()
  try:
    #service = build("sheets", "v4", credentials=creds)
    #sheet = service.spreadsheets()



    # Znajdź pierwszy wolny wiersz w arkuszu 'Magazyn'.
    first_empty_row_magazyn = find_first_empty_row(WAREHOUSE_SHEET,'A')

    # Znajdź pierwszy wolny wiersz w arkuszu 'Logi'.
    first_empty_row_logi = find_first_empty_row(LOGS_SHEET,'A')

    try: # Ustawia wartość 0.0 gdy podana cena jest nieprawodłowa
        cena_netto_float = float(str(Cena_netto).replace(',', '.'))
    except ValueError:
        cena_netto_float = 0.0
    values_to_save = [[ID, Producent, Rozmiar, Nazwa, Kolor, cena_netto_float, localization]]

    # Zapisz dane do arkusza 'Magazyn'.
    save_range_magazyn = f"{WAREHOUSE_SHEET}!A{first_empty_row_magazyn}:G{first_empty_row_magazyn}"
    data = {'values': values_to_save}
    sheet.values().update(
      spreadsheetId=DOCUMENT_ID,
      range=save_range_magazyn,
      valueInputOption="RAW",
      body=data
    ).execute()

    # Logowanie danych.
    save_range_logi = f"{LOGS_SHEET}!A{first_empty_row_logi}:K{first_empty_row_logi}"
    logs_to_save = [[day_now(), time_now(), ID, worker,new_product_text, Producent, Rozmiar, Nazwa, Kolor, cena_netto_float, localization]] #
    data_logs = {'values': logs_to_save}
    sheet.values().update(
      spreadsheetId=DOCUMENT_ID,
      range=save_range_logi,
      valueInputOption="RAW",
      body=data_logs
    ).execute()
    print_user_message(user_message, added_do_database_text + ' ID: ' + ID)

  except HttpError as err:
    print(err)

def find_data_by_id(search_id):
  """Przeszukuje arkusz danych w kolumnie A w poszukiwaniu podanego ID i zwraca cały wiersz od A do G, jeśli ID zostanie znalezione."""
  #creds = credentials() # pobierz poświadczenia
  # Logika pozyskiwania poświadczeń (taka sama jak w poprzednich funkcjach)...

  try:
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    # Pobierz wszystkie wartości z kolumny A.
    column_range = f"{WAREHOUSE_SHEET}!A:G"
    column_data = sheet.values().get(
      spreadsheetId=DOCUMENT_ID, range=column_range
    ).execute()
    rows = column_data.get("values", [])

    # Przeszukaj wiersze w poszukiwaniu podanego ID.
    for row in rows:
      if row[0] == search_id:
        return row  # Zwróć cały wiersz, jeśli ID zostanie znalezione.

    return None  # Zwróć None, jeśli ID nie zostanie znalezione.

  except HttpError as err:
    print(err)
    return None

def shipment(ship_id):
  """Usuwa wiersz z arkusza 'Magazyn' na podstawie ID i dodaje log do arkusza 'Logi'."""

  #creds = credentials()  # Pobierz poświadczenia

  try:
    # Logowanie danych.
    product_data = find_data_by_id(ship_id)
    if product_data != None: # zprawdzam czy produkt jest w bazie
      first_empty_row_logi = find_first_empty_row(LOGS_SHEET,'A')
      save_range_logi = f"{LOGS_SHEET}!A{first_empty_row_logi}:K{first_empty_row_logi}"

      try:  # Ustawia wartość 0.0 gdy podana cena jest nieprawodłowa
          cena_netto_float = float(str(product_data[5]).replace(',', '.'))
      except ValueError:
          cena_netto_float = 0.0

      logs_to_save = [
        [day_now(), time_now(), ship_id, worker, ship_text, product_data[1], product_data[2], product_data[3], product_data[4], cena_netto_float, localization]]
      data_logs = {'values': logs_to_save}
      sheet.values().update(
        spreadsheetId=DOCUMENT_ID,
        range=save_range_logi,
        valueInputOption="RAW",
        body=data_logs
      ).execute()

      # Znajdź i usuń wiersz z arkusza 'Magazyn'.
      warehouse_range = f"{WAREHOUSE_SHEET}!A:G"
      warehouse_data = sheet.values().get(
        spreadsheetId=DOCUMENT_ID, range=warehouse_range
      ).execute()
      warehouse_values = warehouse_data.get("values", [])

      row_to_delete = -1
      for i, row in enumerate(warehouse_values):
        if row[0] == ship_id:
          row_to_delete = i
          break

      if row_to_delete >= 0:
        # Usuń wiersz.
        batch_update_spreadsheet_request_body = {
          "requests": [
            {
              "deleteRange": {
                "range": {
                  "sheetId": get_sheet_id_by_name(WAREHOUSE_SHEET),  # potrzebujesz ID arkusza 'Magazyn'
                  "startRowIndex": row_to_delete,
                  "endRowIndex": row_to_delete + 1
                },
                "shiftDimension": "ROWS"
              }
            }
          ]
        }
        service.spreadsheets().batchUpdate(
          spreadsheetId=DOCUMENT_ID, body=batch_update_spreadsheet_request_body
        ).execute()
        # Komunikat przy wysyłce
        print_user_message(user_message_ship, f'{ship_text}: {logs_to_save[0][5]} {logs_to_save[0][6]} {logs_to_save[0][7]} {logs_to_save[0][8]}')
      else:
        print("ID nie znaleziono w arkuszu 'Magazyn'")
        #print_user_message(user_message_ship, no_found_id_text)
        return
    else:
      print('no ID')
      print_user_message(user_message_ship, no_found_id_text)
  except HttpError as err:
    print(err)

def remove(ship_id, reason = none_text):
  """Usuwa wiersz z arkusza 'Magazyn' na podstawie ID i dodaje log do arkusza 'Logi'."""

  #creds = credentials()  # Pobierz poświadczenia

  try:
    # Logowanie danych.
    product_data = find_data_by_id(ship_id)
    if product_data != None: # zprawdzam czy produkt jest w bazie
      first_empty_row_logi = find_first_empty_row(LOGS_SHEET,'A')
      save_range_logi = f"{LOGS_SHEET}!A{first_empty_row_logi}:L{first_empty_row_logi}"

      try:  # Ustawia wartość 0.0 gdy podana cena jest nieprawodłowa
          cena_netto_float = float(str(product_data[5]).replace(',', '.'))
      except ValueError:
          cena_netto_float = 0.0

      logs_to_save = [
        [day_now(), time_now(), ship_id, worker, type_remove_text, product_data[1], product_data[2], product_data[3], product_data[4], cena_netto_float, localization, reason]]
      data_logs = {'values': logs_to_save}
      sheet.values().update(
        spreadsheetId=DOCUMENT_ID,
        range=save_range_logi,
        valueInputOption="RAW",
        body=data_logs
      ).execute()

      # Znajdź i usuń wiersz z arkusza 'Magazyn'.
      warehouse_range = f"{WAREHOUSE_SHEET}!A:G"
      warehouse_data = sheet.values().get(
        spreadsheetId=DOCUMENT_ID, range=warehouse_range
      ).execute()
      warehouse_values = warehouse_data.get("values", [])

      row_to_delete = -1
      for i, row in enumerate(warehouse_values):
        if row[0] == ship_id:
          row_to_delete = i
          break

      if row_to_delete >= 0:
        # Usuń wiersz.
        batch_update_spreadsheet_request_body = {
          "requests": [
            {
              "deleteRange": {
                "range": {
                  "sheetId": get_sheet_id_by_name(WAREHOUSE_SHEET),  # potrzebujesz ID arkusza 'Magazyn'
                  "startRowIndex": row_to_delete,
                  "endRowIndex": row_to_delete + 1
                },
                "shiftDimension": "ROWS"
              }
            }
          ]
        }
        service.spreadsheets().batchUpdate(
          spreadsheetId=DOCUMENT_ID, body=batch_update_spreadsheet_request_body
        ).execute()
        # Komunikat przy wysyłce
        print_user_message(user_message_remove, f'{remove_text}: {logs_to_save[0][5]} {logs_to_save[0][6]} {logs_to_save[0][7]} {logs_to_save[0][8]}')
      else:
        print("ID nie znaleziono w arkuszu 'Magazyn'")
        #print_user_message(user_message_remove, no_found_id_text)
        return
    else:
      print('no ID')
      print_user_message(user_message_remove, no_found_id_text)
  except HttpError as err:
    print(err)


def change_localization(product_id, new_localization):
  #creds = credentials()  # Pobierz poświadczenia
  #service = build("sheets", "v4", credentials=creds)
  #sheet = service.spreadsheets()

  try:
    # Pobierz dane z arkusza 'Magazyn'.
    range_name = f"{WAREHOUSE_SHEET}!A:K"  # Zakładamy, że lokalizacja jest w kolumnie K.
    result = sheet.values().get(spreadsheetId=DOCUMENT_ID, range=range_name).execute()
    values = result.get('values', [])

    row_number = None
    for i, row in enumerate(values):
      if len(row) > 0 and row[0] == product_id:
        row_number = i + 1  # +1, ponieważ indeksowanie w arkuszu zaczyna się od 1, a w Pythonie od 0.
        break

    if row_number is None:
      print_user_message(user_message_restorage, no_ID_text)
      return

    # Aktualizuj lokalizację.
    update_range = f"{WAREHOUSE_SHEET}!G{row_number}"
    values = [[new_localization]]
    body = {'values': values}
    sheet.values().update(
      spreadsheetId=DOCUMENT_ID, range=update_range,
      valueInputOption="USER_ENTERED", body=body).execute()

    # Logowanie danych.
    product_data = find_data_by_id(product_id)
    first_empty_row_logi = find_first_empty_row(LOGS_SHEET,'A')
    save_range_logi = f"{LOGS_SHEET}!A{first_empty_row_logi}:K{first_empty_row_logi}"
    try:  # Ustawia wartość 0.0 gdy podana cena jest nieprawodłowa
        cena_netto_float = float(str(product_data[5]).replace(',', '.'))
    except ValueError:
        cena_netto_float = 0.0
    logs_to_save = [[day_now(), time_now(), product_id, worker,change_localization_text, product_data[1], product_data[2], product_data[3], product_data[4], cena_netto_float, new_localization]]
    data_logs = {'values': logs_to_save}
    sheet.values().update(
      spreadsheetId=DOCUMENT_ID,
      range=save_range_logi,
      valueInputOption="RAW",
      body=data_logs
    ).execute()

    print(f"Lokalizacja dla ID {product_id} została zmieniona na {new_localization}.")
    print_user_message(user_message_restorage, f'{change_localization_text}: {product_data[0]} {product_data[1]} {product_data[2]} {product_data[3]} {product_data[4]} {new_localization}')

  except HttpError as err:
    print(err)

def return_item(search_id):

  #creds = credentials()  # Pobierz poświadczenia
  #service = build("sheets", "v4", credentials=creds)
  #sheet = service.spreadsheets()
  found_ID_in_logs = False
  try:
    # Zdefiniuj zakres, który obejmuje całe arkusze.
    range_name = f"{LOGS_SHEET}!A:K"
    result = sheet.values().get(spreadsheetId=DOCUMENT_ID, range=range_name).execute()
    rows = result.get('values', [])
    # sprawdzam najpierw czy już nie ma w magazynie produktu
    if find_data_by_id(search_id) == None:
    # Przeszukaj wiersze w poszukiwaniu podanego ID.
        for row in rows:
          # Sprawdź, czy długość wiersza jest wystarczająca i czy kolumna C (indeks 2) zawiera ID.
          if len(row) > 2 and row[2] == search_id:
            found_ID_in_logs = True # flaga informująca, że produkt został znaleziony w logach
            # jeżeli znaleziono artykuł w logach to dopisz go do magazynu i go logów jako zwrot
            # dopisywanie artykułu:
            try:
              # Znajdź pierwszy wolny wiersz w arkuszu 'Magazyn'.
              first_empty_row_magazyn = find_first_empty_row(WAREHOUSE_SHEET,'A')
              # Znajdź pierwszy wolny wiersz w arkuszu 'Logi'.
              first_empty_row_logi = find_first_empty_row(LOGS_SHEET,'A')
              try:  # Ustawia wartość 0.0 gdy podana cena jest nieprawodłowa
                  cena_netto_float = float(str(row[9]).replace(',', '.'))
              except ValueError:
                  cena_netto_float = 0.0
              # Dane do zapisania.
              values_to_save = [[search_id, row[5], row[6], row[7], row[8], cena_netto_float, localization]]

              # Zapisz dane do arkusza 'Magazyn'.
              save_range_magazyn = f"{WAREHOUSE_SHEET}!A{first_empty_row_magazyn}:G{first_empty_row_magazyn}"
              data = {'values': values_to_save}
              sheet.values().update(
                spreadsheetId=DOCUMENT_ID,
                range=save_range_magazyn,
                valueInputOption="RAW",
                body=data
              ).execute()

              try:  # Ustawia wartość 0.0 gdy podana cena jest nieprawodłowa
                  cena_netto_float = float(str(row[9]).replace(',', '.'))
              except ValueError:
                  cena_netto_float = 0.0
              # Logowanie danych.
              save_range_logi = f"{LOGS_SHEET}!A{first_empty_row_logi}:K{first_empty_row_logi}"
              logs_to_save = [[day_now(), time_now(), search_id, worker, return_itme_text, row[5], row[6], row[7], row[8], cena_netto_float,
                               localization]]
              data_logs = {'values': logs_to_save}
              sheet.values().update(
                spreadsheetId=DOCUMENT_ID,
                range=save_range_logi,
                valueInputOption="RAW",
                body=data_logs
              ).execute()
              # wyświetl informację, że produkt wrócił do magazynu
              print_user_message(user_message_return, f'{product_text} ID: {search_id} {values_to_save[0][1]} '
                                                      f'{values_to_save[0][2]} {values_to_save[0][3]} '
                                                      f'{values_to_save[0][4]} {return_to_warehouse}')


            except HttpError as err:
              print(err)
            # koniec dopisywania artykułu
            break

        if found_ID_in_logs == False: #Jeśli ID nie zostanie znalezione, zwróć informację.
            print_user_message(user_message_return, f'ID: {search_id} {no_history_log_text}')
    else:
        print_user_message(user_message_return, f'ID: {search_id} {exists_in_warehouse}')
  except HttpError as err:
    print(err)
    return "Wystąpił błąd podczas dostępu do arkusza Google Sheets."

def read_definitions(sheet_name, column):
    """ Funcja pobiera z arkusza definicji wybraną kolumnę
    i zwraca wartosci zapisane w niej w w formie listy"""

    # Zakres, który chcesz pobrać (np. 'Definicje!A2:A')
    zakres = f'{sheet_name}!{column}2:{column}'

    # Pobieranie danych
    arkusz = service.spreadsheets()
    wynik = arkusz.values().get(spreadsheetId=DOCUMENT_ID, range=zakres).execute()
    wartosci = wynik.get('values', [])

    # Zwrócenie danych jako listy
    return [wiersz[0] for wiersz in wartosci if wiersz]  # Filtruje puste wiersze

# Funkcje obsługi skanera
""" Odczyt skanera jest uruchamiany w osobnym wątku
    Tak żeby działał niezależnie od programu wyświetlającego GUI.
    Kod skanera jest przechwycony na podstawie czasów wprowadzania
    znaków. Jeżeli znaki są wprowadzane z większą niż zdefiniowana czestotliwość
    to znaczy że jest to ciąg znaków ze skanera a nie z klawiatury"""
last_time = time.time()
barcode = ''
# Globalna zmienna flagowa
close_tread = False
def start_listener():
    global close_tread

    def on_press(key):
        global last_time, barcode
        current_time = time.time()
        if current_time - last_time > 0.5:  # Reset if delay between characters is too long
            barcode = ''
        if hasattr(key, 'char') and key.char:
            barcode += key.char
        last_time = current_time

    def on_release(key):
        global barcode
        if key == Key.enter and barcode:
            print(selected_tab)
            # Uruchomienie funkcji wysyłki towaru
            if selected_tab == ship_text:
                shipment(barcode)
            # Uruchomienie funkcji usunięcie towaru
            if selected_tab == remove_text:
                remove(barcode, remove_combobox.get())
            # Uruchomienie funkcji wysyłki towaru
            if selected_tab == change_localization_text:
                if len(restorage_combobox.get())>3:
                    change_localization(barcode, restorage_combobox.get())
                else:
                    print_user_message(user_message_restorage, no_data_to_restorage_text)
            # Uruchomienie funkcji zwrotu towaru do magazynu
            if selected_tab == returns_text:
                return_item(barcode)

            barcode = ''
        if key == Key.esc:
            return False

    # Listener
    with Listener(on_press=on_press, on_release=on_release) as listener:
        while True:
            if close_tread:
                print('Wątek zatrzymany')
                break
            time.sleep(0.1)
        listener.stop()

# Uruchomienie wątku
listener_thread = threading.Thread(target=start_listener)
listener_thread.start()


# Funkcja interfejsu uzytkownika
def stworz_okno():
    # Tworzenie głównego okna
    global okno
    okno = tk.Tk()
    okno.title("Simple Warehouse")
    okno.geometry("800x600")  # Ustawianie wymiarów okna

    # Tworzenie widżetu Notebook (zakładki)
    notebook = ttk.Notebook(okno)
    notebook.place(x=0, y=0, width=800, height=600)

    def active_tab_detection(event):
        """Funkcja do wykrywania aktywnej zakładki"""
        global selected_tab
        selected_tab = event.widget.tab(event.widget.index("current"), "text")



    # Zakładka Wprowadzanie produktu
    tab_input = tk.Frame(notebook, width=790, height=600)  # Ustawianie rozmiarów zakładki
    notebook.add(tab_input, text=input_item_text)
    # Tworzenie pola tekstowego do wyświetlania komunikatów
    user_message = tk.Text(tab_input, height=4)
    user_message.place(x=0, y=475, width=800, height=95)
    # Dodawanie elementów do zakładki Wprowadzanie produktu
    # Pole kodu kreskowego
    barcode_label = tk.Label(tab_input, text=barcode_text)
    barcode_label.place(x=20, y=20, width=120, height=20)
    barcode_entry = tk.Entry(tab_input)
    barcode_entry.place(x=149, y=20, width=201, height=22)

    def update_combobox(name_combobox, definitions_sheet, column):
        """Funckaj służy do aktualizacji listy wybieranej o nową wartość.
        Uruchamiana jest przez wciśnięcie przycisku +
        combobox_name: nazwa obiektu combobox
        definition_sheets: nazwa arkusza z definicjami
        column: litera kolumny w której są przechowywane wartości"""
        # 1. Dodaj wartość do listy w arkuszu definicji
        new_value = name_combobox.get()
        first_empty_row_def = find_first_empty_row(definitions_sheet,column)
        # Zapisz dane do arkusza 'Definicje'.
        save_range_def = f"{definitions_sheet}!{column}{first_empty_row_def}"
        data = {'values': [[new_value]]}  # Lista list, ponieważ Google Sheets oczekuje tego formatu
        sheet.values().update(
            spreadsheetId=DOCUMENT_ID,
            range=save_range_def,
            valueInputOption="RAW",  # Można użyć "USER_ENTERED" dla formatowania zgodnego z Google Sheets
            body=data
        ).execute()
        print_user_message(user_message, added_new_difinition_text)
        # 2. Odczytaj wartości z kolumny arkusza definicji
        new_values = read_definitions(definitions_sheet, column)  # Pobiera wartości z bazy danych
        # 3. Zaktualizuj combobox
        name_combobox.configure(values=new_values)

    # Pole wybrania marki
    brand_label = tk.Label(tab_input, text=brand_text)
    brand_label.place(x=20, y=45, width=120, height=20)
    brand_values = read_definitions(DEFINITION_SHEET, 'A') # Pobiera wartości z bazy danych
    brand_values.sort()
    brand_combobox = AutocompleteCombobox(tab_input, values=brand_values)
    brand_combobox.place(x=150, y=45, width=200, height=20)
    # Utworzenie przycisku dodawania marki do listy
    add_brand_button = tk.Button(tab_input, text="+", command= lambda: update_combobox(brand_combobox, DEFINITION_SHEET, 'A'))
    add_brand_button.place(x=370, y=46, width=20, height=20)

    # Pole wybrania rozmiaru
    size_label = tk.Label(tab_input, text=size_text)
    size_label.place(x=20, y=70, width=120, height=20)
    size_values = read_definitions(DEFINITION_SHEET, 'B')  # Pobiera wartości z bazy danych
    size_combobox = AutocompleteCombobox(tab_input, values=size_values)
    size_combobox.place(x=150, y=70, width=200, height=20)
    # Utworzenie przycisku dodawania rozmiaru do listy
    add_brand_button = tk.Button(tab_input, text="+",
                                 command=lambda: update_combobox(size_combobox, DEFINITION_SHEET, 'B'))
    add_brand_button.place(x=370, y=71, width=20, height=20)

    # Pole wybrania nazwy
    name_label = tk.Label(tab_input, text=name_text)
    name_label.place(x=20, y=95, width=120, height=20)
    name_values = read_definitions(DEFINITION_SHEET, 'C')  # Pobiera wartości z bazy danych
    name_values.sort()
    name_combobox = AutocompleteCombobox(tab_input, values=name_values)
    name_combobox.place(x=150, y=95, width=200, height=20)
    # Utworzenie przycisku dodawania nazwy do listy
    add_brand_button = tk.Button(tab_input, text="+",
                                 command=lambda: update_combobox(name_combobox, DEFINITION_SHEET, 'C'))
    add_brand_button.place(x=370, y=96, width=20, height=20)

    # Pole wybrania koloru
    color_label = tk.Label(tab_input, text=color_text)
    color_label.place(x=20, y=120, width=120, height=20)
    color_values = read_definitions(DEFINITION_SHEET, 'D')  # Pobiera wartości z bazy danych
    color_values.sort()
    color_combobox = AutocompleteCombobox(tab_input, values=color_values)
    color_combobox.place(x=150, y=120, width=200, height=20)
    # Utworzenie przycisku dodawania koloru do listy
    add_brand_button = tk.Button(tab_input, text="+",
                                 command=lambda: update_combobox(color_combobox, DEFINITION_SHEET, 'D'))
    add_brand_button.place(x=370, y=121, width=20, height=20)

    # Pole wpisania ceny
    price_label = tk.Label(tab_input, text=price_text)
    price_label.place(x=20, y=145, width=120, height=20)
    price_entry = tk.Entry(tab_input)
    price_entry.place(x=149, y=145, width=201, height=22)



    def add_data_to_sheet():
        """W zmiennej new_barcode_list przechowuje tymczasowo barkody,
        które załadowane są do arkusza tksheet do wprowadzania towarów.
        Później artykół, który chcę dodać do arkusza tksheet sprawdzam
        czy znajduje się na liście w celu zapobiegnięcia dodania dwóch
        artykułów do arkusza tksheet o tym samym numerze ID"""
        global new_barcode_list
        # Funkcja dodaje do arkusza tksheet nowy wiersz
        new_row = [barcode_entry.get(),
                   brand_combobox.get(),
                   size_combobox.get(),
                   name_combobox.get(),
                   color_combobox.get(),
                   price_entry.get()]
        if find_data_by_id(new_row[0]) == None and not new_row[0] in new_barcode_list:
            arkusz.insert_row(values=new_row, idx="end")  # Dodaje nowy wiersz na końcu arkusza
            print_user_message(user_message, added_to_list_text + ' ID: ' + str(new_row[0]))
            new_barcode_list.append(new_row[0]) # dodaje nowe ID do tymczasowej listy
        else:
            messagebox.showwarning(worning_text, ID_exists_text)

    # Utworzenie przycisku dodaj do listy
    add_to_list_button = tk.Button(tab_input, text=add_to_list_text, command=add_data_to_sheet)
    add_to_list_button.place(x=550, y=40, width=110, height=110)

    # Arkusz wprowadzonych danych:
    # Tworzenie arkusza
    arkusz = tksheet.Sheet(tab_input)
    arkusz.place(x=10, y=190, width=780, height=250)
    # Zdefiniowanie pierwszego wiersza
    data_head_insert_sheet = [["Id", brand_text, size_text,name_text, color_text, price_text],]
    # Ustawienie pierwszego wiersza
    arkusz.set_sheet_data(data_head_insert_sheet)
    # Funkcje umożliwiające edycję
    arkusz.enable_bindings(("single_select",  # kliknięcie wybiera komórkę
                            "drag_select",  # przeciąganie wybiera komórki
                            "column_drag_and_drop",
                            "row_drag_and_drop",
                            "column_select",
                            "row_select",
                            "column_width_resize",
                            "double_click_column_resize",
                            "row_width_resize",
                            "column_height_resize",
                            "arrowkeys",
                            "row_height_resize",
                            "double_click_row_resize",
                            "right_click_popup_menu",
                            "rc_select",
                            "rc_insert_row",
                            "rc_delete_row",
                            "rc_insert_column",
                            "rc_delete_column",
                            "copy",
                            "cut",
                            "paste",
                            "delete",
                            "undo",
                            "edit_cell"))

    def reed_from_input_sheet():
        global new_barcode_list
        # Funkcja pobiera dane z arkusza wprowadzania produktów
        # wysyła do bazy danych
        # i tworzy komunikat do okna dialogowego
        data_from_input_sheet = arkusz.get_sheet_data()
        for row in data_from_input_sheet[1:]:
            save_data(row[0], row[1], row[2], row[3], row[4], row[5])
        arkusz.set_sheet_data([data_head_insert_sheet[0]]) # czyści arkusz zostawiając tylko nagłówek
        print_user_message(user_message,added_do_database_all_text)
        new_barcode_list = [] # czyści tymczsową listę ID

    # Utworzenie przycisku Zatwierdź
    confirm_button = tk.Button(tab_input, text=confirm_text, command=reed_from_input_sheet)
    confirm_button.place(x=690, y=448, width=100, height=20)


    # Zakładka Wysyłka
    tab_ship = tk.Frame(notebook, width=790, height=500)
    notebook.add(tab_ship, text=ship_text)
    # Tworzenie pola tekstowego do wyświetlania komunikatów wysyłkowych
    global user_message_ship
    user_message_ship = tk.Text(tab_ship, height=4)
    user_message_ship.place(x=50, y=60, width=700, height=450)
    # Dodawanie elementów do zakładki Wysyłka
    # Pole kodu kreskowego
    barcode_label_ship = tk.Label(tab_ship, text=barcode_text)
    barcode_label_ship.place(x=20, y=20, width=120, height=20)
    barcode_entry_ship = tk.Entry(tab_ship)
    barcode_entry_ship.place(x=149, y=20, width=202, height=22)
    # Utworzenie przycisku Zatwierdź
    confirm_button_ship = tk.Button(tab_ship, text=confirm_text, command=lambda: shipment(barcode_entry_ship.get()))
    confirm_button_ship.place(x=400, y=20, width=100, height=22)

    # Zakładka Usunięcie produktu
    global remove_combobox
    tab_remove = tk.Frame(notebook, width=790, height=500)
    notebook.add(tab_remove, text=remove_text)
    # Tworzenie pola tekstowego do wyświetlania komunikatów wysyłkowych
    global user_message_remove
    user_message_remove = tk.Text(tab_remove, height=4)
    user_message_remove.place(x=50, y=160, width=700, height=350)
    # Dodawanie elementów do zakładki Wysyłka
    # Pole kodu kreskowego
    barcode_label_remove = tk.Label(tab_remove, text=barcode_text)
    barcode_label_remove.place(x=20, y=20, width=120, height=20)
    barcode_entry_remove = tk.Entry(tab_remove)
    barcode_entry_remove.place(x=149, y=20, width=202, height=22)
    # Utworzenie przycisku Zatwierdź
    confirm_button_remove = tk.Button(tab_remove, text=confirm_text, command=lambda: remove(barcode_entry_remove.get(), remove_combobox.get()))
    confirm_button_remove.place(x=400, y=20, width=100, height=22)
    # Pole wybrania powodu usunięcia
    remove_label = tk.Label(tab_remove, text=remove_text)
    remove_label.place(x=20, y=70, width=120, height=20)
    reason_removes = read_definitions(DEFINITION_SHEET, 'F')  # Pobiera wartości z bazy danych
    remove_combobox = AutocompleteCombobox(tab_remove, values=reason_removes)
    remove_combobox.place(x=150, y=70, width=200, height=20)
    # Utworzenie przycisku dodawania rozmiaru do listy
    add_remove_button = tk.Button(tab_remove, text="+",
                                 command=lambda: update_combobox(remove_combobox, DEFINITION_SHEET, 'F'))
    add_remove_button.place(x=370, y=71, width=20, height=20)


    # Zakładka Przemagazynowanie
    global restorage_combobox
    tab_restorage = tk.Frame(notebook, width=790, height=500)
    notebook.add(tab_restorage, text=change_localization_text)
    # Tworzenie pola tekstowego do wyświetlania komunikatów wysyłkowych
    global user_message_restorage
    user_message_restorage = tk.Text(tab_restorage, height=4)
    user_message_restorage.place(x=50, y=60, width=700, height=450)
    # Dodawanie elementów do zakładki Przemagazynowanie
    # Pole kodu kreskowego
    barcode_label_restorage = tk.Label(tab_restorage, text=barcode_text)
    barcode_label_restorage.place(x=35, y=20, width=50, height=20)
    barcode_entry_restorage = tk.Entry(tab_restorage)
    barcode_entry_restorage.place(x=80, y=20, width=202, height=22)
    # Pole Magazynu do którego nastąpi przemagazzynowanie
    destiny_label_restorage = tk.Label(tab_restorage, text=destiny_restorage_text)
    destiny_label_restorage.place(x=405, y=20, width=120, height=20)
    restorage_values = read_definitions(DEFINITION_SHEET, 'E')  # Pobiera wartości z bazy danych
    restorage_combobox = ttk.Combobox(tab_restorage, values=restorage_values, state='readonly')
    restorage_combobox.place(x=540, y=20, width=200, height=20)
    def apply_restorage(barcode, destiny):
        """Funkcja wywołująca funkcję przemagazynowania ale
        tylko gdy podane argumenty są prawidłowe"""
        if len(barcode)<3 or len(destiny)<3:
            messagebox.showwarning(worning_text, no_data_to_restorage_text)
        else:
            change_localization(barcode, destiny)
    # Utworzenie przycisku Zatwierdź
    confirm_button_restorage = tk.Button(tab_restorage, text=confirm_text,
                                         command=lambda: apply_restorage(barcode_entry_restorage.get(),restorage_combobox.get()))
    confirm_button_restorage.place(x=285, y=20, width=100, height=22)



    # Zakładka Zwroty
    tab_return = tk.Frame(notebook, width=790, height=500)
    notebook.add(tab_return, text=returns_text)
    # Tworzenie pola tekstowego do wyświetlania komunikatów wysyłkowych
    global user_message_return
    user_message_return = tk.Text(tab_return, height=4)
    user_message_return.place(x=50, y=60, width=700, height=450)
    # Dodawanie elementów do zakładki Wysyłka
    # Pole kodu kreskowego
    barcode_label_return = tk.Label(tab_return, text=barcode_text)
    barcode_label_return.place(x=20, y=20, width=120, height=20)
    barcode_entry_return = tk.Entry(tab_return)
    barcode_entry_return.place(x=149, y=20, width=202, height=22)
    # Utworzenie przycisku Zatwierdź
    confirm_button_return = tk.Button(tab_return, text=confirm_text, command=lambda: return_item(barcode_entry_return.get()))
    confirm_button_return.place(x=400, y=20, width=100, height=22)

    # Zakładka Ustawienia
    tab_settings= tk.Frame(notebook, width=790, height=500)
    notebook.add(tab_settings, text=settings_text)
    # Pole Imię
    global my_name_entry
    my_name_label = tk.Label(tab_settings, text=my_name_text)
    my_name_label.place(x=20, y=20, width=120, height=20)
    my_name_entry = tk.Entry(tab_settings)
    my_name_entry.place(x=149, y=20, width=202, height=22)
    # Pole wyboru mojej lokalizacji
    global my_localization_combobox
    my_localization_label = tk.Label(tab_settings, text=my_localization_text)
    my_localization_label .place(x=20, y=70, width=120, height=20)
    my_localization_values = read_definitions(DEFINITION_SHEET, 'E')  # Pobiera wartości z bazy danych
    my_localization_combobox = ttk.Combobox(tab_settings, values=my_localization_values)
    my_localization_combobox.place(x=150, y=70, width=200, height=20)
    # Dodanie przycisku do zapisywania ustawień
    save_button = tk.Button(tab_settings, text=save_txt, command=save_settings)
    save_button.place(x=20, y=120)


    # Dodanie obsługi zdarzenia wykrywającego aktywną zakładkę
    notebook.bind("<<NotebookTabChanged>>", active_tab_detection)



    # Obsługa zamnięcia okna programu
    # zamknięcie również wątku obsługi skanera
    def close_program():
        global close_tread
        okno.destroy()
        close_tread = True
    okno.protocol("WM_DELETE_WINDOW", close_program )

    return okno, user_message




# Uruchomienie aplikacji

if __name__ == "__main__":
    app, user_message = stworz_okno()
    load_settings()
    print_user_message(user_message, hello_text)
    app.mainloop()


#return_item("018")
#save_data('032', 'sroon', 'M', 'Dres', 'czerwony', 120.80)
#print(find_data_by_id('012'))
#shipment('018')
#change_localization('010', 'Łódź')

# notatki:
#
# Dla pola od barkodu. Jeżeli chcemy zmienić wartość w tym polu bo skaner coś odczytał to:
#def ustaw_wartosc(dane_ze_skanera):
  # Ustawia wartość w Entry
#  barcode_entry.delete(0, tk.END)
#  barcode_entry.insert(0, zmienna)
# Jeżeli chcemy zaczytać wartość widniejącą w polu tekstowym i
# w tym przykładzie wyprintować to:
#def obrob_wartosc():
  # Pobiera wartość z Entry i wyświetla ją (lub jakąkolwiek inną operację)
#  wprowadzona_wartosc = barcode_entry.get()
#  print("Wprowadzona wartość:", wprowadzona_wartosc)
