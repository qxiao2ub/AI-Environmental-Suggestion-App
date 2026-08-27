import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
} from "recharts";
import {
  Leaf,
  Sprout,
  Building2,
  Search,
  Bell,
  Send,
  Flame,
  TrendingUp,
  Award,
  Droplets,
  Recycle,
  Sun,
  TreePine,
  Car,
  LandPlot,
  ShieldCheck,
  ChevronRight,
  Sparkles,
  ArrowUpRight,
  Target,
} from "lucide-react";
import { HomeScene } from "@/components/HomeScene";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Tailored AI Environmental Suggester — Dashboard" },
      {
        name: "description",
        content:
          "Your personalized dashboard of AI environmental suggestions. Track impact, apply actions, and grow a greener community — for residents, farmers, and local government.",
      },
      { property: "og:title", content: "Tailored AI Environmental Suggester — Dashboard" },
      {
        property: "og:description",
        content:
          "Personalized AI environmental suggestions and impact tracking for residents, farmers, and local government.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

type Audience = "residents" | "farmers" | "government";

type Category =
  | "Energy"
  | "Water"
  | "Waste"
  | "Land"
  | "Transport"
  | "Policy";

type Suggestion = {
  id: string;
  title: string;
  summary: string;
  category: Category;
  impact: number; // kg CO2e / year
  audience: Audience[];
  priority: "High" | "Medium" | "Rising";
  effort: "Low" | "Medium" | "High";
  applied?: boolean;
};

const AUDIENCES: { id: Audience; label: string; icon: typeof Leaf }[] = [
  { id: "residents", label: "Residents", icon: Leaf },
  { id: "farmers", label: "Farmers", icon: Sprout },
  { id: "government", label: "Government", icon: Building2 },
];

const CATEGORY_STYLE: Record<
  Category,
  { bg: string; text: string; icon: typeof Leaf; ring: string; tint: string }
> = {
  Energy: { bg: "bg-amber/25", text: "text-sun", icon: Sun, ring: "ring-amber/30", tint: "from-amber/10 via-card to-panel-2" },
  Water: { bg: "bg-sky/25", text: "text-ocean", icon: Droplets, ring: "ring-sky/30", tint: "from-sky/10 via-card to-panel-2" },
  Waste: { bg: "bg-leaf/25", text: "text-leaf", icon: Recycle, ring: "ring-leaf/30", tint: "from-leaf/10 via-card to-panel-2" },
  Land: { bg: "bg-emerald/25", text: "text-emerald", icon: TreePine, ring: "ring-emerald/30", tint: "from-emerald/10 via-card to-panel-2" },
  Transport: { bg: "bg-velvet/25", text: "text-velvet", icon: Car, ring: "ring-velvet/30", tint: "from-velvet/10 via-card to-panel-2" },
  Policy: { bg: "bg-ocean/25", text: "text-ocean", icon: LandPlot, ring: "ring-ocean/30", tint: "from-ocean/10 via-card to-panel-2" },
};

const PRIORITY_STYLE: Record<Suggestion["priority"], string> = {
  High: "bg-sun/15 text-sun",
  Medium: "bg-sky/15 text-ocean",
  Rising: "bg-velvet/15 text-velvet",
};

const INITIAL_SUGGESTIONS: Suggestion[] = [
  {
    id: "s1",
    title: "Switch to a cold-water laundry routine",
    summary:
      "Washing in cold water cuts up to 90% of the energy your machine uses per load — and extends garment life.",
    category: "Energy",
    impact: 240,
    audience: ["residents"],
    priority: "High",
    effort: "Low",
  },
  {
    id: "s2",
    title: "Plant winter cover crops on fallow fields",
    summary:
      "Rye and clover cover crops prevent erosion, fix nitrogen, and build soil organic matter over the off-season.",
    category: "Land",
    impact: 4200,
    audience: ["farmers"],
    priority: "High",
    effort: "Medium",
  },
  {
    id: "s3",
    title: "Launch a tree-canopy equity program",
    summary:
      "Target street-tree planting in the hottest, lowest-canopy neighborhoods to cut surface temps by up to 5°C.",
    category: "Policy",
    impact: 18000,
    audience: ["government"],
    priority: "High",
    effort: "High",
  },
  {
    id: "s4",
    title: "Retrofit drip irrigation on high-value beds",
    summary:
      "Drip delivers water to the root zone, cutting field water use 30–50% versus overhead sprinklers.",
    category: "Water",
    impact: 310,
    audience: ["farmers", "residents"],
    priority: "Medium",
    effort: "Medium",
  },
  {
    id: "s5",
    title: "Compost food scraps at home",
    summary:
      "A backyard bin diverts ~140 kg of organics from landfill each year and creates rich soil amendment.",
    category: "Waste",
    impact: 180,
    audience: ["residents"],
    priority: "Rising",
    effort: "Low",
  },
  {
    id: "s6",
    title: "Transition the municipal fleet to EVs",
    summary:
      "Replacing light-duty fleet vehicles with EVs pairs cleanly with on-site solar charging and cuts fuel O&M.",
    category: "Transport",
    impact: 9600,
    audience: ["government"],
    priority: "Medium",
    effort: "High",
  },
  {
    id: "s7",
    title: "Install bioswales along key corridors",
    summary:
      "Vegetated swales capture stormwater runoff, filter pollutants, and reduce flash-flood pressure on drains.",
    category: "Water",
    impact: 1200,
    audience: ["government", "residents"],
    priority: "Rising",
    effort: "Medium",
  },
  {
    id: "s8",
    title: "Agroforestry buffer strips along waterways",
    summary:
      "Planting native trees and shrubs at field edges intercepts nutrient runoff and diversifies farm income.",
    category: "Land",
    impact: 2600,
    audience: ["farmers"],
    priority: "Medium",
    effort: "Medium",
  },
];

const IMPACT_DATA = [
  { m: "Mar", co2: 42 },
  { m: "Apr", co2: 58 },
  { m: "May", co2: 71 },
  { m: "Jun", co2: 89 },
  { m: "Jul", co2: 104 },
  { m: "Aug", co2: 131 },
  { m: "Sep", co2: 158 },
];

const CONTRIBUTORS = [
  { name: "Riverside Co-op", value: "2,140 kg", icon: Sprout, tone: "leaf" },
  { name: "Maple District", value: "1,680 kg", icon: Building2, tone: "ocean" },
  { name: "Oak Street Block", value: "940 kg", icon: Leaf, tone: "sun" },
];

const QUICK_ACTIONS: { label: string; icon: typeof Leaf; tone: string }[] = [
  { label: "Plan a tree-planting day", icon: TreePine, tone: "leaf" },
  { label: "Audit home energy", icon: Sun, tone: "amber" },
  { label: "Start a rain barrel", icon: Droplets, tone: "sky" },
  { label: "Apply for a green grant", icon: ShieldCheck, tone: "velvet" },
];

function Index() {
  const [audience, setAudience] = useState<Audience | "all">("all");
  const [query, setQuery] = useState("");
  const [prompt, setPrompt] = useState("");
  const [suggestions, setSuggestions] = useState<Suggestion[]>(INITIAL_SUGGESTIONS);
  const [generating, setGenerating] = useState(false);

  const visible = useMemo(() => {
    return suggestions.filter((s) => {
      const matchAud =
        audience === "all" || s.audience.includes(audience);
      const matchQuery =
        query.trim() === "" ||
        (s.title + s.summary + s.category)
          .toLowerCase()
          .includes(query.toLowerCase());
      return matchAud && matchQuery;
    });
  }, [suggestions, audience, query]);

  const appliedCount = suggestions.filter((s) => s.applied).length;
  const totalImpact = suggestions
    .filter((s) => s.applied)
    .reduce((acc, s) => acc + s.impact, 0);

  function toggleApply(id: string) {
    setSuggestions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, applied: !s.applied } : s)),
    );
  }

  function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    if (prompt.trim() === "") return;
    setGenerating(true);
    const text = prompt.trim();
    setTimeout(() => {
      const generated: Suggestion = {
        id: `gen-${Date.now()}`,
        title: "AI-tailored action for your goal",
        summary: `Based on "${text}", Tailored AI Environmental Suggester matched a high-impact, low-effort action suited to your audience and region. Apply it to start tracking the savings.`,
        category: "Land",
        impact: 320,
        audience:
          audience === "all"
            ? ["residents", "farmers", "government"]
            : [audience],
        priority: "Rising",
        effort: "Low",
      };
      setSuggestions((prev) => [generated, ...prev]);
      setPrompt("");
      setGenerating(false);
    }, 700);
  }

  return (
    <div className="flex min-h-screen bg-app-mesh text-foreground">
      {/* Sidebar */}
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-border bg-gradient-to-b from-lime/12 via-card/70 to-ocean/12 backdrop-blur lg:flex">
        <div className="flex items-center gap-2.5 px-6 py-6">
          <div className="grid size-9 place-items-center rounded-xl bg-gradient-canopy text-white shadow-pop">
            <Leaf className="size-5" />
          </div>
          <div className="leading-tight">
            <p className="font-display text-base font-extrabold leading-tight tracking-tight text-gradient-aurora">Tailored AI Environmental Suggester</p>
            <p className="text-[11px] font-medium text-muted-foreground">
              Greener, together
            </p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3">
          <p className="px-3 pb-1 pt-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            Workspace
          </p>
          {[
            { label: "Dashboard", icon: Sparkles, active: true },
            { label: "Suggestions", icon: Target },
            { label: "Impact", icon: TrendingUp },
            { label: "Resources", icon: ShieldCheck },
            { label: "Community", icon: Award },
          ].map((item) => (
            <button
              key={item.label}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                item.active
                  ? "bg-leaf/12 text-leaf"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`}
            >
              <item.icon className="size-4.5" />
              {item.label}
            </button>
          ))}
        </nav>

        <div className="m-3 rounded-2xl bg-gradient-bloom p-4 text-white shadow-pop">
          <p className="font-display text-sm font-bold">Community rank</p>
          <p className="mt-0.5 text-2xl font-extrabold">Top 8%</p>
          <p className="text-xs text-white/80">of local districts</p>
          <div className="mt-3 h-2 w-full rounded-full bg-white/25">
            <div className="h-2 w-4/5 rounded-full bg-white" />
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Topbar */}
        <header className="sticky top-0 z-20 border-b border-border bg-gradient-to-r from-lime/15 via-background/80 to-sky/20 backdrop-blur">
          <div className="flex items-center gap-3 px-4 py-3 sm:px-6">
            <div className="flex items-center gap-2 lg:hidden">
              <div className="grid size-8 place-items-center rounded-lg bg-gradient-canopy text-white">
                <Leaf className="size-4.5" />
              </div>
              <span className="font-display text-sm font-extrabold leading-tight text-gradient-aurora">Tailored AI Environmental Suggester</span>
            </div>

            {/* Audience filter */}
            <div className="hidden items-center gap-1 rounded-full panel p-1 sm:flex">
              <button
                onClick={() => setAudience("all")}
                className={`rounded-full px-3 py-1.5 text-xs font-semibold transition-colors ${
                  audience === "all"
                    ? "bg-forest text-white"
                    : "text-panel-muted hover:text-card-foreground"
                }`}
              >
                Everyone
              </button>
              {AUDIENCES.map((a) => (
                <button
                  key={a.id}
                  onClick={() => setAudience(a.id)}
                  className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold transition-colors ${
                    audience === a.id
                      ? "bg-leaf text-white"
                      : "text-panel-muted hover:text-card-foreground"
                  }`}
                >
                  <a.icon className="size-3.5" />
                  {a.label}
                </button>
              ))}
            </div>

            {/* Search */}
            <div className="relative ml-auto hidden flex-1 max-w-sm md:block">
              <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-panel-muted" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search suggestions…"
                className="w-full panel rounded-full py-2 pl-9 pr-4 text-sm outline-none transition-shadow focus:ring-2 focus:ring-leaf/40"
              />
            </div>

            <button className="ml-auto grid size-9 place-items-center panel rounded-full text-panel-muted transition-colors hover:text-card-foreground md:ml-0">
              <Bell className="size-4.5" />
            </button>
            <div className="grid size-9 place-items-center rounded-full bg-gradient-ocean text-white font-semibold">
              AK
            </div>
          </div>

          {/* Mobile audience filter */}
          <div className="flex items-center gap-1 overflow-x-auto px-4 pb-3 sm:hidden">
            <button
              onClick={() => setAudience("all")}
              className={`shrink-0 rounded-full px-3 py-1.5 text-xs font-semibold ${
                audience === "all" ? "bg-forest text-white" : "panel text-panel-muted"
              }`}
            >
              Everyone
            </button>
            {AUDIENCES.map((a) => (
              <button
                key={a.id}
                onClick={() => setAudience(a.id)}
                className={`flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold ${
                  audience === a.id ? "bg-leaf text-white" : "panel text-panel-muted"
                }`}
              >
                <a.icon className="size-3.5" />
                {a.label}
              </button>
            ))}
          </div>
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 space-y-6 px-4 py-6 sm:px-6">
          {/* Home screen — bright farm scene with app title */}
          <section className="relative flex min-h-[22rem] items-center justify-center overflow-hidden rounded-3xl border border-border shadow-pop sm:min-h-[24rem]">
            <HomeScene />
            <div className="relative z-10 max-w-2xl px-6 text-center">
              <h1 className="font-display text-3xl font-extrabold leading-tight tracking-tight text-gradient-sunrise drop-shadow-[0_2px_10px_rgba(255,255,255,0.6)] sm:text-5xl">
                Tailored AI Environmental Suggester
              </h1>
            </div>
          </section>



          {/* Ask Verda — moved below the welcome screen */}
          <section className="panel rounded-3xl border border-border p-5 shadow-soft sm:p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-panel-muted sm:text-base">
                Tailored AI Environmental Suggester matched{" "}
                <span className="font-bold text-leaf">{visible.length}</span>{" "}
                actions to your goals. Apply one to grow this week's impact.
              </p>
            </div>
            <form
              onSubmit={handleAsk}
              className="mt-4 flex max-w-xl items-center gap-2 rounded-2xl border border-white/20 bg-white/95 p-2 shadow-pop backdrop-blur"
            >
              <Sparkles className="ml-2 size-5 shrink-0 text-leaf" />
              <input
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Ask Tailored AI Environmental Suggester for a tailored environmental action…"
                className="min-w-0 flex-1 bg-transparent px-1 text-sm text-foreground outline-none placeholder:text-muted-foreground"
              />
              <button
                type="submit"
                disabled={generating}
                className="flex shrink-0 items-center gap-1.5 rounded-xl bg-gradient-canopy px-4 py-2.5 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-60"
              >
                {generating ? (
                  <span className="size-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                ) : (
                  <>
                    Generate
                    <Send className="size-3.5" />
                  </>
                )}
              </button>
            </form>
          </section>

          {/* Stat cards */}
          <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard
              icon={TrendingUp}
              tone="leaf"
              label="CO₂e avoided"
              value={`${(totalImpact / 1000).toFixed(1)}t`}
              hint="this year"
            />
            <StatCard
              icon={Target}
              tone="sun"
              label="Actions applied"
              value={`${appliedCount}`}
              hint={`${suggestions.length} suggested`}
            />
            <StatCard
              icon={Flame}
              tone="velvet"
              label="Streak"
              value="12 days"
              hint="keep it growing"
            />
            <StatCard
              icon={Award}
              tone="ocean"
              label="Community rank"
              value="Top 8%"
              hint="of districts"
            />
          </section>

          {/* Feed + side */}
          <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Suggestion feed */}
            <div className="lg:col-span-2">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="font-display text-lg font-bold text-gradient-leaf">
                  Suggested actions
                </h2>
                <span className="text-xs font-medium text-muted-foreground">
                  {visible.length} match{visible.length === 1 ? "" : "es"}
                </span>
              </div>
              <div className="space-y-3">
                {visible.length === 0 && (
                  <div className="panel rounded-2xl border-dashed p-8 text-center text-sm text-panel-muted">
                    No suggestions for this filter. Try another audience or ask
                    Tailored AI Environmental Suggester above.
                  </div>
                )}
                {visible.map((s) => (
                  <SuggestionCard
                    key={s.id}
                    s={s}
                    onApply={() => toggleApply(s.id)}
                  />
                ))}
              </div>
            </div>

            {/* Side panel */}
            <div className="space-y-6">
              {/* Impact chart */}
              <div className="panel rounded-2xl p-5 shadow-soft">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-display text-base font-bold text-leaf">
                      Impact trend
                    </h3>
                    <p className="text-xs text-panel-muted">
                      CO₂e avoided per month
                    </p>
                  </div>
                  <span className="flex items-center gap-1 rounded-full bg-leaf/12 px-2.5 py-1 text-xs font-semibold text-leaf">
                    <ArrowUpRight className="size-3.5" />
                    +21%
                  </span>
                </div>
                <div className="mt-4 h-36">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={IMPACT_DATA}
                      margin={{ top: 4, right: 4, left: 4, bottom: 0 }}
                    >
                      <defs>
                        <linearGradient id="impactFill" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="oklch(0.70 0.18 150)" stopOpacity={0.5} />
                          <stop offset="100%" stopColor="oklch(0.70 0.18 150)" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <XAxis
                        dataKey="m"
                        tick={{ fontSize: 11, fill: "oklch(0.80 0.032 150)" }}
                        axisLine={false}
                        tickLine={false}
                      />
                      <Tooltip
                        cursor={false}
                        contentStyle={{
                          borderRadius: 12,
                          border: "1px solid oklch(0.40 0.055 165)",
                          background: "oklch(0.20 0.042 175)",
                          color: "oklch(0.97 0.012 95)",
                          fontSize: 12,
                        }}
                        formatter={(v: number) => [`${v} kg`, "CO₂e"]}
                      />
                      <Area
                        type="monotone"
                        dataKey="co2"
                        stroke="oklch(0.70 0.18 150)"
                        strokeWidth={2.5}
                        fill="url(#impactFill)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Contributors */}
              <div className="panel rounded-2xl p-5 shadow-soft">
                <h3 className="font-display text-base font-bold text-ocean">
                  Top contributors
                </h3>
                <div className="mt-3 space-y-2.5">
                  {CONTRIBUTORS.map((c) => (
                    <div
                      key={c.name}
                      className={`flex items-center gap-3 rounded-xl border border-${c.tone}/35 bg-${c.tone}/20 px-3 py-2.5`}
                    >
                      <div
                        className={`grid size-9 place-items-center rounded-lg bg-${c.tone}/25 text-${c.tone}`}
                      >
                        <c.icon className="size-4.5" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className={`truncate text-sm font-semibold text-${c.tone}`}>{c.name}</p>
                        <p className="text-xs text-panel-muted">
                          {c.value} avoided
                        </p>
                      </div>
                      <ChevronRight className="size-4 text-panel-muted" />
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick actions */}
              <div className="panel rounded-2xl p-5 shadow-soft">
                <h3 className="font-display text-base font-bold text-velvet">
                  Quick actions
                </h3>
                <div className="mt-3 grid grid-cols-2 gap-2.5">
                  {QUICK_ACTIONS.map((q) => (
                    <button
                      key={q.label}
                      className={`flex flex-col gap-2 rounded-xl border border-panel-border bg-${q.tone}/20 p-3 text-left transition-shadow hover:shadow-soft`}
                    >
                      <div
                        className={`grid size-8 place-items-center rounded-lg bg-${q.tone}/25 text-${q.tone}`}
                      >
                        <q.icon className="size-4" />
                      </div>
                      <span className="text-xs font-semibold leading-snug">
                        {q.label}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </section>

          <footer className="pb-4 pt-2 text-center text-xs text-muted-foreground">
            Tailored AI Environmental Suggester · AI environmental suggestions for residents, farmers & local
            government
          </footer>
        </main>
      </div>
    </div>
  );
}

function audienceLabel(a: Audience | "all") {
  if (a === "all") return "everyone";
  return AUDIENCES.find((x) => x.id === a)?.label.toLowerCase() ?? "you";
}

function StatCard({
  icon: Icon,
  tone,
  label,
  value,
  hint,
}: {
  icon: typeof Leaf;
  tone: "leaf" | "sun" | "velvet" | "ocean";
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <div className={`panel rounded-2xl border-${tone}/35 p-4 shadow-soft`}>
      <div className="flex items-center justify-between">
        <span
          className={`grid size-9 place-items-center rounded-xl bg-${tone}/25 text-${tone}`}
        >
          <Icon className="size-4.5" />
        </span>
        <ArrowUpRight className={`size-4 text-${tone}/70`} />
      </div>
      <p className={`mt-3 font-display text-2xl font-extrabold text-${tone}`}>{value}</p>
      <p className="text-sm font-semibold">{label}</p>
      <p className="text-xs text-panel-muted">{hint}</p>
    </div>
  );
}

function SuggestionCard({
  s,
  onApply,
}: {
  s: Suggestion;
  onApply: () => void;
}) {
  const cat = CATEGORY_STYLE[s.category];
  const CatIcon = cat.icon;
  return (
    <article
      className={`group rounded-2xl border panel p-4 shadow-soft transition-shadow hover:shadow-pop sm:p-5 ${
        s.applied ? "border-leaf/40" : "border-panel-border"
      }`}
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
        <div
          className={`grid size-11 shrink-0 place-items-center rounded-xl ${cat.bg} ${cat.text}`}
        >
          <CatIcon className="size-5" />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ${cat.bg} ${cat.text} ${cat.ring}`}
            >
              {s.category}
            </span>
            <span
              className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${PRIORITY_STYLE[s.priority]}`}
            >
              {s.priority}
            </span>
            <span className="text-[11px] font-medium text-panel-muted">
              Effort: {s.effort}
            </span>
          </div>

          <h3 className={`mt-2 font-display text-base font-bold leading-snug ${cat.text}`}>
            {s.title}
          </h3>
          <p className="mt-1 text-sm text-panel-muted">{s.summary}</p>

          <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs">
            <span className="flex items-center gap-1 font-semibold text-leaf">
              <TrendingUp className="size-3.5" />
              {s.impact.toLocaleString()} kg CO₂e/yr
            </span>
            <span className="flex items-center gap-1 text-panel-muted">
              {s.audience.map((a) => {
                const A = AUDIENCES.find((x) => x.id === a)!;
                return (
                  <span key={a} className="flex items-center gap-1">
                    <A.icon className="size-3.5" />
                    {A.label}
                  </span>
                );
              })}
            </span>
          </div>
        </div>

        <div className="flex shrink-0 items-center sm:flex-col">
          <button
            onClick={onApply}
            className={`flex w-full items-center justify-center gap-1.5 rounded-xl px-4 py-2.5 text-sm font-semibold transition-colors sm:w-auto ${
              s.applied
                ? "border border-leaf bg-leaf/10 text-leaf"
                : "bg-gradient-canopy text-white hover:opacity-90"
            }`}
          >
            {s.applied ? (
              <>
                <ShieldCheck className="size-4" />
                Applied
              </>
            ) : (
              <>
                Apply
                <ChevronRight className="size-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </article>
  );
}
