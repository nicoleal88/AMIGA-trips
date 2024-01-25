import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1YhJjQ8S2XnuOCl-9dg6187vChm0nUYG4UjBj1_vtNVA"
SAMPLE_RANGE_NAME = "Respuestas de formulario 1!A1:D"


def main():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
        .execute()
    )
    values = result.get("values", [])

    if not values:
      print("No data found.")
      return
    
    # print(values)
    
    # print("Name, Major:")
    for row in values:
      if (row[0] != ""):
        date = row[0].split(" ")[-1]
        newdate = date.split("-")
        date = newdate[2] + "-" + newdate[1] + "-" + newdate[0]
        id = row[2].split("=")[1][:-1]
        filename = date + "_" + id + ".md"
        content = row[1]
        path = "../src/pages/trips/" + filename
        # print(path)

        md_content = content
        # Extract data from the original Markdown content
        extracted_data = extract_data(md_content)
        # print(extracted_data)
        if extracted_data:
          # Generate the new Markdown content
          new_md_content = generate_new_md(extracted_data, md_content)

          # Write the new content to a new Markdown file
          with open(path, "w", encoding="utf-8") as output_file:
              output_file.write(new_md_content)
        else:
          print("Data extraction failed.")
        # with open(path, 'w') as file:
        #   file.write(content)
      else:
        print("Empty filename")
    #   print (row[1])
    #   print("--------------")
      # Print columns A and E, which correspond to indices 0 and 4.
      # print(f"{row[0]}, {row[1]}")
      pass
  except HttpError as err:
    print(err)

def extract_data(md_content):
    # Define a regular expression pattern to extract relevant information
    pattern = r"# ([\w\s.]+) \(id=(\d+)\) - (\w+ \d+/\d+/\d+)"
    match = re.search(pattern, md_content)

    if match:
        position, id, date = match.groups()
        team_pattern = r"Team: (.+)"
        team_match = re.search(team_pattern, md_content)
        team = team_match.group(1).split(', ')

        report_pattern = r"Reporta: (.+)"
        report_match = re.search(report_pattern, md_content)
        report = report_match.group(1)

        # Extract information from "## Tipo de salida: Mantenimiento general"
        type_pattern = r"## Tipo de salida: (.+)"
        type_match = re.search(type_pattern, md_content)
        salida_type = type_match.group(1).title()  # Capitalize the first letter of each word

        return {
            "position": position,
            "id": id,
            "date": date,
            "team": team,
            "report": report,
            "type": salida_type
        }

    return None

def generate_new_md(data, md_content):
    frontmatter = f"---\nposition: \"{data['position']}\"\nid: {data['id']}\ndate: \"{data['date']}\"\nteam: {data['team']}\nreport: \"{data['report']}\"\ntype: \"{data['type']}\"\n---\n\n"

    new_md_content = frontmatter + md_content

    return new_md_content


if __name__ == "__main__":
  main()