# StudyMate frontend

SPA на React 19 + Vite: интерфейс StudyMate. Обращается к backend по REST, токен хранит
в `localStorage`, сгенерированный тест — в `sessionStorage` вкладки.

## Стек

- React 19, TypeScript
- Vite 8, Tailwind CSS 4 (`@tailwindcss/vite`)
- React Router
- shadcn/ui на `@base-ui/react`, иконки `lucide-react`
- Шрифты Manrope и Inter подключаются self-hosted через `@fontsource-variable/*`

## Запуск

```bash
npm install
copy .env.example .env.local     # адрес backend в VITE_API_URL
npm run dev                      # http://localhost:3000
```

Остальные команды:

```bash
npm run build     # проверка типов (tsc --noEmit) и сборка в dist/
npm run preview   # локальный просмотр собранного dist/
npm run lint      # ESLint
```

Для продакшена достаточно раздать содержимое `dist/` любым статическим хостингом:
Node-сервер не нужен.

## Структура

```text
src/
  app/
    router.tsx        маршруты
    require-auth.tsx  защита приватных маршрутов
    shell/            оболочка: сайдбар, профиль, навигация
  pages/              страницы (overview, practice, login, register)
  components/         переиспользуемые компоненты, practice/ — шаги теста
  hooks/              use-session, use-theme
  lib/                API-клиент, хранение теста, форматирование
  styles/aurora.css   токены тем, поверхности, анимации
```

## Темы

Тёмная и светлая темы заданы CSS-переменными в `src/styles/aurora.css`. Класс `dark` на
`<html>` выставляется инлайн-скриптом в `index.html` до первого пейнта, поэтому вспышки
чужой темы нет. Выбор пользователя хранится в `localStorage`, при отсутствии выбора
используется системная настройка.
