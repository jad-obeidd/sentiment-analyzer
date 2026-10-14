<script>
  import { onMount } from 'svelte';
  import { analyze, getHistory, deleteItem, clearHistory, getStats } from './api.js';
  import ResultCard from './lib/ResultCard.svelte';
  import StatsBar from './lib/StatsBar.svelte';

  const MAX = 2000;
  const EXAMPLES = [
    'I absolutely love this phone, the battery lasts forever!',
    'The delivery was late and the food was cold.',
    'The meeting is scheduled for 3pm on Tuesday.',
  ];

  let text = $state('');
  let result = $state(null);
  let history = $state([]);
  let stats = $state(null);
  let filter = $state('');
  let loading = $state(false);
  let error = $state('');

  async function refresh() {
    const [h, s] = await Promise.all([getHistory(filter), getStats()]);
    history = h.items;
    stats = s;
  }

  async function submit(event) {
    event.preventDefault();
    if (!text.trim()) return;
    loading = true;
    error = '';
    try {
      result = await analyze(text);
      await refresh();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function remove(id) {
    await deleteItem(id);
    if (result?.id === id) result = null;
    await refresh();
  }

  async function clearAll() {
    if (!confirm('Delete all saved analyses?')) return;
    await clearHistory();
    result = null;
    await refresh();
  }

  function setFilter(label) {
    filter = label;
    refresh().catch((err) => (error = err.message));
  }

  onMount(() => {
    refresh().catch(() => (error = 'Cannot reach the API. Is the Flask server running on port 5000?'));
  });
</script>

<main>
  <header>
    <h1>🧠 Sentiment Analyzer</h1>
    <p>Classify any text as positive, negative or neutral with a DistilBERT NLP model.</p>
  </header>

  <section class="card">
    <form onsubmit={submit}>
      <label for="text">Text to analyze</label>
      <textarea id="text" bind:value={text} maxlength={MAX} rows="5" placeholder="Type or paste a review, tweet or message…"></textarea>
      <div class="row">
        <div class="examples">
          {#each EXAMPLES as example}
            <button type="button" class="chip" onclick={() => (text = example)}>{example.slice(0, 28)}…</button>
          {/each}
        </div>
        <span class="count">{text.length}/{MAX}</span>
      </div>
      <button class="primary" disabled={loading || !text.trim()}>
        {loading ? 'Analyzing…' : 'Analyze sentiment'}
      </button>
    </form>
    {#if error}<p class="error">{error}</p>{/if}
    {#if result}<ResultCard {result} />{/if}
  </section>

  {#if stats}<StatsBar {stats} />{/if}

  <section class="card">
    <div class="row">
      <h2>History</h2>
      <div class="filters">
        {#each [['', 'All'], ['POSITIVE', 'Positive'], ['NEGATIVE', 'Negative'], ['NEUTRAL', 'Neutral']] as [value, label]}
          <button class="chip" class:active={filter === value} onclick={() => setFilter(value)}>{label}</button>
        {/each}
        {#if history.length}<button class="chip danger" onclick={clearAll}>Clear all</button>{/if}
      </div>
    </div>
    {#if history.length === 0}
      <p class="muted">No analyses yet.</p>
    {:else}
      <ul>
        {#each history as item (item.id)}
          <li>
            <span class="badge {item.label.toLowerCase()}">{item.label}</span>
            <span class="text">{item.text}</span>
            <span class="muted small">{Math.round(item.confidence * 100)}%</span>
            <button class="icon" aria-label="Delete" onclick={() => remove(item.id)}>✕</button>
          </li>
        {/each}
      </ul>
    {/if}
  </section>
</main>

<style>
  main {
    max-width: 760px;
    margin: 0 auto;
    padding: 32px 16px 64px;
  }
  header h1 {
    margin: 0 0 4px;
  }
  header p,
  .muted {
    color: var(--muted);
  }
  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    margin-top: 20px;
  }
  label {
    font-weight: 600;
    display: block;
    margin-bottom: 8px;
  }
  textarea {
    width: 100%;
    font: inherit;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid var(--border);
    background: var(--bg);
    color: var(--text);
    resize: vertical;
  }
  .row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin: 10px 0;
  }
  .row h2 {
    margin: 0;
    font-size: 1.1rem;
  }
  .examples,
  .filters {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }
  .chip {
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.8rem;
  }
  .chip.active {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
  }
  .chip.danger {
    color: var(--negative);
  }
  .count,
  .small {
    font-size: 0.8rem;
  }
  .primary {
    width: 100%;
    padding: 12px;
    border: 0;
    border-radius: 10px;
    background: var(--accent);
    color: white;
    font-weight: 600;
  }
  .error {
    color: var(--negative);
  }
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  li {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 0;
    border-top: 1px solid var(--border);
  }
  .text {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .badge {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 6px;
    color: white;
  }
  .badge.positive {
    background: var(--positive);
  }
  .badge.negative {
    background: var(--negative);
  }
  .badge.neutral {
    background: var(--neutral);
  }
  .icon {
    border: 0;
    background: none;
    color: var(--muted);
  }
</style>
