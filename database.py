import asyncpg, os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")

pool: asyncpg.Pool | None = None

# ---------- подключение ----------
async def connect_db():
    global pool
    pool = await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
    )

# ---------- создание таблиц ----------
# database.py
async def init_schema():
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                username    TEXT,
                full_name   TEXT
            );

            CREATE TABLE IF NOT EXISTS profiles (
                telegram_id BIGINT PRIMARY KEY
                    REFERENCES users(telegram_id) ON DELETE CASCADE,
                gender     TEXT    NOT NULL,
                name       TEXT    NOT NULL,
                age        INT     NOT NULL,
                location   TEXT    NOT NULL,
                phone      TEXT    NOT NULL,
                photo_data BYTEA   NOT NULL,    -- ← запятая здесь
                lang       TEXT    NOT NULL DEFAULT 'ru'
            );

            /* ↓↓↓ добавили блокировки — ОБЯЗАТЕЛЬНО с ; перед следующим CREATE */
            CREATE TABLE IF NOT EXISTS blocks (
                blocker_id BIGINT NOT NULL,
                blocked_id BIGINT NOT NULL,
                PRIMARY KEY (blocker_id, blocked_id)
            );

            CREATE TABLE IF NOT EXISTS dialogs (
                user_id    BIGINT PRIMARY KEY,
                partner_id BIGINT NOT NULL,
                started_at TIMESTAMP DEFAULT now()
            );
            
            CREATE TABLE IF NOT EXISTS admins (
                tg_id    BIGINT PRIMARY KEY,
                is_admin BOOLEAN NOT NULL
            );
            
           CREATE TABLE IF NOT EXISTS bans(
                telegram_id BIGINT PRIMARY KEY,
                until       TIMESTAMP,
                reason      TEXT,
                banned_at   TIMESTAMP DEFAULT now()
            );
            
     
               CREATE TABLE IF NOT EXISTS messages (
                id           BIGSERIAL   PRIMARY KEY,
                user1        BIGINT      NOT NULL,
                user2        BIGINT      NOT NULL,
                sender_id    BIGINT      NOT NULL,
                receiver_id  BIGINT      NOT NULL,
                body         TEXT        NOT NULL,
                sent_at      TIMESTAMPTZ DEFAULT now()
            );
            
            CREATE TABLE IF NOT EXISTS feedback_threads (
                id          BIGSERIAL PRIMARY KEY,
                user_id     BIGINT  NOT NULL,          -- автор-пользователь
                admin_id    BIGINT,                    -- кто взял в работу (NULL = никто)
                status      TEXT   NOT NULL DEFAULT 'open',   -- open / closed
                created_at  TIMESTAMPTZ DEFAULT now(),
                updated_at  TIMESTAMPTZ DEFAULT now()
            );
            
            CREATE TABLE IF NOT EXISTS feedback_messages (
                id          BIGSERIAL PRIMARY KEY,
                thread_id   BIGINT      REFERENCES feedback_threads(id) ON DELETE CASCADE,
                sender_id   BIGINT      NOT NULL,      -- user_id или admin_id
                body        TEXT,
                file_id     TEXT,
                file_type   TEXT,
                sent_at     TIMESTAMPTZ DEFAULT now()
            );
            
            CREATE TABLE IF NOT EXISTS reactions (
                user_id    BIGINT      NOT NULL,
                target_id  BIGINT      NOT NULL,
                reaction   TEXT        NOT NULL,
                reacted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                PRIMARY KEY (user_id, target_id)
            );
         
            ALTER TABLE profiles
            DROP COLUMN IF EXISTS photo_path;

-- 3) Добавить photo_data, если её нет
            ALTER TABLE profiles
            ADD COLUMN IF NOT EXISTS photo_data BYTEA NOT NULL DEFAULT ''::bytea;

-- 4) Добавить lang, если её нет
            ALTER TABLE profiles
            ADD COLUMN IF NOT EXISTS lang TEXT NOT NULL DEFAULT 'ru';
            
            ALTER TABLE reactions
            ADD COLUMN IF NOT EXISTS reacted_at TIMESTAMPTZ NOT NULL DEFAULT now();
            CREATE INDEX IF NOT EXISTS idx_fb_messages_thread ON feedback_messages(thread_id, sent_at);
            ALTER TABLE messages
            ADD COLUMN IF NOT EXISTS user1      BIGINT,
            ADD COLUMN IF NOT EXISTS user2      BIGINT,
            ADD COLUMN IF NOT EXISTS file_id TEXT,
            ADD COLUMN IF NOT EXISTS file_type TEXT;
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP DEFAULT now();
            CREATE INDEX IF NOT EXISTS idx_users_last_seen ON users(last_seen);
            CREATE INDEX IF NOT EXISTS idx_messages_pair
            ON messages (LEAST(sender_id, receiver_id), GREATEST(sender_id, receiver_id), sent_at DESC);
        """)


# ---------- бизнес-функции ----------
async def add_user(telegram_id: int, username: str | None, full_name: str | None):
    """Вставка пользователя, если его ещё нет"""
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (telegram_id, username, full_name)
            VALUES ($1,$2,$3)
            ON CONFLICT (telegram_id) DO NOTHING;
            """,
            telegram_id, username, full_name
        )

async def upsert_profile(
    tg_id: int,
    *,
    gender: str,
    name: str,
    age: int,
    location: str,
    phone: str,
    photo_data: bytes,
    lang: str
):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO profiles
              (telegram_id, gender, name, age, location, phone, photo_data, lang)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
            ON CONFLICT (telegram_id) DO UPDATE
            SET
              gender     = EXCLUDED.gender,
              name       = EXCLUDED.name,
              age        = EXCLUDED.age,
              location   = EXCLUDED.location,
              phone      = EXCLUDED.phone,
              photo_data = EXCLUDED.photo_data,
              lang       = EXCLUDED.lang
            """,
            tg_id, gender, name, age, location, phone, photo_data, lang
        )
async def user_exists(tg_id: int) -> bool:
    """
    True  – запись с таким telegram_id уже есть
    False – в таблице нет
    """
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT 1 FROM users WHERE telegram_id=$1",
            tg_id
        ) is not None

async def get_profile(tg_id: int) -> asyncpg.Record | None:
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT telegram_id, gender, name, age, location, phone,
                   photo_data, lang
            FROM profiles
            WHERE telegram_id=$1
            """,
            tg_id
        )

# Обновление одного поля
async def update_profile_field(tg_id: int, field: str, value):
    assert field in {"name", "age", "location", "photo_data"}
    async with pool.acquire() as conn:
        await conn.execute(
            f"UPDATE profiles SET {field}=$2 WHERE telegram_id=$1",
            tg_id, value
        )



async def set_user_language(tg_id: int, lang: str):
    """Обновить только поле lang в профиле."""
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE profiles SET lang = $2 WHERE telegram_id = $1",
            tg_id, lang
        )

async def get_candidates_list(my_gender: str, viewer_id: int) -> list[int]:
    """Вернёт список telegram_id кандидатов противоположного пола,
       сначала из вашего города, затем остальных в random-порядке."""
    # 1) Узнаём город смотрящего
    me = await pool.fetchrow(
        "SELECT location FROM profiles WHERE telegram_id = $1",
        viewer_id
    )
    my_city = me["location"] if me else None

    # 2) Получаем all telegram_id
    rows = await pool.fetch(
        """
        SELECT telegram_id
        FROM profiles
        WHERE gender <> $1
          AND telegram_id <> $2
        ORDER BY
          (location = $3) DESC,
          random()
        """,
        my_gender, viewer_id, my_city
    )
    return [r["telegram_id"] for r in rows]

async def get_profile_by_id(telegram_id: int) -> asyncpg.Record | None:
    """Берёт полную запись профиля по telegram_id."""
    return await pool.fetchrow(
        "SELECT * FROM profiles WHERE telegram_id = $1",
        telegram_id
    )

async def set_dialog(me: int, partner: int) -> bool:
    """
    True  → запись была создана впервые
    False → пара уже существовала (обновили started_at)
    """
    async with pool.acquire() as conn:
        status = await conn.execute("""
            INSERT INTO dialogs (user_id, partner_id)
            VALUES ($1,$2)
            ON CONFLICT (user_id) DO UPDATE
            SET partner_id=$2, started_at=now();
        """, me, partner)
    # status = 'INSERT 0 1' при новой строке, 'UPDATE 0 1' при существующей
    return status.startswith("INSERT")

async def get_partner(me: int) -> int | None:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT partner_id FROM dialogs WHERE user_id=$1", me
        )

async def clear_dialog(me: int):
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM dialogs WHERE user_id=$1", me)

async def get_display_name(tg_id: int) -> str:
    """
    Возвращает имя из анкеты (profiles.name),
    а если анкеты нет – full_name из Telegram.
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT name FROM profiles WHERE telegram_id=$1", tg_id
        )
    if row and row["name"]:
        return row["name"]
    # резерв – имя из Telegram, если анкеты нет
    return None

async def is_blocked(sender: int, recipient: int) -> bool:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT 1 FROM blocks WHERE blocker_id=$1 AND blocked_id=$2",
            recipient, sender          # важен порядок!
        ) is not None

async def add_block(blocker: int, target: int) -> bool:
    """
    True  → блокировка создана впервые
    False → запись уже была
    """
    async with pool.acquire() as conn:
        status = await conn.execute(
            """
            INSERT INTO blocks(blocker_id, blocked_id)
            VALUES ($1,$2)
            ON CONFLICT DO NOTHING
            """,
            blocker, target
        )
    return status.startswith("INSERT")

async def remove_block(user_id: int, target_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM blocks WHERE blocker_id=$1 AND blocked_id=$2",
            user_id, target_id
        )

async def get_blocked(blocker: int) -> list[asyncpg.Record]:
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT
                b.blocked_id,
                COALESCE(p.name, '') AS display_name
            FROM blocks b
            LEFT JOIN profiles p
              ON p.telegram_id = b.blocked_id
            WHERE b.blocker_id = $1
            """,
            blocker
        )


# admin

async def get_all_users(limit: int | None = None):
    q = "SELECT telegram_id, COALESCE(full_name, username, telegram_id::text) FROM users ORDER BY telegram_id"
    if limit:
        q += f" LIMIT {limit}"
    async with pool.acquire() as conn:
        return await conn.fetch(q)

async def get_profile_counts():
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT COUNT(*)                            AS total,
                   COUNT(*) FILTER (WHERE gender='Տղա')   AS males,
                   COUNT(*) FILTER (WHERE gender='Աղջիկ') AS females
            FROM profiles
        """)
    return row["total"], row["males"], row["females"]

async def search_profiles_by_name(substr: str) -> list[asyncpg.Record]:
    """
    Ищет профили по подстроке substr (регистр не важен).
    Возвращает telegram_id, name и photo_data.
    """
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT
                telegram_id,
                name,
                photo_data
            FROM profiles
            WHERE name ILIKE '%' || $1 || '%'
            ORDER BY name
            """,
            substr
        )

async def set_admin(tg_id: int, is_admin: bool):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO admins(tg_id, is_admin)
            VALUES ($1,$2)
            ON CONFLICT (tg_id) DO UPDATE SET is_admin=$2
        """, tg_id, is_admin)

async def is_admin(tg_id: int) -> bool:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT is_admin FROM admins WHERE tg_id=$1", tg_id
        ) or False

async def get_all_admin_ids() -> list[int]:
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT tg_id FROM admins WHERE is_admin")
        return [r["tg_id"] for r in rows]

async def update_last_seen(tg_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET last_seen = now() WHERE telegram_id=$1",
            tg_id
        )

async def get_online_count(hours: int = 24) -> int:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            """
            SELECT COUNT(*) FROM users
            WHERE last_seen > now() - ($1 || ' hours')::interval
            """,
            str(hours)                    # ← конвертируем в str
        )

async def ban(user_id: int,
              hours: int | None = None,
              reason: str = ""):
    """
    • hours=None  → бессрочный бан
    • hours=24    → бан на 24 часа
    """
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO bans (telegram_id, until, reason)
            VALUES (
                $1,
                CASE
                    WHEN $2::int IS NULL             -- ЯВНО задаём тип INT
                    THEN NULL                        --  → NULL = вечный бан
                    ELSE now() +                     -- иначе считаем время
                         ($2::int * interval '1 hour')
                END,
                $3
            )
            ON CONFLICT (telegram_id) DO UPDATE
            SET until  = EXCLUDED.until,
                reason = EXCLUDED.reason
            """,
            user_id,
            hours,        # может быть None – теперь допустимо
            reason
        )

async def unban(user_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM bans WHERE telegram_id=$1",
            user_id
        )

async def get_all_bans():
    """
    Возвращает все активные баны:
    telegram_id, until (None = навсегда), reason
    """
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT telegram_id, until, reason
            FROM bans
            WHERE until IS NULL OR until > now()
            ORDER BY banned_at DESC
            """
        )

async def is_banned(user_id: int) -> bool:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT 1 FROM bans WHERE telegram_id=$1 AND (until IS NULL OR until>now())",
            user_id
        ) is not None

async def save_msg(sender: int, receiver: int,
                   text: str | None = None,
                   file_id: str | None = None,
                   file_type: str | None = None):
    a, b = sorted((sender, receiver))
    await pool.execute(
        """INSERT INTO messages
             (user1,user2,sender_id,receiver_id,body,file_id,file_type)
           VALUES ($1,$2,$3,$4,$5,$6,$7)""",
        a, b, sender, receiver, text or "", file_id, file_type
    )

async def get_pairs(limit: int = 200) -> list[dict]:
    rows = await pool.fetch(
        """
        SELECT LEAST(user1,user2)  AS u1,
               GREATEST(user1,user2) AS u2,
               MAX(sent_at)          AS last_msg
        FROM   messages
        GROUP  BY 1,2
        ORDER  BY last_msg DESC
        LIMIT  $1
        """,
        limit
    )
    return [dict(r) for r in rows]

async def get_messages_between(a: int, b: int, limit: int = 50):
    u1, u2 = sorted((a, b))
    rows = await pool.fetch(
        """
        SELECT sender_id,
               receiver_id,
               body,
               file_id,
               file_type,
               sent_at
        FROM   messages
        WHERE  user1=$1 AND user2=$2
        ORDER  BY sent_at DESC
        LIMIT  $3
        """,
        u1, u2, limit
    )
    return [dict(r) for r in rows]

async def get_or_create_thread(user_id: int) -> int:
    async with pool.acquire() as c:
        tid = await c.fetchval("""
            SELECT id FROM feedback_threads
            WHERE user_id=$1 AND status='open'
            ORDER BY id DESC LIMIT 1
        """, user_id)
        if tid:                 # уже есть открытый
            return tid
        return await c.fetchval(
            "INSERT INTO feedback_threads(user_id) VALUES ($1) RETURNING id",
            user_id
        )

async def save_fb_message(thread_id: int, sender_id: int,
                          body: str | None = None,
                          file_id: str | None = None,
                          file_type: str | None = None):
    async with pool.acquire() as c:
        await c.execute("""
            INSERT INTO feedback_messages(thread_id,sender_id,body,
                                          file_id,file_type)
            VALUES ($1,$2,$3,$4,$5)
        """, thread_id, sender_id, body or "", file_id, file_type)
        await c.execute("""
            UPDATE feedback_threads SET updated_at=now()
            WHERE id=$1
        """, thread_id)

async def list_open_threads() -> list[asyncpg.Record]:
    async with pool.acquire() as c:
        return await c.fetch("""
            SELECT  t.id, t.user_id,
                    (SELECT body FROM feedback_messages m
                     WHERE m.thread_id = t.id
                     ORDER BY sent_at DESC LIMIT 1)    AS last_msg,
                    t.updated_at
            FROM feedback_threads t
            WHERE t.status='open'
            ORDER BY t.updated_at DESC
        """)

async def thread_messages(thread_id: int, limit: int = 50):
    async with pool.acquire() as c:
        return await c.fetch("""
            SELECT * FROM feedback_messages
            WHERE thread_id=$1
            ORDER BY sent_at DESC
            LIMIT $2
        """, thread_id, limit)

async def get_thread_user(tid: int) -> int | None:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT user_id FROM feedback_threads WHERE id=$1",
            tid
        )


# New Like dislike

async def set_reaction(user_id: int, target_id: int, reaction: str):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO reactions (user_id, target_id, reaction, reacted_at)
            VALUES ($1, $2, $3, now())
            ON CONFLICT (user_id, target_id)
            DO UPDATE SET
              reaction   = EXCLUDED.reaction,
              reacted_at = now()
            """,
            user_id, target_id, reaction
        )

async def get_reaction(user_id: int, target_id: int) -> str | None:
    rec = await get_reaction_record(user_id, target_id)
    return rec["reaction"] if rec else None

async def count_reactions(target_id: int) -> tuple[int,int]:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
              COUNT(*) FILTER (WHERE reaction='like')    AS likes,
              COUNT(*) FILTER (WHERE reaction='dislike') AS dislikes
            FROM reactions
            WHERE target_id = $1
            """,
            target_id
        )
    return row["likes"], row["dislikes"]


async def get_reaction_record(user_id: int, target_id: int) -> asyncpg.Record | None:
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT reaction, reacted_at
            FROM reactions
            WHERE user_id = $1 AND target_id = $2
            """,
            user_id, target_id
        )