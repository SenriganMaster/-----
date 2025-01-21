import argparse
from datetime import datetime
from typing import Optional, List, Dict
import sys
from googleapiclient.errors import HttpError

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

def format_datetime(datetime_str: str) -> str:
    """日時文字列を見やすい形式に整形"""
    dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:00+09:00")
    return dt.strftime("%Y年%m月%d日 %H:%M")

def validate_datetime(datetime_str: str) -> bool:
    """日時文字列の検証"""
    try:
        datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False

def handle_add(start_datetime_str: str, end_datetime_str: str, title: str,
              detail: Optional[str] = None, recurrence: Optional[str] = None,
              events_file: str = "events.yml") -> None:
    """
    イベントを追加

    Args:
        start_datetime_str: 開始日時 (例: "2024-03-20 15:00")
        end_datetime_str: 終了日時 (例: "2024-03-20 16:00")
        title: イベントのタイトル
        detail: イベントの詳細（オプション）
        recurrence: 定期イベントのパターン（オプション）
        events_file: イベントファイルのパス
    """
    try:
        # 日時のバリデーション
        if not validate_datetime(start_datetime_str) or not validate_datetime(end_datetime_str):
            print("エラー: 日時のフォーマットが不正です。'YYYY-MM-DD HH:MM'の形式で指定してください。")
            print("例: 2024-03-20 15:00")
            sys.exit(1)

        # 開始時刻が終了時刻より後でないかチェック
        start_dt = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M")
        if start_dt >= end_dt:
            print("エラー: 開始時刻は終了時刻より前である必要があります。")
            sys.exit(1)

        # Google Calendarに追加
        service = get_authenticated_service()
        event = google_add_event(service, start_datetime_str, end_datetime_str, title, detail, recurrence=recurrence)

        # ローカルにも保存
        events = load_events(events_file)
        local_event = {
            'id': event['id'],
            'title': title,
            'start_datetime': start_datetime_str,
            'end_datetime': end_datetime_str,
            'detail': detail,
            'recurrence': recurrence
        }
        updated_events = add_local_event(events, local_event)
        save_events(events_file, updated_events)
        
        print(f"\n✨ イベントを追加しました")
        print(f"タイトル: {title}")
        print(f"開始時刻: {start_datetime_str}")
        print(f"終了時刻: {end_datetime_str}")
        if detail:
            print(f"詳細: {detail}")
        if recurrence:
            print(f"繰り返し: {recurrence}")

    except HttpError as error:
        print(f"エラー: Google Calendar APIとの通信に失敗しました（{error.status_code}）")
        if error.status_code == 401:
            print("認証に失敗しました。認証情報を確認してください。")
        elif error.status_code == 403:
            print("アクセス権限がありません。")
        sys.exit(1)
    except Exception as error:
        print(f"エラー: 予期せぬエラーが発生しました - {str(error)}")
        sys.exit(1)

def handle_update(event_id: str, new_title: Optional[str] = None,
                 new_start_datetime: Optional[str] = None, new_end_datetime: Optional[str] = None,
                 new_detail: Optional[str] = None, new_recurrence: Optional[str] = None,
                 events_file: str = "events.yml") -> None:
    """
    イベントを更新

    Args:
        event_id: 更新対象のイベントID
        new_title: 新しいタイトル（オプション）
        new_start_datetime: 新しい開始日時（オプション）
        new_end_datetime: 新しい終了日時（オプション）
        new_detail: 新しい詳細（オプション）
        new_recurrence: 新しい繰り返しパターン（オプション）
        events_file: イベントファイルのパス
    """
    try:
        # 日時のバリデーション
        if new_start_datetime and not validate_datetime(new_start_datetime):
            print("エラー: 開始日時のフォーマットが不正です。'YYYY-MM-DD HH:MM'の形式で指定してください。")
            print("例: 2024-03-20 15:00")
            sys.exit(1)
        if new_end_datetime and not validate_datetime(new_end_datetime):
            print("エラー: 終了日時のフォーマットが不正です。'YYYY-MM-DD HH:MM'の形式で指定してください。")
            print("例: 2024-03-20 16:00")
            sys.exit(1)

        # 開始時刻と終了時刻の整合性チェック
        if new_start_datetime and new_end_datetime:
            start_dt = datetime.strptime(new_start_datetime, "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(new_end_datetime, "%Y-%m-%d %H:%M")
            if start_dt >= end_dt:
                print("エラー: 開始時刻は終了時刻より前である必要があります。")
                sys.exit(1)

        # Google Calendarを更新
        service = get_authenticated_service()
        event = google_update_event(
            service, event_id,
            new_title=new_title,
            new_start_datetime=new_start_datetime,
            new_end_datetime=new_end_datetime,
            new_detail=new_detail,
            new_recurrence=new_recurrence
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
        if new_recurrence:
            new_data['recurrence'] = new_recurrence

        updated_events = update_local_event(events, event_id, new_data)
        save_events(events_file, updated_events)
        
        print(f"\n✨ イベントを更新しました")
        print(f"イベントID: {event_id}")
        if new_title:
            print(f"新しいタイトル: {new_title}")
        if new_start_datetime:
            print(f"新しい開始時刻: {new_start_datetime}")
        if new_end_datetime:
            print(f"新しい終了時刻: {new_end_datetime}")
        if new_detail:
            print(f"新しい詳細: {new_detail}")
        if new_recurrence:
            print(f"新しい繰り返し: {new_recurrence}")

    except HttpError as error:
        print(f"エラー: Google Calendar APIとの通信に失敗しました（{error.status_code}）")
        if error.status_code == 401:
            print("認証に失敗しました。認証情報を確認してください。")
        elif error.status_code == 403:
            print("アクセス権限がありません。")
        elif error.status_code == 404:
            print("指定されたイベントが見つかりません。イベントIDを確認してください。")
        sys.exit(1)
    except Exception as error:
        print(f"エラー: 予期せぬエラーが発生しました - {str(error)}")
        sys.exit(1)

def handle_delete(event_id: str, events_file: str = "events.yml") -> None:
    """
    イベントを削除

    Args:
        event_id: 削除対象のイベントID
        events_file: イベントファイルのパス
    """
    try:
        # Google Calendarから削除
        service = get_authenticated_service()
        google_delete_event(service, event_id)

        # ローカルからも削除
        events = load_events(events_file)
        updated_events = delete_local_event(events, event_id)
        save_events(events_file, updated_events)
        
        print(f"\n✨ イベントを削除しました")
        print(f"イベントID: {event_id}")

    except HttpError as error:
        print(f"エラー: Google Calendar APIとの通信に失敗しました（{error.status_code}）")
        if error.status_code == 401:
            print("認証に失敗しました。認証情報を確認してください。")
        elif error.status_code == 403:
            print("アクセス権限がありません。")
        elif error.status_code == 404:
            print("指定されたイベントが見つかりません。イベントIDを確認してください。")
        sys.exit(1)
    except Exception as error:
        print(f"エラー: 予期せぬエラーが発生しました - {str(error)}")
        sys.exit(1)

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
    try:
        # Google Calendarから取得
        service = get_authenticated_service()
        events = google_list_events(service, start_date, end_date)

        # ローカルデータと同期
        local_events = load_events(events_file)
        
        # イベントを表示
        if not events:
            print("\n📅 該当期間のイベントはありません")
            if start_date and end_date:
                print(f"期間: {start_date} から {end_date}")
            elif start_date:
                print(f"開始日: {start_date} 以降")
            elif end_date:
                print(f"終了日: {end_date} まで")
        else:
            print("\n📅 イベント一覧")
            if start_date and end_date:
                print(f"期間: {start_date} から {end_date}")
            elif start_date:
                print(f"開始日: {start_date} 以降")
            elif end_date:
                print(f"終了日: {end_date} まで")
            print("=" * 50)
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                print(f"\n🔖 {event['summary']}")
                print(f"  ID: {event['id']}")
                print(f"  開始: {format_datetime(start)}")
                print(f"  終了: {format_datetime(end)}")
                if 'description' in event and event['description']:
                    print(f"  詳細: {event['description']}")
                print("-" * 50)

        return events

    except HttpError as error:
        print(f"エラー: Google Calendar APIとの通信に失敗しました（{error.status_code}）")
        if error.status_code == 401:
            print("認証に失敗しました。認証情報を確認してください。")
        elif error.status_code == 403:
            print("アクセス権限がありません。")
        sys.exit(1)
    except Exception as error:
        print(f"エラー: 予期せぬエラーが発生しました - {str(error)}")
        sys.exit(1)

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='WithAI Calendar CLI - Google Calendarを使ったタスク管理ツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  イベントの追加:
    python calendar_manager.py add "2024-03-20 15:00" "2024-03-20 16:00" "ミーティング" --detail "プロジェクトの進捗確認"
    python calendar_manager.py add "2024-03-20 15:00" "2024-03-20 16:00" "定例MTG" --recurrence daily

  イベントの更新:
    python calendar_manager.py update EVENT_ID --title "新しいタイトル"
    python calendar_manager.py update EVENT_ID --start_datetime "2024-03-20 16:00" --end_datetime "2024-03-20 17:00"
    python calendar_manager.py update EVENT_ID --recurrence weekly

  イベントの削除:
    python calendar_manager.py delete EVENT_ID

  イベント一覧の表示:
    python calendar_manager.py list
    python calendar_manager.py list --start "2024-03-01" --end "2024-03-31"
    """
    )
    subparsers = parser.add_subparsers(dest='command', help='サブコマンド')

    # addコマンド
    add_parser = subparsers.add_parser('add', help='イベントを追加')
    add_parser.add_argument('start_datetime', help='開始日時 (例: "2024-03-20 15:00")')
    add_parser.add_argument('end_datetime', help='終了日時 (例: "2024-03-20 16:00")')
    add_parser.add_argument('title', help='イベントのタイトル')
    add_parser.add_argument('--detail', help='イベントの詳細')
    add_parser.add_argument('--recurrence', choices=['daily', 'weekly', 'monthly', 'weekday'],
                           help='繰り返しパターン（daily=毎日, weekly=毎週, monthly=毎月, weekday=平日のみ）')

    # updateコマンド
    update_parser = subparsers.add_parser('update', help='イベントを更新')
    update_parser.add_argument('event_id', help='更新対象のイベントID')
    update_parser.add_argument('--title', help='新しいタイトル')
    update_parser.add_argument('--start_datetime', help='新しい開始日時 (例: "2024-03-20 15:00")')
    update_parser.add_argument('--end_datetime', help='新しい終了日時 (例: "2024-03-20 16:00")')
    update_parser.add_argument('--detail', help='新しい詳細')
    update_parser.add_argument('--recurrence', choices=['daily', 'weekly', 'monthly', 'weekday', 'none'],
                             help='新しい繰り返しパターン（none=繰り返しを解除）')

    # deleteコマンド
    delete_parser = subparsers.add_parser('delete', help='イベントを削除')
    delete_parser.add_argument('event_id', help='削除対象のイベントID')

    # listコマンド
    list_parser = subparsers.add_parser('list', help='イベント一覧を表示')
    list_parser.add_argument('--start', help='取得開始日 (例: "2024-03-01")')
    list_parser.add_argument('--end', help='取得終了日 (例: "2024-03-31")')

    args = parser.parse_args()

    if args.command == 'add':
        handle_add(args.start_datetime, args.end_datetime, args.title, args.detail, args.recurrence)
    elif args.command == 'update':
        handle_update(
            args.event_id,
            new_title=args.title,
            new_start_datetime=args.start_datetime,
            new_end_datetime=args.end_datetime,
            new_detail=args.detail,
            new_recurrence=args.recurrence
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