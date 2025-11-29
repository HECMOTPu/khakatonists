import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Настройка страницы
st.set_page_config(
    page_title="Анализатор видео - Безопасность труда",
    layout="wide"
)

st.title("ДАШБОРД АНАЛИЗА ВИДЕО ДЛЯ БЕЗОПАСНОСТИ ТРУДА")
st.markdown("---")

# Боковая панель
with st.sidebar:
    st.header("Настройки")

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

    analyze_btn = st.button("Запустить анализ", type="primary")


# Имитация нейросети для анализа безопасности
class VideoAnalyzer:
    def __init__(self):
        self.classes = ['человек', 'поезд', 'оборудование']
        self.danger_actions = [
            'человек близко к краю платформы',
            'человек на путях',
            'быстрое движение у края',
            'падение',
            'толкание'
        ]

    def analyze_frame(self, frame_num, total_frames=100):
        np.random.seed(frame_num)
        detections = []

        # Генерация людей (случайное количество от 0 до 8)
        num_people = np.random.randint(0, 9)
        for i in range(num_people):
            detections.append({
                'class': 'человек',
                'confidence': np.random.uniform(0.7, 0.98),
                'frame': frame_num,
                'timestamp': frame_num / 30,
                'position_x': np.random.uniform(0, 100),
                'position_y': np.random.uniform(0, 100),
                'in_danger_zone': np.random.choice([True, False], p=[0.15, 0.85]),
                'danger_action': np.random.choice(self.danger_actions, p=[0.85, 0.05, 0.05, 0.03,
                                                                          0.02]) if np.random.random() < 0.2 else None
            })

        # Генерация поезда (логика появления/исчезновения)
        train_present = False
        train_status = "нет поезда в кадре"

        # Имитация логики движения поезда
        if 20 <= frame_num <= 40:
            train_status = "прибывает"
            train_present = True
        elif 41 <= frame_num <= 70:
            train_status = "стоит"
            train_present = True
        elif 71 <= frame_num <= 90:
            train_status = "отбывает"
            train_present = True

        if train_present:
            detections.append({
                'class': 'поезд',
                'confidence': np.random.uniform(0.9, 0.99),
                'frame': frame_num,
                'timestamp': frame_num / 30,
                'status': train_status
            })

        return detections


# Основная логика
if uploaded_file:
    st.subheader("Предпросмотр видео")
    st.video(uploaded_file)

if analyze_btn and uploaded_file:
    st.subheader("Результаты анализа безопасности")

    progress_bar = st.progress(0)
    status_text = st.empty()

    analyzer = VideoAnalyzer()
    all_detections = []

    # Имитация анализа 100 кадров
    total_frames = 100
    for i in range(total_frames):
        progress_bar.progress((i + 1) / total_frames)
        status_text.text(f"Анализ кадра {i + 1}/{total_frames}")

        detections = analyzer.analyze_frame(i, total_frames)
        all_detections.extend(detections)

    status_text.text("Анализ завершен!")

    if all_detections:
        df = pd.DataFrame(all_detections)

        # Анализ людей по кадрам
        people_detections = df[df['class'] == 'человек']
        train_detections = df[df['class'] == 'поезд']

        # Количество людей по кадрам
        people_by_frame = people_detections.groupby('frame').size()
        if not people_by_frame.empty:
            max_people = people_by_frame.max()
            max_people_frame = people_by_frame.idxmax()
        else:
            max_people = 0
            max_people_frame = 0

        # Опасные действия
        danger_actions = people_detections[people_detections['danger_action'].notna()]
        danger_count = len(danger_actions)

        # Время опасных ситуаций по кадрам
        danger_frames = danger_actions[['frame', 'timestamp', 'danger_action']].copy()

        # Анализ поезда
        train_arrival_time = None
        train_status_by_frame = []

        if not train_detections.empty:
            # Время прибытия поезда (первое появление)
            first_train_frame = train_detections['frame'].min()
            train_arrival_time = first_train_frame / 30

            # Статус поезда по кадрам
            for frame in range(total_frames):
                frame_train_data = train_detections[train_detections['frame'] == frame]
                if not frame_train_data.empty:
                    status = frame_train_data.iloc[0]['status']
                else:
                    status = "нет поезда в кадре"
                train_status_by_frame.append({
                    'frame': frame,
                    'timestamp': frame / 30,
                    'status': status
                })

        # ОСНОВНЫЕ ПОКАЗАТЕЛИ
        st.subheader("Основные показатели безопасности")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Максимальное количество людей в кадре",
                f"{max_people} чел.",
                delta=f"кадр {max_people_frame}"
            )

        with col2:
            st.metric(
                "Количество опасных действий",
                danger_count,
                delta="Внимание" if danger_count > 0 else "Безопасно",
                delta_color="inverse" if danger_count > 0 else "normal"
            )

        with col3:
            if train_arrival_time:
                st.metric(
                    "Время прибытия поезда",
                    f"{train_arrival_time:.1f} сек",
                    delta=f"кадр {first_train_frame}"
                )
            else:
                st.metric(
                    "Время прибытия поезда",
                    "Не обнаружено"
                )

        with col4:
            if not train_detections.empty:
                current_status = train_status_by_frame[-1]['status'] if train_status_by_frame else "нет поезда в кадре"
                st.metric(
                    "Текущий статус поезда",
                    current_status
                )
            else:
                st.metric(
                    "Текущий статус поезда",
                    "нет поезда в кадре"
                )

        # ГРАФИК КОЛИЧЕСТВА ЛЮДЕЙ В КАДРЕ
        st.subheader("График количества людей в кадре")

        # Создаем полный DataFrame по всем кадрам
        frames_data = []
        for frame in range(total_frames):
            people_count = len(people_detections[people_detections['frame'] == frame])
            frames_data.append({
                'frame': frame,
                'timestamp': frame / 30,
                'people_count': people_count
            })

        people_df = pd.DataFrame(frames_data)

        fig_people = px.line(
            people_df,
            x='timestamp',
            y='people_count',
            title='Количество людей в кадре по времени',
            labels={'timestamp': 'Время (секунды)', 'people_count': 'Количество людей'}
        )
        fig_people.update_traces(line=dict(color='blue', width=3))
        fig_people.add_hline(y=max_people, line_dash="dash", line_color="red",
                             annotation_text=f"Максимум: {max_people} чел.")
        st.plotly_chart(fig_people, use_container_width=True)

        # ТАБЛИЦА КОЛИЧЕСТВА ЛЮДЕЙ ПО КАДРАМ
        st.subheader("Количество людей в кадре по фреймам")

        display_people_df = people_df[['frame', 'timestamp', 'people_count']].copy()
        display_people_df['timestamp'] = display_people_df['timestamp'].round(2)
        display_people_df.columns = ['Кадр', 'Время (сек)', 'Количество людей']

        st.dataframe(display_people_df, height=300, use_container_width=True)

        # СТАТУС ПОЕЗДА ПО КАДРАМ
        if train_status_by_frame:
            st.subheader("Статус поезда по фреймам")

            train_status_df = pd.DataFrame(train_status_by_frame)
            train_status_df['timestamp'] = train_status_df['timestamp'].round(2)
            train_status_df.columns = ['Кадр', 'Время (сек)', 'Статус поезда']

            st.dataframe(train_status_df, height=300, use_container_width=True)

        # ОПАСНЫЕ ДЕЙСТВИЯ
        if danger_count > 0:
            st.subheader("Опасные действия по времени")

            danger_display = danger_frames.copy()
            danger_display['timestamp'] = danger_display['timestamp'].round(2)
            danger_display.columns = ['Кадр', 'Время (сек)', 'Тип опасного действия']
            danger_display = danger_display.sort_values('Кадр')

            st.dataframe(danger_display, height=300, use_container_width=True)

            # График опасных действий по времени
            danger_timeline = danger_frames.groupby('frame').size().reset_index(name='danger_count')
            danger_timeline['timestamp'] = danger_timeline['frame'] / 30

            fig_danger = px.scatter(
                danger_timeline,
                x='timestamp',
                y='danger_count',
                title='Опасные действия по времени',
                labels={'timestamp': 'Время (секунды)', 'danger_count': 'Количество опасных действий'}
            )
            st.plotly_chart(fig_danger, use_container_width=True)
        else:
            st.success("Опасные действия не обнаружены")

    else:
        st.warning("Объекты не обнаружены")

else:
    st.info("Загрузите видеофайл и настройте параметры анализа")