import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="BV計データ解析アプリ", layout="wide")
st.title("\U0001f489 血液ボリューム (BV)・透析評価ツール")

uploaded_file = st.file_uploader("CSVデータをアップロード", type=["csv"])
dw_input = st.number_input("DW (ドライウェイト) を入力してください", min_value=30.0, max_value=120.0, value=60.0, step=0.1)

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="shift_jis")

    with st.expander("データサマリを表示（任意）"):
        st.dataframe(df.head())

    df['Time(min)'] = df['treat-time[sec]'] / 60
    df['BV'] = df['dBV[%]*10'] / 10
    df['UF_rate'] = df['UFP-speed[L/h]*100'] / 100
    df['UF_volume'] = df['UF-volume[L]*100'] / 100
    df['SBP'] = df['sys-BP[mmHg]']
    df['DBP'] = df['dia-BP[mmHg]']
    df['Pulse'] = df['pulse[bpm]']
    df['MAP'] = df['DBP'] + (df['SBP'] - df['DBP']) / 3

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("BVの変化とリファレンス")
        fig1, ax1 = plt.subplots()
        ax1.plot(df['Time(min)'], df['BV'], label="BV", color='blue', linestyle='-', marker='o')
        ax1.axhline(y=0, color='black', linestyle='--')
        ax1.fill_between(df['Time(min)'], -20, -8, color='red', alpha=0.3, label="危険域")
        ax1.fill_between(df['Time(min)'], -8, 0, color='yellow', alpha=0.3, label="注意域")
        ax1.set_xlabel("時間 (分)")
        ax1.set_ylabel("BV (%変化)")
        ax1.set_title("BV動態と評価ゾーン")
        ax1.legend()
        st.pyplot(fig1)

    with col2:
        st.subheader("血圧とMAPの推移")
        fig2, ax2 = plt.subplots()
        ax2.plot(df['Time(min)'], df['SBP'], label="SBP", color='orange', marker='.')
        ax2.plot(df['Time(min)'], df['DBP'], label="DBP", color='purple', marker='.')
        ax2.plot(df['Time(min)'], df['MAP'], label="MAP", color='gray', linestyle='--')
        ax2.set_xlabel("時間 (分)")
        ax2.set_ylabel("血圧 (mmHg)")
        ax2.legend()
        st.pyplot(fig2)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("除水速度とPRR")
        fig3, ax3 = plt.subplots()
        ax3.plot(df['Time(min)'], df['UF_rate'], label="除水速度 (L/h)", color='green', marker='.')
        if 'PRR[L/h]*100' in df.columns:
            df['PRR'] = df['PRR[L/h]*100'] / 100
            ax3.plot(df['Time(min)'], df['PRR'], label="PRR (L/h)", color='red', linestyle='--')
        ax3.set_xlabel("時間 (分)")
        ax3.set_ylabel("速度")
        ax3.legend()
        st.pyplot(fig3)

    with col4:
        st.subheader("心拍数の推移")
        fig4, ax4 = plt.subplots()
        ax4.plot(df['Time(min)'], df['Pulse'], label="Pulse", color='red', marker='.')
        ax4.set_xlabel("時間 (分)")
        ax4.set_ylabel("拍動数 (bpm)")
        ax4.legend()
        st.pyplot(fig4)

    st.subheader("\U0001f4cb 評価結果")

    prr = (df['BV'].iloc[-1] - df['BV'].iloc[0]) / (df['Time(min)'].iloc[-1] - df['Time(min)'].iloc[0])
    st.markdown(f"**PRR**: {prr:.2f} %/min")
    if prr < -0.05:
        st.error("PRRが低下 → 除水速度過剰の可能性")
    elif prr > 0:
        st.warning("BVが増加傾向 → DW再評価が必要")
    else:
        st.success("PRRは安定")

    sbp_drop = df['SBP'].iloc[0] - df['SBP'].min()
    low_bp_events = (df['SBP'] < 100).sum()
    st.markdown(f"**収縮期血圧低下量**: {sbp_drop:.1f} mmHg")
    st.markdown(f"**SBP 100mmHg未満のイベント回数**: {low_bp_events} 回")
    if sbp_drop >= 20:
        st.error("SBP急降下 → 循環動態不安定")
    elif sbp_drop >= 10:
        st.warning("SBPがやや低下傾向")
    else:
        st.success("血圧変動は許容範囲")

    uf_rate_kg = df['UF_rate'].mean() * 1000 / dw_input
    st.markdown(f"**除水速度 (mL/hr/kg)**: {uf_rate_kg:.2f}")
    if uf_rate_kg > 13:
        st.error("危険レベルの除水速度")
    elif uf_rate_kg > 10:
        st.warning("やや高めの除水速度")
    elif uf_rate_kg >= 5:
        st.success("適切な除水速度")
    else:
        st.warning("除水速度が低すぎる可能性")

    pulse_var = df['Pulse'].max() - df['Pulse'].min()
    st.markdown(f"**Pulse変動幅**: {pulse_var:.1f} bpm")
    if pulse_var > 20:
        st.warning("Pulse変動が大きく循環不安定の可能性")
    else:
        st.success("Pulseは安定しています")
