interface PipelinePreviewProps {
  title: string;
  data: unknown;
  compact?: boolean;
}

export function PipelinePreview({ title, data, compact = false }: PipelinePreviewProps) {
  return (
    <section className={compact ? "artifact-card" : "panel"}>
      <h2>{title}</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </section>
  );
}
