# Телеграм-бот для работы с Учебным офисом и LMS(LMS Buddy)

### Описание проекта
Телеграм-бот для взаимодействия студентов с Учебным офисом и системой LMS. Бот предоставляет удобные функции для получения уведомлений о занятиях, поиска свободных аудиторий, просмотра часто задаваемых вопросов, подачи заявок на справки, а также подготовки к независимым экзаменам.

### Функционал
- **Уведомления об учебных парах**: бот отправляет напоминания о предстоящих занятиях с указанием времени, предмета и аудитории.
- **Поиск свободных аудиторий**: возможность найти доступные аудитории для самостоятельной работы.
- **F.A.Q. для студентов**: база часто задаваемых вопросов, доступная для быстрого поиска.
- **Сбор справок**: удобная подача заявок на различные справки.
- **Подготовка к независимым экзаменам**: информация и напоминания для студентов, готовящихся к экзаменам.
- **Обратная связь с Учебным офисом**: доска объявлений и возможность отправки отзывов от студентов.

### Структура проекта
1. **База данных**
   - **Таблица студентов**: ID студента, имя, контактные данные, статус подписки на уведомления.
   - **Таблица расписания**: дата, время, предмет, аудитория.
   - **Таблица аудиторий**: номер аудитории, доступность.
   - **Таблица FAQ**: вопросы и ответы.

2. **Архитектура**
   - **Backend**: Python, библиотека для работы с Telegram API.
   - **Frontend**: интерфейс взаимодействия через Телеграм.
   - **API**: подключение к LMS для получения актуального расписания и данных.

3. **Логика проекта**
   - Модуль для рассылки уведомлений.
   - Модуль поиска свободных аудиторий.
   - Модуль FAQ и заявок на справки.
   - Модуль для работы с доской объявлений.

### Распределение по ролям (4 человека)

- **Технический лидер и разработчик бота**: (Даниил, Telegram: @uchenlk)  
  Отвечает за разработку основной логики бота и подключение к LMS. Занимается интеграцией API и разработкой базового функционала: уведомления, FAQ, сбор справок и поиск аудиторий.

- **Ответственный за интерфейс и UX**: (Георгий, Telegram: @alibaba_dushan)  
  Проектирует сценарии взаимодействия, обеспечивает удобство использования и отвечает за представление данных. Настраивает функции обратной связи, доску объявлений и взаимодействие с пользователями через Телеграм.

- **Ответственный за базу данных и тестирование**: (Степан, Telegram: @S_1vnv)  
  Проектирует и поддерживает базу данных, отвечает за хранение данных о студентах, расписании, FAQ и справках. Проводит тестирование функциональности бота, исправляет ошибки и собирает отзывы команды для улучшений.


- **Ответственный за поиск данных и систему привилегий пользователей**: (Никита, Telegram: @Sauforn)
  Отвечает за логику, написание и тестирование функций поиска данных о студентах, расписании, FAQ и справках. 
Реализует систему доступа пользователей к различным операциям: формирование постов для досок объявлений, редактирование FAQ.  Дает гарантию доступа пользователей только к собственным данным.
