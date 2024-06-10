# Simple Warehouse Application Documentation

## Overview
The Simple Warehouse application is a desktop tool for managing a product warehouse, using Google Sheets as a database. The application allows adding new products, shipping products, relocating products within the warehouse, and managing returns. Additionally, it logs all operations in the sheet for tracking purposes. More about the application can be found at: [Simple Warehouse](https://www.linkedin.com/posts/damian-urba%C5%84ski-2a6976282_simplewarehouse-ecommercesolutions-inventorymanagement-activity-7157457285722587136-nqh1?utm_source=share&utm_medium=member_desktop)

## Program Features
- **Product Introduction**: Adding new products to the warehouse.
- **Shipping**: Recording and managing product shipments.
- **Relocation**: Changing the location of products within the warehouse.
- **Return Acceptance**: Managing product returns.
- **Settings**: Customizing user settings such as name and location.
- **Barcode Scanner Integration**: Automatic detection and handling of barcode scans.
- **Autocomplete**: Enhancing user data entry with autocomplete functionality for various fields.

## Installation
- **Cloning the Repository**: Clone the application repository from the version control system.
- **Dependencies**: Ensure all required dependencies are installed:
```google-auth```
```google-auth-oauthlib```
```google-auth-httplib2```
```google-api-python-client```
```tkinter```
```tksheet```
```pynput```
- **Google API Credentials**: Obtain Google API credentials and place the `credentials.json` file in the application directory.
- **Token File**: If available, place the `token.json` file in the application directory to use existing Google credentials.

## Configuration
- **Google Sheets API**:
  - Ensure the Google Sheets API is enabled for your project.
  - Obtain the spreadsheet ID for the Google Sheets document and update the `DOCUMENT_ID` constant in the script.

## Defined Functions
- **Obtaining Credentials**
The `credentials` function handles user authentication and obtaining credentials for using the Google Sheets API.

- **Getting Sheet ID**
The `get_sheet_id_by_name(sheet_name)` function returns the ID of the sheet with the given name.

- **Finding the First Empty Row**
The `find_first_empty_row(sheet_name, column)` function finds the first empty row in the given sheet and column.

- **Getting Current Date and Time**
The `day_now()` and `time_now()` functions return the current date and time in the Warsaw time zone.

- **Displaying User Messages**
The `print_user_message(widget, message)` function displays messages for the user in the GUI.

- **Saving Settings**
The `save_settings()` function saves user settings to a file.

- **Loading Settings**
The `load_settings()` function loads user settings from a file and assigns them to the respective variables.

- **Autocomplete in Combobox**
The `AutocompleteCombobox` class extends the functionality of the combobox with autocomplete.

- **Saving Product Data**
The `save_data(ID, Brand, Size, Name, Color, Price_net)` function saves product data to the warehouse sheet and logs.

- **Searching Data by ID**
The `find_data_by_id(search_id)` function searches the data sheet in column A for the given ID and returns the entire row if found.

- **Product Shipping**
The `shipment(ship_id)` function removes a row from the warehouse sheet based on the ID and logs the action in the logs sheet.

- **Removing Product**
The `remove(ship_id, reason=none_text)` function removes a row from the warehouse sheet based on the ID and logs the action in the logs sheet.

- **Changing Product Location**
The `change_localization(product_id, new_localization)` function changes the location of a product in the warehouse sheet and logs the action.

- **Returning Product**
The `return_item(search_id)` function returns an item to the warehouse based on its ID and logs the action.

- **Reading Definitions**
The `read_definitions(sheet_name, column)` function reads a column from the definitions sheet and returns the values as a list.

- **Barcode Scanner Handling - Scanner Listener**
Barcode scanner handling is implemented in a separate thread to operate independently of the GUI. The `start_listener()` function starts a listener that recognizes keyboard inputs and interprets them as barcode scans.

- **Creating the Window**
The `create_window()` function creates the main application window and tabs for various functions.

- **Application Initialization**
In the main part of the script, the application is initialized, user settings are loaded, and the listener thread for the barcode scanner is started. Finally, the main application loop `app.mainloop()` is launched.
