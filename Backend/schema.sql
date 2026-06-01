
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    phone           TEXT    NOT NULL,
    email           TEXT    NOT NULL UNIQUE,
    hashed_password TEXT    NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1,
    is_admin        INTEGER NOT NULL DEFAULT 0,
    avatar_url      TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_name  ON users(name);


CREATE TABLE IF NOT EXISTS categories (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE,
    slug            TEXT    NOT NULL UNIQUE,
    description     TEXT,
    parent_id       INTEGER,
    image_url       TEXT,
    sort_order      INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_categories_slug      ON categories(slug);
CREATE INDEX IF NOT EXISTS idx_categories_parent_id  ON categories(parent_id);


CREATE TABLE IF NOT EXISTS products (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    category        TEXT,
    category_id     INTEGER,
    description     TEXT,
    price           REAL    NOT NULL DEFAULT 0,
    old_price       REAL,                          -- стара ціна (для відображення знижки)
    image_url       TEXT,
    stock           INTEGER NOT NULL DEFAULT 0,     -- кількість на складі
    specs           TEXT,                           -- JSON з характеристиками
    is_available    INTEGER NOT NULL DEFAULT 1,
    is_rental       INTEGER NOT NULL DEFAULT 0,     -- 1 = доступний для оренди
    rental_price    REAL,                          -- ціна оренди за день
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_products_name        ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_category    ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_price       ON products(price);


CREATE TABLE IF NOT EXISTS product_images (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL,
    image_url       TEXT    NOT NULL,
    sort_order      INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_product_images_product_id ON product_images(product_id);

-- 5. Замовлення
CREATE TABLE IF NOT EXISTS orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER,
    order_number    TEXT    NOT NULL UNIQUE,         -- напр. "ORD-20260601-0001"
    status          TEXT    NOT NULL DEFAULT 'pending',
                    -- pending | confirmed | processing | shipped | delivered | cancelled
    total_amount    REAL    NOT NULL DEFAULT 0,
    delivery_cost   REAL    NOT NULL DEFAULT 0,
    discount_amount REAL    NOT NULL DEFAULT 0,

    -- Контактна інформація
    customer_name   TEXT    NOT NULL,
    customer_email  TEXT    NOT NULL,
    customer_phone  TEXT    NOT NULL,

    -- Адреса доставки
    address         TEXT,
    apartment       TEXT,
    postcode        TEXT,
    location_lat    REAL,
    location_lng    REAL,
    branch_name     TEXT,                           -- назва відділення

    -- Оплата
    payment_method  TEXT    NOT NULL DEFAULT 'cash',
                    -- card | transfer | cash | crypto
    payment_status  TEXT    NOT NULL DEFAULT 'pending',
                    -- pending | paid | failed | refunded
    promo_code      TEXT,

    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_user_id      ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_number ON orders(order_number);
CREATE INDEX IF NOT EXISTS idx_orders_status       ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at   ON orders(created_at);


CREATE TABLE IF NOT EXISTS order_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    product_name    TEXT    NOT NULL,                -- зберігаємо назву на момент покупки
    quantity        INTEGER NOT NULL DEFAULT 1,
    unit_price      REAL    NOT NULL,
    total_price     REAL    NOT NULL,
    FOREIGN KEY (order_id)   REFERENCES orders(id)   ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id   ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);


CREATE TABLE IF NOT EXISTS cart_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    quantity        INTEGER NOT NULL DEFAULT 1,
    added_at        TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, product_id),
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cart_items_user_id ON cart_items(user_id);


CREATE TABLE IF NOT EXISTS rentals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'pending',
                    -- pending | active | returned | overdue | cancelled
    start_date      TEXT    NOT NULL,
    end_date        TEXT    NOT NULL,
    daily_rate      REAL    NOT NULL,
    total_cost      REAL    NOT NULL,
    deposit         REAL    NOT NULL DEFAULT 0,
    return_date     TEXT,                           -- фактична дата повернення
    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rentals_user_id    ON rentals(user_id);
CREATE INDEX IF NOT EXISTS idx_rentals_product_id ON rentals(product_id);
CREATE INDEX IF NOT EXISTS idx_rentals_status     ON rentals(status);


CREATE TABLE IF NOT EXISTS promocodes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT    NOT NULL UNIQUE,
    discount_percent REAL   NOT NULL DEFAULT 0,      -- відсоток знижки (0-100)
    discount_amount  REAL   NOT NULL DEFAULT 0,      -- фіксована знижка в грн
    min_order_amount REAL   NOT NULL DEFAULT 0,      -- мінімальна сума замовлення
    max_uses        INTEGER NOT NULL DEFAULT 0,      -- 0 = безліміт
    used_count      INTEGER NOT NULL DEFAULT 0,
    is_active       INTEGER NOT NULL DEFAULT 1,
    valid_from      TEXT    NOT NULL DEFAULT (datetime('now')),
    valid_until     TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_promocodes_code ON promocodes(code);


CREATE TABLE IF NOT EXISTS promocode_usages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    promocode_id    INTEGER NOT NULL,
    user_id         INTEGER NOT NULL,
    order_id        INTEGER,
    used_at         TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (promocode_id) REFERENCES promocodes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)      REFERENCES users(id)      ON DELETE CASCADE,
    FOREIGN KEY (order_id)     REFERENCES orders(id)     ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_promo_usages_user  ON promocode_usages(user_id);
CREATE INDEX IF NOT EXISTS idx_promo_usages_promo ON promocode_usages(promocode_id);


CREATE TABLE IF NOT EXISTS customization_requests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER,
    status          TEXT    NOT NULL DEFAULT 'pending',
                    -- pending | in_review | approved | in_progress | completed | cancelled

    cpu             TEXT,
    gpu             TEXT,
    ram             TEXT,
    storage         TEXT,
    case_type       TEXT,
    cooling         TEXT,
    power_supply    TEXT,
    extras          TEXT,
    total_estimate  REAL,
    customer_name   TEXT,
    customer_email  TEXT,
    customer_phone  TEXT,
    notes           TEXT,
    admin_comment   TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_customization_user_id ON customization_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_customization_status  ON customization_requests(status);


CREATE TABLE IF NOT EXISTS news (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT    NOT NULL,
    slug            TEXT    NOT NULL UNIQUE,
    content         TEXT    NOT NULL,
    excerpt         TEXT,                           -- короткий опис
    image_url       TEXT,
    author_id       INTEGER,
    is_published    INTEGER NOT NULL DEFAULT 0,
    views_count     INTEGER NOT NULL DEFAULT 0,
    published_at    TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_news_slug         ON news(slug);
CREATE INDEX IF NOT EXISTS idx_news_published_at ON news(published_at);
CREATE INDEX IF NOT EXISTS idx_news_is_published ON news(is_published);


CREATE TABLE IF NOT EXISTS reviews (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL,
    user_id         INTEGER NOT NULL,
    rating          INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    comment         TEXT,
    is_approved     INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(product_id, user_id),                   -- один відгук на товар від одного юзера
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id    ON reviews(user_id);


CREATE TABLE IF NOT EXISTS wishlist (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    added_at        TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, product_id),
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_wishlist_user_id ON wishlist(user_id);


INSERT OR IGNORE INTO promocodes (code, discount_percent, is_active) VALUES
    ('COCA-COLA',                     10, 1),
    ('PCCOMPANYTOP',                  10, 1),
    ('14SECRET88',                    10, 1),
    ('WHOHASTHEBESTPC?-PCCOMPANY',    10, 1),
    ('BELLISSIMO',                    10, 1),
    ('ЯлюблюPCCOMPANY',              10, 1);


INSERT OR IGNORE INTO categories (name, slug, description) VALUES
    ('Комп''ютери',    'computers',   'Ігрові та офісні комп''ютери'),
    ('Ноутбуки',       'laptops',     'Ноутбуки провідних брендів'),
    ('Комплектуючі',   'components',  'Процесори, відеокарти, RAM, SSD тощо'),
    ('Периферія',      'peripherals', 'Клавіатури, миші, монітори'),
    ('Аксесуари',      'accessories', 'Сумки, підставки, кабелі');
