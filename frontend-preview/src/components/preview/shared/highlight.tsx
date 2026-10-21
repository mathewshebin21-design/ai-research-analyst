/** Renders a source extract with the span the verifier relied on marked. */
export function HighlightedExtract({ text, highlight, markClassName }: { text: string; highlight: string; markClassName: string }) {
  const i = text.indexOf(highlight);
  if (i < 0) return <>{text}</>;
  return (
    <>
      {text.slice(0, i)}
      <mark className={markClassName}>{highlight}</mark>
      {text.slice(i + highlight.length)}
    </>
  );
}
