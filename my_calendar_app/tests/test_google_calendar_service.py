import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from ..google_calendar_service import (
    get_authenticated_service,
    add_event,
    update_event,
    delete_event,
    list_events
)

@pytest.fixture
def mock_credentials():
    """認証情報のモック"""
    return Mock()

@pytest.fixture
def mock_service():
    """Google Calendar APIサービスのモック"""
    service = Mock()
    # events()メソッドのモックを作成
    events = Mock()
    service.events = Mock(return_value=events)
    return service

@pytest.fixture
def sample_google_event():
    """Google Calendar APIの形式に合わせたイベントデータ"""
    return {
        'id': 'test_event_id_1',
        'summary': 'テストミーティング',
        'description': 'テスト用ミーティング',
        'start': {
            'dateTime': '2024-03-20T15:00:00+09:00',
        },
        'end': {
            'dateTime': '2024-03-20T16:00:00+09:00',
        }
    }

def test_get_authenticated_service(mock_credentials):
    """認証サービスの取得テスト"""
    with patch('google.oauth2.credentials.Credentials.from_authorized_user_file', return_value=mock_credentials):
        with patch('googleapiclient.discovery.build') as mock_build:
            mock_build.return_value = Mock()
            service = get_authenticated_service()
            assert service is not None
            mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_credentials)

def test_add_event(mock_service, sample_event):
    """イベント追加のテスト"""
    # モックの設定
    mock_service.events().insert().execute.return_value = {
        'id': 'new_event_id',
        'summary': sample_event['title'],
        'start': {'dateTime': f"{sample_event['start_datetime']}:00+09:00"},
        'end': {'dateTime': f"{sample_event['end_datetime']}:00+09:00"},
        'description': sample_event.get('detail', '')
    }

    # テスト実行
    result = add_event(
        mock_service,
        sample_event['start_datetime'],
        sample_event['end_datetime'],
        sample_event['title'],
        sample_event.get('detail')
    )

    # 検証
    assert result['id'] == 'new_event_id'
    assert result['summary'] == sample_event['title']
    mock_service.events().insert.assert_called_once()

def test_update_event(mock_service, sample_event):
    """イベント更新のテスト"""
    event_id = 'test_event_id'
    new_title = '更新後のミーティング'
    
    # モックの設定
    mock_service.events().get().execute.return_value = sample_google_event
    mock_service.events().update().execute.return_value = {
        'id': event_id,
        'summary': new_title,
        'start': {'dateTime': f"{sample_event['start_datetime']}:00+09:00"},
        'end': {'dateTime': f"{sample_event['end_datetime']}:00+09:00"}
    }

    # テスト実行
    result = update_event(
        mock_service,
        event_id,
        new_title=new_title
    )

    # 検証
    assert result['id'] == event_id
    assert result['summary'] == new_title
    mock_service.events().update.assert_called_once()

def test_delete_event(mock_service):
    """イベント削除のテスト"""
    event_id = 'test_event_id'
    
    # モックの設定
    mock_service.events().delete().execute.return_value = None

    # テスト実行
    delete_event(mock_service, event_id)

    # 検証
    mock_service.events().delete.assert_called_once_with(
        calendarId='primary',
        eventId=event_id
    )

def test_list_events(mock_service, sample_google_event):
    """イベント一覧取得のテスト"""
    # モックの設定
    mock_service.events().list().execute.return_value = {
        'items': [sample_google_event]
    }

    # テスト実行
    start_date = '2024-03-01'
    end_date = '2024-03-31'
    events = list_events(mock_service, start_date, end_date)

    # 検証
    assert len(events) == 1
    assert events[0]['id'] == sample_google_event['id']
    mock_service.events().list.assert_called_once()

def test_list_events_empty(mock_service):
    """イベントが存在しない場合のテスト"""
    # モックの設定
    mock_service.events().list().execute.return_value = {
        'items': []
    }

    # テスト実行
    events = list_events(mock_service)

    # 検証
    assert isinstance(events, list)
    assert len(events) == 0 