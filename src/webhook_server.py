"""LINE Webhook サーバー"""

import json
import os

from flask import Flask, abort, request

from src.line_notifier import LineNotifier
from src.user_manager import UserManager
from src.storage import Storage

app = Flask(__name__)

# グローバルインスタンス
storage = Storage()
user_manager = UserManager(storage)


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    LINE Webhookエンドポイント
    """
    print("=" * 60)
    print("Webhook受信")
    print("=" * 60)
    
    # 署名検証
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    print(f"Body長: {len(body)} bytes")
    print(f"Signature: {signature[:20]}..." if signature else "Signature: なし")
    
    try:
        notifier = LineNotifier()
        print("✓ LineNotifier初期化成功")
        
        # 署名を検証
        if notifier.channel_secret:
            if not notifier.verify_signature(body, signature):
                print("❌ 署名検証失敗")
                abort(400)
            print("✓ 署名検証成功")
        else:
            print("⚠️  チャネルシークレット未設定（署名検証スキップ）")
        
    except ValueError as e:
        print(f"❌ LINE Notifierの初期化エラー: {e}")
        abort(500)
    
    # イベントを処理
    try:
        events = json.loads(body)['events']
        print(f"イベント数: {len(events)}")
        
        for i, event in enumerate(events, 1):
            event_type = event.get('type')
            print(f"\n--- イベント {i}/{len(events)} ---")
            print(f"タイプ: {event_type}")
            
            # メッセージイベント
            if event_type == 'message':
                message_type = event['message'].get('type')
                print(f"メッセージタイプ: {message_type}")
                
                if message_type == 'text':
                    handle_text_message(event, notifier)
                else:
                    handle_unsupported_message(event, notifier)
            
            # Follow/Unfollowイベント
            elif event_type == 'follow':
                handle_follow_event(event, notifier)
            elif event_type == 'unfollow':
                handle_unfollow_event(event)
        
        print("\n" + "=" * 60)
        print("Webhook処理完了")
        print("=" * 60)
        return 'OK', 200
        
    except Exception as e:
        print(f"❌ Webhookエラー: {e}")
        import traceback
        traceback.print_exc()
        abort(500)


def handle_text_message(event: dict, notifier: LineNotifier):
    """
    テキストメッセージを処理
    
    Args:
        event: LINEイベント
        notifier: LineNotifierインスタンス
    """
    reply_token = event['replyToken']
    message_text = event['message']['text'].strip()
    user_id = event['source'].get('userId', 'unknown')
    
    print(f"▶ 受信メッセージ: '{message_text}' (ユーザーID: {user_id[:10]}...)")
    
    # コマンド処理
    if message_text == '登録':
        handle_register_command(reply_token, user_id, notifier)
    elif message_text.startswith('購読 '):
        category = message_text.replace('購読 ', '').strip()
        handle_subscribe_command(reply_token, user_id, category, notifier)
    elif message_text.startswith('購読解除 '):
        category = message_text.replace('購読解除 ', '').strip()
        handle_unsubscribe_command(reply_token, user_id, category, notifier)
    elif message_text == 'サイト一覧':
        handle_sites_list_command(reply_token, notifier)
    else:
        # デフォルト: ヘルプメッセージ
        handle_help_message(reply_token, notifier)


def handle_register_command(reply_token: str, user_id: str, notifier: LineNotifier):
    """
    ユーザー登録コマンドを処理
    
    Args:
        reply_token: リプライトークン
        user_id: ユーザーID
        notifier: LineNotifierインスタンス
    """
    print(f"  → ユーザー登録処理")
    
    success = user_manager.register_user(user_id)
    if success:
        message = """✅ 登録が完了しました！

以下のコマンドが使用できます：
• 購読 [カテゴリ名] - カテゴリを購読
• 購読解除 [カテゴリ名] - 購読を解除
• サイト一覧 - 登録されているサイト一覧を表示"""
    else:
        message = "❌ 登録に失敗しました。しばらくしてから再度お試しください。"
    
    notifier.reply_text_message(reply_token, message)


def handle_subscribe_command(reply_token: str, user_id: str, category: str, notifier: LineNotifier):
    """
    カテゴリ購読コマンドを処理
    
    Args:
        reply_token: リプライトークン
        user_id: ユーザーID
        category: カテゴリ名
        notifier: LineNotifierインスタンス
    """
    print(f"  → カテゴリ購読処理: {category}")
    
    # ユーザーが登録されているかチェック
    user = user_manager.get_user(user_id)
    if not user:
        notifier.reply_text_message(
            reply_token,
            "❌ ユーザーが登録されていません。まず「登録」コマンドで登録してください。"
        )
        return
    
    success = user_manager.subscribe_category(user_id, category)
    if success:
        message = f"✅ 「{category}」カテゴリを購読しました！\n\n新着情報が配信されます。"
    else:
        message = f"❌ 「{category}」カテゴリの購読に失敗しました。"
    
    notifier.reply_text_message(reply_token, message)


def handle_unsubscribe_command(reply_token: str, user_id: str, category: str, notifier: LineNotifier):
    """
    カテゴリ購読解除コマンドを処理
    
    Args:
        reply_token: リプライトークン
        user_id: ユーザーID
        category: カテゴリ名
        notifier: LineNotifierインスタンス
    """
    print(f"  → カテゴリ購読解除処理: {category}")
    
    success = user_manager.unsubscribe_category(user_id, category)
    if success:
        message = f"✅ 「{category}」カテゴリの購読を解除しました。"
    else:
        message = f"❌ 「{category}」カテゴリの購読解除に失敗しました。"
    
    notifier.reply_text_message(reply_token, message)


def handle_sites_list_command(reply_token: str, notifier: LineNotifier):
    """
    サイト一覧コマンドを処理
    
    Args:
        reply_token: リプライトークン
        notifier: LineNotifierインスタンス
    """
    print(f"  → サイト一覧表示")
    
    sites_data = storage.load_sites()
    if not sites_data or not sites_data.get('sites'):
        message = "現在登録されているサイトはありません。"
    else:
        sites = sites_data['sites']
        lines = ["📰 登録されているサイト一覧\n"]
        for i, site in enumerate(sites, 1):
            status = "✅" if site.get('enabled', False) else "❌"
            lines.append(f"{i}. {status} {site.get('name', '不明')}")
            lines.append(f"   カテゴリ: {site.get('category', '不明')}")
            if site.get('url'):
                lines.append(f"   URL: {site['url']}")
            lines.append("")
        
        message = "\n".join(lines)
    
    notifier.reply_text_message(reply_token, message)


def handle_help_message(reply_token: str, notifier: LineNotifier):
    """
    ヘルプメッセージを送信
    
    Args:
        reply_token: リプライトークン
        notifier: LineNotifierインスタンス
    """
    message = """📰 情報配信Bot ヘルプ

【コマンド一覧】
• 登録 - ユーザー登録
• 購読 [カテゴリ名] - カテゴリを購読
• 購読解除 [カテゴリ名] - 購読を解除
• サイト一覧 - 登録されているサイト一覧を表示

【例】
• 購読 AI
• 購読解除 ドローン"""
    
    notifier.reply_text_message(reply_token, message)


def handle_unsupported_message(event: dict, notifier: LineNotifier):
    """
    サポートしていないメッセージタイプへの対応
    
    Args:
        event: LINEイベント
        notifier: LineNotifierインスタンス
    """
    reply_token = event['replyToken']
    message_type = event['message'].get('type', 'unknown')
    
    print(f"サポート外メッセージ: {message_type}")
    
    notifier.reply_text_message(
        reply_token,
        "このメッセージタイプには対応していません。\nテキストメッセージでコマンドを送信してください。"
    )


def handle_follow_event(event: dict, notifier: LineNotifier):
    """
    Followイベント（友だち追加）を処理
    
    Args:
        event: LINEイベント
        notifier: LineNotifierインスタンス
    """
    reply_token = event['replyToken']
    user_id = event['source'].get('userId', 'unknown')
    
    print(f"友だち追加: {user_id[:10]}...")
    
    # ウェルカムメッセージを送信
    welcome_message = """📰 情報配信Botへようこそ！

このBotは、AI、ドローン、SDGsなどの最新情報を自動で配信します。

まずは「登録」コマンドでユーザー登録を行ってください。

【コマンド一覧】
• 登録 - ユーザー登録
• 購読 [カテゴリ名] - カテゴリを購読
• 購読解除 [カテゴリ名] - 購読を解除
• サイト一覧 - 登録されているサイト一覧を表示"""
    
    notifier.reply_text_message(reply_token, welcome_message)


def handle_unfollow_event(event: dict):
    """
    Unfollowイベント（ブロック）を処理
    
    Args:
        event: LINEイベント
    """
    user_id = event['source'].get('userId', 'unknown')
    print(f"友だち解除: {user_id[:10]}...")
    
    # ユーザーを登録解除
    user_manager.unregister_user(user_id)


@app.route('/', methods=['GET'])
def index():
    """
    ルートエンドポイント
    """
    return '📰 Information Delivery Bot Webhook Server is running!', 200


@app.route('/health', methods=['GET'])
def health():
    """
    ヘルスチェックエンドポイント
    """
    return 'OK', 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

