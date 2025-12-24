# Инструкция по ссылкам в Mintlify Docs

## Правило #1: Никогда не используй `/docs` в ссылках

**Правильно:**
```html
<a href="/rfe-data/entertainment">Entertainment</a>
```

**Неправильно:**
```html
<a href="/docs/rfe-data/entertainment">Entertainment</a>
```

## Почему так?

Mintlify автоматически обрабатывает базовый путь при деплое:

| Среда | URL в браузере | Ссылка в коде |
|-------|----------------|---------------|
| Локально | `localhost:3000/rfe-data/entertainment` | `/rfe-data/entertainment` |
| Продакшн | `o1eb1.com/docs/rfe-data/entertainment` | `/rfe-data/entertainment` |

Mintlify сам добавляет `/docs` на продакшене. В коде всегда пиши без него.

## Форматы ссылок

### Абсолютные ссылки (внутри docs)
```html
<a href="/rfe-data/nebraska">Nebraska</a>
<a href="/success-stories/cases-preview">Все кейсы</a>
<a href="/community">Сообщество</a>
```

### Внешние ссылки (полный URL)
```html
<a href="https://t.me/talentvisahelp">Telegram</a>
<a href="https://o1eb1.com">Основной сайт</a>
```

## Структура путей

Пути соответствуют структуре в `docs.json` (navigation):

```
/                        → index.mdx
/rfe-data/all           → rfe-data/all.mdx
/rfe-data/nebraska      → rfe-data/nebraska.mdx
/success-stories/index  → success-stories/index.mdx
/community              → community.mdx
```

## Проверка ссылок

### Локально
1. Запусти `npx mintlify dev`
2. Открой `http://localhost:3000`
3. Ссылки должны работать без `/docs`

### На продакшене
1. После пуша проверь на `https://o1eb1.com/docs/`
2. Ссылки автоматически работают с `/docs`

## Если ссылки не работают

1. Проверь, что файл существует в указанном пути
2. Проверь, что страница добавлена в `docs.json` → navigation
3. Убедись, что нет опечаток в пути
4. Перезапусти локальный сервер

## Примеры из проекта

### Кнопки категорий (all.mdx)
```jsx
<a href="/rfe-data/nebraska" style={{...}}>Nebraska 84</a>
<a href="/rfe-data/texas" style={{...}}>Texas 161</a>
<a href="/rfe-data/business" style={{...}}>Business 76</a>
```

### Теги профессий
```jsx
<a href="/rfe-data/it-software" style={{...}}>Software Engineer</a>
<a href="/rfe-data/business" style={{...}}>CEO</a>
```

---

**Дата создания:** 2025-12-23
**Последнее обновление:** 2025-12-23
