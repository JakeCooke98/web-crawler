<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let isCrawling = false;
  export let showNewCrawlButton = false;

  let url = '';
  let result = '';
  let error = '';

  function handleSubmit() {
    dispatch('crawlStarted', { url });
  }

  function handleNewCrawl() {
    dispatch('newCrawl');
  }

  // Reset form when crawling completes
  $: if (!isCrawling) {
    url = '';
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  <div class="input-container">
    <input type="url" bind:value={url} placeholder="Enter URL to crawl" required disabled={isCrawling}>
  </div>
  <div class="button-container">
    <button type="submit" class="btn primary" disabled={isCrawling}>
      {isCrawling ? 'Crawling...' : 'Start Crawling'}
    </button>

    {#if showNewCrawlButton}
      <button type="button" class="btn secondary" on:click={handleNewCrawl}>
        Start New Crawl
      </button>
    {/if}
  </div>
</form>

{#if error}
  <p style="color: red;">{error}</p>
{/if}
{#if result}
  <p style="color: green;">{result}</p>
{/if}

<style>
  form {
    margin-bottom: 1rem;
    width: 100%;
    max-width: 800px;
  }

  .input-container {
    margin-bottom: 1rem;
  }

  input {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 2px solid #e2e8f0;
    border-radius: 0.5rem;
    font-size: 1rem;
    transition: all 0.2s ease;
  }

  input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  input:disabled {
    background-color: #f1f5f9;
    cursor: not-allowed;
    opacity: 0.7;
  }

  .button-container {
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  .btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 0.5rem;
    font-weight: 500;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
    text-transform: uppercase;
    letter-spacing: 0.025em;
  }

  .btn:hover {
    transform: translateY(-1px);
  }

  .btn:active {
    transform: translateY(0);
  }

  .btn.primary {
    background-color: #3b82f6;
    color: white;
  }

  .btn.primary:hover {
    background-color: #2563eb;
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1), 
               0 2px 4px -1px rgba(59, 130, 246, 0.06);
  }

  .btn.primary:disabled {
    background-color: #93c5fd;
    cursor: not-allowed;
    transform: none;
  }

  .btn.secondary {
    background-color: #f1f5f9;
    color: #1e293b;
  }

  .btn.secondary:hover {
    background-color: #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
               0 2px 4px -1px rgba(0, 0, 0, 0.06);
  }
</style> 