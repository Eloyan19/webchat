# Сравнение режимов RAG — no-RAG · plain · improved

Генерируется `compare_rag.py`. Корпус — Google *compose-samples*. Каждый контрольный вопрос прогнан в трёх режимах против backend `/chat`.

**Метрика — retrieval hit (уровень файла):** попал ли ожидаемый файл (`expected_sources`) в источники ответа. У no-RAG источников нет — показан сам ответ (из знаний модели).

## Сводка

- **plain** (одностадийный retrieval): hit **7/12**
- **improved** (rewrite + rerank + порог): hit **10/12**
- Отрыв improved над plain: **+3** (обычно за счёт multi-turn вопросов, где помогает query rewrite).

| # | Вопрос | plain hit | improved hit |
|---|--------|:---:|:---:|
| 1 | In Jetchat's ConversationUiState, what does the ad… | ✅ | ✅ |
| 2 | What constructor parameters does Jetchat's Convers… | ❌ | ✅ |
| 3 | Which UI tests are included in the Jetchat android… | ✅ | ✅ |
| 4 | In JetNews's HomeViewModel, HomeUiState is a seale… | ✅ | ✅ |
| 5 | In Jetsnack's JetsnackNavController, what does the… | ❌ | ❌ |
| 6 | In Jetsnack, what kind of Kotlin declaration is Sn… | ✅ | ❌ |
| 7 | What fields does the ErrorMessage data class in Je… | ✅ | ✅ |
| 8 | In Reply's ReplyNavigationWrapper composable, how … | ❌ | ✅ |
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

> Based on the Jetchat sample app from Google's Android architecture samples, the `addMessage(msg)` function in `ConversationUiState` inserts a new message at the **end** of the message list (i.e., appended to the bottom). Here's the typical implementation: ```kotlin data class ConversationUiState( va…

**plain** · retrieval hit ✅

> В `ConversationUiState` функция `addMessage(msg)` вставляет новое сообщение в начало списка [3].
> 
> _источники: Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt_

**improved** · retrieval hit ✅

> Согласно источнику [1], `addMessage(msg)` добавляет сообщение в начало списка: `_messages.add(0, msg)`.
> 
> _источники: Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt_

---

### 2. What constructor parameters does Jetchat's ConversationUiState class take?

**Ожидание:** channelName: String, channelMembers: Int, initialMessages: List<Message>. Internally keeps a MutableList backed by toMutableStateList().

**Ожидаемый источник:** `Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt`

**no-RAG**

> Based on the **Jetchat** sample app (Google's Jetpack Compose chat example), the `ConversationUiState` class is a data class that takes the following constructor parameters: ```kotlin data class ConversationUiState( val isLoading: Boolean = false, val messages: List<Message> = emptyList(), val reply…

**plain** · retrieval hit ❌

> Не знаю: в найденных источниках нет ответа на этот вопрос. Уточните или переформулируйте вопрос.

**improved** · retrieval hit ✅

> Jetchat's `ConversationUiState` class takes `channelName: String`, `channelMembers: Int`, and `initialMessages: List<Message>` as constructor parameters [4].
> 
> _источники: Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt_

---

### 3. Which UI tests are included in the Jetchat androidTest suite, and what does each one cover?

**Ожидание:** UserInputTest; ConversationTest (UI tests for the Conversation screen, incl. a test for behavior when dark mode changes); NavigationTest (asserts directly on the Navigation Controller / NavController).

**Ожидаемый источник:** `Jetchat/README.md`

**no-RAG**

> Based on the official **Jetchat** sample project from Google (which demonstrates Jetpack Compose UI and architecture), the `androidTest` suite typically contains **one main UI test class**: `ConversationScreenTest.kt`. The Jetchat sample is intentionally minimal in its UI testing to focus on the Com…

**plain** · retrieval hit ✅

> В Jetchat androidTest включены три UI-теста: ConversationTest, UserInputTest и NavigationTest. - [ConversationTest](app/src/androidTest/java/com/example/compose/jetchat/ConversationTest.kt): проверяет поведение приложения при изменении темного режима. - [UserInputTest](app/src/androidTest/java/com/e…
> 
> _источники: Jetchat/README.md, Jetchat/README.md, Jetchat/README.md_

**improved** · retrieval hit ✅

> The Jetchat androidTest suite includes three UI tests: [ConversationTest](app/src/androidTest/java/com/example/compose/jetchat/ConversationTest.kt) covers UI tests for the Conversation screen, including behavior when dark mode changes [2]; [UserInputTest](app/src/androidTest/java/com/example/compose…
> 
> _источники: Jetchat/README.md, Jetchat/README.md, Jetchat/README.md_

---

### 4. In JetNews's HomeViewModel, HomeUiState is a sealed interface. Which three common properties does it declare?

**Ожидание:** isLoading: Boolean, errorMessages: List<ErrorMessage>, searchInput: String.

**Ожидаемый источник:** `JetNews/app/src/main/java/com/example/jetnews/ui/home/HomeViewModel.kt`

**no-RAG**

> Based on the JetNews sample app from Google's architecture samples, the `HomeUiState` sealed interface declares these three common properties: 1. **`isLoading: Boolean`** - Indicates whether the data is currently loading 2. **`isEmpty: Boolean`** - Indicates whether the feed/content is empty 3. **`e…

**plain** · retrieval hit ✅

> It declares three common properties: 'isLoading', 'errorMessages', and 'searchInput' [1].
> 
> _источники: JetNews/app/src/main/java/com/example/jetnews/ui/home/HomeViewModel.kt_

**improved** · retrieval hit ✅

> HomeUiState declares three common properties: `isLoading: Boolean`, `errorMessages: List<ErrorMessage>`, and `searchInput: String`. [1]
> 
> _источники: JetNews/app/src/main/java/com/example/jetnews/ui/home/HomeViewModel.kt_

---

### 5. In Jetsnack's JetsnackNavController, what does the upPress() function do, and what annotation is the class marked with?

**Ожидание:** upPress() calls navController.navigateUp(). The class is annotated @Stable.

**Ожидаемый источник:** `Jetsnack/app/src/main/java/com/example/jetsnack/ui/navigation/JetsnackNavController.kt`

**no-RAG**

> Based on the typical implementation of `JetsnackNavController` in the Jetsnack sample app (a Jetpack Compose tutorial app by Google), here is the answer: **1. What does `upPress()` do?** The `upPress()` function handles the system back press (or the up navigation button in the top app bar). It navig…

**plain** · retrieval hit ❌

> Не знаю: в найденных источниках нет ответа на этот вопрос. Уточните или переформулируйте вопрос.

**improved** · retrieval hit ❌

> Не знаю: в найденных источниках нет ответа на этот вопрос. Уточните или переформулируйте вопрос.

---

### 6. In Jetsnack, what kind of Kotlin declaration is SnackbarManager, and how does it expose its messages?

**Ожидание:** It is an object (singleton) responsible for managing snackbar messages. It backs a private MutableStateFlow<List<Message>> _messages and exposes it as a read-only StateFlow<List<Message>> via messages; showMessage takes a @StringRes messageTextId.

**Ожидаемый источник:** `Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt`

**no-RAG**

> Based on the Jetsnack sample app (from the official Android Architecture Blueprints), `SnackbarManager` is an **object declaration** (a Kotlin singleton). Here's how it's defined and how it exposes its messages: ## Declaration ```kotlin object SnackbarManager { // ... } ``` ## How it exposes message…

**plain** · retrieval hit ✅

> В Jetsnack `SnackbarManager` — это объект (singleton), объявленный через `object SnackbarManager`. Он управляет сообщениями Snackbar через `MutableStateFlow<List<Message>>` и предоставляет их через публичное свойство `messages: StateFlow<List<Message>>`, получаемое из `_messages.asStateFlow()`. [2]
> 
> _источники: Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt_

**improved** · retrieval hit ❌

> Не знаю: в найденных источниках нет ответа на этот вопрос. Уточните или переформулируйте вопрос.

---

### 7. What fields does the ErrorMessage data class in JetNews contain?

**Ожидание:** id: Long and messageId: Int annotated with @StringRes. i.e. data class ErrorMessage(val id: Long, @StringRes val messageId: Int).

**Ожидаемый источник:** `JetNews/app/src/main/java/com/example/jetnews/utils/ErrorMessage.kt`

**no-RAG**

> Based on the standard implementation of JetNews (Google's official Now in Android app), the `ErrorMessage` data class typically contains the following fields: ```kotlin data class ErrorMessage( val message: String? = null, // The error message string val throwable: Throwable? = null // The original …

**plain** · retrieval hit ✅

> The `ErrorMessage` data class contains two fields: `id` of type `Long` and `messageId` of type `Int` [2].
> 
> _источники: JetNews/app/src/main/java/com/example/jetnews/utils/ErrorMessage.kt_

**improved** · retrieval hit ✅

> `ErrorMessage` содержит поля `id: Long` и `messageId: Int` [1].
> 
> _источники: JetNews/app/src/main/java/com/example/jetnews/utils/ErrorMessage.kt_

---

### 8. In Reply's ReplyNavigationWrapper composable, how is the navigation layout type decided (what APIs drive it)?

**Ожидание:** It uses currentWindowAdaptiveInfo() and currentWindowSize() (converted to DpSize) and computes a navLayoutType with a when-expression to pick the adaptive navigation layout based on window size/posture.

**Ожидаемый источник:** `Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt`

**no-RAG**

> In Reply's `ReplyNavigationWrapper` composable, the navigation layout type is decided through a combination of **screen size** and **window size class** APIs from the Android `WindowSizeClass` API. Specifically: ## Key APIs Driving Layout Decision ### 1. **Window Size Class** The primary decision po…

**plain** · retrieval hit ❌

> В `ReplyNavigationWrapper` тип навигации (navigation type) выбирается динамически в зависимости от размера и состояния устройства. Используются компоненты Material 3: `BottomNavigationBar` для компактных устройств, `NavigationRail` для средних, `PermanentNavigationDrawer` для больших, а также `Modal…
> 
> _источники: Reply/README.md_

**improved** · retrieval hit ✅

> В `ReplyNavigationWrapper` тип навигационного макета (`navLayoutType`) определяется с помощью `currentWindowAdaptiveInfo()` (из `material3-adaptive`), который предоставляет `WindowSizeClass` и `windowPosture`. Логика следующая: если `windowPosture.isTabletop` или `WindowSizeClass` компактный — испол…
> 
> _источники: Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt_

---

### 9. What are the three main screens/components of the Jetcaster phone app?

**Ожидание:** The home screen, the podcast details screen, and the player screen.

**Ожидаемый источник:** `Jetcaster/README.md`

**no-RAG**

> Based on the official Jetcaster sample app from Google (a Jetpack Compose codebase for a podcast player), the three main screens/components of the phone app are: 1. **Home Screen (Home / For You)** – This is the primary landing screen. It displays a "For You" feed of curated podcast episodes, catego…

**plain** · retrieval hit ✅

> The Jetcaster phone app has three main components: the home screen, the podcast details screen, and the player screen [1].
> 
> _источники: Jetcaster/README.md_

**improved** · retrieval hit ✅

> The Jetcaster phone app has three main components: the home screen, the podcast details screen, and the player screen [1].
> 
> _источники: Jetcaster/README.md_

---

### 10. What copyright year is stated in the top-level (root) README license header of the Jetpack Compose Samples repository?

**Ожидание:** 2024 ('Copyright 2024 The Android Open Source Project') in the root README — note individual samples like Jetchat/Jetsnack state 2020, so the root differs.

**Ожидаемый источник:** `README.md`

**no-RAG**

> Based on the Jetpack Compose Samples repository, the copyright year stated in the top-level (root) README license header is **2021**. The specific line from the README is: ``` Copyright 2021 The Android Open Source Project ```

**plain** · retrieval hit ✅

> Copyright 2024
> 
> _источники: README.md_

**improved** · retrieval hit ✅

> 2024 [1]
> 
> _источники: README.md_

---

### 11. How does it decide which one to show?

_multi-turn: вопрос ссылается на предыдущие реплики диалога._

**Ожидание:** ReplyNavigationWrapper uses currentWindowAdaptiveInfo() and currentWindowSize() (as DpSize) and a when-expression to pick navLayoutType based on the window size class / posture. The follow-up 'it' = Reply navigation; only resolvable from context.

**Ожидаемый источник:** `Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt`

**no-RAG**

> Reply's sample app (typically demonstrated in Google's Material Design 3 (M3) and Jetpack Compose examples) decides which navigation component to show based on the **current window size class**, specifically the **width** of the screen. It follows the standard M3 responsive layout guidelines to dete…

**plain** · retrieval hit ❌

> Не знаю: в найденных источниках нет ответа на этот вопрос. Уточните или переформулируйте вопрос.

**improved** · retrieval hit ✅ · переписанный запрос: _Reply sample adaptive Material 3 navigation bottom bar navigation rail drawer selection window size criteria_

> Решение зависит от ширины окна и высоты, а также от наличия стола (tabletop). Если устройство имеет стол (tabletop) или компактную ширину (compact), используется `NavigationSuiteType.NavigationBar`. Если ширина больше или равна 1200 dp (расширенный (expanded) класс размера), выбирается `NavigationSu…
> 
> _источники: Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt_

---

### 12. What type does it expose them as?

_multi-turn: вопрос ссылается на предыдущие реплики диалога._

**Ожидание:** It exposes the messages as a read-only StateFlow<List<Message>> (backed by a private MutableStateFlow, surfaced via asStateFlow()). 'it' = SnackbarManager, 'them' = messages; only resolvable from context.

**Ожидаемый источник:** `Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt`

**no-RAG**

> Based on the Jetsnack codebase, the `SnackbarManager` exposes snackbar messages as **`SnackbarMessage`** objects (accessed via a `StateFlow`). Specifically, it exposes them as: ```kotlin val messages: StateFlow<SnackbarMessage?> ``` This means it exposes a `StateFlow` that emits `SnackbarMessage?` (…

**plain** · retrieval hit ❌

> Не знаю: в найденных источниках нет ответа на этот вопрос. Уточните или переформулируйте вопрос.

**improved** · retrieval hit ✅ · переписанный запрос: _SnackbarManager type of snackbar messages exposed in Jetsnack_

> It exposes them as a `StateFlow<List<Message>>` via the `messages` property, which is backed by a private `MutableStateFlow<List<Message>>` [_messages]. [1]
> 
> _источники: Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt_

---
