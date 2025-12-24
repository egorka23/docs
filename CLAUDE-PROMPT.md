# Промпт для Claude Code

## Как запустить сессию

```bash
cd ~/mintlify-docs && claude
```

---

## Скопируй и вставь при начале сессии:

```
Работаем с Mintlify документацией (MDX файлы) для сайта o1eb1.com/docs/
НЕ используем Google Sheets, Notion или другие базы. Только редактирование .mdx файлов.

СТРУКТУРА:
~/mintlify-docs/
├── docs.json              # Конфигурация навигации
├── rfe-data/              # База RFE кейсов (241 кейс)
│   ├── all.mdx            # Все кейсы
│   ├── nebraska.mdx       # По центрам
│   ├── texas.mdx
│   ├── business.mdx       # По профессиям
│   ├── it-software.mdx
│   └── ...
├── success-stories/       # Истории успеха (108 кейсов)
├── administrative-check/  # FAQ по 221(g), Mandamus и т.д.
└── LINKS-GUIDE.md         # Полный гайд по работе

ПРАВИЛА:
1. Ссылки: href="/rfe-data/..." (БЕЗ /docs в начале!)
2. Frontmatter: title короткий, seo.title длинный с ключевыми словами
3. Заголовки: H2 для "On this page" (6-8 макс), H3 для деталей
4. Нет длинных тире (—), нет стрелок (→) - признаки AI
5. Нет эмодзи если не попросили

QA перед пушем:
rg "→|—" ~/mintlify-docs --glob "*.mdx"  # должно быть 0
grep -r 'href="/docs/' ~/mintlify-docs   # должно быть 0

Локально:
cd ~/mintlify-docs && npx mintlify dev
open http://localhost:3000

Деплой:
cd ~/mintlify-docs && git add . && git commit -m "описание" && git push

Прод: https://o1eb1.com/docs/
Полный гайд: ~/mintlify-docs/LINKS-GUIDE.md
```
