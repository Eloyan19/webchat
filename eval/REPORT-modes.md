# Сравнение режимов RAG — no-RAG · plain · improved

Генерируется `compare_rag.py`. Корпус — Google *compose-samples*. Каждый контрольный вопрос прогнан в трёх режимах против backend `/chat`.

**Метрика — retrieval hit (уровень файла):** попал ли ожидаемый файл (`expected_sources`) в источники ответа. У no-RAG источников нет — показан сам ответ (из знаний модели).

## Сводка

- **plain** (одностадийный retrieval): hit **9/12**
- **improved** (rewrite + rerank + порог): hit **12/12**
- Отрыв improved над plain: **+3** (обычно за счёт multi-turn вопросов, где помогает query rewrite).

| # | Вопрос | plain hit | improved hit |
|---|--------|:---:|:---:|
| 1 | In Jetchat's ConversationUiState, what does the ad… | ✅ | ✅ |
| 2 | What constructor parameters does Jetchat's Convers… | ❌ | ✅ |
| 3 | Which UI tests are included in the Jetchat android… | ✅ | ✅ |
| 4 | In JetNews's HomeViewModel, HomeUiState is a seale… | ✅ | ✅ |
| 5 | In Jetsnack's JetsnackNavController, what does the… | ✅ | ✅ |
| 6 | In Jetsnack, what kind of Kotlin declaration is Sn… | ✅ | ✅ |
| 7 | What fields does the ErrorMessage data class in Je… | ✅ | ✅ |
| 8 | In Reply's ReplyNavigationWrapper composable, how … | ✅ | ✅ |
| 9 | What are the three main screens/components of the … | ✅ | ✅ |
| 10 | What copyright year is stated in the top-level (ro… | ✅ | ✅ |
| 11 | 🔁 How does it decide which one to show?… | ❌ | ✅ |
| 12 | 🔁 What type does it expose them as?… | ❌ | ✅ |

---

## По вопросам (ответ каждого режима)

### 1. In Jetchat's ConversationUiState, what does the addMessage(msg) function do — at which position in the list is a new message inserted?

**Ожидание:** It inserts the new message at the beginning of the list (index 0): _messages.add(0, msg). Comment says 'Add to the beginning of the list'.

**Ожидаемый источник:** `Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt`

**no-RAG**

> Based on the standard implementation patterns in Jetchat (which is likely a Jetpack Compose chat application), the `addMessage(msg)` function in `ConversationUiState` typically inserts a new message at the **end** of the messages list. Here's the typical implementation pattern: ```kotlin data class …

**plain** · retrieval hit ✅

> В `ConversationUiState` функция `addMessage(msg)` добавляет новое сообщение **в начало списка** (индекс 0) [3]. ```kotlin fun addMessage(msg: Message) { _messages.add(0, msg) // Add to the beginning of the list } ```
> 
> _источники: Jetchat/app/src/main/java/com/example/compose/jetchat/widget/composables/MessagesWidget.kt, Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/Conversation.kt, Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt, Jetchat/app/src/main/java/com/example/compose/jetchat/widget/composables/MessagesWidget.kt, Jetchat/README.md_

**improved** · retrieval hit ✅

> Согласно коду в [1], функция `addMessage(msg)` добавляет новое сообщение в начало списка `_messages`: ```kotlin fun addMessage(msg: Message) { _messages.add(0, msg) // Add to the beginning of the list } ``` Здесь используется метод `add(0, msg)` — передача индекса 0 означает вставку на нулевую позиц…
> 
> _источники: Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt, Jetchat/README.md, Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/Conversation.kt, Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/Conversation.kt, Jetchat/app/src/main/java/com/example/compose/jetchat/components/JetchatDrawer.kt_

---

### 2. What constructor parameters does Jetchat's ConversationUiState class take?

**Ожидание:** channelName: String, channelMembers: Int, initialMessages: List<Message>. Internally keeps a MutableList backed by toMutableStateList().

**Ожидаемый источник:** `Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt`

**no-RAG**

> Based on the Jetchat sample app from Google's Android architecture samples, the `ConversationUiState` data class typically takes the following constructor parameters: ```kotlin data class ConversationUiState( val profile: Profile, // User profile information val messages: List<Message>, // List of c…

**plain** · retrieval hit ❌

> Исходя из предоставленного контекста, информации о конструкторе класса `ConversationUiState` нет. В контексте упоминается, что этот класс "определяет данные для отображения" [1], но конкретные параметры конструктора не описаны.
> 
> _источники: Jetchat/README.md, Jetchat/README.md, Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/Conversation.kt, Jetchat/README.md, Jetchat/README.md_

**improved** · retrieval hit ✅

> Согласно контексту [4], класс `ConversationUiState` принимает следующие параметры конструктора: - `channelName: String` - `channelMembers: Int` - `initialMessages: List<Message>`
> 
> _источники: Jetchat/README.md, Jetchat/app/src/androidTest/java/com/example/compose/jetchat/ConversationTest.kt, Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/Conversation.kt, Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt, Jetchat/README.md_

---

### 3. Which UI tests are included in the Jetchat androidTest suite, and what does each one cover?

**Ожидание:** UserInputTest; ConversationTest (UI tests for the Conversation screen, incl. a test for behavior when dark mode changes); NavigationTest (asserts directly on the Navigation Controller / NavController).

**Ожидаемый источник:** `Jetchat/README.md`

**no-RAG**

> Based on the **Jetchat** sample app from Google (Android Architecture samples), the `androidTest` suite (specifically in `com.example.compose.jetchat` or similar package) typically includes **three main UI tests**: --- ### 1. **ChatScreenTest** (or `ConversationTest`) **File:** `ChatScreenTest.kt` *…

**plain** · retrieval hit ✅

> Based on the provided context, the Jetchat sample app includes three UI tests in its `androidTest` suite [1]: 1. **ConversationTest** [2]: Contains UI tests for the Conversation screen. It includes a test that checks how the app behaves when dark mode is changed. 2. **UserInputTest** [3]: Checks tha…
> 
> _источники: Jetchat/README.md, Jetchat/README.md, Jetchat/README.md, Jetchat/README.md, Jetchat/README.md_

**improved** · retrieval hit ✅

> Based on the provided context, the Jetchat sample includes three UI tests in its `androidTest` suite [1]: 1. **ConversationTest** – Contains UI tests for the Conversation screen, including a test that checks the behavior of the app when dark mode changes [2]. 2. **UserInputTest** – Checks that the u…
> 
> _источники: Jetchat/README.md, Jetchat/README.md, Jetchat/README.md, Jetchat/README.md, Jetchat/README.md_

---

### 4. In JetNews's HomeViewModel, HomeUiState is a sealed interface. Which three common properties does it declare?

**Ожидание:** isLoading: Boolean, errorMessages: List<ErrorMessage>, searchInput: String.

**Ожидаемый источник:** `JetNews/app/src/main/java/com/example/jetnews/ui/home/HomeViewModel.kt`

**no-RAG**

> Based on the JetNews architecture commonly used in Android development with Jetpack Compose, the `HomeUiState` sealed interface typically declares these three common properties: 1. **`isLoading`** - A boolean indicating whether data is currently being fetched 2. **`errorMessage`** - A nullable Strin…

**plain** · retrieval hit ✅

> В HomeUiState как sealed interface объявлены три общих свойства [1]: 1. **`isLoading: Boolean`** 2. **`errorMessages: List<ErrorMessage>`** 3. **`searchInput: String`** Эти свойства присутствуют в обоих подклассах (`NoPosts` и `HasPosts`) [1].
> 
> _источники: JetNews/app/src/main/java/com/example/jetnews/ui/home/HomeViewModel.kt, JetNews/app/src/main/java/com/example/jetnews/ui/home/HomeViewModel.kt, JetNews/README.md, JetNews/README.md, Jetchat/README.md_

**improved** · retrieval hit ✅

> Согласно контексту [1], `HomeUiState` — это sealed interface, который объявляет три общих свойства: 1. `isLoading: Boolean` 2. `errorMessages: List<ErrorMessage>` 3. `searchInput: String`
> 
> _источники: JetNews/app/src/main/java/com/example/jetnews/ui/home/HomeViewModel.kt, Jetcaster/tv/src/main/java/com/example/jetcaster/tv/ui/discover/DiscoverScreenViewModel.kt, Jetcaster/tv/src/main/java/com/example/jetcaster/tv/ui/player/PlayerScreenViewModel.kt, Jetcaster/tv/src/main/java/com/example/jetcaster/tv/ui/search/SearchScreenViewModel.kt, Jetcaster/README.md_

---

### 5. In Jetsnack's JetsnackNavController, what does the upPress() function do, and what annotation is the class marked with?

**Ожидание:** upPress() calls navController.navigateUp(). The class is annotated @Stable.

**Ожидаемый источник:** `Jetsnack/app/src/main/java/com/example/jetsnack/ui/navigation/JetsnackNavController.kt`

**no-RAG**

> Based on the Jetsnack sample app (part of the official Android Jetpack Compose samples), here is the answer: **What `upPress()` does:** The `upPress()` function is a navigation handler that typically calls `navController.navigateUp()`. Its purpose is to navigate to the previous screen in the back st…

**plain** · retrieval hit ✅

> В предоставленном контексте нет информации о функции `upPress()` в `JetsnackNavController` и об аннотации, которой помечен этот класс. В контексте [2] описывается только composable-функция `rememberJetsnackNavController`, которая создаёт экземпляр `JetsnackNavController`. Для получения ответа на ваш…
> 
> _источники: Jetcaster/core/data/src/main/java/com/example/jetcaster/core/data/Dispatcher.kt, Jetsnack/app/src/main/java/com/example/jetsnack/ui/navigation/JetsnackNavController.kt, Jetsnack/README.md, Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/search/Results.kt, Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/Home.kt_

**improved** · retrieval hit ✅

> Исходя из предоставленного контекста, информация о функции `upPress()` и аннотации класса `JetsnackNavController` отсутствует. В контексте [2] показана только функция `rememberJetsnackNavController()`, которая создаёт экземпляр `JetsnackNavController`, и в контексте [1] `upPress` используется как ко…
> 
> _источники: Jetsnack/app/src/main/java/com/example/jetsnack/ui/JetsnackApp.kt, Jetsnack/app/src/main/java/com/example/jetsnack/ui/navigation/JetsnackNavController.kt, Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/Home.kt, Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/Home.kt, Jetsnack/app/src/main/java/com/example/jetsnack/ui/home/Home.kt_

---

### 6. In Jetsnack, what kind of Kotlin declaration is SnackbarManager, and how does it expose its messages?

**Ожидание:** It is an object (singleton) responsible for managing snackbar messages. It backs a private MutableStateFlow<List<Message>> _messages and exposes it as a read-only StateFlow<List<Message>> via messages; showMessage takes a @StringRes messageTextId.

**Ожидаемый источник:** `Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt`

**no-RAG**

> Based on the Jetpack Compose sample app **Jetsnack**, the `SnackbarManager` is an **object declaration** (a Kotlin singleton). It exposes its messages through a **`StateFlow`** and a **function to send new messages**. Here is the exact pattern used in the Jetsnack codebase: ### 1. The Declaration: `…

**plain** · retrieval hit ✅

> В контексте [2] указано, что `SnackbarManager` — это **`object`** (синглтон). Он предоставляет свои сообщения через **`StateFlow<List<Message>>`**, а точнее — через свойство `messages`, которое является `StateFlow` и доступно для чтения как `_messages.asStateFlow()`.
> 
> _источники: Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snackbar.kt, Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt, Jetsnack/README.md, Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snacks.kt, Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snacks.kt_

**improved** · retrieval hit ✅

> В Jetsnack `SnackbarManager` является объявлением **`object`** (синглтоном) [3]. Он предоставляет доступ к своим сообщениям через публичное свойство `messages: StateFlow<List<Message>>`, которое возвращает неизменяемый `StateFlow` на основе приватного `MutableStateFlow<List<Message>>` [3].
> 
> _источники: JetNews/app/src/androidTest/java/com/example/jetnews/HomeScreenTests.kt, Jetsnack/README.md, Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt, JetNews/app/src/main/java/com/example/jetnews/ui/components/JetnewsSnackbarHost.kt, Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snacks.kt_

---

### 7. What fields does the ErrorMessage data class in JetNews contain?

**Ожидание:** id: Long and messageId: Int annotated with @StringRes. i.e. data class ErrorMessage(val id: Long, @StringRes val messageId: Int).

**Ожидаемый источник:** `JetNews/app/src/main/java/com/example/jetnews/utils/ErrorMessage.kt`

**no-RAG**

> Based on the standard implementation in the **JetNews** sample app from Android Developers (specifically in the `com.example.jetnews.data` or a similar package), the `ErrorMessage` data class typically contains the following field: ```kotlin data class ErrorMessage(val message: String) ``` **Explana…

**plain** · retrieval hit ✅

> Согласно источнику [2], data class `ErrorMessage` содержит два поля: - `val id: Long` - `@StringRes val messageId: Int`
> 
> _источники: JetNews/README.md, JetNews/app/src/main/java/com/example/jetnews/utils/ErrorMessage.kt, JetNews/README.md, JetNews/README.md, JetNews/README.md_

**improved** · retrieval hit ✅

> Согласно контексту [1], data class `ErrorMessage` содержит два поля: - `id: Long` - `messageId: Int` (с аннотацией `@StringRes`)
> 
> _источники: JetNews/app/src/main/java/com/example/jetnews/utils/ErrorMessage.kt, JetNews/app/src/main/java/com/example/jetnews/JetnewsApplication.kt, JetNews/app/src/main/java/com/example/jetnews/ui/home/HomeViewModel.kt, JetNews/README.md, JetNews/app/src/main/java/com/example/jetnews/data/posts/PostsRepository.kt_

---

### 8. In Reply's ReplyNavigationWrapper composable, how is the navigation layout type decided (what APIs drive it)?

**Ожидание:** It uses currentWindowAdaptiveInfo() and currentWindowSize() (converted to DpSize) and computes a navLayoutType with a when-expression to pick the adaptive navigation layout based on window size/posture.

**Ожидаемый источник:** `Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt`

**no-RAG**

> In Reply's `ReplyNavigationWrapper` composable, the navigation layout type is decided through a **sealed class hierarchy** and a **decoration pattern** rather than direct API calls. Here's how it works: ## Key APIs and Decision Mechanism ### 1. **NavigationType Sealed Class** The core decision is dr…

**plain** · retrieval hit ✅

> Исходя из предоставленного контекста, информация о том, как в `ReplyNavigationWrapper` выбирается тип навигационного лэйаута, отсутствует. Однако в контексте [3] указано, что в зависимости от размера и состояния экрана динамически выбирается правильный [тип навигации](app/src/main/java/com/example/r…
> 
> _источники: Reply/app/src/main/java/com/example/reply/ui/ReplyApp.kt, Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt, Reply/README.md, Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt, Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationActions.kt_

**improved** · retrieval hit ✅

> В `ReplyNavigationWrapper` выбор типа навигации осуществляется на основе двух API: **`currentWindowAdaptiveInfo()`** и **`currentWindowSize()`**. Логика выбора `navLayoutType` следующая (из [3]): 1. Если **`adaptiveInfo.windowPosture.isTabletop`** — используется `NavigationBar`. 2. Если **`adaptiveI…
> 
> _источники: Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt, Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt, Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt, Reply/app/src/main/java/com/example/reply/ui/ReplyListContent.kt, Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt_

---

### 9. What are the three main screens/components of the Jetcaster phone app?

**Ожидание:** The home screen, the podcast details screen, and the player screen.

**Ожидаемый источник:** `Jetcaster/README.md`

**no-RAG**

> Based on the standard Jetcaster app structure (the open-source Jetpack Compose podcast app from Google), the three main screens/components are: 1. **Home Screen (Podcast Discovery):** Displays a feed of popular or trending podcast episodes, often with a "For You" section and category-based recommend…

**plain** · retrieval hit ✅

> Основываясь на контексте [1], три основных компонента экрана в приложении Jetcaster для телефона: 1. **Домашний экран** (Home screen) 2. **Экран сведений о подкасте** (Podcast details screen) 3. **Экран плеера** (Player screen)
> 
> _источники: Jetcaster/README.md, Jetcaster/README.md, README.md, Jetcaster/README.md, Jetcaster/README.md_

**improved** · retrieval hit ✅

> Согласно документации [1], Jetcaster sample включает 3 основных компонента: 1. **Home screen (главный экран)** 2. **Podcast details screen (экран с информацией о подкасте)** 3. **Player screen (экран плеера)** Также там отмечено, что на главном экране есть подэкран с вкладками "Your Library" и "Disc…
> 
> _источники: Jetcaster/README.md, Jetcaster/README.md, Jetcaster/README.md, README.md, JetNews/README.md_

---

### 10. What copyright year is stated in the top-level (root) README license header of the Jetpack Compose Samples repository?

**Ожидание:** 2024 ('Copyright 2024 The Android Open Source Project') in the root README — note individual samples like Jetchat/Jetsnack state 2020, so the root differs.

**Ожидаемый источник:** `README.md`

**no-RAG**

> Based on the Jetpack Compose Samples repository, the top-level (root) README file does not contain a direct copyright year in a license header. However, the repository is generally licensed under the Apache License 2.0. The copyright year most commonly associated with the root-level license (found i…

**plain** · retrieval hit ✅

> В лицензии корневого (root) README верхнего уровня для Jetpack Compose Samples указан **2024** год [1].
> 
> _источники: README.md, JetLagged/README.md, Jetsnack/README.md, Jetchat/README.md, README.md_

**improved** · retrieval hit ✅

> Согласно контексту [1], в верхнем (корневом) README файле репозитория Jetpack Compose Samples в заголовке лицензии указан год: **2024**.
> 
> _источники: README.md, Jetchat/README.md, Jetsnack/README.md, JetLagged/README.md, Reply/README.md_

---

### 11. How does it decide which one to show?

_multi-turn: вопрос ссылается на предыдущие реплики диалога._

**Ожидание:** ReplyNavigationWrapper uses currentWindowAdaptiveInfo() and currentWindowSize() (as DpSize) and a when-expression to pick navLayoutType based on the window size class / posture. The follow-up 'it' = Reply navigation; only resolvable from context.

**Ожидаемый источник:** `Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt`

**no-RAG**

> Reply uses **window size classes** (based on the device's screen width) to decide which navigation component to show. This is a standard part of Material 3's adaptive layout strategy in Jetpack Compose. Here is the breakdown of how it decides: 1. **Measuring the Window:** The app measures the curren…

**plain** · retrieval hit ❌

> В предоставленном контексте нет информации о том, как образец *Reply* выбирает, какой навигационный компонент показывать. В контексте упоминается только образец *Jetnews*, в котором используется [`InterestsAdaptiveContentLayout`][4], переключающийся между одной и двумя колонками в зависимости от шир…
> 
> _источники: JetNews/README.md, JetNews/app/src/main/java/com/example/jetnews/ui/interests/SelectTopicButton.kt, Jetcaster/tv/src/main/java/com/example/jetcaster/tv/ui/discover/DiscoverScreenViewModel.kt, JetNews/app/src/main/java/com/example/jetnews/ui/interests/InterestsScreen.kt, JetNews/app/src/main/java/com/example/jetnews/ui/interests/SelectTopicButton.kt_

**improved** · retrieval hit ✅ · переписанный запрос: _Reply sample adaptive navigation selection decision based on window size_

> Reply определяет тип навигации на основе размера и состояния окна устройства. В функции `ReplyNavigationWrapper` [1] используются два основных критерия: 1. **Класс размера окна** (`WindowSizeClass`) и поза устройства (`WindowPosture`) [1][4]. 2. **Ширина окна** в `dp` [1]. Логика выбора следующая [1…
> 
> _источники: Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt, Reply/README.md, Reply/README.md, Reply/README.md, Reply/README.md_

---

### 12. What type does it expose them as?

_multi-turn: вопрос ссылается на предыдущие реплики диалога._

**Ожидание:** It exposes the messages as a read-only StateFlow<List<Message>> (backed by a private MutableStateFlow, surfaced via asStateFlow()). 'it' = SnackbarManager, 'them' = messages; only resolvable from context.

**Ожидаемый источник:** `Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt`

**no-RAG**

> Based on the typical implementation in the **Jetsnack** sample app (from the Android Developers `nowinandroid` / Jetpack Compose samples), the `SnackbarManager` object doesn't just expose snackbar messages directly. Instead, it uses a **`MutableSharedFlow`** (which it exposes as a **`SharedFlow`**).…

**plain** · retrieval hit ❌

> В предоставленном контексте нет информации о `SnackbarManager` и типе данных, который он использует для отображения сообщений.
> 
> _источники: Jetcaster/tv/src/main/java/com/example/jetcaster/tv/ui/discover/DiscoverScreenViewModel.kt, Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Surface.kt, Reply/app/src/main/java/com/example/reply/ui/utils/WindowStateUtils.kt, JetNews/app/src/main/java/com/example/jetnews/ui/home/PostCardTop.kt, Jetcaster/core/domain/src/main/java/com/example/jetcaster/core/model/PodcastInfo.kt_

**improved** · retrieval hit ✅ · переписанный запрос: _SnackbarManager exposes snackbar messages type and usage in Jetsnack_

> It exposes messages as a `StateFlow<List<Message>>` [1].
> 
> _источники: Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt, JetNews/app/src/main/java/com/example/jetnews/ui/components/JetnewsSnackbarHost.kt, Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snackbar.kt, Jetsnack/app/src/main/java/com/example/jetsnack/ui/components/Snacks.kt, JetNews/app/src/androidTest/java/com/example/jetnews/HomeScreenTests.kt_

---
