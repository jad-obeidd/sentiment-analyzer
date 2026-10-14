<script>
  let { stats } = $props();

  const LABELS = [
    ['POSITIVE', 'Positive', 'var(--positive)'],
    ['NEUTRAL', 'Neutral', 'var(--neutral)'],
    ['NEGATIVE', 'Negative', 'var(--negative)'],
  ];
</script>

<section class="stats">
  <div class="total">
    <strong>{stats.total}</strong>
    <span>texts analyzed</span>
  </div>
  {#if stats.total}
    <div class="stack" role="img" aria-label="Distribution of sentiment labels">
      {#each LABELS as [key, , color]}
        {#if stats.counts[key]}
          <div style="flex: {stats.counts[key]}; background: {color}"></div>
        {/if}
      {/each}
    </div>
  {/if}
  <div class="legend">
    {#each LABELS as [key, name, color]}
      <span><i style="background: {color}"></i>{name} {stats.counts[key]}</span>
    {/each}
  </div>
</section>

<style>
  .stats {
    margin-top: 20px;
    padding: 16px 20px;
    border-radius: 14px;
    background: var(--card);
    border: 1px solid var(--border);
  }
  .total strong {
    font-size: 1.4rem;
    margin-right: 6px;
  }
  .total span,
  .legend {
    color: var(--muted);
    font-size: 0.85rem;
  }
  .stack {
    display: flex;
    gap: 2px;
    height: 10px;
    border-radius: 999px;
    overflow: hidden;
    margin: 10px 0;
  }
  .legend {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }
  .legend i {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 3px;
    margin-right: 6px;
    vertical-align: -1px;
  }
</style>
