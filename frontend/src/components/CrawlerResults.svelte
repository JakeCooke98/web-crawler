<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let results = {};
  export const showNewCrawlButton = false;

  function handleNewCrawl() {
    dispatch('newCrawl');
  }
</script>

{#if Object.keys(results).length}
  <div class="results-container">
    <h2>Crawled URLs</h2>
    <ul>
      {#each Object.entries(results) as [page, links]}
        <li>
          <strong>{page}</strong>
          <ul>
            {#each links as link}
              <li><a href={link} target="_blank">{link}</a></li>
            {/each}
          </ul>
        </li>
      {/each}
    </ul>
  </div>
{:else}
  <p>No crawl results yet.</p>
{/if}

<style>
  .results-container {
    margin-top: 2rem;
    padding: 1.5rem;
    background-color: white;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  h2 {
    margin-bottom: 1.5rem;
    color: #1e293b;
  }

  ul {
    list-style-type: none;
    padding-left: 0;
  }

  ul ul {
    padding-left: 1.5rem;
    margin-top: 0.5rem;
  }

  li {
    margin: 0.75rem 0;
    color: #334155;
  }

  a {
    color: #3b82f6;
    text-decoration: none;
    transition: color 0.2s ease;
  }

  a:hover {
    color: #2563eb;
    text-decoration: underline;
  }
</style>
