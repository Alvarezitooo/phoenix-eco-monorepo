# ARCHITECTURE NOTES: DOJO MENTAL COMPONENTS

This document details the architectural decisions and justifications for the refactoring of the `ZazenTimer` and `KaizenGrid` components, elevating them to a production-ready, scalable, and performant standard.

## 1. Refactoring du `ZazenTimer` (Le Métronome Parfait)

**Original Problematic:** The initial `ZazenTimer` used `setInterval`, which is known for its inaccuracy due to JavaScript's single-threaded nature and event loop behavior. It can drift over time and cause unnecessary re-renders. The logic was tightly coupled within the component.

**Architectural Choices & Justifications:**

1.  **Finite-State Machine (FSM) with `useReducer`:**
    *   **Choice:** The breathing cycle logic (inspire -> hold -> expire -> inspire) was modeled as a Finite-State Machine. `useReducer` was chosen to manage the state transitions.
    *   **Justification:**
        *   **Robustness & Predictability:** FSMs provide a clear, explicit model for state transitions, making the logic highly predictable and less prone to bugs. Each state has defined inputs and outputs, ensuring the timer behaves exactly as expected.
        *   **Separation of Concerns:** The state logic is cleanly separated from the UI rendering, improving readability and maintainability.
        *   **Scalability:** As the breathing cycle becomes more complex (e.g., adding more phases, dynamic durations), the FSM can easily accommodate new states and transitions without a complete rewrite.

2.  **`requestAnimationFrame` for Timing:**
    *   **Choice:** Replaced `setInterval` with `requestAnimationFrame` for the core timing mechanism.
    *   **Justification:**
        *   **Precision & Smoothness:** `requestAnimationFrame` synchronizes updates with the browser's refresh rate. This ensures that the timer's visual updates are perfectly smooth, avoiding jank or stuttering, and are as accurate as possible within the browser's rendering cycle.
        *   **Resource Efficiency:** The browser can optimize when to run the animation frame callback, pausing it when the tab is in the background, thus saving CPU and battery life. `setInterval` continues to run regardless, wasting resources.
        *   **Performance:** By only updating when a full second has passed (checked via `deltaTime >= 1000`), we minimize unnecessary `dispatch` calls, further optimizing performance.

3.  **Custom Hook `useBreathingCycle()`:**
    *   **Choice:** Encapsulated all the timer logic (FSM, `requestAnimationFrame`, state management) within a custom React hook `useBreathingCycle()`.
    *   **Justification:**
        *   **Reusability:** The core breathing cycle logic can now be easily reused across different components or even different applications without duplication.
        *   **Clean Component API:** The `ZazenTimer` component becomes purely declarative. It simply consumes the state and actions provided by the hook, making its rendering logic simple and easy to understand.
        *   **Testability:** The hook's logic can be tested independently of the UI component, simplifying unit testing.

4.  **Accessibility (ARIA Attributes):**
    *   **Choice:** Added `role="timer"`, `aria-live="polite"`, `aria-atomic="true"`, and `aria-label` attributes to the visual timer element.
    *   **Justification:**
        *   **Inclusivity:** Ensures that users relying on screen readers can understand the current phase and remaining time of the breathing exercise. `aria-live="polite"` ensures updates are announced without interrupting the user, and `aria-atomic="true"` ensures the entire label is read on change.

## 2. Refactoring du `KaizenGrid` (La Mosaïque de la Discipline)

**Original Problematic:** The initial `KaizenGrid` was a simple static rendering of a small array, lacking scalability for large datasets (e.g., 365+ days) and interactivity.

**Architectural Choices & Justifications:**

1.  **Data Fetching with Custom Hook `useKaizenHistory()`:**
    *   **Choice:** Created a dedicated custom hook `useKaizenHistory` to handle asynchronous data fetching, including loading and error states.
    *   **Justification:**
        *   **Separation of Concerns:** Decouples data fetching logic from the UI component, making both easier to understand, test, and maintain.
        *   **Improved User Experience:** Provides immediate feedback (loading state) and graceful error handling, preventing UI freezes or crashes.
        *   **Reusability:** The data fetching logic can be reused for other components that might need Kaizen history.

2.  **Component Decomposition (`KaizenGrid`, `KaizenCell`):**
    *   **Choice:** Broke down the `KaizenGrid` into smaller, more focused components: `KaizenGrid` (orchestrates the display) and `KaizenCell` (renders individual day's status and tooltip).
    *   **Justification:**
        *   **Modularity & Readability:** Each component has a single responsibility, making the codebase easier to navigate, understand, and debug.
        *   **Performance (Memoization Potential):** Smaller components are easier to optimize with `React.memo` if needed, preventing unnecessary re-renders of individual cells when only a few change.
        *   **Maintainability:** Changes to one part of the UI (e.g., cell styling) are isolated to its specific component.

3.  **Real Virtualization with `react-window`:**
    *   **Choice:** Integrated `FixedSizeGrid` from the `react-window` library.
    *   **Justification:**
        *   **Optimal Performance for Large Datasets:** This is the most critical optimization for `KaizenGrid`. `react-window` ensures that only the cells currently visible within the viewport (plus a small buffer) are actually rendered in the DOM. This drastically reduces the number of DOM nodes, leading to significantly faster initial renders, smoother scrolling, and lower memory consumption, even with thousands of data points.
        *   **True Scalability:** The component can now handle an arbitrary number of Kaizen entries (e.g., years of data) without performance degradation, making it truly scalable for a large user base.
        *   **Industry Standard:** `react-window` is a lightweight, highly optimized, and widely adopted library for list and grid virtualization in React applications, ensuring best practices.

4.  **Optimized Global Tooltip Management:**
    *   **Choice:** Implemented a single, global `Tooltip` component managed by a `useTooltip` custom hook. `KaizenCell` components now trigger the display of this global tooltip by passing their data and position.
    *   **Justification:**
        *   **Performance:** Instead of each `KaizenCell` rendering its own tooltip (which would mean potentially hundreds or thousands of hidden tooltip DOM elements), only one `Tooltip` component exists in the DOM. This significantly reduces the DOM tree size and improves rendering performance, especially crucial in a virtualized list where cells are constantly being mounted/unmounted.
        *   **Centralized Logic:** All tooltip display logic (positioning, visibility, content) is centralized in the `useTooltip` hook, making it easier to manage, debug, and extend (e.g., adding animations, delays).
        *   **Flexibility:** The global tooltip can be positioned precisely relative to the triggering element, even if the element itself is within a virtualized container.

5.  **Interactive Data Mutation with Optimistic UI:**
    *   **Choice:** Implemented click handling on `KaizenCell` to toggle its `isDone` status, with an optimistic UI update followed by a simulated asynchronous backend call.
    *   **Justification:**
        *   **Enhanced User Experience:** Optimistic UI updates provide immediate visual feedback to the user, making the application feel faster and more responsive. The user doesn't have to wait for the backend response to see their action reflected.
        *   **Responsiveness:** Reduces perceived latency, which is crucial for interactive elements.
        *   **Robustness (Rollback):** The `useKaizenHistory` hook includes a rollback mechanism. If the simulated backend update fails, the UI state is reverted to its original state, ensuring data consistency and preventing user confusion.
        *   **Clear State Management:** The `toggleKaizenStatus` function encapsulates the logic for both UI update and backend synchronization, maintaining a clean separation of concerns.

This refactoring ensures that both `ZazenTimer` and `KaizenGrid` are not just functional, but are built on solid architectural principles, ready for high-performance, scalable, and maintainable production environments.