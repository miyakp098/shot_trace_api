# 非同期APIシーケンス


```mermaid
sequenceDiagram
    actor User as User(画面)
    participant API as APIサーバ (FastAPI)
    participant Worker as Worker
    participant Storage as DB

    Note over User,Storage: 動画と付加情報の送信・ジョブ登録
    User->>API: POST /api/v1/analyze (動画+付加情報)
    API->>Worker: ジョブ登録 (uuid, metadata, 動画データ)
    API-->>User: 202 Accepted (uuid, status=queued)

    Note over Worker: 解析処理
    Worker->>Worker: 解析処理（AI推論等）
    Worker->>Storage: 結果JSON保存 (uuid)
    Storage-->>Worker: 保存結果 (OK)
    Worker->>API: ジョブ完了通知 (uuid, status=completed)
    API->>User: 完了通知 (uuid, status=completed)

    Note over User,Storage: 結果取得
    User->>API: GET /api/v1/results/{uuid}
    API->>Storage: 結果JSON取得 (uuid)
    Storage-->>API: 取得成功 (OK)
    API-->>User: 200 OK (解析結果JSON)
```


