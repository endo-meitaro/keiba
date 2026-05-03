import streamlit as st
import pandas as pd
from scraper import get_all_race_data

st.title("🐎 競馬AI予想（完全修正版）")

date = st.text_input("開催日（例：20260503）")

if st.button("AI予想開始"):

    if not date:
        st.warning("日付を入力してください")
        st.stop()

    progress_bar = st.progress(0)
    status_text = st.empty()

    def progress_callback(current, total, rid):
        progress_bar.progress(current / total)
        status_text.text(f"🏁 {rid} 処理中 ({current}/{total})")

    data = get_all_race_data(date, progress_callback)

    progress_bar.empty()
    status_text.empty()

    if not data:
        st.error("データ取得失敗")
        st.stop()

    df = pd.DataFrame(data)

    # =========================
    # スコア
    # =========================
    df["score"] = 1 / (df["odds"] + 1)

    df = df.sort_values(["race_id", "score"], ascending=[True, False])

    # =========================
    # 表示
    # =========================
    for race_id, race_df in df.groupby("race_id"):

        st.subheader(f"🏁 {race_id}")

        show_df = race_df[[
            "umaban",
            "horse",
            "jockey",
            "weight",
            "odds",
            "score"
        ]]

        # 🔥 index完全消す（重要）
        st.dataframe(show_df, use_container_width=True, hide_index=True)

        st.markdown("### 🏆 TOP5")

        for i, row in enumerate(show_df.head(5).itertuples()):

            st.write(
                f"{i+1}位: {row.horse} "
                f"(馬番:{row.umaban} / 騎手:{row.jockey} / 斤量:{row.weight} / オッズ:{row.odds:.2f})"
            )

    df.to_csv("keiba_result.csv", index=False)
    st.success("完了＆CSV保存")