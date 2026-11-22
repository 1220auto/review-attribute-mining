# 데이터 / データ

[한국어](#한국어) | [日本語](#日本語)

---

## 한국어

이 레포에는 데이터 파일이 들어 있지 않다. 원본은 아래 공개 경로에서 직접 받는다.

### 출처

[McAuley-Lab/Amazon-Reviews-2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) (Hugging Face).
데이터셋 관리자는 HF 토론 게시판에서 이 데이터셋에 라이선스를 부여할 수 없다고 밝혔다
([Discussion #1](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/discussions/1)).
그래서 원본과 원본에서 만든 파생 파일을 이 레포로 재배포하지 않는다.

### 1. 전처리 노트북 (All_Beauty)

노트북이 Hugging Face에서 직접 불러오므로 따로 받을 필요는 없다.

| 용도 | 경로 | 크기 |
|---|---|---|
| 상품 메타 | `raw_meta_All_Beauty/full-00000-of-00001.parquet` | 59.6 MB |
| 리뷰 | `raw/review_categories/All_Beauty.jsonl` | - |

전체 규모는 메타 112,590개, 리뷰 701,528건이다. 제출 버전 노트북은 이 중
메타 앞 15,045개, 리뷰 앞 12,358건만 사용했다 (`select(range(N))`, 무작위 추출 아님).

### 2. 추천 앱 (Grocery_and_Gourmet_Food)

| 파일 | 내용 | 받는 방법 |
|---|---|---|
| `meta_Grocery_and_Gourmet_Food.jsonl` | 상품명·가격·이미지 URL 표시용 메타 | HF `raw/meta_categories/` (1.38 GB) |
| `product_vectors.npz` | 50,000 상품 × 9,976 속성 희소행렬 (값: 속성별 감성 -1~1) | **이 레포에서 재생성 불가** |
| `row_parent_asin.csv` | 행렬의 행 = 상품 ASIN | 위와 같음 |
| `col_aspect_index.csv` | 행렬의 열 = 속성(aspect) 이름 | 위와 같음 |

`product_vectors.npz`와 두 인덱스 CSV는 팀원(김병승)이 spaCy + VADER로 만든 파생 파일이다.
생성 코드는 이 레포에 없다. 앱은 이 세 파일이 없으면 실행을 멈추고, 메타 jsonl이 없으면
상품명과 이미지 없이 동작한다.

---

## 日本語

このリポジトリにはデータファイルを含めていない。元データは下記の公開パスから各自で取得する。

### 出典

[McAuley-Lab/Amazon-Reviews-2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023)（Hugging　Face）。
データセット管理者はHFのディスカッションで、このデータセットにライセンスを付与できる立場にないと述べている
（[Discussion　#1](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/discussions/1)）。
そのため、元データおよび元データから作成した派生ファイルはこのリポジトリで再配布しない。

### 1.　前処理ノートブック（All_Beauty）

ノートブックがHugging　Faceから直接読み込むため、事前のダウンロードは不要。

| 用途 | パス | サイズ |
|---|---|---|
| 商品メタデータ | `raw_meta_All_Beauty/full-00000-of-00001.parquet` | 59.6 MB |
| レビュー | `raw/review_categories/All_Beauty.jsonl` | - |

全体の規模はメタデータ112,590件、レビュー701,528件。提出版ノートブックはそのうち
メタデータ先頭15,045件、レビュー先頭12,358件のみを使用した（`select(range(N))`、ランダム抽出ではない）。

### 2.　推薦アプリ（Grocery_and_Gourmet_Food）

| ファイル | 内容 | 取得方法 |
|---|---|---|
| `meta_Grocery_and_Gourmet_Food.jsonl` | 商品名・価格・画像URL表示用メタデータ | HF　`raw/meta_categories/`（1.38 GB） |
| `product_vectors.npz` | 50,000商品×9,976属性の疎行列（値：属性ごとの感情スコア　-1〜1） | **このリポジトリでは再生成不可** |
| `row_parent_asin.csv` | 行列の行＝商品ASIN | 同上 |
| `col_aspect_index.csv` | 行列の列＝属性（aspect）名 | 同上 |

`product_vectors.npz`と2つのインデックスCSVは、チームメンバー（김병승／キム・ビョンスン）がspaCy＋VADERで作成した派生ファイルである。
生成コードはこのリポジトリに含まれていない。アプリはこの3ファイルがないと停止し、メタデータjsonlがない場合は
商品名と画像なしで動作する。
