import type { ReactNode } from "react";

interface FullscreenRuntimeModalProps {
  children: ReactNode;
  onClose: () => void;
}

export function FullscreenRuntimeModal({ children, onClose }: FullscreenRuntimeModalProps) {
  return (
    <div className="fullscreen-modal">
      <div className="fullscreen-scrim" onClick={onClose} />
      <div className="fullscreen-panel">{children}</div>
    </div>
  );
}
