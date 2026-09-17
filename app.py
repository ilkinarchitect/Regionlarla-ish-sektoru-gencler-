import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------- SƏHİFƏ AYARLARI VƏ DİZAYN (İŞIQLI REJİM) -----------------
st.set_page_config(page_title="Tədbirlər Planı Analizi", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Açıq rəngli arxa fon */
    .stApp {background-color: #f7f9f8;} 
    h1, h2, h3 {color: #00995c !important; font-family: 'Arial', sans-serif;}
    [data-testid="stMetricValue"] {color: #ff7900 !important; font-weight: bold; font-size: 1.8rem;}
    /* Sol panelin rəngi (Ağ) */
    [data-testid="stSidebar"] {background-color: #ffffff; border-right: 1px solid #e0e0e0;}
    .stMultiSelect div div div {background-color: #00995c; color: white; border-radius: 5px;}
    /* Ümumi mətn rəngi tündləşdirilir ki, ağ fonda rahat oxunsun */
    p, span, label, .stMarkdown {color: #333333 !important;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("### **#Gənclər**")
st.title("Regionlarla İş Sektorunun Gənclərlə İş Sahəsi Üzrə Tədbirlər Planının Analizi")

# ----------------- DATA YÜKLƏNMƏSİ -----------------
def load_data():
    df = pd.read_excel("data.xlsx")
    df["Column1"] = pd.to_numeric(df.get("Column1"), errors='coerce').fillna(0)
    df["11. Kişi sayı:"] = pd.to_numeric(df.get("11. Kişi sayı:"), errors='coerce').fillna(0)
    df["12. Qadın sayı:"] = pd.to_numeric(df.get("12. Qadın sayı:"), errors='coerce').fillna(0)
    if "Tədbirlər planında var?" in df.columns:
        df["Tədbirlər planında var?"] = df["Tədbirlər planında var?"].fillna("Məlumat yoxdur")
    return df

df = load_data()

# ----------------- İCRA OLUNMAYAN TƏDBİRLƏR BAZASI -----------------
icra_olunmayanlar_bazasi = {
    "Quba-Xaçmaz": {"say": 11, "növ": "8 düşərgə + 2 ekskursiya + 1 ziyarət", "səbəb": "Maliyyə məsələləri + tədbirlər planının təsdiq olunmaması + nəqliyyat problemi"},
    "Mərkəzi Aran": {"say": 2, "növ": "görüş", "səbəb": "İştirakçıların tamamlanmaması + Şahinlərlə üst-üstə düşüb"},
    "Mil-Muğan": {"say": 4, "növ": "2 düşərgə + 1 intellektual oyun + 1 aksiya", "səbəb": "Tələbat materiallarının olmaması + Ezam xərclərinin mütənasib olmaması + komandaların formalaşmaması"},
    "Lənkəran-Astara": {"say": 4, "növ": "3 düşərgə + 1 konsert", "səbəb": "Maliyyə məsələləri + satınalma problemləri"},
    "Qazax-Tovuz": {"say": 5, "növ": "4 düşərgə + 1 forum", "səbəb": "Gec informasiya verilməsi + Nəqliyyat problemi + qonaqlama xərcləri"},
    "Bakı şəhər": {"say": 9, "növ": "ekskursiya + müsabiqə + intellektual oyun + festival", "səbəb": "Təminat olmadığına görə"},
    "Şərqi-Zəngəzur": {"say": 2, "növ": "ekskursiya/düşərgə", "səbəb": "Nəqliyyat problemi"},
    "Gəncə-Daşkəsən": {"say": 8, "növ": "düşərgə + intellektual oyun + görüş", "səbəb": "Maliyyə vəsaiti + Məkanla bağlı icazə verilməməsi + təlimçi olmaması"},
    "Dağlıq Şirvan": {"say": 3, "növ": "görüş + müsabiqə + seminar", "səbəb": "Hava şəraiti + Maddi-texniki təminat + Hesabatdan çıxarılan tədbirlər"},
    "Qarabağ": {"say": 19, "növ": "düşərgə + intellektual oyun + festival", "səbəb": "Maliyyə problemi + ESİ işləmədiyi üçün əmr yazıla bilmədi + iştirakçı qrupu formalaşmaması"},
    "Şəki-Zaqatala": {"say": 2, "növ": "aksiya + görüş", "səbəb": "Məkan problemi + Tədbir barədə əvvəlcədən məlumat verilməməsi"},
    "Şirvan-Salyan": {"say": 5, "növ": "ekskursiya + görüş", "səbəb": "Maddi vəsaitin olmaması (satınalma) + Hava şəraiti"},
    "Abşeron-Xızı": {"say": 7, "növ": "ekskursiya + festival + aksiya", "səbəb": "Maliyyə çatışmazlığı + hava şəraiti"}
}

def get_unexecuted_count(selected_qurumlar):
    if not selected_qurumlar:
        return sum(v["say"] for v in icra_olunmayanlar_bazasi.values())
    total = 0
    for qurum in selected_qurumlar:
        for key, val in icra_olunmayanlar_bazasi.items():
            if key in str(qurum):
                total += val["say"]
                break
    return total

df_sebebler = pd.DataFrame([
    {"İdarə": k, "Say": v["say"], "İcra olunmayan tədbir növləri": v["növ"], "Səbəb": v["səbəb"]}
    for k, v in icra_olunmayanlar_bazasi.items()
])

def get_unique_elements(series):
    elements = set()
    for item in series.dropna().astype(str):
        for val in item.split(';'):
            cleaned_val = val.strip(', ').strip()
            if cleaned_val:
                elements.add(cleaned_val)
    return sorted(list(elements))

qurumlar = sorted(df["1. İcraçı qurum:"].dropna().unique().tolist()) if "1. İcraçı qurum:" in df.columns else []
sektorlar = sorted(df["2. İcraçı sektor:"].dropna().unique().tolist()) if "2. İcraçı sektor:" in df.columns else []
plan_status = sorted(df["Tədbirlər planında var?"].dropna().unique().tolist()) if "Tədbirlər planında var?" in df.columns else []
novler = sorted(df["14. Tədbirin keçirilmə üsulu"].dropna().unique().tolist()) if "14. Tədbirin keçirilmə üsulu" in df.columns else []
saheler = get_unique_elements(df.get("15. Tədbir hansı sahəyə təsir edib ?"))
kateqoriyalar = get_unique_elements(df.get("10. Əhatə edilən gənclər kateqoriyası"))

# ----------------- SOL PANEL -----------------
st.sidebar.header("🔍 İdarəetmə Paneli")
st.sidebar.markdown("*(Seçim edilmədikdə bütün məlumatlar göstərilir)*")

secilmis_qurum = st.sidebar.multiselect("🏢 İdarəni Seçin:", qurumlar, default=[])
secilmis_sektor = st.sidebar.multiselect("🏛️ Sektoru Seçin:", sektorlar, default=[])
secilmis_plan = st.sidebar.multiselect("📋 İcra Vəziyyəti (Plan üzrə):", plan_status, default=[])
secilmis_nov = st.sidebar.multiselect("🎭 Tədbir Növü:", novler, default=[])

st.sidebar.divider()
st.sidebar.markdown("**Daha Dərin Analiz:**")
secilmis_sahe = st.sidebar.multiselect("🎯 Təsir Edilən Sahə:", saheler, default=[])
secilmis_kat = st.sidebar.multiselect("👥 Gənclər Kateqoriyası:", kateqoriyalar, default=[])

# ----------------- FİLTRLƏMƏ -----------------
df_filtered = df.copy()
df_sebebler_filtered = df_sebebler.copy()

if secilmis_qurum:
    df_filtered = df_filtered[df_filtered["1. İcraçı qurum:"].isin(secilmis_qurum)]
    df_sebebler_filtered = df_sebebler[df_sebebler["İdarə"].apply(lambda x: any(x in str(q) for q in secilmis_qurum))]

if secilmis_sektor:
    df_filtered = df_filtered[df_filtered["2. İcraçı sektor:"].isin(secilmis_sektor)]
if secilmis_plan:
    df_filtered = df_filtered[df_filtered["Tədbirlər planında var?"].isin(secilmis_plan)]
if secilmis_nov:
    df_filtered = df_filtered[df_filtered["14. Tədbirin keçirilmə üsulu"].isin(secilmis_nov)]

if secilmis_sahe:
    df_filtered = df_filtered[df_filtered["15. Tədbir hansı sahəyə təsir edib ?"].fillna("").astype(str).apply(
        lambda x: any(s in x for s in secilmis_sahe)
    )]

if secilmis_kat:
    df_filtered = df_filtered[df_filtered["10. Əhatə edilən gənclər kateqoriyası"].fillna("").astype(str).apply(
        lambda x: any(k in x for k in secilmis_kat)
    )]

if df_filtered.empty and df_sebebler_filtered.empty:
    st.warning("⚠️ Seçilmiş filtrlərə uyğun heç bir tədbir tapılmadı.")
    st.stop()

# ----------------- YENİLƏNMİŞ METRİKLƏR -----------------
st.subheader("📊 Analiz Nəticələri")

total_executed = len(df_filtered)
planned_executed = len(df_filtered[df_filtered["Tədbirlər planında var?"] == "Bəli"])
unexecuted_planned = get_unexecuted_count(secilmis_qurum) 
total_planned = planned_executed + unexecuted_planned
exec_rate = (planned_executed / total_planned * 100) if total_planned > 0 else 0

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
col1.metric("📌 İcra Olunan (Cəmi)", f"{total_executed}")
col2.metric("📋 Planda Nəzərdə Tutulan", f"{total_planned}")
col3.metric("✅ Plandan İcra", f"{planned_executed}")
col4.metric("❌ İcra Edilməyən", f"{unexecuted_planned}")
col5.metric("🎯 Planın İcra Faizi", f"{exec_rate:.1f}%")
col6.metric("👥 Əhatə Gənclər", f"{int(df_filtered['Column1'].sum()):,}")
col7.metric("👨/👩 Kişi-Qadın", f"{int(df_filtered['11. Kişi sayı:'].sum())} / {int(df_filtered['12. Qadın sayı:'].sum())}")

st.divider()

# ----------------- QRAFİKLƏR (QARA MƏTNLƏ) -----------------
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Tədbirlər Planının İcra Vəziyyəti")
    fig_donut = go.Figure(data=[go.Pie(
        labels=['İcra olunan (Plandan)', 'İcra olunmayan (Plandan)'], 
        values=[planned_executed, unexecuted_planned], 
        hole=.6
    )])
    # font=dict(color='#333333') məcburi tünd rəng əlavə edildi
    fig_donut.update_traces(textinfo='value', textfont_size=18, marker=dict(colors=['#00995c', '#ff7900']))
    fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='#333333'))
    st.plotly_chart(fig_donut, use_container_width=True)

with row1_col2:
    st.subheader("Tədbir Növləri Üzrə Bölgü")
    usul = df_filtered["14. Tədbirin keçirilmə üsulu"].value_counts().reset_index()
    usul.columns = ['Üsul', 'Say']
    fig_bar1 = px.bar(usul, x='Say', y='Üsul', orientation='h', color_discrete_sequence=['#00995c'])
    fig_bar1.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='#333333'))
    st.plotly_chart(fig_bar1, use_container_width=True)

def get_exploded_counts_filtered(col_name):
    if col_name not in df_filtered.columns:
        return pd.DataFrame()
    s = df_filtered[col_name].dropna().astype(str)
    s = s.apply(lambda x: [item.strip(', ').strip() for item in x.split(';') if item.strip(', ').strip()])
    counts = s.explode().value_counts().reset_index()
    counts.columns = ['Kateqoriya', 'Say']
    return counts

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Əhatə Olunan Gənclər Kateqoriyası")
    kat_df = get_exploded_counts_filtered("10. Əhatə edilən gənclər kateqoriyası")
    if not kat_df.empty:
        fig_bar2 = px.bar(kat_df.head(10), x='Say', y='Kateqoriya', orientation='h', color_discrete_sequence=['#b2b87e'])
        fig_bar2.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='#333333'))
        st.plotly_chart(fig_bar2, use_container_width=True)

with row2_col2:
    st.subheader("Tədbirlərin Təsir Etdiyi Sahələr")
    sahə_df = get_exploded_counts_filtered("15. Tədbir hansı sahəyə təsir edib ?")
    if not sahə_df.empty:
        fig_bar3 = px.bar(sahə_df.head(10), x='Say', y='Kateqoriya', orientation='h', color_discrete_sequence=['#006b3f'])
        fig_bar3.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='#333333'))
        st.plotly_chart(fig_bar3, use_container_width=True)

st.divider()

# ----------------- DETALLI MƏLUMAT CƏDVƏLLƏRİ -----------------
st.subheader("📋 İcra Olunan Tədbirlərin Siyahısı")
columns_to_show = ["1. İcraçı qurum:", "2. İcraçı sektor:", "3. Tədbirin/fəaliyyətin/layihənin adı", "14. Tədbirin keçirilmə üsulu", "15. Tədbir hansı sahəyə təsir edib ?", "Column1", "Tədbirlər planında var?"]
available_cols = [c for c in columns_to_show if c in df_filtered.columns]
st.dataframe(df_filtered[available_cols], use_container_width=True)

st.divider()

st.subheader("⚠️ İcra Olunmayan Tədbirlər və Səbəbləri")
if df_sebebler_filtered.empty:
    st.success("Seçilmiş kriteriyalara uyğun icra olunmayan tədbir yoxdur.")
else:
    st.dataframe(df_sebebler_filtered, use_container_width=True, hide_index=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("**İcraçı: Regionlarla iş sektoru**")