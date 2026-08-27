/**
 * Decorative animated hero backdrop: a swirling hurricane in the top-right,
 * drifting cloud bands, and growing plants along the bottom edge.
 * Pure SVG + CSS — no images, no layout impact.
 */
export function HeroScene() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      {/* Animated multicolor aurora base */}
      <div className="absolute inset-0 bg-hero-aurora" />

      {/* Glow behind the tornado */}
      <div className="absolute -right-16 -top-24 size-80 rounded-full bg-sky/40 blur-3xl animate-pulse-glow" />

      {/* Tornado — classic condensation funnel, top right */}
      <div className="absolute right-0 top-0 h-[27rem] w-64 animate-tornado-wobble sm:w-80">
        <svg viewBox="0 0 200 340" className="size-full">
          <defs>
            {/* Translucent vapor funnel — pale condensation fading to deep blue */}
            <linearGradient id="funnelBody" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="oklch(0.96 0.02 220)" stopOpacity="0.8" />
              <stop offset="38%" stopColor="oklch(0.84 0.06 225)" stopOpacity="0.68" />
              <stop offset="70%" stopColor="oklch(0.74 0.12 235)" stopOpacity="0.55" />
              <stop offset="100%" stopColor="oklch(0.66 0.15 250)" stopOpacity="0.34" />
            </linearGradient>
            {/* Dark storm wall cloud capping the funnel */}
            <radialGradient id="wallCloud" cx="50%" cy="35%" r="65%">
              <stop offset="0%" stopColor="oklch(0.40 0.06 245)" stopOpacity="0.95" />
              <stop offset="60%" stopColor="oklch(0.46 0.06 250)" stopOpacity="0.7" />
              <stop offset="100%" stopColor="oklch(0.52 0.06 250)" stopOpacity="0.15" />
            </radialGradient>
            {/* Dust/debris cloud at the funnel base */}
            <radialGradient id="debrisCloud" cx="50%" cy="45%" r="55%">
              <stop offset="0%" stopColor="oklch(0.76 0.09 248)" stopOpacity="0.9" />
              <stop offset="70%" stopColor="oklch(0.66 0.10 250)" stopOpacity="0.45" />
              <stop offset="100%" stopColor="oklch(0.60 0.10 250)" stopOpacity="0" />
            </radialGradient>
            <filter id="vaporBlur" x="-20%" y="-10%" width="140%" height="120%">
              <feGaussianBlur stdDeviation="1.8" />
            </filter>
            <filter id="cloudBlur" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="2.4" />
            </filter>
          </defs>

          {/* Dark wall cloud — the storm base the funnel descends from */}
          <path
            d="M2 44 C0 22 30 12 62 18 C90 4 126 6 152 12 C182 4 200 20 198 44 C188 54 154 50 130 42 C104 52 74 48 54 42 C28 52 2 54 2 44 Z"
            fill="url(#wallCloud)"
            filter="url(#cloudBlur)"
          />

          {/* Tapered vapor funnel with a gentle S-twist, narrowing to a thin rope */}
          <path
            d="M42 34 C46 56 54 76 60 90 C68 116 76 134 84 150 C85 172 85 192 86 210 C89 228 93 240 96 250 C94 268 93 282 92 295 C96 300 104 300 108 295 C107 282 106 268 106 250 C108 240 112 228 108 210 C109 192 109 172 124 150 C132 134 140 116 132 90 C140 76 148 56 158 34 C128 26 72 26 42 34 Z"
            fill="url(#funnelBody)"
            filter="url(#vaporBlur)"
          />

          {/* Condensation swirls wrapping the funnel (flowing vapor) */}
          {[
            { y: 50, cx: 100, rx: 54, ry: 7, sw: 3, d: "0s", c: "oklch(0.98 0.02 222)" },
            { y: 88, cx: 97, rx: 38, ry: 6, sw: 2.8, d: "-0.5s", c: "oklch(0.94 0.04 226)" },
            { y: 128, cx: 102, rx: 26, ry: 5, sw: 2.6, d: "-1s", c: "oklch(0.90 0.07 230)" },
            { y: 168, cx: 99, rx: 17, ry: 4.5, sw: 2.4, d: "-1.5s", c: "oklch(0.86 0.09 234)" },
            { y: 208, cx: 97, rx: 11, ry: 4, sw: 2.2, d: "-2s", c: "oklch(0.82 0.11 240)" },
            { y: 244, cx: 101, rx: 6, ry: 3, sw: 2, d: "-2.5s", c: "oklch(0.78 0.13 246)" },
            { y: 278, cx: 100, rx: 7, ry: 3, sw: 2, d: "-3s", c: "oklch(0.76 0.13 250)" },
          ].map((b) => (
            <path
              key={b.y}
              d={`M${b.cx - b.rx} ${b.y} Q ${b.cx} ${b.y + b.ry} ${b.cx + b.rx} ${b.y}`}
              fill="none"
              stroke={b.c}
              strokeOpacity="0.85"
              strokeWidth={b.sw}
              strokeLinecap="round"
              strokeDasharray={`${b.rx * 0.7} ${b.rx * 0.9}`}
              className="animate-tornado-band"
              style={{ animationDelay: b.d }}
            />
          ))}

          {/* Ragged dust/debris cloud where the funnel rope meets the ground */}
          <path
            d="M84 296 C78 290 86 286 92 290 C95 283 106 285 107 292 C115 287 120 295 113 299 C118 304 109 309 104 304 C101 311 90 309 88 302 C80 305 78 299 84 296 Z"
            fill="url(#debrisCloud)"
            filter="url(#cloudBlur)"
          />
          {[
            { cx: 80, cy: 300, r: 2.6, d: "0s" },
            { cx: 120, cy: 296, r: 2.2, d: "-1.2s" },
            { cx: 100, cy: 312, r: 2, d: "-2.4s" },
            { cx: 112, cy: 308, r: 1.8, d: "-3.2s" },
          ].map((p) => (
            <circle
              key={p.cx}
              cx={p.cx}
              cy={p.cy}
              r={p.r}
              fill="oklch(0.66 0.10 250)"
              fillOpacity="0.7"
              className="animate-float"
              style={{ animationDelay: p.d }}
            />
          ))}
        </svg>
      </div>

      {/* Counter-rotating wind ring around the funnel top */}
      <svg
        viewBox="0 0 200 200"
        className="absolute -right-20 -top-20 size-72 animate-spin-rev opacity-30 sm:size-96"
      >
        <circle
          cx="100"
          cy="100"
          r="82"
          fill="none"
          stroke="oklch(0.82 0.07 230)"
          strokeWidth="1.5"
          strokeDasharray="18 26"
        />
        <circle
          cx="100"
          cy="100"
          r="64"
          fill="none"
          stroke="oklch(0.74 0.12 245)"
          strokeOpacity="0.6"
          strokeWidth="1.5"
          strokeDasharray="10 22"
        />
      </svg>

      {/* Drifting cloud bands */}
      <div className="absolute left-1/4 top-6 h-16 w-64 rounded-full bg-white/10 blur-2xl animate-drift" />
      <div
        className="absolute left-1/2 top-24 h-14 w-72 rounded-full bg-sky/20 blur-2xl animate-drift"
        style={{ animationDelay: "-6s" }}
      />

      {/* Legibility scrim for the copy — placed behind plants/leaves so they stay vivid */}
      <div className="absolute inset-0 bg-gradient-to-r from-[oklch(0.28_0.10_250)]/85 via-[oklch(0.28_0.10_250)]/45 to-transparent" />

      {/* Floating leaves */}
      {[
        { top: "18%", left: "12%", delay: "0s", color: "oklch(0.85 0.17 55)", size: 26 },
        { top: "58%", left: "34%", delay: "-3s", color: "oklch(0.78 0.16 25)", size: 20 },
        { top: "30%", left: "58%", delay: "-5s", color: "oklch(0.82 0.18 15)", size: 18 },
      ].map((l) => (
        <svg
          key={l.left}
          viewBox="0 0 24 24"
          className="absolute animate-float"
          style={{
            top: l.top,
            left: l.left,
            width: l.size,
            height: l.size,
            animationDelay: l.delay,
            opacity: 0.8,
          }}
        >
          <path
            d="M12 2C7 5 3 9 3 14a7 7 0 0 0 14 0c0-5-1-9-5-12Z"
            fill={l.color}
            fillOpacity="0.9"
          />
          <path d="M12 4v16" stroke="oklch(0.30 0.10 250)" strokeOpacity="0.45" strokeWidth="1" />
        </svg>
      ))}

      {/* Plants growing along the bottom */}
      <svg
        viewBox="0 0 400 120"
        preserveAspectRatio="none"
        className="absolute bottom-0 left-0 h-28 w-full"
      >
        <path
          d="M0 120 C 60 90 120 108 200 96 C 280 84 340 104 400 88 L400 120 Z"
          fill="oklch(0.36 0.08 250)"
          fillOpacity="0.55"
        />
      </svg>
      <div className="absolute bottom-0 left-0 flex w-full items-end gap-6 px-4">
        {[
          { h: 74, color: "oklch(0.82 0.18 45)", delay: "0s" },
          { h: 52, color: "oklch(0.80 0.16 25)", delay: "-1.2s" },
          { h: 92, color: "oklch(0.84 0.17 15)", delay: "-2.4s" },
          { h: 46, color: "oklch(0.85 0.17 95)", delay: "-0.6s" },
          { h: 66, color: "oklch(0.74 0.20 320)", delay: "-1.8s" },
          { h: 38, color: "oklch(0.85 0.15 70)", delay: "-3s" },
        ].map((p, i) => (
          <svg
            key={i}
            viewBox="0 0 40 100"
            className="animate-sway"
            style={{ height: p.h, width: p.h * 0.4, animationDelay: p.delay, opacity: 0.85 }}
          >
            <path d="M20 100 C 20 70 18 45 20 18" stroke={p.color} strokeWidth="3" fill="none" />
            <path d="M20 62 C 6 56 2 44 4 34 C 14 38 20 48 20 62 Z" fill={p.color} fillOpacity="0.85" />
            <path d="M20 46 C 34 40 38 28 36 18 C 26 22 20 32 20 46 Z" fill={p.color} fillOpacity="0.7" />
            <circle cx="20" cy="14" r="5" fill={p.color} fillOpacity="0.9" />
          </svg>
        ))}
      </div>

      {/* Thunderstorm cloud above the plants */}
      <div className="pointer-events-none absolute bottom-24 left-[20%] w-44 animate-cloud-bob sm:left-[22%] sm:w-48">
        {/* Flash glow behind the cloud */}
        <div className="absolute -inset-8 rounded-full bg-[oklch(0.92_0.10_235)]/60 blur-2xl animate-storm-flash" />

        <svg viewBox="0 0 200 96" className="relative w-full">
          <defs>
            <linearGradient id="stormCloud" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="oklch(0.62 0.07 240)" />
              <stop offset="60%" stopColor="oklch(0.42 0.07 250)" />
              <stop offset="100%" stopColor="oklch(0.30 0.06 255)" />
            </linearGradient>
          </defs>
          <g fill="url(#stormCloud)">
            <ellipse cx="60" cy="40" rx="42" ry="24" />
            <ellipse cx="104" cy="30" rx="38" ry="26" />
            <ellipse cx="146" cy="42" rx="36" ry="21" />
            <rect x="22" y="42" width="156" height="16" rx="8" />
          </g>
          {/* Lightning bolts */}
          <path
            d="M92 56 L82 74 L92 74 L84 94"
            fill="none"
            stroke="oklch(0.95 0.15 100)"
            strokeWidth="3"
            strokeLinecap="round"
            className="animate-lightning"
          />
          <path
            d="M132 56 L124 70 L132 70 L126 88"
            fill="none"
            stroke="oklch(0.93 0.13 95)"
            strokeWidth="2.5"
            strokeLinecap="round"
            className="animate-lightning"
            style={{ animationDelay: "-2.4s" }}
          />
        </svg>

        {/* Rain drops */}
        <div className="absolute left-4 right-4 top-[62%] h-14 overflow-hidden">
          {Array.from({ length: 14 }).map((_, i) => (
            <span
              key={i}
              className="absolute top-0 block h-3 w-[2px] rounded-full bg-[oklch(0.86_0.09_235)]/80 animate-rain"
              style={{
                left: `${(i * 100) / 14 + 2}%`,
                animationDelay: `${-(i % 5) * 0.26 - (i % 3) * 0.1}s`,
                animationDuration: `${1.1 + (i % 4) * 0.18}s`,
              }}
            />
          ))}
        </div>
      </div>

      {/* Mirrored thunderstorm cloud further left for symmetry */}
      <div className="pointer-events-none absolute bottom-24 left-[0%] w-44 animate-cloud-bob sm:left-[1%] sm:w-48" style={{ animationDelay: "-3.5s" }}>
        {/* Flash glow behind the cloud */}
        <div className="absolute -inset-8 rounded-full bg-[oklch(0.92_0.10_235)]/60 blur-2xl animate-storm-flash" style={{ animationDelay: "-1.8s" }} />

        <svg viewBox="0 0 200 96" className="relative w-full">
          <defs>
            <linearGradient id="stormCloud2" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="oklch(0.62 0.07 240)" />
              <stop offset="60%" stopColor="oklch(0.42 0.07 250)" />
              <stop offset="100%" stopColor="oklch(0.30 0.06 255)" />
            </linearGradient>
          </defs>
          <g fill="url(#stormCloud2)">
            <ellipse cx="60" cy="40" rx="42" ry="24" />
            <ellipse cx="104" cy="30" rx="38" ry="26" />
            <ellipse cx="146" cy="42" rx="36" ry="21" />
            <rect x="22" y="42" width="156" height="16" rx="8" />
          </g>
          {/* Lightning bolts */}
          <path
            d="M92 56 L82 74 L92 74 L84 94"
            fill="none"
            stroke="oklch(0.95 0.15 100)"
            strokeWidth="3"
            strokeLinecap="round"
            className="animate-lightning"
            style={{ animationDelay: "-1.2s" }}
          />
          <path
            d="M132 56 L124 70 L132 70 L126 88"
            fill="none"
            stroke="oklch(0.93 0.13 95)"
            strokeWidth="2.5"
            strokeLinecap="round"
            className="animate-lightning"
            style={{ animationDelay: "-3.8s" }}
          />
        </svg>

        {/* Rain drops */}
        <div className="absolute left-4 right-4 top-[62%] h-14 overflow-hidden">
          {Array.from({ length: 14 }).map((_, i) => (
            <span
              key={i}
              className="absolute top-0 block h-3 w-[2px] rounded-full bg-[oklch(0.86_0.09_235)]/80 animate-rain"
              style={{
                left: `${(i * 100) / 14 + 2}%`,
                animationDelay: `${-(i % 5) * 0.26 - (i % 3) * 0.1 - 0.5}s`,
                animationDuration: `${1.1 + (i % 4) * 0.18}s`,
              }}
            />
          ))}
        </div>
      </div>

      {/* Healthy birch tree between the plants and the tornado */}
      <div
        className="pointer-events-none absolute bottom-0 left-[44%] w-28 origin-bottom animate-sway sm:left-[48%] sm:w-32"
        style={{ animationDelay: "-1.6s" }}
      >
        <svg viewBox="0 0 100 260" className="h-64 w-full sm:h-72">
          <defs>
            <linearGradient id="birchTrunk" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="oklch(0.94 0.015 110)" />
              <stop offset="50%" stopColor="oklch(0.97 0.008 110)" />
              <stop offset="100%" stopColor="oklch(0.88 0.02 110)" />
            </linearGradient>
            <radialGradient id="birchLeaf" cx="40%" cy="35%" r="70%">
              <stop offset="0%" stopColor="oklch(0.80 0.16 145)" />
              <stop offset="70%" stopColor="oklch(0.66 0.17 150)" />
              <stop offset="100%" stopColor="oklch(0.54 0.15 155)" />
            </radialGradient>
          </defs>

          {/* Trunk — tapered, white birch bark */}
          <path
            d="M44 260 L42 150 L46 60 L48 20 L52 20 L54 60 L50 150 L52 260 Z"
            fill="url(#birchTrunk)"
            stroke="oklch(0.82 0.02 110)"
            strokeWidth="0.6"
          />
          {/* Black lenticel bark markings */}
          {[34, 52, 70, 88, 104, 122, 140, 158, 178, 196, 214, 232].map((y, i) => (
            <rect
              key={y}
              x={i % 2 === 0 ? 43 : 47}
              y={y}
              width={i % 2 === 0 ? 7 : 6}
              height={2.4}
              rx={1.2}
              fill="oklch(0.28 0.02 250)"
              fillOpacity="0.7"
            />
          ))}

          {/* Branches */}
          <path d="M48 70 C 40 64 34 58 30 50" stroke="oklch(0.90 0.015 110)" strokeWidth="2.4" fill="none" strokeLinecap="round" />
          <path d="M52 58 C 60 52 66 48 70 42" stroke="oklch(0.90 0.015 110)" strokeWidth="2.4" fill="none" strokeLinecap="round" />

          {/* Lush canopy clusters */}
          <g fill="url(#birchLeaf)">
            <ellipse cx="50" cy="30" rx="34" ry="26" />
            <ellipse cx="28" cy="44" rx="20" ry="16" />
            <ellipse cx="72" cy="42" rx="20" ry="16" />
            <ellipse cx="50" cy="14" rx="22" ry="16" />
            <ellipse cx="36" cy="24" rx="16" ry="13" />
            <ellipse cx="66" cy="26" rx="17" ry="14" />
          </g>
          {/* Light leaf highlights for a healthy sheen */}
          <g fill="oklch(0.86 0.15 140)" fillOpacity="0.55">
            <ellipse cx="42" cy="18" rx="9" ry="6" />
            <ellipse cx="60" cy="22" rx="8" ry="5" />
            <ellipse cx="50" cy="32" rx="7" ry="5" />
          </g>
        </svg>
      </div>

    </div>

  );
}
