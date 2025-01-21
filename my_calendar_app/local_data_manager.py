import os
import yaml
from typing import List, Dict, Optional

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

def delete_local_event(events_data: List[Dict], event_id: str) -> List[Dict]:
    """
    指定されたIDのイベントを削除

    Args:
        events_data (List[Dict]): 既存のイベントリスト
        event_id (str): 削除対象のイベントID

    Returns:
        List[Dict]: 更新後のイベントリスト
    """
    return [event for event in events_data if event['id'] != event_id] 