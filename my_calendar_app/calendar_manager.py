import argparse
from datetime import datetime
from typing import Optional, List, Dict
import sys

from google_calendar_service import (
    get_authenticated_service,
    add_event as google_add_event,
    update_event as google_update_event,
    delete_event as google_delete_event,
    list_events as google_list_events
)
from local_data_manager import (
    load_events,
    save_events,
    add_local_event,
    update_local_event,
    delete_local_event
)

def validate_datetime(datetime_str: str) -> bool:
    """日時文字列の検証"""
    try:
        datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False

def handle_add(start_datetime_str: str, end_datetime_str: str, title: str,
              detail: Optional[str] = None, events_file: str = "events.yml") -> None:
    """
    イベントを追加

    Args:
        start_datetime_str: 開始日時 (例: "2024-03-20 15:00")
        end_datetime_str: 終了日時 (例: "2024-03-20 16:00")
        title: イベントのタイトル
        detail: イベントの詳細（オプション）
        events_file: イベントファイルのパス
    """
    # 日時のバリデーション
    if not validate_datetime(start_datetime_str) or not validate_datetime(end_datetime_str):
        print("エラー: 日時のフォーマットが不正です。'YYYY-MM-DD HH:MM'の形式で指定してください。")
        sys.exit(1)

    # Google Calendarに追加
    service = get_authenticated_service()
    event = google_add_event(service, start_datetime_str, end_datetime_str, title, detail)

    # ローカルにも保存
    events = load_events(events_file)
    local_event = {
        'id': event['id'],
        'title': title,
        'start_datetime': start_datetime_str,
        'end_datetime': end_datetime_str,
        'detail': detail
    }
    updated_events = add_local_event(events, local_event)
    save_events(events_file, updated_events)
    
    print(f"イベントを追加しました: {title}")

def handle_update(event_id: str, new_title: Optional[str] = None,
                 new_start_datetime: Optional[str] = None, new_end_datetime: Optional[str] = None,
                 new_detail: Optional[str] = None, events_file: str = "events.yml") -> None:
    """
    イベントを更新

    Args:
        event_id: 更新対象のイベントID
        new_title: 新しいタイトル（オプション）
        new_start_datetime: 新しい開始日時（オプション）
        new_end_datetime: 新しい終了日時（オプション）
        new_detail: 新しい詳細（オプション）
        events_file: イベントファイルのパス
    """
    # 日時のバリデーション
    if new_start_datetime and not validate_datetime(new_start_datetime):
        print("エラー: 開始日時のフォーマットが不正です。")
        sys.exit(1)
    if new_end_datetime and not validate_datetime(new_end_datetime):
        print("エラー: 終了日時のフォーマットが不正です。")
        sys.exit(1)

    # Google Calendarを更新
    service = get_authenticated_service()
    event = google_update_event(
        service, event_id,
        new_title=new_title,
        new_start_datetime=new_start_datetime,
        new_end_datetime=new_end_datetime,
        new_detail=new_detail
    )

    # ローカルも更新
    events = load_events(events_file)
    new_data = {}
    if new_title:
        new_data['title'] = new_title
    if new_start_datetime:
        new_data['start_datetime'] = new_start_datetime
    if new_end_datetime:
        new_data['end_datetime'] = new_end_datetime
    if new_detail:
        new_data['detail'] = new_detail

    updated_events = update_local_event(events, event_id, new_data)
    save_events(events_file, updated_events)
    
    print(f"イベントを更新しました: ID {event_id}")

def handle_delete(event_id: str, events_file: str = "events.yml") -> None:
    """
    イベントを削除

    Args:
        event_id: 削除対象のイベントID
        events_file: イベントファイルのパス
    """
    # Google Calendarから削除
    service = get_authenticated_service()
    google_delete_event(service, event_id)

    # ローカルからも削除
    events = load_events(events_file)
    updated_events = delete_local_event(events, event_id)
    save_events(events_file, updated_events)
    
    print(f"イベントを削除しました: ID {event_id}")

def handle_list(start_date: Optional[str] = None, end_date: Optional[str] = None,
                events_file: str = "events.yml") -> List[Dict]:
    """
    イベント一覧を取得

    Args:
        start_date: 取得開始日（オプション）
        end_date: 取得終了日（オプション）
        events_file: イベントファイルのパス

    Returns:
        List[Dict]: イベントのリスト
    """
    # Google Calendarから取得
    service = get_authenticated_service()
    events = google_list_events(service, start_date, end_date)

    # ローカルデータと同期
    local_events = load_events(events_file)
    
    # イベントを表示
    if not events:
        print("該当期間のイベントはありません。")
    else:
        print("\n=== イベント一覧 ===")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            print(f"\nID: {event['id']}")
            print(f"タイトル: {event['summary']}")
            print(f"開始: {start}")
            print(f"終了: {end}")
            if 'description' in event:
                print(f"詳細: {event['description']}")
            print("-" * 30)

    return events

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='Google Calendar CLI')
    subparsers = parser.add_subparsers(dest='command', help='サブコマンド')

    # addコマンド
    add_parser = subparsers.add_parser('add', help='イベントを追加')
    add_parser.add_argument('start_datetime', help='開始日時 (例: "2024-03-20 15:00")')
    add_parser.add_argument('end_datetime', help='終了日時 (例: "2024-03-20 16:00")')
    add_parser.add_argument('title', help='イベントのタイトル')
    add_parser.add_argument('--detail', help='イベントの詳細')

    # updateコマンド
    update_parser = subparsers.add_parser('update', help='イベントを更新')
    update_parser.add_argument('event_id', help='更新対象のイベントID')
    update_parser.add_argument('--title', help='新しいタイトル')
    update_parser.add_argument('--start_datetime', help='新しい開始日時')
    update_parser.add_argument('--end_datetime', help='新しい終了日時')
    update_parser.add_argument('--detail', help='新しい詳細')

    # deleteコマンド
    delete_parser = subparsers.add_parser('delete', help='イベントを削除')
    delete_parser.add_argument('event_id', help='削除対象のイベントID')

    # listコマンド
    list_parser = subparsers.add_parser('list', help='イベント一覧を表示')
    list_parser.add_argument('--start', help='取得開始日 (例: "2024-03-01")')
    list_parser.add_argument('--end', help='取得終了日 (例: "2024-03-31")')

    args = parser.parse_args()

    if args.command == 'add':
        handle_add(args.start_datetime, args.end_datetime, args.title, args.detail)
    elif args.command == 'update':
        handle_update(
            args.event_id,
            new_title=args.title,
            new_start_datetime=args.start_datetime,
            new_end_datetime=args.end_datetime,
            new_detail=args.detail
        )
    elif args.command == 'delete':
        handle_delete(args.event_id)
    elif args.command == 'list':
        handle_list(args.start, args.end)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main() 