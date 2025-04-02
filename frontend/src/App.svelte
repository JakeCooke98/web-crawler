<script>
    import CrawlerForm from "./components/CrawlerForm.svelte";
    import CrawlerResults from "./components/CrawlerResults.svelte";
    import SiteMap from "./components/SiteMap.svelte";

    let results = {};
    let isConnected = false;
    let isCrawling = false;
    let socket;

    function handleCrawlStarted(event) {
        const url = event.detail.url;
        isCrawling = true;
        startWebSocket(url);
    }

    function resetCrawler() {
        isCrawling = false;
        isConnected = false;
        if (socket) {
            socket.close();
        }
    }

    function startWebSocket(url) {
        socket = new WebSocket('ws://localhost:8000/ws');
        
        socket.onopen = () => {
            isConnected = true;
            socket.send(JSON.stringify({ url }));
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.error) {
                console.error('Error:', data.error);
                resetCrawler();
                return;
            }

            if (data.status === 'completed') {
                resetCrawler();
                return;
            }

            // Update results with new page data
            results = {
                ...results,
                [data.page]: data.links
            };
        };

        socket.onclose = () => {
            resetCrawler();
        };

        socket.onerror = () => {
            resetCrawler();
        };
    }

    function handleNewCrawl() {
        results = {};
        resetCrawler();
    }
</script>

<main>
    <h1>Web Crawler</h1>
    <CrawlerForm 
        on:crawlStarted={handleCrawlStarted}
        on:newCrawl={handleNewCrawl}
        {isCrawling}
        showNewCrawlButton={!isCrawling && Object.keys(results).length > 0}
    />
    
    {#if isCrawling}
        <div class="status">
            <p>Crawling in progress...</p>
        </div>
    {/if}

    <div class="results-grid">
        <SiteMap {results} />
        <CrawlerResults {results} />
    </div>
</main>

<style>
    main {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }

    h1 {
        margin-bottom: 2rem;
        color: #1e293b;
    }

    .status {
        margin: 1rem 0;
        padding: 0.75rem 1rem;
        background-color: #dbeafe;
        border-radius: 0.5rem;
        color: #1e40af;
    }

    .results-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 2rem;
        margin-top: 2rem;
    }

    @media (min-width: 1024px) {
        .results-grid {
            grid-template-columns: 3fr 2fr;
        }
    }
</style>
