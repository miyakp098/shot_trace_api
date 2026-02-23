# shot_trace_api

## 概要
`shot_trace_api` は、モバイルやカメラで撮影したバスケットボールの動画を受け取り、ショット検出、選手検出・追跡、イベント抽出などの解析を行って結果をJSONで返すためのAPIプロジェクト向けのリポジトリです。

設計方針は次の通りです。
- 動画はクライアントからアップロードされ、重い解析は非同期ジョブで実行する（短い動画は同期解析もオプションで対応）。
- 解析結果は一貫したJSONスキーマで返却し、アプリ側で表示・集計・再生アノテーションに利用できるようにする。

## 推奨スタック
- 言語 / フレームワーク: `Python` + `FastAPI`（ASGI、型安全、OpenAPI自動生成）
- 非同期ジョブキュー: `Celery` + `Redis` または軽量なら `RQ` + `Redis`（重い解析はワーカーで処理）
- 動画処理: `ffmpeg`（変換/サムネイル生成）、`OpenCV`（フレーム処理）
- モデル実行: `PyTorch` または `TensorFlow`（物体検出・トラッキング・分類）
- ストレージ: ローカル一時保存 → 本番は `S3` 互換ストレージ（例: AWS S3、MinIO）
- データベース: `Postgres`（ジョブメタ・結果参照）／プロトタイプは `SQLite` でも可
- 実行サーバ: `uvicorn`（ASGI）
- 補助ライブラリ: `pydantic`（入力・出力バリデーション）、`aiofiles`（大きなファイル処理）、`python-multipart`（multipart対応）

## API 概要
- `POST /api/v1/analyze` : 動画ファイルとメタデータを送信して解析ジョブを作成。
  - 入力: `multipart/form-data` (`file`, `metadata` JSON文字列, `callback_url` など)
  - 出力（非同期）: `{ "job_id": "<uuid>", "status": "queued" }` (HTTP 202)
  - 出力（同期）: `{ "job_id":"...","status":"completed","result": {...} }` (HTTP 200)
- `GET /api/v1/jobs/{job_id}` : ジョブの状態、進捗、結果（完了時）を取得
- `GET /api/v1/results/{job_id}` : 完了ジョブの解析結果JSONをダウンロード
- `WS /api/v1/ws/jobs/{job_id}` : ジョブ進捗のリアルタイム通知（任意）

## 解析結果（JSON） - 例スキーマ
ルートにはジョブ情報と解析の要約を置き、`shots` / `players` / `events` を配列で返します。例:

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

## 次のステップ
- 非同期ワーカー（`Celery` + `Redis`）導入
- S3 連携と結果保存
- 認証（APIキー / JWT）、レート制限、ファイルサイズ制限の実装
- JSON Schema の確定と OpenAPI への組み込み


## Dockerで起動する

開発コンテナで起動する手順:

```bash
# イメージをビルド（server サービス）
docker compose build server

# バックグラウンドで起動
docker compose up -d

# ブラウザで Swagger UI を開く
# http://127.0.0.1:8000
```