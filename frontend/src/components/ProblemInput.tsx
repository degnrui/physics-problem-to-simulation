interface ProblemInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
}

export function ProblemInput({ value, onChange, onSubmit, loading }: ProblemInputProps) {
  return (
    <section className="panel">
      <h2>题目输入</h2>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="输入一道高中物理题目，后续这里会走 problem -> model -> scene -> simulation 管线。"
        rows={12}
      />
      <button onClick={onSubmit} disabled={loading || !value.trim()}>
        {loading ? "处理中..." : "提交题目"}
      </button>
    </section>
  );
}

