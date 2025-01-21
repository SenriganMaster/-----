import pytest
import yaml
from ..local_data_manager import load_events, save_events, add_local_event, update_local_event, delete_local_event

def test_load_events_empty_file(test_events_file):
    """空のファイルからの読み込みテスト"""
    # 空のファイルを作成
    with open(test_events_file, 'w') as f:
        yaml.dump([], f)
    
    # テスト実行
    events = load_events(test_events_file)
    assert isinstance(events, list)
    assert len(events) == 0

def test_load_events_with_data(test_events_file, sample_events_data):
    """データが存在する場合の読み込みテスト"""
    # テストデータを書き込み
    with open(test_events_file, 'w') as f:
        yaml.dump(sample_events_data, f)
    
    # テスト実行
    events = load_events(test_events_file)
    assert isinstance(events, list)
    assert len(events) == 2
    assert events[0]['id'] == 'test_event_id_1'
    assert events[1]['id'] == 'test_event_id_2'

def test_save_events(test_events_file, sample_events_data):
    """イベントの保存テスト"""
    # テスト実行
    save_events(test_events_file, sample_events_data)
    
    # 保存されたデータを確認
    with open(test_events_file, 'r') as f:
        loaded_data = yaml.safe_load(f)
    
    assert loaded_data == sample_events_data

def test_add_local_event(sample_events_data, sample_event):
    """イベントの追加テスト"""
    # テスト実行
    updated_data = add_local_event(sample_events_data, sample_event)
    
    # 検証
    assert len(updated_data) == len(sample_events_data) + 1
    assert updated_data[-1] == sample_event

def test_update_local_event(sample_events_data):
    """イベントの更新テスト"""
    event_id = 'test_event_id_1'
    new_data = {'title': '更新後のミーティング'}
    
    # テスト実行
    updated_data = update_local_event(sample_events_data, event_id, new_data)
    
    # 検証
    updated_event = next(event for event in updated_data if event['id'] == event_id)
    assert updated_event['title'] == '更新後のミーティング'
    assert updated_event['start_datetime'] == sample_events_data[0]['start_datetime']  # 更新していない項目は変更なし

def test_delete_local_event(sample_events_data):
    """イベントの削除テスト"""
    event_id = 'test_event_id_1'
    
    # テスト実行
    updated_data = delete_local_event(sample_events_data, event_id)
    
    # 検証
    assert len(updated_data) == len(sample_events_data) - 1
    assert not any(event['id'] == event_id for event in updated_data) 