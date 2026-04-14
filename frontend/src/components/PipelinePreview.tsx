interface PipelinePreviewProps {
  title: string;
  data: unknown;
}

export function PipelinePreview({ title, data }: PipelinePreviewProps) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </section>
  );
}

