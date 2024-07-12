import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import base64
from email.mime.text import MIMEText
from langchain.agents import tool

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/gmail.send']

@tool
def authenticate():
    """
    Retrieves user credentials for accessing Google APIs.

    This function checks for existing credentials in a file named 'token.json'. If the credentials are found and valid, they are loaded. If the credentials are expired but can be refreshed, they are refreshed. If no valid credentials are found, the user is prompted to log in, and new credentials are saved to 'token.json'.

    Returns:
        creds: A Credentials object required for authenticating with Google APIs.

    Example:
        creds = get_credentials()
        if creds:
            print("Credentials obtained successfully")
        else:
            print("Failed to obtain credentials")
    """
    # SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
    SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/gmail.send']


    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_console()
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds.to_json()

@tool
def get_document(creds_json, document_id):
    """
    Retrieves a Google Document using the Google Docs API.
    Uses the output of the authenticate tool to authenticate with the Google Docs API.

    Args:
        creds_json: JSON string representing the Credentials object required for authenticating with the Google Docs API.
        document_id: String representing the unique ID of the Google Document to be retrieved.

    Returns:
        A dictionary containing the document's metadata and content if successful, None otherwise.
    """
    creds = Credentials.from_authorized_user_info(creds_json)

    try:
        service = build('docs', 'v1', credentials=creds)
        document = service.documents().get(documentId=document_id).execute()
        return document
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
    
@tool
def find_text_range(document, start_line, end_line):
    """
    Finds the start and end index of a specified range of lines in a Google Document.

    Args:
        document: A dictionary representing the Google Document, obtained via the Google Docs API.
        start_line: Integer representing the starting line number of the text range (0-indexed).
        end_line: Integer representing the ending line number of the text range (0-indexed).
    """
    start_index = None
    end_index = None
    line_counter = 0

    for element in document['body']['content']:
        if 'paragraph' in element:
            for paragraph_element in element['paragraph']['elements']:
                text_run = paragraph_element.get('textRun', {})
                if text_run:
                    content = text_run.get('content', '')
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line_counter == start_line:
                            start_index = paragraph_element['startIndex'] + sum(len(lines[j]) + 1 for j in range(i))
                        if line_counter == end_line:
                            end_index = paragraph_element['startIndex'] + sum(len(lines[j]) + 1 for j in range(i)) + len(line)
                            return start_index, end_index
                        line_counter += 1
    return start_index, end_index

@tool
def suggest_edit(creds, document_id, start_index, end_index, new_text):
    """
    Suggests an edit in a Google Document by replacing text within a specified range with new text.

    Args:
        creds: Credentials object required for authenticating with the Google Docs API.
        document_id: String representing the unique ID of the Google Document to be edited.
        start_index: Integer representing the starting character index of the text to be replaced.
        end_index: Integer representing the ending character index of the text to be replaced.
        new_text: String representing the new text to be inserted at the specified range.

    Returns:
        None if an error occurs; otherwise, prints the result of the suggested edit.
    """
    try:
        service = build('docs', 'v1', credentials=creds)
        requests = [
            {
                'deleteContentRange': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    }
                }
            },
            {
                'insertText': {
                    'location': {
                        'index': start_index
                    },
                    'text': new_text
                }
            }
        ]
        result = service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        print(f"Suggested edit applied: {result}")
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

@tool
def insert_comment(creds_json, file_id, content, anchor):
    """
    Inserts a comment into a Google Drive file.

    Args:
        creds: Credentials object required for authenticating with the Google Drive API.
        file_id: String representing the unique ID of the Google Drive file where the comment will be inserted.
        content: String representing the content of the comment to be inserted.
        anchor: String representing the anchor to which the comment is attached. This can specify the location in the file where the comment should appear.

    Returns:
        None if an error occurs; otherwise, prints the details of the inserted comment.
    """
    try:
        creds = Credentials.from_authorized_user_info(creds_json)

        service = build('drive', 'v3', credentials=creds)
        comment = {
            'content': content,
            'anchor': anchor
        }
        response = service.comments().create(
            fileId=file_id,
            body=comment,
            fields='id,content,createdTime,author,anchor'
        ).execute()
        print(f"Comment inserted: {response}")
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None  
    
@tool
def create_google_doc(creds_json: str, title: str, content: str) -> str:
    """
    Creates a new Google Doc with the specified title and content.

    Args:
        creds_json: JSON string representing the Credentials object required for authenticating with Google APIs.
        title: String representing the title of the new Google Document.
        content: String representing the content to be added to the new Google Document.

    Returns:
        A string containing the link to the newly created Google Document if successful, or an error message if unsuccessful.
    """
    try:
        # Parse the credentials JSON string
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_authorized_user_info(creds_dict)

        # Create Drive API service
        drive_service = build('drive', 'v3', credentials=creds)

        # Create Docs API service
        docs_service = build('docs', 'v1', credentials=creds)

        # Create a new Google Doc
        doc_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        doc = drive_service.files().create(body=doc_metadata).execute()
        doc_id = doc.get('id')

        # Add content to the new document
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1
                    },
                    'text': content
                }
            }
        ]
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

        # Generate the Google Docs link
        doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"

        return f"New Google Doc created successfully. You can access it here: {doc_link}"

    except HttpError as error:
        return f"An error occurred: {error}"
    except json.JSONDecodeError:
        return "Error: Invalid credentials JSON string"
    
@tool
def send_email(creds_json: str, to: str, subject: str, body: str) -> str:
    """
    Sends an email using the Gmail API.

    Args:
        creds_json: JSON string representing the Credentials object required for authenticating with Google APIs.
        to: Email address of the recipient.
        subject: Subject of the email.
        body: Body content of the email.

    Returns:
        A string confirming the email was sent or an error message if unsuccessful.
    """
    try:
        # Parse the credentials JSON string
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_authorized_user_info(creds_dict)

        # Create Gmail API service
        service = build('gmail', 'v1', credentials=creds)

        # Create the email message
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send the email
        send_message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()

        return f"Email sent successfully. Message Id: {send_message['id']}"

    except Exception as error:
        return f"An error occurred: {str(error)}"