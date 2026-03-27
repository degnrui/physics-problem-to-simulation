import { PropsWithChildren } from "react";

type PanelProps = PropsWithChildren<{
  title: string;
  subtitle?: string;
}>;

export function Panel({ title, subtitle, children }: PanelProps) {
  return (
    <section className="panel">
      <header className="panel-header">
        <div>
          <h2>{title}</h2>
          {subtitle ? <p>{subtitle}</p> : null}
        </div>
      </header>
      <div className="panel-body">{children}</div>
    </section>
  );
}
