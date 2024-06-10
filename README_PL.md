# Dokumentacja Aplikacji Simple Warehouse

## Przegląd
Aplikacja Simple Warehouse to narzędzie desktopowe służące do zarządzania magazynem produktów, wykorzystujące Arkusze Google jako bazę danych. Aplikacja umożliwia dodawanie nowych produktów, wysyłkę produktów, relokację produktów w magazynie oraz zarządzanie zwrotami. Ponadto loguje wszystkie operacje w arkuszu dla celów śledzenia.

## Funkcje programu
- Wprowadzenie Produktu: Dodawanie nowych produktów do magazynu.
- Wysyłka: Rejestrowanie i zarządzanie wysyłkami produktów.
- Relokacja: Zmiana lokalizacji produktów w magazynie.
- Akceptacja Zwrotów: Zarządzanie zwrotami produktów.
- Ustawienia: Dostosowywanie ustawień użytkownika, takich jak imię i lokalizacja.
- Integracja ze skanerem kodów kreskowych: Automatyczne wykrywanie i obsługa skanów kodów kreskowych.
- Autouzupełnianie: Ulepszanie wprowadzania danych przez użytkownika dzięki funkcji autouzupełniania dla różnych pól.

## Instalacja
Klonowanie Repozytorium:<br> Sklonuj repozytorium aplikacji z systemu kontroli wersji.
Zależności: Upewnij się, że wszystkie wymagane zależności są zainstalowane: <br>
```google-auth```<br>
```google-auth-oauthlib```<br>
```google-auth-httplib2```<br>
```google-api-python-client```<br>
```tkinter```<br>
```tksheet```<br>
```pynput```<br>
Poświadczenia Google API: <br>
Uzyskaj poświadczenia Google API i umieść plik credentials.json w katalogu aplikacji.
Plik Tokena: Jeśli dostępny, umieść plik token.json w katalogu aplikacji, aby skorzystać z istniejących poświadczeń Google.
Konfiguracja
API Arkuszy Google:
Upewnij się, że API Arkuszy Google jest włączone dla Twojego projektu.
Uzyskaj identyfikator arkusza kalkulacyjnego dla dokumentu Arkuszy Google i zaktualizuj stałą DOCUMENT_ID w skrypcie.<br>
## Zdefiniowane funkcje
- Uzyskiwanie poświadczeń
Funkcja credentials obsługuje uwierzytelnianie użytkownika i uzyskiwanie poświadczeń do korzystania z API Arkuszy Google.

- Uzyskiwanie identyfikatora arkusza
Funkcja get_sheet_id_by_name(sheet_name) zwraca identyfikator arkusza o podanej nazwie.

- Znajdowanie pierwszego pustego wiersza
Funkcja find_first_empty_row(sheet_name, column) znajduje pierwszy pusty wiersz w danym arkuszu i kolumnie.

- Uzyskiwanie bieżącej daty i godziny
Funkcje day_now() i time_now() zwracają bieżącą datę i godzinę w strefie czasowej Warszawy.

- Wyświetlanie komunikatów użytkownika
Funkcja print_user_message(widget, message) wyświetla komunikaty dla użytkownika w interfejsie GUI.

- Zapisywanie ustawień
Funkcja save_settings() zapisuje ustawienia użytkownika do pliku.

- Wczytywanie ustawień
Funkcja load_settings() wczytuje ustawienia użytkownika z pliku i przypisuje je do odpowiednich zmiennych.

- Autouzupełnianie w comboboxie
Klasa AutocompleteCombobox rozszerza funkcjonalność comboboxa o autouzupełnianie.

- Zapisywanie danych produktu
Funkcja save_data(ID, Brand, Size, Name, Color, Price_net) zapisuje dane produktu do arkusza magazynowego i logów.

- Wyszukiwanie danych według ID
Funkcja find_data_by_id(search_id) przeszukuje arkusz danych w kolumnie A w poszukiwaniu podanego ID i zwraca cały wiersz, jeśli zostanie znaleziony.

- Przesyłka produktu
Funkcja shipment(ship_id) usuwa wiersz z arkusza magazynowego na podstawie ID i loguje tę akcję w arkuszu logów.

- Usuwanie produktu
Funkcja remove(ship_id, reason=none_text) usuwa wiersz z arkusza magazynowego na podstawie ID i loguje tę akcję w arkuszu logów.

- Zmiana lokalizacji produktu
Funkcja change_localization(product_id, new_localization) zmienia lokalizację produktu w arkuszu magazynowym i loguje tę akcję.

- Zwracanie produktu
Funkcja return_item(search_id) zwraca produkt do magazynu na podstawie jego ID i loguje tę akcję.

- Odczytywanie definicji
Funkcja read_definitions(sheet_name, column) odczytuje kolumnę z arkusza definicji i zwraca wartości jako listę.

- Obsługa skanera kodów kreskowych
Obsługa skanera kodów kreskowych jest realizowana w osobnym wątku, aby działała niezależnie od interfejsu GUI.

- Nasłuchiwanie skanera
Funkcja start_listener() uruchamia nasłuchiwacz, który rozpoznaje wprowadzenia z klawiatury i interpretuje je jako skany kodów kreskowych.

- Interfejs Użytkownika
Tworzenie Okna
Funkcja create_window() tworzy główne okno aplikacji oraz zakładki dla różnych funkcji.

- Inicjalizacja Aplikacji
W głównej części skryptu inicjalizowana jest aplikacja, wczytywane są ustawienia użytkownika, a także uruchamiany jest wątek nasłuchujący dla skanera kodów kreskowych. Na końcu uruchamiana jest główna pętla aplikacji app.mainloop().
