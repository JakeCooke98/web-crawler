# Design Choices and Trade-offs

## Frontend

### Technology Stack
- **Svelte**: Chosen for its simplicity and reactivity, allowing for efficient UI updates without the overhead of a virtual DOM.
- **D3.js**: Utilized for creating dynamic and interactive visualizations, particularly suitable for rendering complex data structures like graphs.

### Design Choices
- **Component Structure**: The application is divided into modular components (`CrawlerForm`, `CrawlerResults`, `SiteMap`) to separate concerns and improve maintainability.
- **Progressive Rendering**: Implemented in `SiteMap.svelte` to handle large datasets by rendering nodes in batches, reducing initial load time and preventing UI freezes.
- **Responsive Design**: Utilized CSS grid and media queries to ensure the application is accessible on various screen sizes.

### Trade-offs
- **Complexity vs. Performance**: While D3.js provides powerful visualization capabilities, it introduces complexity in managing state and performance, especially with large datasets. Progressive rendering and throttling were used to mitigate these issues.
- **Node Limitation**: To maintain performance, the number of visible nodes is limited, which may not fully represent very large datasets but ensures the application remains responsive.

## Backend

### Technology Stack
- **FastAPI**: Chosen for its asynchronous capabilities and ease of integration with WebSockets, allowing real-time communication with the frontend.
- **aiohttp**: Used for asynchronous HTTP requests, enabling efficient web crawling without blocking the event loop.

### Design Choices
- **Asynchronous Crawling**: The `AsyncWebCrawler` class is designed to perform non-blocking web crawls, utilizing Python's `asyncio` for concurrency.
- **WebSocket Communication**: Provides real-time updates to the frontend, enhancing user experience by displaying crawl progress and results dynamically.

### Trade-offs
- **Concurrency vs. Complexity**: Asynchronous programming introduces complexity in error handling and state management but significantly improves performance and responsiveness.
- **Rate Limiting**: Implemented to prevent overwhelming target servers, which may slow down the crawl process but ensures ethical and responsible web crawling.

Overall, the design choices prioritize performance, responsiveness, and user experience, with trade-offs made to balance complexity and maintainability. The use of modern web technologies and asynchronous programming patterns allows the application to efficiently handle real-time data and large-scale web crawling tasks.
