import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

# .envファイルの内容を読み込む
load_dotenv()

# Flaskアプリのインスタンスを作成
app = Flask(__name__)

# os.getenv("~~")で.envファイルに書いたAPIキーを読み込む
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# 使用するAIモデルを指定
model = genai.GenerativeModel('gemini-2.5-pro')


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    # 辞書型としてフロントエンドのデータを受け取る
    data = request.get_json()
    # 受け取ったデータからfavoriteBooksというキーの値を取り出す
    favorite_books = data.get('favoriteBooks', [])

    # --- Geminiへの指示（プロンプト）を作成 ---
    # 「ブックソムリエAI」への指示書（プロンプト）
    # この指示の書き方で、AIの回答の質が大きく変わる
    prompt = f"""
    あなたはプロのブックソムリエです。
    以下のルールに従って、ユーザーが次に読むべき本をおすすめしてください。

    # ルール
    - ユーザーが好きな本のリストに基づいて、関連性が高く、次に読みたくなるような本を3冊提案してください。
    - 各書籍について、必ず「タイトル」「著者」「おすすめする理由」を提示してください。
    - 「おすすめする理由」は、ユーザーの心に響くように、20文字から30文字程度で簡潔に記述してください。
    - 出力は必ず以下のJSON形式のリストにしてください。他の文章は一切含めないでください。
    [
        {{"title": "本のタイトル", "author": "著者名", "reason": "おすすめ理由"}},
        {{"title": "本のタイトル", "author": "著者名", "reason": "おすすめ理由"}}
    ]
    
    # ユーザーが好きな本のリスト
    {','.join(favorite_books)}
    """

    # Gemini APIの実行と結果の処理
    try:
        # model.generate_content()で、作成したプロンプトをGeminiに送信
        response = model.generate_content(prompt)

        # json.loads()はJSON形式の文字列をPythonデータ構造に変換する関数
        recommendations = json.loads(response.text)

        # 変換したおすすめ書籍のリストをJSON形式でフロントエンドに返却
        return jsonify(recommendations)

    # tryの中でエラーが発生した場合の処理
    except Exception as e:
        # エラーの内容をコンソールに出力
        print(f"エラーが発生しました: {e}")
        # フロントエンドにはエラーが起きたことを示すメッセージをJSONで返す
        return jsonify({"error": "AIによるおすすめの生成に失敗しました。"}), 500

# "/"というURL（トップページ）に対するリクエストを処理する関数
@app.route('/')
def index():
    # ブラウザにメッセージを返す
    return "ブックソムリエAIのバックエンドへようこそ。サーバーは正常に稼働中です"

# このファイルが実行された時だけ、以下のコードが実行される
if __name__ == "__main__":
    app.run(debug=True, port=5001)
