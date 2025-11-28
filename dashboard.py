import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Настройка страницы
st.set_page_config(
    page_title="Анализатор видео - PyCharm",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 ДАШБОРД АНАЛИЗА ВИДЕО")
st.markdown("---")

# Боковая панель
with st.sidebar:
    st.header("⚙️ Настройки")

    uploaded_file = st.file_uploader(
        "Загрузите видеофайл",
        type=['mp4', 'avi', 'mov']
    )

    analysis_frequency = st.slider(
        "Частота анализа (кадров/сек)",
        0.1, 10.0, 1.0
    )

    confidence_threshold = st.slider(
        "Порог уверенности",
        0.1, 1.0, 0.5
    )

    analyze_btn = st.button("🚀 Запустить анализ", type="primary")


# Имитация нейросети
class VideoAnalyzer:
    def __init__(self):
        self.classes = ['человек', 'автомобиль', 'животное', 'лицо']

    def analyze_frame(self, frame_num):
        np.random.seed(frame_num)
        detections = []

        for i in range(np.random.randint(1, 4)):
            detections.append({
                'class': np.random.choice(self.classes),
                'confidence': np.random.uniform(0.6, 0.95),
                'frame': frame_num,
                'timestamp': frame_num / 30
            })
        return detections


# Основная логика
if uploaded_file:
    st.subheader("📹 Предпросмотр видео")
    st.video(uploaded_file)

    st.subheader("📊 Информация о видео")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Статус", "Готов к анализу")
    with col2:
        st.metric("Размер файла", f"{uploaded_file.size / 1024 / 1024:.1f} MB")
    with col3:
        st.metric("Тип файла", uploaded_file.type)

if analyze_btn and uploaded_file:
    st.subheader("📈 Результаты анализа")

    progress_bar = st.progress(0)
    status_text = st.empty()

    analyzer = VideoAnalyzer()
    all_detections = []

    # Имитация анализа
    for i in range(10):
        progress_bar.progress((i + 1) * 10)
        status_text.text(f"Анализ кадра {i + 1}/10")

        detections = analyzer.analyze_frame(i)
        all_detections.extend(detections)

        # Имитация задержки
        import time

        time.sleep(0.5)

    status_text.text("Анализ завершен!")

    # Показ результатов
    if all_detections:
        df = pd.DataFrame(all_detections)

        st.subheader("📊 Статистика")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Всего объектов", len(df))
        with col2:
            st.metric("Уникальные классы", df['class'].nunique())
        with col3:
            st.metric("Средняя уверенность", f"{df['confidence'].mean():.2f}")

        st.subheader("📋 Таблица обнаружений")
        st.dataframe(df)

        st.subheader("📈 Визуализация")
        fig = px.pie(df, names='class', title='Распределение по классам')
        st.plotly_chart(fig)

        fig2 = px.bar(df, x='class', y='confidence', title='Уверенность по классам')
        st.plotly_chart(fig2)
    else:
        st.warning("Объекты не обнаружены")

else:
    st.info("👈 Загрузите видеофайл и настройте параметры анализа")