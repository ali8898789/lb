import streamlit as st
from streamlit_autorefresh import st_autorefresh
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="A股两连板监控", layout="wide")
st.title("📈 A股两连板实时监控系统")

# 自动刷新间隔（单位：毫秒）
st_autorefresh(interval=300000, key="lianban_refresh")  # 每5分钟刷新一次

def get_zt_data_safe(date_str):
    try:
        df = ak.stock_zt_pool_em(date=date_str)

        # 判断所需字段是否都在
        expected_cols = ["序号", "代码", "名称", "涨跌幅", "最新价", "成交额", "流通市值", "总市值", "换手率", "封板资金", "首次封板时间", "最后封板时间", "炸板次数", "涨停统计", "连板数", "所属行业"]
        missing = [col for col in expected_cols if col not in df.columns]

        if missing:
            print(f"[⚠️] 日期 {date_str} 缺少字段: {missing}")
            return pd.DataFrame()  # 返回空表避免程序崩溃

        return df[expected_cols]
    except Exception as e:
        print(f"[❌] 获取 {date_str} 涨停数据失败: {e}")
        return pd.DataFrame()

df = get_zt_data_safe("20250618")
if df.empty:
    st.warning("今日涨停数据抓取失败或数据字段缺失")
else:
    st.dataframe(df)


df = ak.stock_zt_pool_em(date="20250618")
print(df.columns.tolist())

# 获取今天和昨天的日期
today = datetime.now()
#today = "20150618"
yesterday = today - timedelta(days=1)

today_str = today.strftime("%Y%m%d")
yesterday_str = yesterday.strftime("%Y%m%d")

# 获取涨停数据
with st.spinner("正在加载今日和昨日的涨停数据..."):
    df_today = get_zt_data_safe(today_str)
    df_yesterday = get_zt_data_safe(yesterday_str)

# 合并找出两连板
if not df_today.empty and not df_yesterday.empty:
    # 获取昨日涨停股票代码集合
    yesterday_codes = set(df_yesterday["代码"].tolist())

    # 过滤今日涨停股票中，昨天也涨停过的
    df_lianban = df_today[df_today["代码"].isin(yesterday_codes) & (df_today["连板数"] >= 3)]
    df_lianban = df_lianban.sort_values(by="连板数", ascending=False).reset_index(drop=True)

    st.success(f"✅ 当前共检测到 {len(df_lianban)} 只两连板股票：")
    st.dataframe(df_lianban, use_container_width=True)
else:
    st.warning("暂无可用数据，请稍后再试。")
