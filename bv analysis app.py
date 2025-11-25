import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# アプリタイトル
st.set_page_config(page_title="BV評価ツール", layout="wide")
st.title("\u8840\u6db2\u30dc\u30ea\u30e5\u30fc\u30e0 (BV)\u8a55\u4fa1 & \u9664\u6c34\u30ea\u30b9\u30af\u691c\u77e5")

# ファイルアップロード
uploaded_file = st.file_uploader("CSV\u30c7\u30fc\u30bf\u3092\u30a2\u30c3\u30d7\u30ed\u30fc\u30c9", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="shift_jis")
    st.write("\u30c7\u30fc\u30bf\u30b5\u30de\u30ea")
    st.dataframe(df.head())

    # ------
    # 初期処理 ------
    df['Time(min)'] = df['treat-time[sec]'] / 60
    df['BV'] = df['dBV[%]*10'] / 10
    df['UF_rate'] = df['UFP-speed[L/h]*100'] / 100
    df['UF_volume'] = df['UF-volume[L]*100'] / 100
    df['SBP'] = df['sys-BP[mmHg]']
    df['DBP'] = df['dia-BP[mmHg]']
    df['Pulse'] = df['pulse[bpm]']
    df['MAP'] = df['DBP'] + (df['SBP'] - df['DBP']) / 3

    # 体重の自動抽出（列に存在する場合）
    if 'Weight(kg)' in df.columns:
        weight_est = df['Weight(kg)'].iloc[0]
        st.markdown(f"**抽出された体重**: {weight_est:.1f} kg")
    else:
        weight_est = 50  # 仮定
        st.warning("体重情報が見つかりませんでした。仮の50kgで計算しています")

    # ------
    # グラフ表示 ------
    st.subheader(":bar_chart: BV, BP, UF, Pulse \u306e\u63a8\u79fb")

    # BV
    fig1, ax1 = plt.subplots()
    ax1.plot(df['Time(min)'], df['BV'], label="BV", color='blue')
    ax1.axhline(y=95, color='red', linestyle='--', label="Lower Ref")
    ax1.axhline(y=105, color='green', linestyle='--', label="Upper Ref")
    ax1.set_xlabel("Time (min)")
    ax1.set_ylabel("BV (%)")
    ax1.legend()
    st.pyplot(fig1)

    # BP
    fig2, ax2 = plt.subplots()
    ax2.plot(df['Time(min)'], df['SBP'], label="SBP", color='orange')
    ax2.plot(df['Time(min)'], df['DBP'], label="DBP", color='purple')
    ax2.plot(df['Time(min)'], df['MAP'], label="MAP", color='gray')
    ax2.set_xlabel("Time (min)")
    ax2.set_ylabel("BP (mmHg)")
    ax2.legend()
    st.pyplot(fig2)

    # UF rate
    fig3, ax3 = plt.subplots()
    ax3.plot(df['Time(min)'], df['UF_rate'], label="UF Rate", color='green')
    ax3.set_xlabel("Time (min)")
    ax3.set_ylabel("UF Rate (L/h)")
    ax3.legend()
    st.pyplot(fig3)

    # Pulse
    fig4, ax4 = plt.subplots()
    ax4.plot(df['Time(min)'], df['Pulse'], label="Pulse", color='red')
    ax4.set_xlabel("Time (min)")
    ax4.set_ylabel("Pulse (bpm)")
    ax4.legend()
    st.pyplot(fig4)

    # ------
    # 評価 ------
    st.subheader(":clipboard: \u8a55\u4fa1")

    # PRR
    prr = (df['BV'].iloc[-1] - df['BV'].iloc[0]) / (df['Time(min)'].iloc[-1] - df['Time(min)'].iloc[0])
    st.markdown(f"**PRR**: {prr:.2f} %/min")
    if prr < -0.05:
        st.error("\u9664\u6c34\u901f\u5ea6が\u9ad8\u3059\u304e\u3001PRR\u304c\u4f4e\u4e0b\u3057\u3066\u3044\u307e\u3059")
    elif prr > 0:
        st.warning("BV\u5897\u52a0 - DW\u8981\u691c\u8a0e")
    else:
        st.success("PRR\u306f\u9069\u5207")

    # SBP変化
    sbp_drop = df['SBP'].iloc[0] - df['SBP'].min()
    st.markdown(f"**収縮期血圧低下量**: {sbp_drop:.1f} mmHg")
    if sbp_drop > 30:
        st.error("\u53cd\u5fa9\u6027\u4f4e\u8840\u5727\u306e\u53ef\u80fd\u6027")
    else:
        st.success("BP\u5909\u5316\u306f\u53ef\u8a31\u7bc4\u56f2")

    # UF rate/kg
    uf_rate_kg = df['UF_rate'].mean() * 1000 / weight_est
    st.markdown(f"**除水速度 (mL/hr/kg)**: {uf_rate_kg:.2f}")
    if uf_rate_kg > 10:
        st.error("除水速度が高すぎます")
    else:
        st.success("除水速度は妥当です")

    # Pulse変動
    pulse_var = df['Pulse'].max() - df['Pulse'].min()
    st.markdown(f"**Pulse変動幅**: {pulse_var} bpm")
    if pulse_var > 20:
        st.warning("Pulse変動が大きいです。循環動態に注意")
    else:
        st.success("Pulseは安定しています")
