from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
import os.path

SCOPES = ['https://www.googleapis.com/auth/calendar']  # 書き込み権限

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret_786062260954-g6bu62ippt09ljh2ll9ksf9rr27s4v2v.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def main():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    # ✅ 検索対象カレンダーのリスト
    calendar_ids = [
        '70ae7cc54fb7d0f2721fe617f26c2baf05cac34711cc7b7f9cd520167b6ce6cb@group.calendar.google.com',
        '2o5suvn6j21dvm4u23jqmgs8nc@group.calendar.google.com',
        'c_1cb8ae71bd956592935f22f3a4b9bbcf117b442158fe501c5343a46e38f2dee1@group.calendar.google.com'
    ]

    query = '高尾'
    now = datetime.datetime.now().isoformat() + 'Z'

    for calendar_id in calendar_ids:
        print(f"\n📅 カレンダー: {calendar_id}")
        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime',
                q=query
            ).execute()
            events = events_result.get('items', [])

            if not events:
                print('🔍 一致する予定は見つかりませんでした。')
                continue

            for event in events:
                start = event['start']
                end = event['end']
                summary = event.get('summary', '無題イベント')

                # ✅ 自分のカレンダーにコピー
                new_event = {
                    'summary': f"[コピー] {summary}",
                    'start': start,
                    'end': end,
                    'description': f"元カレンダー: {calendar_id}"
                }

                created_event = service.events().insert(
                    calendarId='primary',
                    body=new_event
                ).execute()

                print(f"✅ 追加: {created_event.get('summary')} → {created_event.get('htmlLink')}")

        except Exception as e:
            print(f"⚠️ エラー（{calendar_id}）: {e}")

if __name__ == '__main__':
    main()
