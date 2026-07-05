# Цитаты, источники и режим «не знаю» — отчёт eval

Генерируется `compare.py`. Корпус — Google *compose-samples*. Прогон в **cited-режиме** (`useRag=true, improvedRag=true`): извлечение → порог-фильтр → генерация со структурированными цитатами. Цитаты валидируются backend как дословные подстроки чанков; здесь судья DeepSeek проверяет, следует ли смысл ответа из этих цитат.

## Сводка

- **Источники в ответе:** 12/12
- **Цитаты в ответе:** 12/12
- **Ответ обоснован цитатами (судья):** 10/12
- **Off-topic → «не знаю» (abstain):** 5/5

## In-domain

| # | Вопрос | Источники | Цитаты | Обоснован | Retrieval hit |
|---|--------|:---:|:---:|:---:|:---:|
| 1 | In Jetchat's ConversationUiState, what does th… | ✅ | ✅ | ✅ | ✅ |
| 2 | What constructor parameters does Jetchat's Con… | ✅ | ✅ | ✅ | ✅ |
| 3 | Which UI tests are included in the Jetchat and… | ✅ | ✅ | ✅ | ✅ |
| 4 | In JetNews's HomeViewModel, HomeUiState is a s… | ✅ | ✅ | ✅ | ✅ |
| 5 | In Jetsnack's JetsnackNavController, what does… | ✅ | ✅ | ❌ | ✅ |
| 6 | In Jetsnack, what kind of Kotlin declaration i… | ✅ | ✅ | ✅ | ✅ |
| 7 | What fields does the ErrorMessage data class i… | ✅ | ✅ | ✅ | ✅ |
| 8 | In Reply's ReplyNavigationWrapper composable, … | ✅ | ✅ | ✅ | ✅ |
| 9 | What are the three main screens/components of … | ✅ | ✅ | ✅ | ✅ |
| 10 | What copyright year is stated in the top-level… | ✅ | ✅ | ✅ | ✅ |
| 11 | 🔁 How does it decide which one to show?… | ✅ | ✅ | ✅ | ✅ |
| 12 | 🔁 What type does it expose them as?… | ✅ | ✅ | ❌ | ❌ |

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

**Судья:** Цитата [1] показывает, что addMessage добавляет сообщение с индексом 0, то есть в начало списка, что соответствует ответу.

**Ответ:**

> The `addMessage(msg)` function adds the message to the beginning of the list, as indicated by the comment *Add to the beginning of the list* [1].

**Источники и цитаты:**

1. `Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt` :: ConversationUiState

> fun addMessage(msg: Message) {
>         _messages.add(0, msg) // Add to the beginning of the list
>     }

---

## 2. What constructor parameters does Jetchat's ConversationUiState class take?

**Ожидание:** channelName: String, channelMembers: Int, initialMessages: List<Message>. Internally keeps a MutableList backed by toMutableStateList().

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ полностью соответствует цитате: перечислены те же три параметра с теми же типами.

**Ответ:**

> Класс `ConversationUiState` принимает три параметра конструктора: `channelName` (String), `channelMembers` (Int) и `initialMessages` (List<Message>) [4].

**Источники и цитаты:**

1. `Jetchat/app/src/main/java/com/example/compose/jetchat/conversation/ConversationUiState.kt` :: ConversationUiState

> class ConversationUiState(val channelName: String, val channelMembers: Int, initialMessages: List<Message>)

---

## 3. Which UI tests are included in the Jetchat androidTest suite, and what does each one cover?

**Ожидание:** UserInputTest; ConversationTest (UI tests for the Conversation screen, incl. a test for behavior when dark mode changes); NavigationTest (asserts directly on the Navigation Controller / NavController).

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ ассистента полностью соответствует цитатам: перечислены три теста, их описания совпадают с источниками.

**Ответ:**

> The Jetchat androidTest suite includes three UI tests: [1] ConversationTest covers UI tests for the Conversation screen, including behavior when dark mode changes. [2] UserInputTest checks that the user input composable and extended controls behave as expected with keyboard show/hide. [3] NavigationTest shows how to write tests that assert directly on the Navigation Controller.

**Источники и цитаты:**

1. `Jetchat/README.md` :: Jetchat sample > Features > UI tests

> Jetchat sample > Features > UI tests
> ### UI tests
> In [androidTest](app/src/androidTest/java/com/example/compose/jetchat) you'll find a suite of UI tests that showcase interesting patterns in Compose:

2. `Jetchat/README.md` :: Jetchat sample > Features > UI tests > [ConversationTest](app/src/androidTest/java/com/example/compose/jetchat/ConversationTest.kt)

> #### [ConversationTest](app/src/androidTest/java/com/example/compose/jetchat/ConversationTest.kt)
> UI tests for the Conversation screen. Includes a test that checks the behavior of the app when dark mode changes.

3. `Jetchat/README.md` :: Jetchat sample > Features > UI tests > [UserInputTest](app/src/androidTest/java/com/example/compose/jetchat/UserInputTest.kt)

> #### [UserInputTest](app/src/androidTest/java/com/example/compose/jetchat/UserInputTest.kt)
> Checks that the user input composable, including extended controls, behave as expected showing and hiding the keyboard.

4. `Jetchat/README.md` :: Jetchat sample > Features > UI tests > [NavigationTest](app/src/androidTest/java/com/example/compose/jetchat/NavigationTest.kt)

> #### [NavigationTest](app/src/androidTest/java/com/example/compose/jetchat/NavigationTest.kt)
> Shows how to write tests that assert directly on the [Navigation Controller](https://developer.android.com/reference/androidx/navigation/NavController).

---

## 4. In JetNews's HomeViewModel, HomeUiState is a sealed interface. Which three common properties does it declare?

**Ожидание:** isLoading: Boolean, errorMessages: List<ErrorMessage>, searchInput: String.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ полностью соответствует цитате, перечисляющей три свойства с указанными типами.

**Ответ:**

> В HomeUiState объявлены три общих свойства: `isLoading` (тип Boolean), `errorMessages` (тип List<ErrorMessage>) и `searchInput` (тип String) [1].

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

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ❌ · retrieval hit ✅

**Судья:** В цитатах нет информации о функции upPress() и аннотациях класса JetsnackNavController, поэтому ответ, утверждающий, что upPress() определена в другом классе и что класс не содержит аннотаций, не подтверждается цитатами.

**Ответ:**

> В JetsnackNavController нет функции upPress() — она определена в другом классе. Сам класс JetsnackNavController не содержит аннотаций в предоставленных источниках [2].

**Источники и цитаты:**

1. `Jetsnack/app/src/main/java/com/example/jetsnack/ui/navigation/JetsnackNavController.kt` :: rememberJetsnackNavController

> @Composable
> fun rememberJetsnackNavController(navController: NavHostController = rememberNavController()): JetsnackNavController =
>     remember(navController) {
>         JetsnackNavController(navController)
>     }

---

## 6. In Jetsnack, what kind of Kotlin declaration is SnackbarManager, and how does it expose its messages?

**Ожидание:** It is an object (singleton) responsible for managing snackbar messages. It backs a private MutableStateFlow<List<Message>> _messages and exposes it as a read-only StateFlow<List<Message>> via messages; showMessage takes a @StringRes messageTextId.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Цитата [1] явно показывает, что SnackbarManager объявлен как object, а его свойство messages — это StateFlow<List<Message>>, получаемый через asStateFlow() из приватного _messages, что полностью соответствует утверждению в ответе.

**Ответ:**

> In Jetsnack, `SnackbarManager` is an `object` (a Kotlin singleton) and it exposes its messages as a `StateFlow` via the `messages` property, which is a `StateFlow<List<Message>>` backed by a private `MutableStateFlow`. [3]

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

**Судья:** Цитата содержит именно эти поля с теми же типами (Long, Int) и аннотацией @StringRes, что указано в ответе.

**Ответ:**

> The `ErrorMessage` data class contains two fields: `id` of type `Long` and `messageId` of type `Int` (annotated with `@StringRes`). [1]

**Источники и цитаты:**

1. `JetNews/app/src/main/java/com/example/jetnews/utils/ErrorMessage.kt` :: ErrorMessage

> data class ErrorMessage(val id: Long, @StringRes val messageId: Int)

---

## 8. In Reply's ReplyNavigationWrapper composable, how is the navigation layout type decided (what APIs drive it)?

**Ожидание:** It uses currentWindowAdaptiveInfo() and currentWindowSize() (converted to DpSize) and computes a navLayoutType with a when-expression to pick the adaptive navigation layout based on window size/posture.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Ответ полностью соответствует коду из цитаты: условия и возвращаемые типы совпадают.

**Ответ:**

> Нavigation layout type is decided based on `adaptiveInfo.windowPosture`, `adaptiveInfo.windowSizeClass`, and `windowSize.width`. If the window posture is tabletop or the size class is compact, it uses `NavigationSuiteType.NavigationBar`; if the width is at least 1200.dp, it uses `NavigationSuiteType.NavigationDrawer`; otherwise, `NavigationSuiteType.NavigationRail`[3].

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

**Судья:** Ответ полностью соответствует цитате, в которой указаны три компонента: home screen, podcast details screen и player screen.

**Ответ:**

> Три основных компонента Jetcaster phone app: экран 'Home', экран 'Podcast details' и экран 'Player' [1].

**Источники и цитаты:**

1. `Jetcaster/README.md` :: Jetcaster sample 🎙️ > Phone app > Features

> This sample has 3 components: the home screen, the podcast details screen, and the player screen

---

## 10. What copyright year is stated in the top-level (root) README license header of the Jetpack Compose Samples repository?

**Ожидание:** 2024 ('Copyright 2024 The Android Open Source Project') in the root README — note individual samples like Jetchat/Jetsnack state 2020, so the root differs.

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ✅ · retrieval hit ✅

**Судья:** Цитата [1] явно указывает год 2024, что соответствует утверждению в ответе.

**Ответ:**

> The top-level (root) README license header states the copyright year 2024 [1].

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

**Судья:** Ответ полностью соответствует коду из цитаты [1] и упомянутому в [2] жесту открытия drawer из rail.

**Ответ:**

> The navigation type is chosen based on device size and state using `adaptiveInfo.windowSizeClass`, `adaptiveInfo.windowPosture.isTabletop`, and window width. For example, [2] shows: `NavigationSuiteType.NavigationBar` for compact or tabletop; `NavigationSuiteType.NavigationDrawer` if width ≥ 1200.dp and expanded breakpoint; otherwise `NavigationSuiteType.NavigationRail`. The drawer can also be opened via gesture on rail [2].

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

**Проверки:** источники ✅ · цитаты ✅ · отброшено цитат 0 · обоснован ❌ · retrieval hit ❌

**Судья:** Цитата содержит SnackbarHostState, но ответ утверждает, что SnackbarManager не существует в контексте Jetsnack, однако ни одна из цитат не подтверждает отсутствие упоминаний SnackbarManager; ответ основан на неподтверждённом выводе.

**Ответ:**

> The SnackbarManager does not exist in the provided context. The relevant snippet is from JetNews, not Jetsnack, and shows a `SnackbarHostState` being used. In the context of Jetsnack, there is no `SnackbarManager` mentioned. Therefore, I cannot answer the question based on the given sources.

**Источники и цитаты:**

1. `JetNews/app/src/main/java/com/example/jetnews/ui/components/JetnewsSnackbarHost.kt` :: JetnewsSnackbarHost

> hostState: SnackbarHostState

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
