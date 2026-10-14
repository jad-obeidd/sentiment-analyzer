<script>
  let { result } = $props();

  const EMOJI = { POSITIVE: '😊', NEGATIVE: '😞', NEUTRAL: '😐' };
  const BARS = [
    ['Positive', 'positive', 'pos'],
    ['Neutral', 'neutral', 'neu'],
    ['Negative', 'negative', 'neg'],
  ];
  const pct = (v) => `${Math.round(v * 100)}%`;
  const topIsNeutral = $derived(result.neutral >= result.positive && result.neutral >= result.negative);
</script>

<div class="result {result.label.toLowerCase()}">
  <div class="headline">
    <span class="emoji">{EMOJI[result.label]}</span>
    <div>
      <div class="label">{result.label}</div>
      <div class="confidence">Model confidence {pct(result.confidence)}</div>
    </div>
  </div>
  <div class="bars">
    {#each BARS as [name, key, cls]}
      <div class="bar-row">
        <span>{name}</span>
        <div class="bar"><div class="fill {cls}" style="width: {pct(result[key])}"></div></div>
        <span class="value">{pct(result[key])}</span>
      </div>
    {/each}
  </div>
  {#if result.label === 'NEUTRAL' && !topIsNeutral}
    <p class="note">The model's lean was too weak to count as real sentiment, so this is reported as neutral.</p>
  {/if}
</div>

<style>
  .result {
    margin-top: 18px;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid var(--border);
    border-left: 6px solid var(--neutral);
  }
  .result.positive {
    border-left-color: var(--positive);
  }
  .result.negative {
    border-left-color: var(--negative);
  }
  .headline {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }
  .emoji {
    font-size: 2rem;
  }
  .label {
    font-weight: 700;
    font-size: 1.2rem;
  }
  .confidence,
  .note {
    color: var(--muted);
    font-size: 0.85rem;
  }
  .note {
    margin: 10px 0 0;
  }
  .bar-row {
    display: grid;
    grid-template-columns: 70px 1fr 44px;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    margin: 6px 0;
  }
  .bar {
    height: 8px;
    border-radius: 999px;
    background: var(--border);
    overflow: hidden;
  }
  .fill {
    height: 100%;
    transition: width 0.4s ease;
  }
  .fill.pos {
    background: var(--positive);
  }
  .fill.neg {
    background: var(--negative);
  }
  .fill.neu {
    background: var(--neutral);
  }
  .value {
    text-align: right;
  }
</style>
