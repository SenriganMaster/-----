import pytest
from unittest.mock import Mock, patch, MagicMock, call
from ..calendar_manager import main, handle_add, handle_update, handle_delete, handle_list

WITHAI_CALENDAR_ID = 'withai_calendar_id'

@pytest.fixture
def mock_google_service():
    """Google Calendar APIサービスのモック"""
    mock_service = MagicMock()
    
    # WithAIカレンダーのモック設定
    mock_service.calendarList().list().execute.return_value = {
        'items': [
            {
                'id': WITHAI_CALENDAR_ID,
                'summary': 'WithAI'
            }
        ]
    }
    
    # カレンダー作成のモック設定
    mock_service.calendars().insert().execute.return_value = {
        'id': WITHAI_CALENDAR_ID,
        'summary': 'WithAI'
    }
    
    return mock_service

@pytest.fixture
def mock_local_events():
    """ローカルイベントデータのモック"""
    return [
        {
            'id': 'event_1',
            'title': 'ミーティングA',
            'start_datetime': '2024-03-20 15:00',
            'end_datetime': '2024-03-20 16:00',
            'detail': 'プロジェクトAについて'
        },
        {
            'id': 'event_2',
            'title': 'ミーティングB',
            'start_datetime': '2024-03-20 18:00',
            'end_datetime': '2024-03-20 19:00',
            'detail': 'プロジェクトBについて'
        }
    ]

def test_handle_add(mock_google_service, tmp_path):
    """イベント追加のテスト"""
    # モックの設定
    event_id = 'new_event_id'
    mock_event = {
        'id': event_id,
        'summary': 'テストミーティング',
        'start': {'dateTime': '2024-03-20T15:00:00+09:00'},
        'end': {'dateTime': '2024-03-20T16:00:00+09:00'}
    }
    mock_google_service.events().insert().execute.return_value = mock_event

    # テスト用のYAMLファイル
    events_file = tmp_path / "events.yml"

    with patch('google_calendar_service.get_authenticated_service', return_value=mock_google_service):
        with patch('local_data_manager.load_events', return_value=[]):
            with patch('local_data_manager.save_events'):
                # テスト実行
                handle_add(
                    start_datetime_str='2024-03-20 15:00',
                    end_datetime_str='2024-03-20 16:00',
                    title='テストミーティング',
                    detail='テスト用',
                    events_file=str(events_file)
                )

                # 検証
                expected_body = {
                    'summary': 'テストミーティング',
                    'description': 'テスト用',
                    'start': {
                        'dateTime': '2024-03-20T15:00:00+09:00',
                        'timeZone': 'Asia/Tokyo'
                    },
                    'end': {
                        'dateTime': '2024-03-20T16:00:00+09:00',
                        'timeZone': 'Asia/Tokyo'
                    }
                }
                mock_google_service.events().insert.assert_called_with(
                    calendarId=WITHAI_CALENDAR_ID,
                    body=expected_body
                )

def test_handle_update(mock_google_service, mock_local_events, tmp_path):
    """イベント更新のテスト"""
    event_id = 'event_1'
    new_title = '更新後のミーティング'
    
    # モックの設定
    mock_event = {
        'id': event_id,
        'summary': 'ミーティングA',
        'start': {'dateTime': '2024-03-20T15:00:00+09:00'},
        'end': {'dateTime': '2024-03-20T16:00:00+09:00'}
    }
    mock_google_service.events().get().execute.return_value = mock_event
    mock_google_service.events().update().execute.return_value = {
        **mock_event,
        'summary': new_title
    }

    # テスト用のYAMLファイル
    events_file = tmp_path / "events.yml"
    
    with patch('google_calendar_service.get_authenticated_service', return_value=mock_google_service):
        with patch('local_data_manager.load_events', return_value=mock_local_events):
            with patch('local_data_manager.save_events'):
                # テスト実行
                handle_update(
                    event_id=event_id,
                    new_title=new_title,
                    events_file=str(events_file)
                )

                # 検証
                mock_google_service.events().get.assert_called_with(
                    calendarId=WITHAI_CALENDAR_ID,
                    eventId=event_id
                )
                mock_google_service.events().update.assert_called()

def test_handle_delete(mock_google_service, mock_local_events, tmp_path):
    """イベント削除のテスト"""
    event_id = 'event_1'
    
    # テスト用のYAMLファイル
    events_file = tmp_path / "events.yml"
    
    with patch('google_calendar_service.get_authenticated_service', return_value=mock_google_service):
        with patch('local_data_manager.load_events', return_value=mock_local_events):
            with patch('local_data_manager.save_events'):
                # テスト実行
                handle_delete(event_id, events_file=str(events_file))

                # 検証
                mock_google_service.events().delete.assert_called_with(
                    calendarId=WITHAI_CALENDAR_ID,
                    eventId=event_id
                )

def test_handle_list(mock_google_service, mock_local_events, tmp_path):
    """イベント一覧取得のテスト"""
    # モックの設定
    mock_events = {
        'items': [
            {
                'id': 'event_1',
                'summary': 'ミーティングA',
                'start': {'dateTime': '2024-03-20T15:00:00+09:00'},
                'end': {'dateTime': '2024-03-20T16:00:00+09:00'}
            }
        ]
    }
    mock_google_service.events().list().execute.return_value = mock_events

    # テスト用のYAMLファイル
    events_file = tmp_path / "events.yml"
    
    with patch('google_calendar_service.get_authenticated_service', return_value=mock_google_service):
        with patch('local_data_manager.load_events', return_value=mock_local_events):
            # テスト実行
            events = handle_list(
                start_date='2024-03-01',
                end_date='2024-03-31',
                events_file=str(events_file)
            )

            # 検証
            assert len(events) > 0
            mock_google_service.events().list.assert_called_with(
                calendarId=WITHAI_CALENDAR_ID,
                timeMin='2024-03-01T00:00:00+09:00',
                timeMax='2024-03-31T23:59:59+09:00',
                singleEvents=True,
                orderBy='startTime'
            ) 