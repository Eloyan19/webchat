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

**Судья:** Цитата [1] содержит код, где addMessage добавляет сообщение в начало списка по индексу 0, что полностью соответствует утверждению в ответе.

**Ответ:**

> The `addMessage(msg)` function adds a message to the beginning of the list (at index 0) [1].

**Источники и цитаты:**

1. `Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt` :: ConversationUiState

> fun addMessage(msg: Message) {
>         _messages.add(0, msg) // Add to the beginning of the list
>     }

---

## 2. What constructor parameters does Jetchat's ConversationUiState class take?

**Ожидание:** channelName: String, channelMembers: Int, initialMessages: List<Message>. Internally keeps a MutableList backed by toMutableStateList().

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ соответствует данным из цитаты [1], где указаны те же три параметра конструктора.

**Ответ:**

> В соответствии с [4] конструктор `ConversationUiState` принимает три параметра: `val channelName: String`, `val channelMembers: Int` и `initialMessages: List<Message>`.

**Источники и цитаты:**

1. `Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt` :: ConversationUiState

> class ConversationUiState(val channelName: String, val channelMembers: Int, initialMessages: List<Message>)

---

## 3. Which UI tests are included in the Jetchat androidTest suite, and what does each one cover?

**Ожидание:** UserInputTest; ConversationTest (UI tests for the Conversation screen, incl. a test for behavior when dark mode changes); NavigationTest (asserts directly on the Navigation Controller / NavController).

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ полностью соответствует цитатам: перечислены те же три теста, их описания совпадают по смыслу.

**Ответ:**

> The Jetchat sample includes UI tests in the [androidTest](app/src/androidTest/java/com/example/compose/jetchat) folder, which are [ConversationTest] [2], [UserInputTest] [3], and [NavigationTest] [4]. 
> - [ConversationTest] [2] contains UI tests for the Conversation screen, including behavior when dark mode changes. 
> - [UserInputTest] [3] checks that user input composables (including extended controls) behave as expected regarding keyboard show/hide. 
> - [NavigationTest] [4] shows how to write tests that assert directly on the Navigation Controller.

**Источники и цитаты:**

1. `Jetchat/README.md` :: Jetchat sample > Features > UI tests

> In [androidTest](app/src/androidTest/java/com/example/compose/jetchat) you'll find a suite of UI tests that showcase interesting patterns in Compose:

2. `Jetchat/README.md` :: Jetchat sample > Features > UI tests > [ConversationTest](app/src/androidTest/java/com/example/compose/jetchat/ConversationTest.kt)

> [ConversationTest](app/src/androidTest/java/com/example/compose/jetchat/ConversationTest.kt)
> UI tests for the Conversation screen. Includes a test that checks the behavior of the app when dark mode changes.

3. `Jetchat/README.md` :: Jetchat sample > Features > UI tests > [UserInputTest](app/src/androidTest/java/com/example/compose/jetchat/UserInputTest.kt)

> [UserInputTest](app/src/androidTest/java/com/example/compose/jetchat/UserInputTest.kt)
> Checks that the user input composable, including extended controls, behave as expected showing and hiding the keyboard.

4. `Jetchat/README.md` :: Jetchat sample > Features > UI tests > [NavigationTest](app/src/androidTest/java/com/example/compose/jetchat/NavigationTest.kt)

> [NavigationTest](app/src/androidTest/java/com/example/compose/jetchat/NavigationTest.kt)
> Shows how to write tests that assert directly on the [Navigation Controller](https://developer.android.com/reference/androidx/navigation/NavController).

---

## 4. In JetNews's HomeViewModel, HomeUiState is a sealed interface. Which three common properties does it declare?

**Ожидание:** isLoading: Boolean, errorMessages: List<ErrorMessage>, searchInput: String.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ подтверждается цитатой: перечисленные свойства совпадают с объявленными в исходном коде.

**Ответ:**

> В HomeUiState declared three common properties: `isLoading`, `errorMessages`, and `searchInput` [1].

**Источники и цитаты:**

1. `JetNews/app/src/main/java/com/example/jetnews/ui/home/HomeViewModel.kt` :: HomeUiState

> sealed interface HomeUiState {
> 
>     val isLoading: Boolean
>     val errorMessages: List<ErrorMessage>
>     val searchInput: String

---

## 5. In Jetsnack's JetsnackNavController, what does the upPress() function do, and what annotation is the class marked with?

**Ожидание:** upPress() calls navController.navigateUp(). The class is annotated @Stable.

**Проверки:** источники ❌ · цитаты ❌ · отброшено цитат 0 · обоснован — · retrieval hit ❌

**Судья:** ассистент воздержался (не знаю)

**Ответ:**

> Не знаю: в найденных источниках нет ответа на этот вопрос. Уточните или переформулируйте вопрос.

**Источники и цитаты:**

_нет_

---

## 6. In Jetsnack, what kind of Kotlin declaration is SnackbarManager, and how does it expose its messages?

**Ожидание:** It is an object (singleton) responsible for managing snackbar messages. It backs a private MutableStateFlow<List<Message>> _messages and exposes it as a read-only StateFlow<List<Message>> via messages; showMessage takes a @StringRes messageTextId.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Цитата [1] подтверждает, что SnackbarManager является объектом (object), а поле messages — StateFlow, построенным на MutableStateFlow.

**Ответ:**

> В Jetsnack `SnackbarManager` — это объявление `object` (синглтон). Он предоставляет сообщения через [3] `StateFlow<List<Message>>` (поле `messages`), которое является `StateFlow`, построенным на `MutableStateFlow`.

**Источники и цитаты:**

1. `Jetsnack/app/src/main/java/com/example/jetsnack/model/SnackbarManager.kt` :: SnackbarManager

> object SnackbarManager {
> 
>     private val _messages: MutableStateFlow<List<Message>> = MutableStateFlow(emptyList())
>     val messages: StateFlow<List<Message>> get() = _messages.asStateFlow()

---

## 7. What fields does the ErrorMessage data class in JetNews contain?

**Ожидание:** id: Long and messageId: Int annotated with @StringRes. i.e. data class ErrorMessage(val id: Long, @StringRes val messageId: Int).

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ полностью соответствует цитате: указаны те же два поля с теми же типами и аннотацией.

**Ответ:**

> Класс `ErrorMessage` содержит два поля: `id` (тип `Long`) и `messageId` (тип `Int` с аннотацией `@StringRes`) [1].

**Источники и цитаты:**

1. `JetNews/app/src/main/java/com/example/jetnews/utils/ErrorMessage.kt` :: ErrorMessage

> data class ErrorMessage(val id: Long, @StringRes val messageId: Int)

---

## 8. In Reply's ReplyNavigationWrapper composable, how is the navigation layout type decided (what APIs drive it)?

**Ожидание:** It uses currentWindowAdaptiveInfo() and currentWindowSize() (converted to DpSize) and computes a navLayoutType with a when-expression to pick the adaptive navigation layout based on window size/posture.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ полностью соответствует логике цитаты, перечислены те же условия для определения типа навигации, включая isTabletop, isCompact, isWidthAtLeastBreakpoint и проверку ширины окна.

**Ответ:**

> В `ReplyNavigationWrapper` тип навигации определяется с помощью `adaptiveInfo.windowPosture.isTabletop`, `adaptiveInfo.windowSizeClass.isCompact()`, `adaptiveInfo.windowSizeClass.isWidthAtLeastBreakpoint(WindowSizeClass.WIDTH_DP_EXPANDED_LOWER_BOUND)` и `windowSize.width >= 1200.dp` [3].

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

**Судья:** Ответ полностью соответствует содержанию цитаты, в которой перечислены те же три компонента.

**Ответ:**

> The three main screens/components of the Jetcaster phone app are: the home screen, the podcast details screen, and the player screen [1].

**Источники и цитаты:**

1. `Jetcaster/README.md` :: Jetcaster sample 🎙️ > Phone app > Features

> This sample has 3 components: the home screen, the podcast details screen, and the player screen

---

## 10. What copyright year is stated in the top-level (root) README license header of the Jetpack Compose Samples repository?

**Ожидание:** 2024 ('Copyright 2024 The Android Open Source Project') in the root README — note individual samples like Jetchat/Jetsnack state 2020, so the root differs.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Цитата [1] явно содержит копирайт 2024 года, что совпадает с ответом.

**Ответ:**

> The copyright year stated in the top-level (root) README license header is 2024 [1].

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

**Судья:** Ответ соответствует цитате: компактные устройства -> NavigationBar, ширина >= 1200 dp -> NavigationDrawer, иначе NavigationRail, упомянуты AdaptiveInfo и windowSize.

**Ответ:**

> On compact devices it shows a [bottom navigation bar][4]; on medium devices a [navigation rail][4]; on large devices (width ≥ 1200 dp) a [permanent navigation drawer][4]. The rail is also used with a modal drawer for extra content. Choices come from `AdaptiveInfo` and window size checks[4].

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

**Судья:** Цитата [1] подтверждает, что сообщения представлены как `StateFlow<List<Message>>`, что соответствует ответу.

**Ответ:**

> SnackbarManager exposes messages as `StateFlow<List<Message>>` [2].

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
