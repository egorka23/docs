# Руководство по работе с Mintlify Docs

## 1. Ссылки

### Правило: Никогда не используй `/docs` в ссылках

**Правильно:**
```html
<a href="/rfe-data/entertainment">Entertainment</a>
```

**Неправильно:**
```html
<a href="/docs/rfe-data/entertainment">Entertainment</a>
```

### Почему?

Mintlify автоматически обрабатывает базовый путь при деплое:

| Среда | URL в браузере | Ссылка в коде |
|-------|----------------|---------------|
| Локально | `localhost:3000/rfe-data/entertainment` | `/rfe-data/entertainment` |
| Продакшн | `o1eb1.com/docs/rfe-data/entertainment` | `/rfe-data/entertainment` |

### Форматы ссылок

```html
<!-- Внутренние (без /docs) -->
<a href="/rfe-data/nebraska">Nebraska</a>
<a href="/success-stories/cases-preview">Все кейсы</a>

<!-- Внешние (полный URL) -->
<a href="https://t.me/talentvisahelp">Telegram</a>
```

---

## 2. Frontmatter (заголовки страниц)

### Структура

```yaml
---
title: "Короткий title"           # Показывается в меню навигации
sidebarTitle: "Еще короче"        # Опционально, для меню если title длинный
description: "Описание страницы"  # Meta description для SEO
seo:
  title: "Полный SEO заголовок с ключевыми словами"  # Для поисковиков
icon: "icon-name"                 # Иконка в меню
mode: "wide"                      # Опционально, для широких страниц
---
```

### Пример

```yaml
---
title: "Mandamus"
sidebarTitle: "Mandamus"
description: "Как подать Mandamus при задержке визы 221(g)"
seo:
  title: "Mandamus при 221(g): пошаговое руководство по подаче иска"
icon: "gavel"
---
```

### Правила

1. `title` - короткий, для компактного меню (1-3 слова)
2. `seo.title` - длинный, с ключевыми словами для Google
3. Не теряй ключевые слова (221(g), DS-5535, TAL, Mandamus и т.д.)

---

## 3. Заголовки и "On this page"

### Иерархия

```markdown
## Основной раздел (H2)     → Показывается в "On this page"
### Подраздел (H3)          → Показывается как вложенный
#### Детали (H4)            → Не показывается в навигации
```

### Оптимизация "On this page"

Если слишком много пунктов в "On this page":
1. Сгруппируй H3 вопросы под H2 секции
2. Оставь 6-8 H2 секций максимум
3. H3 внутри секций для деталей

**До:**
```markdown
### Вопрос 1?
### Вопрос 2?
### Вопрос 3?
... (20 вопросов)
```

**После:**
```markdown
## Основы Mandamus
### Вопрос 1?
### Вопрос 2?

## Подача иска
### Вопрос 3?
### Вопрос 4?
```

---

## 4. QA перед пушем

### Обязательные проверки

```bash
# 1. Нет длинных тире (признак AI)
rg "→|—" ~/mintlify-docs --glob "*.mdx"
# Должно быть 0 результатов

# 2. Нет /docs в ссылках
grep -r 'href="/docs/' ~/mintlify-docs --include="*.mdx"
# Должно быть 0 результатов

# 3. Локальная проверка
npx mintlify dev
# Открой localhost:3000 и проверь страницы
```

### Что проверять визуально

- [ ] Меню навигации компактное
- [ ] "On this page" не перегружен (6-8 пунктов)
- [ ] Ссылки работают
- [ ] Нет AI-признаков (длинные тире, эмодзи без запроса)

---

## 5. Commit и Push

### Стандартный процесс

```bash
# 1. Добавить файлы
git add ~/mintlify-docs/path/to/files/*.mdx

# 2. Коммит с понятным сообщением
git commit -m "Краткое описание изменений"

# 3. Пуш
git push
```

### Примеры коммит-сообщений

```
"Shorten nav titles, keep SEO titles"
"Fix links format, add wide mode"
"Add statistics to category pages"
"Group mandamus FAQ into sections"
```

---

## 6. После деплоя

### Проверка на продакшене

1. Открой https://o1eb1.com/docs/
2. Проверь измененные страницы
3. Убедись что ссылки работают
4. Проверь мобильную версию

---

## 7. Типичный workflow задачи

```
A) Изменения в файлах
   - Какие файлы менять
   - Что именно менять

B) QA проверки
   - rg проверки
   - Локальный просмотр

C) Commit + Push
   git add ...
   git commit -m "..."
   git push

D) Проверка на проде
   - Открыть страницы
   - Убедиться что все работает
```

---

**Дата создания:** 2025-12-23
