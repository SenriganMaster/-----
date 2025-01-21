import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from ..google_calendar_service import (
    get_authenticated_service,
    add_event,
    update_event,
    delete_event,
    list_events,
    get_or_create_calendar,
    CALENDAR_NAME
)

@pytest.fixture
def mock_service():
    """Google Calendar APIサービスのモック"""
    service = MagicMock()
    
    # カレンダーリスト関連のモックを追加
    calendar_list = MagicMock()
    service.calendarList.return_value = calendar_list
    
    # イベント関連のモックを設定
    events = MagicMock()
    service.events.return_value = events
    
    return service

@pytest.fixture
def mock_withai_calendar():
    """WithAIカレンダーのモックデータ"""
    return {
        'id': 'withai_calendar_id',
        'summary': CALENDAR_NAME,
        'timeZone': 'Asia/Tokyo'
    }

@pytest.fixture
def sample_event():
    """テスト用のイベントデータ"""
    return {
        'title': 'テストミーティング',
        'start_datetime': '2024-03-20 15:00',
        'end_datetime': '2024-03-20 16:00',
        'detail': 'テスト用ミーティング'
    }

@pytest.fixture
def sample_google_event():
    """Google Calendar API形式のイベントデータ"""
    return {
        'id': 'test_event_id_1',
        'summary': 'テストミーティング',
        'description': 'テスト用ミーティング',
        'start': {
            'dateTime': '2024-03-20T15:00:00+09:00',
            'timeZone': 'Asia/Tokyo'
        },
        'end': {
            'dateTime': '2024-03-20T16:00:00+09:00',
            'timeZone': 'Asia/Tokyo'
        }
    }

def test_get_or_create_calendar_existing(mock_service, mock_withai_calendar):
    """既存のWithAIカレンダーを取得するテスト"""
    # モックの設定
    mock_service.calendarList.return_value.list.return_value.execute.return_value = {
        'items': [mock_withai_calendar]
    }
    
    # テスト実行
    calendar_id = get_or_create_calendar(mock_service)
    
    # 検証
    assert calendar_id == mock_withai_calendar['id']
    mock_service.calendarList.return_value.list.assert_called_once()
    mock_service.calendars.return_value.insert.assert_not_called()

def test_get_or_create_calendar_new(mock_service, mock_withai_calendar):
    """新規WithAIカレンダーを作成するテスト"""
    # モックの設定
    mock_service.calendarList.return_value.list.return_value.execute.return_value = {
        'items': []  # 既存のカレンダーなし
    }
    mock_service.calendars.return_value.insert.return_value.execute.return_value = mock_withai_calendar
    
    # テスト実行
    calendar_id = get_or_create_calendar(mock_service)
    
    # 検証
    assert calendar_id == mock_withai_calendar['id']
    mock_service.calendarList.return_value.list.assert_called_once()
    mock_service.calendars.return_value.insert.assert_called_once()

@patch('os.path.exists')
@patch('google.oauth2.credentials.Credentials.from_authorized_user_file')
@patch('my_calendar_app.google_calendar_service.build')
def test_get_authenticated_service(mock_build, mock_from_file, mock_exists):
    """認証サービスの取得テスト"""
    # モックの設定
    mock_exists.return_value = True  # token.jsonが存在する場合
    mock_creds = MagicMock()
    mock_creds.valid = True  # 有効な認証情報
    mock_from_file.return_value = mock_creds
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    # テスト実行
    result = get_authenticated_service()

    # 検証
    mock_exists.assert_called_once_with('token.json')
    mock_from_file.assert_called_once_with('token.json', ['https://www.googleapis.com/auth/calendar'])
    mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_creds)
    assert result == mock_service

def test_add_event(mock_service, sample_event, sample_google_event, mock_withai_calendar):
    """イベント追加のテスト"""
    # モックの設定
    mock_service.calendarList.return_value.list.return_value.execute.return_value = {
        'items': [mock_withai_calendar]
    }
    mock_service.events.return_value.insert.return_value.execute.return_value = sample_google_event

    # テスト実行
    result = add_event(
        mock_service,
        sample_event['start_datetime'],
        sample_event['end_datetime'],
        sample_event['title'],
        sample_event['detail']
    )

    # 検証
    assert result == sample_google_event
    mock_service.events.return_value.insert.assert_called_once()
    args, kwargs = mock_service.events.return_value.insert.call_args
    assert kwargs['calendarId'] == mock_withai_calendar['id']
    assert kwargs['body']['summary'] == sample_event['title']

def test_update_event(mock_service, sample_google_event, mock_withai_calendar):
    """イベント更新のテスト"""
    event_id = 'test_event_id'
    new_title = '更新後のミーティング'
    
    # モックの設定
    mock_service.calendarList.return_value.list.return_value.execute.return_value = {
        'items': [mock_withai_calendar]
    }
    mock_service.events.return_value.get.return_value.execute.return_value = sample_google_event.copy()
    mock_service.events.return_value.update.return_value.execute.return_value = {
        **sample_google_event,
        'summary': new_title
    }

    # テスト実行
    result = update_event(
        mock_service,
        event_id,
        new_title=new_title
    )

    # 検証
    assert result['summary'] == new_title
    mock_service.events.return_value.update.assert_called_once()
    args, kwargs = mock_service.events.return_value.update.call_args
    assert kwargs['calendarId'] == mock_withai_calendar['id']
    assert kwargs['eventId'] == event_id

def test_delete_event(mock_service, mock_withai_calendar):
    """イベント削除のテスト"""
    event_id = 'test_event_id'
    
    # モックの設定
    mock_service.calendarList.return_value.list.return_value.execute.return_value = {
        'items': [mock_withai_calendar]
    }
    
    # テスト実行
    delete_event(mock_service, event_id)

    # 検証
    mock_service.events.return_value.delete.assert_called_once()
    args, kwargs = mock_service.events.return_value.delete.call_args
    assert kwargs['calendarId'] == mock_withai_calendar['id']
    assert kwargs['eventId'] == event_id

def test_list_events(mock_service, sample_google_event, mock_withai_calendar):
    """イベント一覧取得のテスト"""
    # モックの設定
    mock_service.calendarList.return_value.list.return_value.execute.return_value = {
        'items': [mock_withai_calendar]
    }
    mock_service.events.return_value.list.return_value.execute.return_value = {
        'items': [sample_google_event]
    }

    # テスト実行
    start_date = '2024-03-01'
    end_date = '2024-03-31'
    events = list_events(mock_service, start_date, end_date)

    # 検証
    assert len(events) == 1
    assert events[0] == sample_google_event
    mock_service.events.return_value.list.assert_called_once()
    args, kwargs = mock_service.events.return_value.list.call_args
    assert kwargs['calendarId'] == mock_withai_calendar['id']
    assert kwargs['timeMin'] == f"{start_date}T00:00:00+09:00"
    assert kwargs['timeMax'] == f"{end_date}T23:59:59+09:00"

def test_list_events_empty(mock_service, mock_withai_calendar):
    """空のイベント一覧取得のテスト"""
    # モックの設定
    mock_service.calendarList.return_value.list.return_value.execute.return_value = {
        'items': [mock_withai_calendar]
    }
    mock_service.events.return_value.list.return_value.execute.return_value = {
        'items': []
    }

    # テスト実行
    events = list_events(mock_service)

    # 検証
    assert isinstance(events, list)
    assert len(events) == 0
    mock_service.events.return_value.list.assert_called_once()
    args, kwargs = mock_service.events.return_value.list.call_args
    assert kwargs['calendarId'] == mock_withai_calendar['id'] 