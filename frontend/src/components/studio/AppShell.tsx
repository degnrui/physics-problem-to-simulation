import type { ReactNode } from "react";

interface AppShellProps {
  rail: ReactNode;
  sidebar: ReactNode;
  main: ReactNode;
  preview: ReactNode;
  fullscreenLayer?: ReactNode;
}

export function AppShell({ rail, sidebar, main, preview, fullscreenLayer }: AppShellProps) {
  return (
    <>
      <div className="app-shell">
        {rail}
        {sidebar}
        <main className="min-w-0 flex-1">{main}</main>
        {preview}
      </div>
      {fullscreenLayer}
    </>
  );
}
