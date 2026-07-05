# Цитаты, источники и режим «не знаю» — отчёт eval

Генерируется `compare.py`. Корпус — Google *compose-samples*. Прогон в **cited-режиме** (`useRag=true, improvedRag=true`): извлечение → порог-фильтр → генерация со структурированными цитатами. Цитаты валидируются backend как дословные подстроки чанков; здесь судья DeepSeek проверяет, следует ли смысл ответа из этих цитат.

## Сводка

- **Источники в ответе:** 11/12
- **Цитаты в ответе:** 11/12
- **Ответ обоснован цитатами (судья):** 11/12
- **Off-topic → «не знаю» (abstain):** 5/5

## In-domain

| # | Вопрос | Источники | Цитаты | Обоснован | Retrieval hit |
|---|--------|:---:|:---:|:---:|:---:|
| 1 | In Jetchat's ConversationUiState, what does th… | ✅ | ✅ | ✅ | ✅ |
| 2 | What constructor parameters does Jetchat's Con… | ✅ | ✅ | ✅ | ✅ |
| 3 | Which UI tests are included in the Jetchat and… | ✅ | ✅ | ✅ | ✅ |
| 4 | In JetNews's HomeViewModel, HomeUiState is a s… | ✅ | ✅ | ✅ | ✅ |
| 5 | In Jetsnack's JetsnackNavController, what does… | ❌ | ❌ | — | ❌ |
| 6 | In Jetsnack, what kind of Kotlin declaration i… | ✅ | ✅ | ✅ | ✅ |
| 7 | What fields does the ErrorMessage data class i… | ✅ | ✅ | ✅ | ✅ |
| 8 | In Reply's ReplyNavigationWrapper composable, … | ✅ | ✅ | ✅ | ✅ |
| 9 | What are the three main screens/components of … | ✅ | ✅ | ✅ | ✅ |
| 10 | What copyright year is stated in the top-level… | ✅ | ✅ | ✅ | ✅ |
| 11 | 🔁 How does it decide which one to show?… | ✅ | ✅ | ✅ | ✅ |
| 12 | 🔁 What type does it expose them as?… | ✅ | ✅ | ✅ | ✅ |

## Off-topic (проверка режима «не знаю»)

| # | Вопрос | Abstain «не знаю»? |
|---|--------|:---:|
| 13 | What is the boiling point of water at sea level?… | ✅ |
| 14 | Who won the FIFA World Cup in 1998?… | ✅ |
| 15 | Give me a recipe for classic Italian tiramisu.… | ✅ |
| 16 | What is the capital of Australia?… | ✅ |
| 17 | How does photosynthesis convert sunlight into energy… | ✅ |

---

## 1. In Jetchat's ConversationUiState, what does the addMessage(msg) function do — at which position in the list is a new message inserted?

**Ожидание:** It inserts the new message at the beginning of the list (index 0): _messages.add(0, msg). Comment says 'Add to the beginning of the list'.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Цитата подтверждает, что addMessage(msg) добавляет сообщение в начало списка.

**Ответ:**

> В `ConversationUiState` метод `addMessage(msg)` вставляет новое сообщение в начало списка [1].

**Источники и цитаты:**

1. `Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt` :: ConversationUiState

> fun addMessage(msg: Message) {
>         _messages.add(0, msg) // Add to the beginning of the list
>     }

---

## 2. What constructor parameters does Jetchat's ConversationUiState class take?

**Ожидание:** channelName: String, channelMembers: Int, initialMessages: List<Message>. Internally keeps a MutableList backed by toMutableStateList().

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ полностью соответствует цитате: перечислены те же параметры с теми же типами.

**Ответ:**

> Класс `ConversationUiState` принимает параметры: `channelName: String`, `channelMembers: Int` и `initialMessages: List<Message>` [4].

**Источники и цитаты:**

1. `Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt` :: ConversationUiState

> class ConversationUiState(val channelName: String, val channelMembers: Int, initialMessages: List<Message>)

---

## 3. Which UI tests are included in the Jetchat androidTest suite, and what does each one cover?

**Ожидание:** UserInputTest; ConversationTest (UI tests for the Conversation screen, incl. a test for behavior when dark mode changes); NavigationTest (asserts directly on the Navigation Controller / NavController).

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 1 · обоснован ✅ · retrieval hit ✅

**Судья:** Все три теста (ConversationTest для dark mode, UserInputTest для клавиатуры, NavigationTest для навигации) упомянуты в ответе и подтверждены цитатами [1] и [2].

**Ответ:**

> The UI tests included in the Jetchat androidTest suite are: [ConversationTest](app/src/androidTest/java/com/example/compose/jetchat/ConversationTest.kt), [UserInputTest](app/src/androidTest/java/com/example/compose/jetchat/UserInputTest.kt), and [NavigationTest](app/src/androidTest/java/com/example/compose/jetchat/NavigationTest.kt). ConversationTest includes a test that checks the behavior of the app when dark mode changes [2]. UserInputTest checks that the user input composable, including extended controls, behave as expected showing and hiding the keyboard [3]. NavigationTest shows how to write tests that assert directly on the Navigation Controller [4].

**Источники и цитаты:**

1. `Jetchat/README.md` :: Jetchat sample > Features > UI tests > [ConversationTest](app/src/androidTest/java/com/example/compose/jetchat/ConversationTest.kt)

> UI tests for the Conversation screen. Includes a test that checks the behavior of the app when dark mode changes.

2. `Jetchat/README.md` :: Jetchat sample > Features > UI tests > [UserInputTest](app/src/androidTest/java/com/example/compose/jetchat/UserInputTest.kt)

> Checks that the user input composable, including extended controls, behave as expected showing and hiding the keyboard.

---

## 4. In JetNews's HomeViewModel, HomeUiState is a sealed interface. Which three common properties does it declare?

**Ожидание:** isLoading: Boolean, errorMessages: List<ErrorMessage>, searchInput: String.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** В цитате перечислены именно три свойства: isLoading, errorMessages, searchInput, что полностью соответствует ответу.

**Ответ:**

> В HomeUiState объявлены три общих свойства: `isLoading: Boolean`, `errorMessages: List<ErrorMessage>` и `searchInput: String` [1].

**Источники и цитаты:**

1. `JetNews/app/src/main/java/com/example/jetnews/ui/home/HomeViewModel.kt` :: HomeUiState

> sealed interface HomeUiState {
> 
>     val isLoading: Boolean
>     val errorMessages: List<ErrorMessage>
>     val searchInput: String
> 
>     /**
>      * There are no posts to render.
>      *
>      * This could either be because they are still loading or they failed to load, and we are
>      * waiting to reload them.
>      */
>     data class NoPosts(override val isLoading: Boolean, override val errorMessages: List<ErrorMessage>, override val searchInput: String) :
>         HomeUiState
> 
>     /**
>      * There are posts to render, as contained in [postsFeed].
>      */
>     data class HasPosts(
>         val postsFeed: PostsFeed,
>         val favorites: Set<String>,
>         override val isLoading: Boolean,
>         override val errorMessages: List<ErrorMessage>,
>         override val searchInput: String,
>     ) : HomeUiState
> }

---

## 5. In Jetsnack's JetsnackNavController, what does the upPress() function do, and what annotation is the class marked with?

**Ожидание:** upPress() calls navController.navigateUp(). The class is annotated @Stable.

**Проверки:** источники ❌ · цитаты ❌ · отброшено цитат 0 · обоснован — · retrieval hit ❌

**Судья:** нет цитат для проверки

**Ответ:**

> Не знаю: в источниках нет ответа на этот вопрос, уточните вопрос

**Источники и цитаты:**

_нет_

---

## 6. In Jetsnack, what kind of Kotlin declaration is SnackbarManager, and how does it expose its messages?

**Ожидание:** It is an object (singleton) responsible for managing snackbar messages. It backs a private MutableStateFlow<List<Message>> _messages and exposes it as a read-only StateFlow<List<Message>> via messages; showMessage takes a @StringRes messageTextId.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Цитата [1] подтверждает, что SnackbarManager объявлен как object, а поле 'messages' является StateFlow<List<Message>>.

**Ответ:**

> SnackbarManager — это `object` (синглтон) [3]. Сообщения для Snackbar предоставляются через `StateFlow<List<Message>>`, доступный как `messages` [3].

**Источники и цитаты:**

1. `Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt` :: SnackbarManager

> object SnackbarManager {
> 
>     private val _messages: MutableStateFlow<List<Message>> = MutableStateFlow(emptyList())
>     val messages: StateFlow<List<Message>> get() = _messages.asStateFlow()
> 
>     fun showMessage(@StringRes messageTextId: Int) {
>         _messages.update { currentMessages ->
>             currentMessages + Message(
>                 id = UUID.randomUUID().mostSignificantBits,
>                 messageId = messageTextId,
>             )
>         }
>     }
> 
>     fun setMessageShown(messageId: Long) {
>         _messages.update { currentMessages ->
>             currentMessages.filterNot { it.id == messageId }
>         }
>     }
> }

---

## 7. What fields does the ErrorMessage data class in JetNews contain?

**Ожидание:** id: Long and messageId: Int annotated with @StringRes. i.e. data class ErrorMessage(val id: Long, @StringRes val messageId: Int).

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ ассистента полностью соответствует цитате: поля id (тип Long) и messageId (тип Int) указаны в data class ErrorMessage.

**Ответ:**

> ErrorMessage data class содержит поля: `id: Long` и `messageId: Int` [1].

**Источники и цитаты:**

1. `JetNews/app/src/main/java/com/example/jetnews/utils/ErrorMessage.kt` :: ErrorMessage

> data class ErrorMessage(val id: Long, @StringRes val messageId: Int)

---

## 8. In Reply's ReplyNavigationWrapper composable, how is the navigation layout type decided (what APIs drive it)?

**Ожидание:** It uses currentWindowAdaptiveInfo() and currentWindowSize() (converted to DpSize) and computes a navLayoutType with a when-expression to pick the adaptive navigation layout based on window size/posture.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ полностью соответствует логике определения типа навигации из цитаты: используется `adaptiveInfo` (полученный от `currentWindowAdaptiveInfo`) и `windowSize.width` (от `currentWindowSize`), условия приоритета и значения совпадают.

**Ответ:**

> В `ReplyNavigationWrapper` тип навигации определяется с помощью двух API: `currentWindowAdaptiveInfo()` [3] и `currentWindowSize()` [3]. `currentWindowAdaptiveInfo()` предоставляет `windowPosture` и `windowSizeClass`; если `windowPosture.isTabletop` или `windowSizeClass.isCompact()` — выбирается `NavigationBar` [3]; если ширина окна >= 1200.dp и `windowSizeClass.isWidthAtLeastBreakpoint(WIDTH_DP_EXPANDED_LOWER_BOUND)` — выбирается `NavigationDrawer` [3]; иначе — `NavigationRail` [3]. `currentWindowSize()` используется для проверки ширины окна в dp [3].

**Источники и цитаты:**

1. `Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt` :: ReplyNavigationWrapper

> val navLayoutType = when {
>         adaptiveInfo.windowPosture.isTabletop -> NavigationSuiteType.NavigationBar
> 
>         adaptiveInfo.windowSizeClass.isCompact() -> NavigationSuiteType.NavigationBar
> 
>         adaptiveInfo.windowSizeClass.isWidthAtLeastBreakpoint(WindowSizeClass.WIDTH_DP_EXPANDED_LOWER_BOUND) &&
>             windowSize.width >= 1200.dp -> NavigationSuiteType.NavigationDrawer
> 
>         else -> NavigationSuiteType.NavigationRail
>     }

---

## 9. What are the three main screens/components of the Jetcaster phone app?

**Ожидание:** The home screen, the podcast details screen, and the player screen.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ дословно повторяет информацию из цитаты, где перечислены три компонента: home screen, podcast details screen, player screen.

**Ответ:**

> The Jetcaster phone app has three main components: the home screen, the podcast details screen, and the player screen [1].

**Источники и цитаты:**

1. `Jetcaster/README.md` :: Jetcaster sample 🎙️ > Phone app > Features

> This sample has 3 components: the home screen, the podcast details screen, and the player screen

---

## 10. What copyright year is stated in the top-level (root) README license header of the Jetpack Compose Samples repository?

**Ожидание:** 2024 ('Copyright 2024 The Android Open Source Project') in the root README — note individual samples like Jetchat/Jetsnack state 2020, so the root differs.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Цитата [1] прямо подтверждает, что указан год 2024, что соответствует ответу.

**Ответ:**

> The top-level README license header states copyright 2024 [1].

**Источники и цитаты:**

1. `README.md` :: Jetpack Compose Samples > License

> Copyright 2024 The Android Open Source Project

---

## 11. How does it decide which one to show?

**Контекст диалога (multi-turn):**

> user: Tell me about the Reply sample's navigation.
> assistant: Reply uses adaptive Material 3 navigation components (bottom bar, navigation rail, drawer) chosen by window size.

**Ожидание:** ReplyNavigationWrapper uses currentWindowAdaptiveInfo() and currentWindowSize() (as DpSize) and a when-expression to pick navLayoutType based on the window size class / posture. The follow-up 'it' = Reply navigation; only resolvable from context.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ полностью соответствует логике условия в коде из цитаты: сначала проверка isTabletop и компактного размера (NavigationBar), затем ширина >= 1200.dp (NavigationDrawer), остальное — NavigationRail.

**Ответ:**

> It decides based on `ReplyNavigationWrapper` in [1]. First, if `windowPosture.isTabletop` is true or the window size class is compact, it uses `NavigationBar`. Otherwise, if the width is at least 1200.dp (expanded), it uses `NavigationDrawer`. In all other cases (e.g., medium width), it uses `NavigationRail`. This logic is implemented in `navLayoutType` via `when` expressions in [1].

**Источники и цитаты:**

1. `Reply/app/src/main/java/com/example/reply/ui/navigation/ReplyNavigationComponents.kt` :: ReplyNavigationWrapper

> val navLayoutType = when {
>         adaptiveInfo.windowPosture.isTabletop -> NavigationSuiteType.NavigationBar
> 
>         adaptiveInfo.windowSizeClass.isCompact() -> NavigationSuiteType.NavigationBar
> 
>         adaptiveInfo.windowSizeClass.isWidthAtLeastBreakpoint(WindowSizeClass.WIDTH_DP_EXPANDED_LOWER_BOUND) &&
>             windowSize.width >= 1200.dp -> NavigationSuiteType.NavigationDrawer
> 
>         else -> NavigationSuiteType.NavigationRail
>     }

---

## 12. What type does it expose them as?

**Контекст диалога (multi-turn):**

> user: Tell me about the SnackbarManager in Jetsnack.
> assistant: SnackbarManager is an object that manages snackbar messages shown in Jetsnack.

**Ожидание:** It exposes the messages as a read-only StateFlow<List<Message>> (backed by a private MutableStateFlow, surfaced via asStateFlow()). 'it' = SnackbarManager, 'them' = messages; only resolvable from context.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Цитата утверждает, что поле messages имеет тип StateFlow<List<Message>>, что совпадает с ответом.

**Ответ:**

> It exposes messages as a `StateFlow<List<Message>>`. [1]

**Источники и цитаты:**

1. `Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt` :: SnackbarManager

> val messages: StateFlow<List<Message>> get() = _messages.asStateFlow()

---

## Off-topic — ответы

### 13. What is the boiling point of water at sea level?

**Abstain:** ✅

> Не знаю: в найденных источниках нет ответа на этот вопрос. Уточните или переформулируйте вопрос.

### 14. Who won the FIFA World Cup in 1998?

**Abstain:** ✅

> Не знаю: в найденных источниках нет ответа на этот вопрос. Уточните или переформулируйте вопрос.

### 15. Give me a recipe for classic Italian tiramisu.

**Abstain:** ✅

> Не знаю: в найденных источниках нет ответа на этот вопрос. Уточните или переформулируйте вопрос.

### 16. What is the capital of Australia?

**Abstain:** ✅

> Не знаю: в найденных источниках нет ответа на этот вопрос. Уточните или переформулируйте вопрос.

### 17. How does photosynthesis convert sunlight into energy in plants?

**Abstain:** ✅

> Не знаю: в найденных источниках нет ответа на этот вопрос. Уточните или переформулируйте вопрос.
