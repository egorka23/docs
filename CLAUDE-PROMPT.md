# Промпт для Claude Code

Скопируй и вставь при начале новой сессии:

---

```
Работаем с Mintlify docs в ~/mintlify-docs/

ПРАВИЛА:
1. Ссылки: href="/rfe-data/..." (БЕЗ /docs). Mintlify сам добавит /docs на проде
2. Frontmatter: title короткий (для меню), seo.title длинный (для Google)
3. Заголовки: H2 для "On this page" (6-8 макс), H3 для деталей
4. Нет длинных тире (—), нет стрелок (→) - это признаки AI
5. Нет эмодзи если не попросили

QA перед пушем:
rg "→|—" ~/mintlify-docs --glob "*.mdx"  # должно быть 0
grep -r 'href="/docs/' ~/mintlify-docs   # должно быть 0

Локально:
cd ~/mintlify-docs && npx mintlify dev
open http://localhost:3000

Деплой:
git add . && git commit -m "описание" && git push

Прод: https://o1eb1.com/docs/
Полный гайд: ~/mintlify-docs/LINKS-GUIDE.md
```

---

## Короткая версия (минимум)

```
Mintlify docs: ~/mintlify-docs/
- Ссылки без /docs: href="/rfe-data/..."
- Нет — и →
- Гайд: ~/mintlify-docs/LINKS-GUIDE.md
```
