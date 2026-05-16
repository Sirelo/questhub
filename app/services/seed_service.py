from __future__ import annotations

from werkzeug.security import generate_password_hash

from app.repository import (
    add_comment,
    create_badge,
    create_checkin_record,
    create_expedition,
    create_participation,
    create_user,
    get_expedition_by_title,
    get_user_by_email,
    update_participation_progress,
)
from app.services.badge_service import evaluate_user_badges


BADGES = [
    ("first_expedition", "Первопроходец", "Создайте первую экспедицию.", "🚀"),
    ("first_join", "В команде", "Присоединитесь к чужой экспедиции.", "🤝"),
    ("streak_3", "Ритм 3", "Держите серию 3 дня подряд.", "🔥"),
    ("streak_7", "Ритм 7", "Держите серию 7 дней подряд.", "⚡"),
    ("points_100", "Сотня очков", "Наберите 100 баллов прогресса.", "💯"),
    ("mentor", "Наставник", "Создайте три экспедиции.", "🧭"),
]


def seed_badges() -> None:
    for code, title, description, icon in BADGES:
        create_badge(code, title, description, icon)


def seed_demo_data() -> None:
    if get_expedition_by_title("Город в 7 кадрах") is not None:
        return

    demo_users = [
        ("alice", "alice@example.com", "Москва", "Фотографирую детали города и люблю короткие маршруты."),
        ("misha", "misha@example.com", "Санкт-Петербург", "Собираю аккуратные учебные челленджи и люблю статистику."),
        ("sonya", "sonya@example.com", "Казань", "Веду творческие марафоны и ищу идеи для заметок."),
        ("timur", "timur@example.com", "Екатеринбург", "Люблю городские прогулки и небольшие спортивные цели."),
        ("lena", "lena@example.com", "Новосибирск", "Слежу за экологичными привычками и командной атмосферой."),
        ("artem", "artem@example.com", "Нижний Новгород", "Делаю фото, бегаю по утрам и люблю длинные серии."),
    ]

    for username, email, city, bio in demo_users:
        if get_user_by_email(email) is None:
            create_user(
                username=username,
                email=email,
                city=city,
                bio=bio,
                password_hash=generate_password_hash("password123"),
            )

    alice = get_user_by_email("alice@example.com")
    misha = get_user_by_email("misha@example.com")
    sonya = get_user_by_email("sonya@example.com")
    timur = get_user_by_email("timur@example.com")
    lena = get_user_by_email("lena@example.com")
    artem = get_user_by_email("artem@example.com")

    expeditions = {
        "city_frames": create_expedition(
            title="Город в 7 кадрах",
            summary="Неделя наблюдений: каждый день искать один необычный городской сюжет.",
            description=(
                "Участники выходят на короткую прогулку, замечают деталь, которую обычно пропускают, "
                "и оставляют короткую запись о том, почему именно этот кадр запомнился."
            ),
            category="photo",
            difficulty="easy",
            city="Москва",
            duration_days=7,
            target_points=70,
            is_public=True,
            creator_id=alice.id,
            cover_filename=None,
        ),
        "quiet_streets": create_expedition(
            title="Тихие улицы после учебы",
            summary="Маршрут без спешки, чтобы замечать новые места в знакомом районе.",
            description=(
                "После учебы участник выбирает спокойный путь домой, идет без спешки и записывает, "
                "какие дворы, окна, вывески или короткие проходы он раньше пропускал."
            ),
            category="city",
            difficulty="medium",
            city="Санкт-Петербург",
            duration_days=10,
            target_points=120,
            is_public=True,
            creator_id=timur.id,
            cover_filename=None,
        ),
        "study_sprint": create_expedition(
            title="5 вечерних спринтов по математике",
            summary="Короткие занятия по 30 минут, чтобы спокойно закрыть одну тему.",
            description=(
                "Каждый день участник берет один небольшой блок: формулы, задачи или разбор ошибок, "
                "а затем фиксирует, что стало понятнее к концу спринта."
            ),
            category="study",
            difficulty="medium",
            city="Казань",
            duration_days=5,
            target_points=75,
            is_public=True,
            creator_id=misha.id,
            cover_filename=None,
        ),
        "eco_week": create_expedition(
            title="Экологичная неделя дома",
            summary="7 простых действий: вода, свет, повторное использование и сортировка.",
            description=(
                "Экспедиция про маленькие бытовые шаги: своя бутылка, меньше лишнего света, "
                "повторное использование упаковки и сбор того, что можно сдать отдельно."
            ),
            category="eco",
            difficulty="easy",
            city="Новосибирск",
            duration_days=7,
            target_points=70,
            is_public=True,
            creator_id=lena.id,
            cover_filename=None,
        ),
        "creative_notes": create_expedition(
            title="12 идей для творческого блокнота",
            summary="Каждый день одна маленькая визуальная или текстовая заметка.",
            description=(
                "Участники заполняют блокнот мини-зарисовками, наблюдениями, списками ассоциаций "
                "и короткими историями, чтобы не терять творческий ритм."
            ),
            category="creative",
            difficulty="hard",
            city="Екатеринбург",
            duration_days=12,
            target_points=180,
            is_public=True,
            creator_id=sonya.id,
            cover_filename=None,
        ),
    }

    participations = {
        "misha_city_frames": create_participation(misha.id, expeditions["city_frames"]),
        "artem_city_frames": create_participation(artem.id, expeditions["city_frames"]),
        "lena_city_frames": create_participation(lena.id, expeditions["city_frames"]),
        "alice_quiet_streets": create_participation(alice.id, expeditions["quiet_streets"]),
        "sonya_quiet_streets": create_participation(sonya.id, expeditions["quiet_streets"]),
        "misha_eco_week": create_participation(misha.id, expeditions["eco_week"]),
        "timur_eco_week": create_participation(timur.id, expeditions["eco_week"]),
        "lena_study_sprint": create_participation(lena.id, expeditions["study_sprint"]),
        "artem_study_sprint": create_participation(artem.id, expeditions["study_sprint"]),
        "alice_creative_notes": create_participation(alice.id, expeditions["creative_notes"]),
        "misha_creative_notes": create_participation(misha.id, expeditions["creative_notes"]),
        "lena_creative_notes": create_participation(lena.id, expeditions["creative_notes"]),
    }

    demo_progress = [
        (
            participations["misha_city_frames"],
            misha.id,
            expeditions["city_frames"],
            "completed",
            7,
            75,
            "2026-05-13",
            [
                ("2026-05-07", "Нашел отражение старого дома в витрине кофейни.", "focused", 10),
                ("2026-05-09", "Снял пустой двор с длинными тенями после дождя.", "energized", 10),
                ("2026-05-13", "Поймал удачный кадр с желтым трамваем у поворота.", "steady", 15),
            ],
        ),
        (
            participations["artem_city_frames"],
            artem.id,
            expeditions["city_frames"],
            "active",
            4,
            45,
            "2026-05-12",
            [
                ("2026-05-08", "Заметил необычный свет во дворе между домами.", "focused", 10),
                ("2026-05-10", "Сделал серию снимков мостовой после дождя.", "energized", 15),
                ("2026-05-12", "Нашел тихий проход с интересной геометрией окон.", "steady", 20),
            ],
        ),
        (
            participations["lena_city_frames"],
            lena.id,
            expeditions["city_frames"],
            "active",
            3,
            30,
            "2026-05-11",
            [
                ("2026-05-06", "Сфотографировала аккуратную вывеску старой мастерской.", "steady", 10),
                ("2026-05-10", "Нашла уютный уголок с зеленью между домами.", "focused", 10),
                ("2026-05-11", "Сняла длинные тени от лестницы у школы.", "energized", 10),
            ],
        ),
        (
            participations["alice_quiet_streets"],
            alice.id,
            expeditions["quiet_streets"],
            "active",
            5,
            75,
            "2026-05-13",
            [
                ("2026-05-08", "Пошла домой через старую набережную и нашла тихий двор.", "focused", 15),
                ("2026-05-11", "Маршрут через парк оказался заметно спокойнее привычного.", "steady", 20),
                ("2026-05-13", "Составила карту трех самых уютных переулков района.", "energized", 40),
            ],
        ),
        (
            participations["sonya_quiet_streets"],
            sonya.id,
            expeditions["quiet_streets"],
            "active",
            2,
            30,
            "2026-05-12",
            [
                ("2026-05-09", "Сделала заметки про дворы с самыми интересными окнами.", "focused", 15),
                ("2026-05-12", "Нашла короткий путь через сквер, который раньше пропускала.", "steady", 15),
            ],
        ),
        (
            participations["misha_eco_week"],
            misha.id,
            expeditions["eco_week"],
            "completed",
            7,
            80,
            "2026-05-13",
            [
                ("2026-05-07", "Неделю пользовался своей бутылкой и не покупал воду.", "steady", 10),
                ("2026-05-10", "Разобрал дома упаковку и отделил бумагу от пластика.", "focused", 20),
                ("2026-05-13", "Собрал набор правил, которые реально удобно соблюдать.", "energized", 50),
            ],
        ),
        (
            participations["timur_eco_week"],
            timur.id,
            expeditions["eco_week"],
            "active",
            4,
            40,
            "2026-05-12",
            [
                ("2026-05-08", "Начал выключать лишний свет в коридоре и на кухне.", "steady", 10),
                ("2026-05-11", "Переиспользовал упаковку для хранения мелочей.", "focused", 10),
                ("2026-05-12", "Отнес батарейки в пункт сбора рядом с домом.", "energized", 20),
            ],
        ),
        (
            participations["lena_study_sprint"],
            lena.id,
            expeditions["study_sprint"],
            "completed",
            5,
            90,
            "2026-05-13",
            [
                ("2026-05-09", "Закрыла тему по тригонометрии и выписала формулы.", "focused", 15),
                ("2026-05-11", "Разобрала ошибки в задачах и пересобрала конспект.", "steady", 30),
                ("2026-05-13", "Решила мини-набор задач без подсказок.", "energized", 45),
            ],
        ),
        (
            participations["artem_study_sprint"],
            artem.id,
            expeditions["study_sprint"],
            "active",
            3,
            45,
            "2026-05-12",
            [
                ("2026-05-08", "Сделал 30 минут задач на вероятность.", "focused", 15),
                ("2026-05-10", "Повторил формулы и отдельно записал трудные места.", "steady", 15),
                ("2026-05-12", "Разобрал одну сложную задачу до конца.", "energized", 15),
            ],
        ),
        (
            participations["alice_creative_notes"],
            alice.id,
            expeditions["creative_notes"],
            "active",
            4,
            80,
            "2026-05-13",
            [
                ("2026-05-08", "Заполнила разворот ассоциациями про городской шум.", "focused", 20),
                ("2026-05-10", "Собрала заметку из коротких фраз и цветовых пятен.", "steady", 20),
                ("2026-05-13", "Сделала серию мини-эскизов про двор и лестницы.", "energized", 40),
            ],
        ),
        (
            participations["misha_creative_notes"],
            misha.id,
            expeditions["creative_notes"],
            "active",
            6,
            120,
            "2026-05-13",
            [
                ("2026-05-07", "Записал 12 идей для коротких историй из поездок.", "focused", 20),
                ("2026-05-09", "Оформил страницу с геометрическими паттернами улиц.", "steady", 40),
                ("2026-05-13", "Сделал полноценный разворот со схемой района и заметками.", "energized", 60),
            ],
        ),
        (
            participations["lena_creative_notes"],
            lena.id,
            expeditions["creative_notes"],
            "active",
            2,
            40,
            "2026-05-11",
            [
                ("2026-05-08", "Собрала страницу из билетов и коротких фраз.", "focused", 20),
                ("2026-05-11", "Описала один день через пять предметов и пять цветов.", "steady", 20),
            ],
        ),
    ]

    for participation_id, user_id, expedition_id, status, streak_days, total_points, last_day, checkins in demo_progress:
        update_participation_progress(
            participation_id=participation_id,
            status=status,
            streak_days=streak_days,
            total_points=total_points,
            last_checkin_date=last_day,
        )
        for checkin_day, note, mood, points in checkins:
            create_checkin_record(
                participation_id=participation_id,
                user_id=user_id,
                expedition_id=expedition_id,
                note=note,
                mood=mood,
                points_earned=points,
                checkin_day=checkin_day,
            )

    comments = [
        (alice.id, expeditions["city_frames"], "Формат с одним кадром в день отлично работает: не перегружает и заставляет смотреть внимательнее."),
        (misha.id, expeditions["study_sprint"], "Короткие спринты вечером удобнее длинных занятий, проще начать даже после тяжелого дня."),
        (lena.id, expeditions["eco_week"], "Самым легким пунктом оказалась своя бутылка, а самым сложным — не забывать про сортировку."),
        (sonya.id, expeditions["creative_notes"], "Нравится, что можно чередовать текст, рисунок и короткие списки идей."),
        (artem.id, expeditions["quiet_streets"], "После двух дней уже начинаешь замечать маршрут совсем иначе."),
    ]
    for user_id, expedition_id, text in comments:
        add_comment(user_id, expedition_id, text)

    for user in [alice, misha, sonya, timur, lena, artem]:
        evaluate_user_badges(user)
