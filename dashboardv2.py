import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Настройка страницы
st.set_page_config(
    page_title="Анализатор видео - PyCharm",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 ДАШБОРД АНАЛИЗА ВИДЕО ДЛЯ БЕЗОПАСНОСТИ ТРУДА")
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


# Имитация нейросети с расширенной функциональностью
class VideoAnalyzer:
    def __init__(self):
        self.classes = ['человек', 'автомобиль', 'животное', 'лицо']
        self.danger_actions = [
            'падение', 'быстрое движение', 'нахождение в опасной зоне',
            'неправильное использование оборудования', 'отсутствие СИЗ'
        ]

    def analyze_frame(self, frame_num):
        np.random.seed(frame_num)
        detections = []

        for i in range(np.random.randint(1, 4)):
            detections.append({
                'class': np.random.choice(self.classes),
                'confidence': np.random.uniform(0.6, 0.95),
                'frame': frame_num,
                'timestamp': frame_num / 30,
                'speed': np.random.uniform(0.5, 5.0),  # м/с
                'in_danger_zone': np.random.choice([True, False], p=[0.2, 0.8]),
                'has_ppe': np.random.choice([True, False], p=[0.7, 0.3])  # СИЗ - средства индивидуальной защиты
            })
        return detections

    def detect_danger_actions(self, detections_history):
        """Обнаружение опасных действий на основе истории детекций"""
        dangerous_frames = []

        for frame_data in detections_history:
            for detection in frame_data:
                # Логика обнаружения опасных действий
                if detection['speed'] > 3.0:  # слишком быстрая ходьба/бег
                    dangerous_frames.append(('быстрое движение', detection['frame']))
                if not detection['has_ppe']:
                    dangerous_frames.append(('отсутствие СИЗ', detection['frame']))
                if detection['in_danger_zone']:
                    dangerous_frames.append(('нахождение в опасной зоне', detection['frame']))

        return dangerous_frames


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
    detections_history = []

    # Имитация анализа
    for i in range(10):
        progress_bar.progress((i + 1) * 10)
        status_text.text(f"Анализ кадра {i + 1}/10")

        detections = analyzer.analyze_frame(i)
        all_detections.extend(detections)
        detections_history.append(detections)

        # Имитация задержки
        import time

        time.sleep(0.3)

    status_text.text("Анализ завершен!")

    # Показ результатов
    if all_detections:
        df = pd.DataFrame(all_detections)

        # Расчет дополнительных метрик
        human_detections = df[df['class'] == 'человек']

        # Среднее время человека в кадре
        avg_human_time = len(human_detections) * (1 / analysis_frequency) if len(human_detections) > 0 else 0

        # Средняя скорость человека
        avg_human_speed = human_detections['speed'].mean() if len(human_detections) > 0 else 0

        # Количество опасных действий
        danger_actions = analyzer.detect_danger_actions(detections_history)
        danger_count = len(danger_actions)

        st.subheader("📊 Основная статистика")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Всего объектов", len(df))
        with col2:
            st.metric("Уникальные классы", df['class'].nunique())
        with col3:
            st.metric("Средняя уверенность", f"{df['confidence'].mean():.2f}")

        st.subheader("🚨 Анализ безопасности труда")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Среднее время человека в кадре",
                f"{avg_human_time:.1f} сек",
                delta=f"{len(human_detections)} обнаружений"
            )

        with col2:
            speed_status = "Высокая" if avg_human_speed > 2.5 else "Нормальная"
            st.metric(
                "Средняя скорость человека",
                f"{avg_human_speed:.1f} м/с",
                delta=speed_status,
                delta_color="inverse" if avg_human_speed > 2.5 else "normal"
            )

        with col3:
            st.metric(
                "Количество опасных действий",
                danger_count,
                delta="⚠️ Требует внимания" if danger_count > 0 else "✅ Безопасно",
                delta_color="inverse" if danger_count > 0 else "normal"
            )

        with col4:
            ppe_compliance = (df[df['class'] == 'человек']['has_ppe'].mean() * 100) if len(
                human_detections) > 0 else 100
            st.metric(
                "Соблюдение СИЗ",
                f"{ppe_compliance:.0f}%",
                delta="✅ Хорошо" if ppe_compliance > 80 else "⚠️ Нужно улучшить",
                delta_color="normal" if ppe_compliance > 80 else "off"
            )

        # Детализация опасных действий
        if danger_count > 0:
            st.subheader("📋 Детали опасных действий")
            danger_df = pd.DataFrame(danger_actions, columns=['Тип действия', 'Кадр'])
            st.dataframe(danger_df)

            # Визуализация опасных действий
            danger_by_type = danger_df['Тип действия'].value_counts()
            fig_danger = px.bar(
                x=danger_by_type.index,
                y=danger_by_type.values,
                title="Распределение опасных действий по типам",
                labels={'x': 'Тип действия', 'y': 'Количество'}
            )
            st.plotly_chart(fig_danger)

        st.subheader("📋 Таблица обнаружений")
        st.dataframe(df)

        st.subheader("📈 Визуализация")
        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(df, names='class', title='Распределение по классам')
            st.plotly_chart(fig)

        with col2:
            fig2 = px.bar(df, x='class', y='confidence', title='Уверенность по классам')
            st.plotly_chart(fig2)

        # Дополнительные графики
        if len(human_detections) > 0:
            col3, col4 = st.columns(2)

            with col3:
                fig3 = px.histogram(
                    human_detections,
                    x='speed',
                    title='Распределение скорости людей',
                    nbins=10
                )
                st.plotly_chart(fig3)

            with col4:
                # Временная шкала появления людей
                human_timeline = human_detections.groupby('frame').size().reset_index(name='count')
                fig4 = px.line(
                    human_timeline,
                    x='frame',
                    y='count',
                    title='Количество людей по кадрам'
                )
                st.plotly_chart(fig4)

    else:
        st.warning("Объекты не обнаружены")

else:
    st.info("👈 Загрузите видеофайл и настройте параметры анализа")

# Раздел с советами по повышению безопасности труда
st.markdown("---")
st.header("💡 Советы по повышению безопасности труда")

with st.expander("📋 Рекомендации на основе анализа", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🛡️ Профилактические меры")
        st.markdown("""
        - **Регулярный инструктаж** по технике безопасности
        - **Контроль скорости** перемещения в рабочих зонах
        - **Обязательное использование** СИЗ (средств индивидуальной защиты)
        - **Разметка опасных зон** яркой сигнальной окраской
        - **Установка предупреждающих знаков** и табличек
        """)

        st.subheader("📊 Мониторинг и анализ")
        st.markdown("""
        - **Ежедневный анализ** видео с камер наблюдения
        - **Ведение статистики** нарушений и опасных ситуаций
        - **Периодические проверки** соблюдения нормативов
        - **Система оповещения** при обнаружении нарушений
        """)

    with col2:
        st.subheader("🎓 Обучение и мотивация")
        st.markdown("""
        - **Тренинги** по безопасным методам работы
        - **Система поощрений** за соблюдение правил безопасности
        - **Разбор случаев** нарушений с командой
        - **Вовлечение работников** в улучшение условий труда
        """)

        st.subheader("🔧 Технические решения")
        st.markdown("""
        - **Автоматические системы** остановки оборудования при нарушении
        - **Датчики присутствия** в опасных зонах
        - **Системы контроля доступа** в специальные помещения
        - **Видеонаблюдение** с аналитикой в реальном времени
        """)

# Дополнительная информация
st.markdown("---")
st.markdown("""
<div style='background-color: #292732; padding: 20px; border-radius: 10px;'>
    <h4 style='color: #1f77b4;'>ℹ️ Информация о системе</h4>
    <p>Данная система анализа видео помогает выявлять потенциально опасные ситуации на рабочем месте и предоставляет рекомендации по улучшению условий труда.</p>
    <p><strong>Последнее обновление:</strong> {}</p>
</div>
""".format(datetime.now().strftime("%d.%m.%Y %H:%M")), unsafe_allow_html=True)