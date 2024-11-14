from requests.auth import HTTPBasicAuth
import requests
import json
from pypdf import PdfReader, PdfWriter
import pandas as pd
import mimetypes
import time
from selenium.webdriver.common.by import By

def click_button(xpath, driver, timeout=None):
    start_time = time.time()
    while True:
        try:
            button = driver.find_element(By.XPATH, xpath)
            button.click()
            break
        except Exception as e:
            if timeout is not None:
                if (time.time() - start_time) > timeout:
                    print(f'Error clicking button: {e}')
                    break


def send_text(text, xpath, driver, timeout=None):
    start_time = time.time()
    while True:
        try:
            box = driver.find_element(By.XPATH, xpath)
            box.send_keys(text)
            break
        except Exception as e:
            if timeout is not None:
                if (time.time() - start_time) > timeout:
                    print(f'Error sending text: {e}')
                    break

def switch_to_iframe(xpath, driver, timeout=None):
    start_time = time.time()
    while True:
        try:
            iframe = driver.find_element(By.XPATH, xpath)
            driver.switch_to.frame(iframe)
            break
        except Exception as e:
            if timeout is not None:
                if (time.time() - start_time) > timeout:
                    print(f'Error clicking button: {e}')
                    break

def switch_to_default_frame(driver):
    driver.switch_to.default_content()

def refresh_quickbooks_access_token(QUICKBOOKS_TOKENS, QUICKBOOKS_CLIENT_ID, QUICKBOOKS_CLIENT_SECRET):

    # QuickBooks Online OAuth2 token endpoint
    token_url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'

    # Prepare the request payload
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': QUICKBOOKS_TOKENS['refreshToken'],
    }

    # Make the request to get a new access token
    response = requests.post(
        token_url,
        data=payload,
        auth=HTTPBasicAuth(QUICKBOOKS_CLIENT_ID, QUICKBOOKS_CLIENT_SECRET),
        headers={'Accept': 'application/json'},
    )

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        new_tokens = response.json()
        QUICKBOOKS_TOKENS['accessToken'] = new_tokens.get('access_token')
        QUICKBOOKS_TOKENS['refreshToken'] = new_tokens.get('refresh_token')
        print('TOKENS REFRESHED SUCCESSFULLY')
        # print(json.dumps(new_tokens,indent=2))
    else:
        # Handle errors
        print(f"FAILED TO REFRESH TOKENS: {response.status_code}")
        #print(response.json())
    return QUICKBOOKS_TOKENS


def get_pdf(filepath):
    reader = PdfReader(filepath)

    fields = reader.get_fields()

    field_names = []
    field_types = []
    field_values = []

    for field_name, field in fields.items():
        field_type = field.get('/FT', '')
        field_value = field.get('/V', '')

        field_names.append(field_name)
        field_types.append(field_type)
        field_values.append(field_value)

    df = pd.DataFrame(columns=['name', 'type', 'value'])
    df['name'] = field_names
    df['type'] = field_types
    df['value'] = field_values
    return df

def create_pdf(templatepath, topath, update_dict):
    # Open the PDF
    reader = PdfReader(templatepath)
    writer = PdfWriter()
    writer.append(reader)

    # Write data to each page in the PDF file
    pagenum = 0
    while True:
        try:
            writer.update_page_form_field_values(writer.pages[pagenum], update_dict)
            pagenum = pagenum + 1
        except Exception: # An exception is raised when the pagenum exceeds the number of pages in the PDF document. When that happens, we are done adding data to the PDF file so we break out of this while loop.
            break

    # Save the updated PDF
    with open(topath, "wb") as pdf_output:
        writer.write(pdf_output)

# Add attachment to a GMAIL email

def add_attachment(path_to_file, message):

    if '/' in path_to_file:
        filename = path_to_file.split('/')[-1]
    if '\\' in path_to_file:
        filename = path_to_file.split('\\')[-1]

    mime_type, _ = mimetypes.guess_type(path_to_file)
    mime_type, mime_subtype = mime_type.split('/')
    with open(path_to_file, 'rb') as file:
        message.add_attachment(file.read(), maintype=mime_type, subtype=mime_subtype, filename=filename)
    return message