interface StudioBrandProps {
  compact?: boolean;
}

function BrandGlyph() {
  return (
    <svg viewBox="0 0 64 64" aria-hidden="true" className="brand-glyph">
      <rect x="8" y="8" width="48" height="48" rx="16" className="brand-glyph-shell" />
      <path
        d="M25 20h-4.5c-3.6 0-6.5 2.9-6.5 6.5v11c0 8.3 5.7 14.5 14.6 14.5H40"
        className="brand-glyph-stroke"
      />
      <path
        d="M39.5 21.5c-3.2-1.6-6.3-2.2-10.1-2.2-4.8 0-8.5 2.4-8.5 6.1 0 3.2 2.5 5.3 7.4 6.5l4.1 1c3.2.8 4.7 1.9 4.7 4 0 2.7-2.5 4.5-6.8 4.5-3.5 0-6.5-.8-9.7-2.6"
        className="brand-glyph-stroke"
      />
      <circle cx="47" cy="18" r="4.5" className="brand-glyph-dot" />
    </svg>
  );
}

export function StudioBrand({ compact = false }: StudioBrandProps) {
  return (
    <span className={compact ? "studio-brand compact" : "studio-brand"}>
      <span className="brand-mark-shell">
        <BrandGlyph />
      </span>
      <span className="brand-name">ClassSim</span>
      <span className="brand-tagline">TEACHER SIMULATION STUDIO</span>
    </span>
  );
}
