def get_or_create_calendar(service) -> str:
    """
    'WithAI'カレンダーを取得または作成する
    
    Returns:
        str: カレンダーID
    """
    try:
        # 既存のカレンダーリストを取得
        calendar_list = service.calendarList().list().execute()
        
        # WithAIカレンダーを探す
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == CALENDAR_NAME:
                return calendar_list_entry['id']
        
        # なければ新規作成
        calendar = {
            'summary': CALENDAR_NAME,
            'timeZone': 'Asia/Tokyo'
        }
        created_calendar = service.calendars().insert(body=calendar).execute()
        
        # 作成したカレンダーをリストに追加
        calendar_list_entry = {
            'id': created_calendar['id']
        }
        service.calendarList().insert(body=calendar_list_entry).execute()
        
        return created_calendar['id']
    except Exception as e:
        print(f"カレンダーの取得/作成中にエラーが発生しました: {e}")
        return 'primary'  # エラーが発生した場合はプライマリーカレンダーを使用 