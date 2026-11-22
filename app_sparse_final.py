import os
import numpy as np
import pandas as pd
import scipy.sparse as sp
import streamlit as st
from sklearn.preprocessing import normalize

# ----------------------------------------------------
# 기본 환경
# ----------------------------------------------------
st.set_page_config(page_title="Aspect-Opinion 추천 ", layout="wide")
st.title("Aspect-Opinion 기반 상품 추천")

# ----------------------------------------------------
# 사용할 파일
# ----------------------------------------------------
NPZ  = "product_vectors.npz"
ROW  = "row_parent_asin.csv"
COL  = "col_aspect_index.csv"
META = "meta_Grocery_and_Gourmet_Food.jsonl"

# ----------------------------------------------------
# Sidebar: 파일 검증
# ----------------------------------------------------
with st.sidebar:
    st.header("파일 검증")
    st.write(os.listdir())

    def file_ok(p):
        if os.path.exists(p):
            st.success(f"✔ {p} 발견")
            return True
        else:
            st.error(f"❌ {p} 없음")
            return False

    if not all([file_ok(NPZ), file_ok(ROW), file_ok(COL)]):
        st.stop()


# ----------------------------------------------------
# 데이터 로딩
# ----------------------------------------------------
@st.cache_resource(show_spinner=True)
def load_sparse():
    mat = sp.load_npz(NPZ).tocsr().astype(np.float32)

    df_row = pd.read_csv(ROW)
    df_col = pd.read_csv(COL)

    asins = df_row["parent_asin"].astype(str).tolist()
    aspects = df_col["aspect"].astype(str).tolist()

    mat_norm = normalize(mat, axis=1, copy=True)

    return mat, mat_norm, asins, aspects


@st.cache_resource(show_spinner=True)
def load_meta(path: str):
    if not os.path.exists(path):
        return {}

    import json
    meta = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except:
                continue

            asin = str(obj.get("parent_asin", "")).strip()
            if not asin:
                continue

            title = obj.get("title", "")
            price = obj.get("price")
            image = None

            imgs = obj.get("images") or []
            for key in ("hi_res", "large", "thumb"):
                if image:
                    break
                for im in imgs:
                    if isinstance(im, dict) and im.get(key):
                        image = im.get(key)
                        break

            meta[asin] = {"title": title, "price": price, "image": image}
    return meta


mat, mat_norm, asins, aspects = load_sparse()
meta_map = load_meta(META)

N_ITEMS, N_ASPECTS = mat.shape

# ----------------------------------------------------
# 유효한 속성 필터링
# ----------------------------------------------------
csc = mat.tocsc()
col_nnz = np.diff(csc.indptr)
valid_aspects = [aspects[i] for i in range(len(aspects)) if col_nnz[i] > 0]

st.sidebar.write(f"총 속성 수: {len(aspects):,}")
st.sidebar.write(f"유효 속성 수: {len(valid_aspects):,}")


# ----------------------------------------------------
# (1) 기준 상품 선택
# ----------------------------------------------------
st.header("1) 기준 상품 선택")

asin = st.selectbox("상품 선택", options=asins, index=0)
asin_idx = asins.index(asin)

# 세션 상태 초기화
if "base_vec" not in st.session_state or st.session_state.get("last_asin") != asin:
    st.session_state.base_vec = mat.getrow(asin_idx).toarray().ravel().astype(np.float32)
    st.session_state.last_asin = asin

base_vec = st.session_state.base_vec


def show_meta(a):
    m = meta_map.get(a, {})
    title = m.get("title", "")
    price = m.get("price", "")
    image = m.get("image")

    c1, c2 = st.columns([1, 3])
    with c1:
        if image:
            st.image(image, caption=a, use_container_width=True)
        else:
            st.write("(이미지 없음)")
    with c2:
        st.write(f"**ASIN:** `{a}`")
        st.write(f"**상품명:** {title}")
        st.write(f"**가격:** {price}")

show_meta(asin)


# ----------------------------------------------------
# (2) 속성 편집
# ----------------------------------------------------
st.header("2) 오피니언(속성 감성) 수정")

nz_idx = np.flatnonzero(base_vec)
cur_aspects = [aspects[i] for i in nz_idx]
cur_values = [float(base_vec[i]) for i in nz_idx]

with st.expander(f"현재 속성 {len(cur_aspects)}개 (수정/삭제)", expanded=False):

    df_edit = pd.DataFrame({
        "aspect": cur_aspects,
        "sentiment": cur_values,
        "삭제": [False]*len(cur_aspects)
    })

    edited = st.data_editor(
        df_edit,
        num_rows="dynamic",
        key="editor_v9",
        column_config={
            "aspect": st.column_config.TextColumn(disabled=True),
            "sentiment": st.column_config.NumberColumn(min_value=-1, max_value=1, step=0.05),
            "삭제": st.column_config.CheckboxColumn(),
        },
    )

if edited is not None:
    new_vec = base_vec.copy()

    for _, row in edited.iterrows():
        idx = aspects.index(row["aspect"])
        if row["삭제"]:
            new_vec[idx] = 0.0
        else:
            new_vec[idx] = np.float32(float(row["sentiment"]))

    st.session_state.base_vec = new_vec
    base_vec = new_vec



st.subheader("속성 추가")

aspect_counts = np.diff(mat.tocsc().indptr)
top150_aspects = [
    aspects[i] for i in np.argsort(-aspect_counts)[:150]
    if aspect_counts[i] > 0
]


c1, c2, c3 = st.columns([2, 2, 1])

with c1:
    selected_aspect = st.selectbox(
        "추천 속성",
        options=top150_aspects,
        key="add_aspect_top150"
    )

with c2:
    user_input_aspect = st.text_input(
        "직접 속성 입력",
        placeholder="원하는 속성을 직접 입력"
    )

# 최종 aspect 결정: 직접 입력 > 추천 선택
final_aspect = user_input_aspect.strip() if user_input_aspect.strip() else selected_aspect

with c3:
    add_value = st.number_input(
        "감성값(-1~1)",
        -1.0, 1.0, 0.3, step=0.05,
        key="add_value_top150"
    )

# 속성 추가/갱신 버튼
if st.button("속성 추가/갱신", key="btn_add_top150"):
    if final_aspect not in aspects:
        st.warning(f"'{final_aspect}' 는 전체 벡터에 존재하지 않아 적용할 수 없습니다.")
    else:
        idx = aspects.index(final_aspect)
        st.session_state.base_vec[idx] = np.float32(add_value)
        base_vec = st.session_state.base_vec
        st.success(f"{final_aspect} = {add_value} 적용 완료!")


# ----------------------------------------------------
# (3) 추천 계산
# ----------------------------------------------------
st.header("3) 추천 계산")

topk = st.number_input("추천 개수", 5, 100, 20, step=5)

if st.button("추천 계산"):
    base_vec = st.session_state.base_vec

    v_norm = normalize(base_vec.reshape(1, -1), axis=1).astype(np.float32)
    sim = (mat_norm @ v_norm.T).ravel()
    sim[asin_idx] = -np.inf

    K = min(int(topk), len(sim) - 1)
    idx = np.argpartition(-sim, K)[:K]
    idx = idx[np.argsort(-sim[idx])]
    scores = sim[idx]

    result = []
    for r, (i, sc) in enumerate(zip(idx, scores), start=1):
        a = asins[i]
        meta = meta_map.get(a, {})
        result.append({
            "rank": r,
            "parent_asin": a,
            "title": meta.get("title", ""),
            "price": meta.get("price", ""),
            "image": meta.get("image", ""),
            "similarity": round(float(sc), 4),
        })

    df_rec = pd.DataFrame(result)

    st.success("추천 계산 완료!")

    cols = st.columns(4)
    for k in range(min(8, len(df_rec))):
        row = df_rec.iloc[k]
        with cols[k % 4]:
            if row["image"]:
                st.image(row["image"], use_container_width=True)
            st.caption(f"{row['rank']}. {row['title']} (sim={row['similarity']})")

    st.dataframe(df_rec.drop(columns=["image"]), use_container_width=True)

    st.download_button(
        "CSV 다운로드",
        df_rec.to_csv(index=False).encode("utf-8"),
        file_name="recommendations_v9_small.csv",
        mime="text/csv"
    )
