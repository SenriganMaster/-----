import os
import yaml
from typing import List, Dict, Optional
from datetime import datetime

def load_events(file_path: str = "events.yml") -> List[Dict]:
    """
    YAMLファイルからイベントデータを読み込む

    Args:
        file_path (str): 読み込むYAMLファイルのパス。デフォルトは"events.yml"

    Returns:
        List[Dict]: イベントのリスト。ファイルが存在しない場合は空リスト
    """
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        return data if data is not None else []

def save_events(file_path: str, events_data: List[Dict]) -> None:
    """
    イベントデータをYAMLファイルに保存

    Args:
        file_path (str): 保存先のYAMLファイルパス
        events_data (List[Dict]): 保存するイベントのリスト

    Returns:
        None
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(events_data, f, allow_unicode=True, sort_keys=False)

def add_local_event(events_data: List[Dict], event_data: Dict) -> List[Dict]:
    """
    イベントリストに新しいイベントを追加

    Args:
        events_data (List[Dict]): 既存のイベントリスト
        event_data (Dict): 追加する新しいイベントのデータ

    Returns:
        List[Dict]: 更新後のイベントリスト
    """
    return events_data + [event_data]

def update_local_event(events_data: List[Dict], event_id: str, new_data: Dict) -> List[Dict]:
    """
    指定されたIDのイベントを更新

    Args:
        events_data (List[Dict]): 既存のイベントリスト
        event_id (str): 更新対象のイベントID
        new_data (Dict): 更新するデータ（部分的な更新可能）

    Returns:
        List[Dict]: 更新後のイベントリスト
    """
    updated_data = []
    for event in events_data:
        if event['id'] == event_id:
            # 既存のイベントデータを更新用データで上書き
            updated_event = event.copy()
            updated_event.update(new_data)
            updated_data.append(updated_event)
        else:
            updated_data.append(event)
    return updated_data

def save_deleted_event(event: Dict, deleted_events_file: str = "deletedevents.yml") -> None:
    """
    削除されたイベントを保存

    Args:
        event (Dict): 削除されたイベント情報
        deleted_events_file (str): 削除済みイベントファイルのパス
    """
    # 既存の削除済みイベントを読み込む
    try:
        with open(deleted_events_file, 'r', encoding='utf-8') as f:
            deleted_events = yaml.safe_load(f) or []
    except FileNotFoundError:
        deleted_events = []

    # 削除日時を追加
    event['deleted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 削除済みイベントリストに追加
    deleted_events.append(event)

    # 保存
    with open(deleted_events_file, 'w', encoding='utf-8') as f:
        yaml.dump(deleted_events, f, allow_unicode=True)

def delete_local_event(events_data: List[Dict], event_id: str, deleted_events_file: str = "deletedevents.yml") -> List[Dict]:
    """
    指定されたIDのイベントを削除し、削除済みイベントファイルに保存

    Args:
        events_data (List[Dict]): 既存のイベントリスト
        event_id (str): 削除対象のイベントID
        deleted_events_file (str): 削除済みイベントファイルのパス

    Returns:
        List[Dict]: 更新後のイベントリスト
    """
    # 削除対象のイベントを見つける
    deleted_event = next((event for event in events_data if event['id'] == event_id), None)
    if deleted_event:
        # 削除済みイベントとして保存
        save_deleted_event(deleted_event.copy(), deleted_events_file)

    # イベントリストから削除
    return [event for event in events_data if event['id'] != event_id] 