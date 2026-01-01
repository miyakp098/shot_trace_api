# APIインターフェース定義書

## POST /api/v1/analyze

### 概要
動画ファイルとメタデータを送信し、解析ジョブを作成します。ジョブIDが返却され、解析が完了すると結果を取得できます。

### リクエスト
- メソッド: POST
- パス: `/api/v1/analyze`
- Content-Type: `multipart/form-data`

#### パラメータ
| 名前         | 型              | 必須 | 説明                                  |
|--------------|-----------------|------|---------------------------------------|
| file         | file            | ○    | 解析対象の動画ファイル                |
| metadata     | string (JSON)   | 任意 | 付随情報（例: 試合ID, カメラ情報等）  |
| callback_url | string (URL)    | 任意 | 解析完了時に結果を通知するURL          |

#### リクエスト例（curl）
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "file=@/path/to/video.mp4" \
  -F 'metadata={"match_id":"m1"}'
```

### レスポンス
#### レスポンス（非同期のみ）
- ステータス: 202 Accepted
- Body:
```json
{
  "job_id": "uuid-xxxx",
  "status": "queued"
}
```

### エラー例
- 400 Bad Request: ファイル未指定、JSON不正等
- 413 Payload Too Large: ファイルサイズ超過
- 500 Internal Server Error: サーバー側エラー

---

## GET /api/v1/results/{job_id}

### 概要
指定したジョブIDの解析結果JSONをダウンロードします。ジョブが完了していない場合はエラーとなります。

### リクエスト
- メソッド: GET
- パス: `/api/v1/results/{job_id}`
- パスパラメータ:
  - `job_id`: 解析ジョブのID（UUID）

### レスポンス
- ステータス: 200 OK
- Content-Type: `application/json`
- Body: 解析結果JSON

#### 解析結果JSON例
```json
{
  "job_id": "uuid-123",
  "match_id": "match-20251231",
  "video_duration": 150.5,
  "frame_rate": 30,
  "analysis_version": "v0.1.0",
  "shots": [ { "shot_id":"s1","start_sec":12.3,"end_sec":13.1,"confidence":0.92 } ],
  "players": [ { "player_id":"p23","team":"home","bbox":{"x":100,"y":50,"w":40,"h":120},"confidence":0.95 } ],
  "events": [ { "event_id":"e1","type":"shot","timestamp_sec":12.7,"players":["p23"],"meta":{"made":true},"confidence":0.9 } ],
  "summary": { "total_shots":10, "total_events":25 },
  "attachments": { "annotated_video_url": null }
}
```

### エラー例
- 404 Not Found: ジョブIDが存在しない、または未完了
- 500 Internal Server Error: サーバー側エラー

---

## 備考
- 本APIは非同期処理を前提としています。解析完了後はGETで結果を取得してください。
- 認証（APIキー/JWT）、レート制限、ファイルサイズ制限は今後追加予定
- 詳細なJSONスキーマは `README.md` 参照
