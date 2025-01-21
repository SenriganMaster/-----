def load_events():
    """
    変数:
        なし
    返り値:
        events_data: list (YAMLを読み込んだ結果。各要素はdict)
    処理内容:
        - events.ymlを読み込み
        - list形式で返す。例えば[{'id': 'xxx', 'title': 'xxx', 'start_datetime': '...', 'end_datetime': '...', ...}, ...]
    """
    return

def save_events(events_data):
    """
    変数:
        events_data: list
    返り値:
        なし
    処理内容:
        - 受け取ったevents_dataをYAMLとしてevents.ymlに書き込む
    """
    return

def add_local_event(events_data, event_data):
    """
    変数:
        events_data: list (既存イベントの配列)
        event_data: dict (新規追加するイベント情報: { 'id': str, 'title': str, 'start_datetime': str, 'end_datetime': str, ... })
    返り値:
        updated_data: list (追加後のイベント一覧)
    処理内容:
        - event_dataをevents_dataに追加
        - 返り値として更新された全イベント情報を返す
    """
    return

def update_local_event(events_data, event_id, new_data):
    """
    変数:
        events_data: list (既存イベントの配列)
        event_id: str
        new_data: dict (更新内容を持つ: { 'title': '...', 'start_datetime': '...', 'end_datetime': '...', ... })
    返り値:
        updated_data: list (更新後のイベント一覧)
    処理内容:
        - events_dataの中から該当IDのイベントを探す
        - new_dataにあるキーだけ更新し、全体を返す
    """
    return

def delete_local_event(events_data, event_id):
    """
    変数:
        events_data: list
        event_id: str
    返り値:
        updated_data: list (削除後のイベント一覧)
    処理内容:
        - 該当IDのイベントをリストから除去して返す
    """
    return 