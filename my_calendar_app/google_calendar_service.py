import os
from typing import List, Dict, Optional
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

# 必要なスコープを定義
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_NAME = 'WithAI'

# 定期イベントのパターン定義
RECURRENCE_PATTERNS = {
    'daily': 'RRULE:FREQ=DAILY',
    'weekly': 'RRULE:FREQ=WEEKLY',
    'monthly': 'RRULE:FREQ=MONTHLY',
    'weekday': 'RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR'
}

def get_or_create_calendar(service) -> str:
    """
    'WithAI'カレンダーを取得または作成する
    
    Returns:
        str: カレンダーID
    """
    # 既存のカレンダーリストを取得
    calendar_list = service.calendarList().list().execute()
    
    # WithAIカレンダーを探す
    for calendar_list_entry in calendar_list['items']:
        if calendar_list_entry['summary'] == CALENDAR_NAME:
            return calendar_list_entry['id']
    
    # なければ新規作成
    calendar = {
        'summary': CALENDAR_NAME,
        'timeZone': 'Asia/Tokyo'
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar['id']

def get_authenticated_service() -> any:
    """
    Google Calendar APIの認証済みサービスを取得

    Returns:
        service: 認証済みのGoogle Calendar APIサービスインスタンス
    """
    creds = None
    # token.jsonが存在する場合は、それを使用
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # 有効な認証情報がない場合は、取得する
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 認証情報をtoken.jsonに保存
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Google Calendar APIのサービスを構築
    service = build('calendar', 'v3', credentials=creds)
    return service

def add_event(service: any, start_datetime_str: str, end_datetime_str: str, title: str, 
              detail: Optional[str] = None, calendar_id: Optional[str] = None,
              recurrence: Optional[str] = None) -> Dict:
    """
    Google Calendarに新しいイベントを追加

    Args:
        service: Google Calendar APIサービスインスタンス
        start_datetime_str: 開始日時 (例: "2024-03-20 15:00")
        end_datetime_str: 終了日時 (例: "2024-03-20 16:00")
        title: イベントのタイトル
        detail: イベントの詳細説明（オプション）
        calendar_id: カレンダーID（オプション）
        recurrence: 定期イベントのパターン（'daily', 'weekly', 'monthly', 'weekday'）

    Returns:
        Dict: 作成されたイベントの情報
    """
    if calendar_id is None:
        calendar_id = get_or_create_calendar(service)

    # 日時文字列をGoogle Calendar API形式に変換
    start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")
    end_datetime = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M")

    event = {
        'summary': title,
        'description': detail if detail else '',
        'start': {
            'dateTime': start_datetime.strftime("%Y-%m-%dT%H:%M:00+09:00"),
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': end_datetime.strftime("%Y-%m-%dT%H:%M:00+09:00"),
            'timeZone': 'Asia/Tokyo',
        },
    }

    # 定期イベントの設定
    if recurrence and recurrence in RECURRENCE_PATTERNS:
        event['recurrence'] = [RECURRENCE_PATTERNS[recurrence]]

    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return event

def update_event(service: any, event_id: str, new_title: Optional[str] = None,
                new_start_datetime: Optional[str] = None, new_end_datetime: Optional[str] = None,
                new_detail: Optional[str] = None, calendar_id: Optional[str] = None,
                new_recurrence: Optional[str] = None) -> Dict:
    """
    既存のイベントを更新

    Args:
        service: Google Calendar APIサービスインスタンス
        event_id: 更新対象のイベントID
        new_title: 新しいタイトル（オプション）
        new_start_datetime: 新しい開始日時（オプション）
        new_end_datetime: 新しい終了日時（オプション）
        new_detail: 新しい詳細説明（オプション）
        calendar_id: カレンダーID（オプション）
        new_recurrence: 新しい定期イベントのパターン（オプション）

    Returns:
        Dict: 更新されたイベントの情報
    """
    if calendar_id is None:
        calendar_id = get_or_create_calendar(service)

    # 現在のイベント情報を取得
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

    # 更新する項目を設定
    if new_title:
        event['summary'] = new_title
    if new_detail:
        event['description'] = new_detail
    if new_start_datetime:
        start_datetime = datetime.strptime(new_start_datetime, "%Y-%m-%d %H:%M")
        event['start']['dateTime'] = start_datetime.strftime("%Y-%m-%dT%H:%M:00+09:00")
    if new_end_datetime:
        end_datetime = datetime.strptime(new_end_datetime, "%Y-%m-%d %H:%M")
        event['end']['dateTime'] = end_datetime.strftime("%Y-%m-%dT%H:%M:00+09:00")
    if new_recurrence:
        if new_recurrence in RECURRENCE_PATTERNS:
            event['recurrence'] = [RECURRENCE_PATTERNS[new_recurrence]]
        elif new_recurrence == 'none':
            event.pop('recurrence', None)

    # イベントを更新
    updated_event = service.events().update(
        calendarId=calendar_id,
        eventId=event_id,
        body=event
    ).execute()

    return updated_event

def delete_event(service: any, event_id: str, calendar_id: Optional[str] = None) -> None:
    """
    イベントを削除

    Args:
        service: Google Calendar APIサービスインスタンス
        event_id: 削除対象のイベントID
        calendar_id: カレンダーID（オプション）
    """
    if calendar_id is None:
        calendar_id = get_or_create_calendar(service)

    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

def list_events(service: any, start_date: Optional[str] = None, end_date: Optional[str] = None, calendar_id: Optional[str] = None) -> List[Dict]:
    """
    イベント一覧を取得

    Args:
        service: Google Calendar APIサービスインスタンス
        start_date: 取得開始日（例: "2024-03-01"）
        end_date: 取得終了日（例: "2024-03-31"）
        calendar_id: カレンダーID（オプション）

    Returns:
        List[Dict]: イベントのリスト
    """
    if calendar_id is None:
        calendar_id = get_or_create_calendar(service)

    # 検索条件を設定
    params = {
        'calendarId': calendar_id,
        'orderBy': 'startTime',
        'singleEvents': True,
    }

    if start_date:
        params['timeMin'] = f"{start_date}T00:00:00+09:00"
    if end_date:
        params['timeMax'] = f"{end_date}T23:59:59+09:00"

    # イベントを取得
    events_result = service.events().list(**params).execute()
    return events_result.get('items', []) 