interface HtmlRuntimeFrameProps {
  title: string;
  source: string;
  fullscreen?: boolean;
}

export function HtmlRuntimeFrame({ title, source, fullscreen = false }: HtmlRuntimeFrameProps) {
  return (
    <div className={fullscreen ? "html-runtime-frame-shell fullscreen" : "html-runtime-frame-shell"}>
      <iframe
        title={title}
        className="html-runtime-frame"
        srcDoc={source}
        sandbox="allow-scripts"
      />
    </div>
  );
}
