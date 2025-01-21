import pytest
import os
import yaml

@pytest.fixture
def sample_event():
    """テスト用のイベントデータを提供するフィクスチャ"""
    return {
        'id': 'test_event_id_1',
        'title': 'テストミーティング',
        'start_datetime': '2024-03-20 15:00',
        'end_datetime': '2024-03-20 16:00',
        'detail': 'テスト用ミーティング'
    }

@pytest.fixture
def test_events_file(tmp_path):
    """テスト用の一時的なYAMLファイルを提供するフィクスチャ"""
    test_file = tmp_path / "test_events.yml"
    return str(test_file)

@pytest.fixture
def sample_events_data():
    """複数のテスト用イベントデータを提供するフィクスチャ"""
    return [
        {
            'id': 'test_event_id_1',
            'title': 'ミーティングA',
            'start_datetime': '2024-03-20 15:00',
            'end_datetime': '2024-03-20 16:00',
            'detail': 'プロジェクトAについて'
        },
        {
            'id': 'test_event_id_2',
            'title': 'ミーティングB',
            'start_datetime': '2024-03-20 18:00',
            'end_datetime': '2024-03-20 19:00',
            'detail': 'プロジェクトBについて'
        }
    ] 