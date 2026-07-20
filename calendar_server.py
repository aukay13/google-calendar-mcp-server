import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from mcp.server.fastmcp import FastMCP

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

mcp = FastMCP("calendar-server")


def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


@mcp.tool()
def list_events(max_results: int = 10) -> str:
    """List upcoming events from the user's primary Google Calendar.

    Args:
        max_results: The maximum number of upcoming events to return. Defaults to 10.

    Returns:
        A newline-separated string listing each event's start time and title,
        or a message indicating no upcoming events were found.
    """
    creds = get_credentials()

    try:
        service = build("calendar", "v3", credentials=creds)

        now = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return "No upcoming events found."

        lines = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            lines.append(f"{start}  {event.get('summary', '(no title)')}")

        return "\n".join(lines)

    except HttpError as error:
        return f"An error occurred: {error}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
