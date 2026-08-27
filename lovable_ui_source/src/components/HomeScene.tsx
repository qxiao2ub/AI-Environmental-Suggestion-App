/**
 * Bright animated home-screen backdrop: a sunny farm landscape with an
 * animated sun (top right), a thick-trunked leafy tree (bottom left),
 * spinning windmills, and swaying crops. Pure SVG + CSS — no images.
 */
export function HomeScene() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      {/* Bright daytime sky */}
      <div className="absolute inset-0 bg-gradient-to-b from-[oklch(0.90_0.10_225)] via-[oklch(0.93_0.06_200)] to-[oklch(0.96_0.04_140)]" />

      {/* Sun — top right (nudged further out) */}
      <div className="absolute -right-2 -top-2 size-28 sm:right-4 sm:top-2 sm:size-36">
        {/* Rotating rays */}
        <svg viewBox="0 0 100 100" className="absolute inset-0 size-full animate-spin-slow" style={{ animationDuration: "40s" }}>
          {Array.from({ length: 12 }).map((_, i) => {
            const a = (i * 30 * Math.PI) / 180;
            const x1 = 50 + 34 * Math.cos(a);
            const y1 = 50 + 34 * Math.sin(a);
            const x2 = 50 + 46 * Math.cos(a);
            const y2 = 50 + 46 * Math.sin(a);
            return (
              <line
                key={i}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke="oklch(0.88 0.18 95)"
                strokeWidth="3.5"
                strokeLinecap="round"
                opacity="0.9"
              />
            );
          })}
        </svg>
        {/* Glow + disc */}
        <div className="absolute inset-4 rounded-full bg-[oklch(0.92_0.16_100)]/70 blur-lg animate-pulse-glow" />
        <svg viewBox="0 0 100 100" className="absolute inset-0 size-full">
          <defs>
            <radialGradient id="sunDisc" cx="42%" cy="38%" r="70%">
              <stop offset="0%" stopColor="oklch(0.96 0.16 105)" />
              <stop offset="65%" stopColor="oklch(0.90 0.17 90)" />
              <stop offset="100%" stopColor="oklch(0.84 0.18 75)" />
            </radialGradient>
          </defs>
          <circle cx="50" cy="50" r="30" fill="url(#sunDisc)" />
        </svg>
      </div>

      {/* Drifting clouds */}
      {[
        { top: "12%", left: "18%", w: 130, delay: "0s" },
        { top: "26%", left: "52%", w: 150, delay: "-7s" },
      ].map((c, i) => (
        <svg
          key={i}
          viewBox="0 0 160 60"
          className="absolute animate-drift opacity-90"
          style={{ top: c.top, left: c.left, width: c.w, animationDelay: c.delay }}
        >
          <g fill="oklch(0.99 0.01 230)">
            <ellipse cx="48" cy="36" rx="34" ry="16" />
            <ellipse cx="82" cy="28" rx="30" ry="19" />
            <ellipse cx="116" cy="38" rx="28" ry="14" />
          </g>
        </svg>
      ))}

      {/* Rolling farmland hills */}
      <svg viewBox="0 0 1200 200" preserveAspectRatio="none" className="absolute bottom-0 left-0 h-2/5 w-full">
        <defs>
          <linearGradient id="hillBack" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="oklch(0.78 0.17 130)" />
            <stop offset="100%" stopColor="oklch(0.68 0.17 140)" />
          </linearGradient>
          <linearGradient id="hillFront" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="oklch(0.70 0.19 135)" />
            <stop offset="100%" stopColor="oklch(0.56 0.17 145)" />
          </linearGradient>
        </defs>
        <path d="M0 90 C 200 40 420 110 640 70 C 860 30 1040 100 1200 60 L1200 200 L0 200 Z" fill="url(#hillBack)" />
        <path d="M0 140 C 240 90 480 160 720 120 C 920 90 1080 150 1200 120 L1200 200 L0 200 Z" fill="url(#hillFront)" />
        {/* Crop rows on the front hill */}
        {Array.from({ length: 9 }).map((_, i) => (
          <path
            key={i}
            d={`M0 ${150 + i * 6} C 240 ${100 + i * 5.4} 480 ${168 + i * 4} 720 ${128 + i * 5.4} C 920 ${98 + i * 5.4} 1080 ${158 + i * 4.6} 1200 ${128 + i * 5}`}
            fill="none"
            stroke="oklch(0.50 0.15 145)"
            strokeOpacity="0.45"
            strokeWidth="2"
          />
        ))}
      </svg>

      {/* Vibrant garden beds — varied agriculture across the middle ground */}
      <div className="absolute bottom-[18%] left-0 right-0 flex items-end justify-center gap-1 px-6 sm:gap-2 sm:px-10">
        {[
          // Tomatoes / red crops
          { w: 38, h: 22, c: "oklch(0.62 0.22 28)", edge: "oklch(0.50 0.20 30)", delay: "0s" },
          // Sunflowers / yellow
          { w: 46, h: 26, c: "oklch(0.88 0.18 95)", edge: "oklch(0.78 0.17 85)", delay: "-0.6s" },
          // Leafy greens / lettuce
          { w: 34, h: 18, c: "oklch(0.74 0.20 145)", edge: "oklch(0.62 0.18 150)", delay: "-1.2s" },
          // Lavender / purple
          { w: 42, h: 24, c: "oklch(0.60 0.20 300)", edge: "oklch(0.52 0.18 305)", delay: "-0.3s" },
          // Carrots / orange
          { w: 36, h: 20, c: "oklch(0.74 0.17 55)", edge: "oklch(0.64 0.16 50)", delay: "-1.5s" },
          // Blueberries / blue
          { w: 40, h: 22, c: "oklch(0.56 0.16 250)", edge: "oklch(0.46 0.15 255)", delay: "-0.9s" },
          // Bell peppers mix
          { w: 32, h: 18, c: "oklch(0.66 0.22 145)", edge: "oklch(0.55 0.20 150)", delay: "-2s" },
          // Beets / magenta
          { w: 38, h: 22, c: "oklch(0.58 0.22 12)", edge: "oklch(0.48 0.20 15)", delay: "-1.1s" },
        ].map((g, i) => (
          <div
            key={i}
            className="animate-sway"
            style={{ width: g.w, height: g.h, animationDelay: g.delay, animationDuration: "5s" }}
          >
            <svg viewBox={`0 0 ${g.w} ${g.h}`} className="h-full w-full">
              {/* Soil bed */}
              <rect x="0" y={g.h * 0.45} width={g.w} height={g.h * 0.55} rx="3" fill="oklch(0.40 0.06 50)" />
              <rect x="0" y={g.h * 0.45} width={g.w} height={g.h * 0.55} rx="3" fill="oklch(0.32 0.07 45)" opacity="0.35" />
              {/* Crop tufts */}
              {Array.from({ length: Math.max(3, Math.round(g.w / 6)) }).map((_, j) => {
                const cx = (j + 0.5) * (g.w / Math.max(3, Math.round(g.w / 6)));
                const cy = g.h * 0.42;
                return (
                  <g key={j}>
                    <circle cx={cx} cy={cy} r={g.h * 0.16} fill={g.c} />
                    <circle cx={cx - g.h * 0.06} cy={cy - g.h * 0.05} r={g.h * 0.1} fill={g.edge} opacity="0.7" />
                    <circle cx={cx + g.h * 0.05} cy={cy + g.h * 0.02} r={g.h * 0.08} fill={g.c} opacity="0.85" />
                  </g>
                );
              })}
            </svg>
          </div>
        ))}
      </div>

      {/* Flower strip — bright blooms scattered across the front edge */}
      <div className="absolute bottom-[14%] left-0 right-0 flex items-end justify-center gap-3 px-12 opacity-95 sm:gap-6 sm:px-20">
        {[
          { c: "oklch(0.72 0.22 20)", s: 9, d: "0s" },
          { c: "oklch(0.82 0.20 95)", s: 7, d: "-1s" },
          { c: "oklch(0.66 0.20 300)", s: 8, d: "-2s" },
          { c: "oklch(0.78 0.18 350)", s: 6, d: "-0.5s" },
          { c: "oklch(0.84 0.17 145)", s: 9, d: "-1.6s" },
          { c: "oklch(0.72 0.22 25)", s: 7, d: "-2.4s" },
        ].map((f, i) => (
          <svg key={i} viewBox="0 0 20 28" className="animate-sway" style={{ height: f.s + 14, width: f.s + 14, animationDelay: f.d }}>
            <path d="M10 28 C 10 20 9 14 10 8" stroke="oklch(0.66 0.14 145)" strokeWidth="1.6" fill="none" />
            <g transform="translate(10 6)">
              {[0, 72, 144, 216, 288].map((deg) => (
                <ellipse key={deg} cx="0" cy="-3" rx="2.6" ry="4" fill={f.c} transform={`rotate(${deg})`} />
              ))}
              <circle cx="0" cy="0" r="2" fill="oklch(0.88 0.17 90)" />
            </g>
          </svg>
        ))}
      </div>

      <svg viewBox="0 0 120 90" className="absolute bottom-[16%] right-[30%] w-16 sm:w-24">
        <rect x="22" y="38" width="76" height="46" fill="oklch(0.56 0.16 25)" />
        <path d="M16 40 L60 10 L104 40 Z" fill="oklch(0.44 0.14 30)" />
        <rect x="52" y="58" width="16" height="26" fill="oklch(0.30 0.08 40)" />
        <path d="M52 58 L68 84 M68 58 L52 84" stroke="oklch(0.85 0.05 80)" strokeWidth="1.5" />
        <rect x="30" y="48" width="10" height="10" fill="oklch(0.90 0.06 90)" />
      </svg>

      {/* Windmills with spinning blades */}
      {[
        { left: "58%", scale: 1, delay: "0s" },
        { left: "74%", scale: 0.8, delay: "-1.4s" },
      ].map((m, i) => (
        <svg
          key={i}
          viewBox="0 0 60 120"
          className="absolute bottom-[14%]"
          style={{ left: m.left, width: 44 * m.scale }}
        >
          {/* Tower */}
          <path d="M26 120 L28 52 L32 52 L34 120 Z" fill="oklch(0.92 0.02 95)" stroke="oklch(0.62 0.05 90)" strokeWidth="1" />
          <path d="M26 84 L34 84" stroke="oklch(0.62 0.05 90)" strokeWidth="1" />
          {/* Spinning blades */}
          <g
            className="animate-spin-slow"
            style={{ transformOrigin: "30px 50px", animationDuration: "7s", animationDelay: m.delay }}
          >
            {[0, 90, 180, 270].map((deg) => (
              <path
                key={deg}
                d="M30 50 L26 14 L34 14 L30 50 Z"
                fill="oklch(0.96 0.02 100)"
                stroke="oklch(0.58 0.05 90)"
                strokeWidth="0.8"
                transform={`rotate(${deg} 30 50)`}
              />
            ))}
          </g>
          <circle cx="30" cy="50" r="3.5" fill="oklch(0.55 0.10 60)" />
        </svg>
      ))}

      {/* Swaying wheat / crops in the foreground */}
      <div className="absolute bottom-0 left-0 flex w-full items-end justify-between px-2">
        {[
          { h: 46, c: "oklch(0.84 0.17 95)", d: "0s" },
          { h: 34, c: "oklch(0.80 0.18 80)", d: "-1s" },
          { h: 52, c: "oklch(0.86 0.16 100)", d: "-2s" },
          { h: 30, c: "oklch(0.78 0.17 75)", d: "-0.5s" },
          { h: 42, c: "oklch(0.85 0.17 90)", d: "-1.6s" },
          { h: 36, c: "oklch(0.81 0.18 85)", d: "-2.6s" },
          { h: 48, c: "oklch(0.84 0.16 95)", d: "-3.2s" },
        ].map((w, i) => (
          <svg
            key={i}
            viewBox="0 0 20 60"
            className="animate-sway"
            style={{ height: w.h, width: w.h * 0.34, animationDelay: w.d }}
          >
            <path d="M10 60 C 10 42 9 30 10 14" stroke="oklch(0.66 0.14 110)" strokeWidth="2.2" fill="none" />
            <ellipse cx="10" cy="10" rx="4.5" ry="9" fill={w.c} />
            <path d="M10 4 L10 18 M6 8 L14 8 M7 12 L13 12" stroke={w.c} strokeWidth="1.2" />
          </svg>
        ))}
      </div>

      {/* Thick-trunked leafy tree — bottom left */}
      <div className="absolute bottom-0 left-0 w-40 origin-bottom animate-sway sm:left-1 sm:w-52" style={{ animationDelay: "-0.8s" }}>
        <svg viewBox="0 0 160 220" className="h-56 w-full sm:h-64">
          <defs>
            <linearGradient id="treeTrunk" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="oklch(0.38 0.07 60)" />
              <stop offset="50%" stopColor="oklch(0.48 0.08 65)" />
              <stop offset="100%" stopColor="oklch(0.34 0.06 55)" />
            </linearGradient>
            <radialGradient id="treeLeaf" cx="42%" cy="32%" r="75%">
              <stop offset="0%" stopColor="oklch(0.82 0.18 140)" />
              <stop offset="65%" stopColor="oklch(0.68 0.18 145)" />
              <stop offset="100%" stopColor="oklch(0.54 0.16 150)" />
            </radialGradient>
          </defs>
          {/* Thick trunk with branches */}
          <path d="M64 220 L62 150 C 60 130 56 118 48 106 L56 100 C 62 112 66 124 68 140 L70 100 L74 100 L76 140 C 78 124 84 110 92 100 L100 106 C 90 118 84 132 82 152 L84 220 Z" fill="url(#treeTrunk)" />
          {/* Bark texture lines */}
          <path d="M68 200 L67 170 M76 210 L77 180 M71 160 L70 130" stroke="oklch(0.30 0.05 55)" strokeWidth="1.6" strokeOpacity="0.6" fill="none" />
          {/* Lush green canopy */}
          <g fill="url(#treeLeaf)">
            <ellipse cx="74" cy="60" rx="52" ry="40" />
            <ellipse cx="36" cy="80" rx="30" ry="24" />
            <ellipse cx="114" cy="78" rx="30" ry="24" />
            <ellipse cx="74" cy="26" rx="34" ry="24" />
            <ellipse cx="50" cy="44" rx="24" ry="18" />
            <ellipse cx="100" cy="46" rx="25" ry="19" />
          </g>
          {/* Sunlit leaf highlights */}
          <g fill="oklch(0.88 0.17 135)" fillOpacity="0.6">
            <ellipse cx="56" cy="34" rx="12" ry="8" />
            <ellipse cx="88" cy="40" rx="10" ry="7" />
            <ellipse cx="70" cy="56" rx="9" ry="6" />
          </g>
        </svg>
      </div>
    </div>
  );
}
