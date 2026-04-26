import { BookOpen, MessageSquare, Bot, PanelLeftClose, PanelLeftOpen, SlidersHorizontal, ChevronDown, ExternalLink, Trash2, Download, Check } from 'lucide-react';
import { useState, useEffect, useRef, useCallback } from 'react';

// ── Types ──────────────────────────────────────────────────────────────────────

const SpanishFlag = () => (
  <svg width="16" height="11" viewBox="0 0 3 2" style={{ borderRadius: '3px', display: 'block', flexShrink: 0, boxShadow: '0 0 0 1px oklch(0.16 0.010 58 / 0.12)' }}>
    <rect width="3" height="2" fill="#c60b1e" />
    <rect y="0.5" width="3" height="1" fill="#ffc400" />
  </svg>
);

const navItems = [
  { id: 'articles', label: 'Artículos', sublabel: 'Articles', icon: BookOpen },
  { id: 'tweets',   label: 'Tweets',    sublabel: 'Social',   icon: MessageSquare },
  { id: 'pau',      label: 'Pau',       sublabel: 'Tutor IA', icon: Bot },
];

interface Article {
  id: string;
  source: string;
  title: string;
  summary: string | null;
  url: string;
  published_at: string | null;
  fetched_at: string;
  image_url: string | null;
}

interface SavedPhrase {
  id: string;
  phrase: string;
  sentence: string;
  translation: string | null;
  definition: string | null;
  article_id: string | null;
  source: string | null;
  saved_at: string;
}

interface TooltipState {
  phrase: string;
  sentence: string;
  x: number;
  y: number;
  loading: boolean;
  definition: string;
  translation: string;
  articleId: string;
  source: string;
  saved: boolean;
}

// ── Constants ─────────────────────────────────────────────────────────────────

const SOURCE_META: Record<string, { label: string; color: string; bg: string }> = {
  marca:          { label: 'Marca',         color: 'oklch(0.40 0.010 58)', bg: 'oklch(0.93 0.008 68)' },
  as:             { label: 'AS',            color: 'oklch(0.40 0.010 58)', bg: 'oklch(0.93 0.008 68)' },
  sport:          { label: 'Sport',         color: 'oklch(0.45 0.100 42)', bg: 'oklch(0.91 0.045 44)' },
  mundodeportivo: { label: 'Mundo Dep.',    color: 'oklch(0.45 0.100 42)', bg: 'oklch(0.91 0.045 44)' },
  lavanguardia:   { label: 'La Vanguardia', color: 'oklch(0.40 0.010 58)', bg: 'oklch(0.93 0.008 68)' },
  elpais:         { label: 'El País',       color: 'oklch(0.40 0.010 58)', bg: 'oklch(0.93 0.008 68)' },
};

const FOOTBALL_KW = [
  'fútbol', 'futbol', 'laliga', 'la liga', 'champions', 'gol', 'golazo', 'partido',
  'barça', 'barca', 'barcelona', 'real madrid', 'atlético', 'atletico', 'villarreal',
  'sevilla', 'valencia', 'betis', 'athletic', 'sociedad', 'osasuna', 'girona',
  'espanyol', 'getafe', 'celta', 'rayo vallecano', 'mallorca', 'premier league',
  'bundesliga', 'serie a', 'ligue 1', 'mundial', 'eurocopa', 'selección', 'portero',
  'delantero', 'centrocampista', 'goleador', 'remate', 'penalti', 'offside',
];

function isFootball(a: Article): boolean {
  const text = `${a.title} ${a.summary ?? ''}`.toLowerCase();
  return FOOTBALL_KW.some(kw => text.includes(kw));
}

function timeAgo(dateStr: string): string {
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
  if (diff < 3600) return `hace ${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)}h`;
  return `hace ${Math.floor(diff / 86400)}d`;
}

const EASE = 'cubic-bezier(0.16, 1, 0.3, 1)';
const WIDTH_DURATION = '0.3s';

// ── Sidebar ───────────────────────────────────────────────────────────────────

const Sidebar = ({
  activeTab, setActiveTab, collapsed, setCollapsed,
}: {
  activeTab: string;
  setActiveTab: (id: string) => void;
  collapsed: boolean;
  setCollapsed: (v: boolean) => void;
}) => {
  const textTransition = collapsed
    ? `opacity 0.08s ease 0s, max-width ${WIDTH_DURATION} ${EASE}`
    : `opacity 0.15s ease 0.18s, max-width ${WIDTH_DURATION} ${EASE}`;

  return (
    <aside
      className="flex-shrink-0 bg-sidebar flex flex-col overflow-hidden"
      style={{ width: collapsed ? '76px' : '375px', borderRight: '1px solid oklch(0.89 0.018 68)', transition: `width ${WIDTH_DURATION} ${EASE}` }}
    >
      <div className="animate-fade-in flex-shrink-0" style={{ padding: collapsed ? '54px 0 48px' : '54px 44px 48px', transition: `padding ${WIDTH_DURATION} ${EASE}`, animationDelay: '0ms' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: collapsed ? 'center' : 'flex-start' }}>
          <div className="bg-accent flex-shrink-0" style={{ width: '27px', height: '27px', borderRadius: '6px', transform: 'rotate(12deg)' }} />
          <h1 className="font-sans text-ink" style={{ fontSize: '33px', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1, whiteSpace: 'nowrap', overflow: 'hidden', opacity: collapsed ? 0 : 1, maxWidth: collapsed ? 0 : '260px', marginLeft: collapsed ? 0 : '16px', transition: textTransition }}>
            Mes Que Un AI
          </h1>
        </div>
      </div>

      <nav className="flex-1" style={{ padding: collapsed ? '0 6px 22px' : '0 22px 22px', transition: `padding ${WIDTH_DURATION} ${EASE}` }}>
        <p className="text-ink-faint uppercase" style={{ fontSize: '12px', fontWeight: 700, letterSpacing: '0.18em', padding: collapsed ? '0 0 18px' : '0 22px 18px', opacity: collapsed ? 0 : 1, maxWidth: collapsed ? 0 : '260px', overflow: 'hidden', whiteSpace: 'nowrap', transition: `${textTransition}, padding ${WIDTH_DURATION} ${EASE}` }}>
          Modos
        </p>
        <ul style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item, i) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <li key={item.id} className="animate-fade-in-up" style={{ animationDelay: `${120 + i * 55}ms` }}>
                <button
                  onClick={() => setActiveTab(item.id)}
                  className="w-full text-left rounded-xl"
                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-start', padding: collapsed ? '15px 23px' : '15px 22px', background: isActive ? 'oklch(0.91 0.045 44)' : 'transparent', transition: 'background 0.2s ease' }}
                  onMouseEnter={e => { if (!isActive) (e.currentTarget as HTMLButtonElement).style.background = 'oklch(0.92 0.014 72 / 0.7)'; }}
                  onMouseLeave={e => { if (!isActive) (e.currentTarget as HTMLButtonElement).style.background = 'transparent'; }}
                >
                  <Icon size={20} style={{ flexShrink: 0, color: 'oklch(0.16 0.010 58)' }} />
                  <div style={{ overflow: 'hidden', opacity: collapsed ? 0 : 1, maxWidth: collapsed ? 0 : '220px', marginLeft: collapsed ? 0 : '14px', whiteSpace: 'nowrap', transition: textTransition }}>
                    <span className="block leading-tight" style={{ fontSize: '16px', fontWeight: isActive ? 700 : 500, color: 'oklch(0.16 0.010 58)', letterSpacing: '-0.01em' }}>{item.label}</span>
                    <span className="block leading-tight" style={{ fontSize: '13px', fontWeight: 500, color: isActive ? 'oklch(0.42 0.020 55)' : 'oklch(0.65 0.014 60)', letterSpacing: '0.01em', marginTop: '4px' }}>{item.sublabel}</span>
                  </div>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="animate-fade-in flex-shrink-0 flex items-center" style={{ borderTop: '1px solid oklch(0.89 0.018 68)', padding: collapsed ? '36px 0' : '36px 20px', justifyContent: collapsed ? 'center' : 'space-between', transition: `padding ${WIDTH_DURATION} ${EASE}`, animationDelay: '400ms' }}>
        <span style={{ flexShrink: 0, opacity: collapsed ? 0 : 1, maxWidth: collapsed ? 0 : '16px', overflow: 'hidden', display: 'flex', transition: textTransition }}><SpanishFlag /></span>
        <p className="text-ink-faint uppercase" style={{ fontSize: '10.5px', fontWeight: 600, letterSpacing: '0.14em', textAlign: 'center', flex: collapsed ? '0 0 0px' : 1, opacity: collapsed ? 0 : 1, overflow: 'hidden', whiteSpace: 'nowrap', transition: textTransition }}>
          A language learning app
        </p>
        <button onClick={() => setCollapsed(!collapsed)} className="text-ink-faint hover:text-ink transition-colors duration-150 flex-shrink-0" style={{ padding: '28px', margin: '-28px' }} title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
          {collapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
        </button>
      </div>
    </aside>
  );
};

// ── App ───────────────────────────────────────────────────────────────────────

export default function App() {
  const [activeTab, setActiveTab] = useState('articles');
  const [collapsed, setCollapsed] = useState(false);

  // Articles
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [articleContent, setArticleContent] = useState<Record<string, string | 'loading' | 'error'>>({});
  const [narratives, setNarratives] = useState<Record<string, string | 'loading' | 'error'>>({});
  const [articleFontSize, setArticleFontSize] = useState<number>(() => {
    const s = localStorage.getItem('article-font-size');
    return s ? parseInt(s, 10) : 17;
  });

  // Filters
  const [filterSource, setFilterSource] = useState<string | null>('elpais');
  const [showFilter, setShowFilter] = useState(false);
  const filterRef = useRef<HTMLDivElement>(null);

  // Lookup tooltip
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  // Deck (Pau tab)
  const [deck, setDeck] = useState<SavedPhrase[]>([]);
  const [deckLoading, setDeckLoading] = useState(false);

  // ── Effects ──

  useEffect(() => {
    if (activeTab !== 'articles') return;
    setLoading(true);
    fetch('/api/articles')
      .then(r => r.json())
      .then((data: Article[]) => setArticles(data))
      .catch(() => setArticles([]))
      .finally(() => setLoading(false));
  }, [activeTab]);

  const fetchDeck = useCallback(() => {
    setDeckLoading(true);
    fetch('/api/deck')
      .then(r => r.json())
      .then(setDeck)
      .catch(() => setDeck([]))
      .finally(() => setDeckLoading(false));
  }, []);

  useEffect(() => {
    if (activeTab === 'pau') fetchDeck();
  }, [activeTab, fetchDeck]);

  useEffect(() => {
    if (!showFilter) return;
    const h = (e: MouseEvent) => { if (!filterRef.current?.contains(e.target as Node)) setShowFilter(false); };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, [showFilter]);

  useEffect(() => {
    if (!tooltip) return;
    const h = (e: MouseEvent) => { if (!tooltipRef.current?.contains(e.target as Node)) setTooltip(null); };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, [tooltip]);

  // ── Handlers ──

  const adjustFontSize = (delta: number) => {
    setArticleFontSize(prev => {
      const next = Math.max(14, Math.min(26, prev + delta));
      localStorage.setItem('article-font-size', String(next));
      return next;
    });
  };

  const handleExpand = (articleId: string) => {
    const next = expandedId === articleId ? null : articleId;
    setExpandedId(next);
    if (!next) return;

    if (!articleContent[next]) {
      setArticleContent(c => ({ ...c, [next]: 'loading' }));
      fetch(`/api/articles/${next}/content`)
        .then(r => r.json())
        .then(d => setArticleContent(c => ({ ...c, [next]: d.content || 'No se pudo cargar el artículo.' })))
        .catch(() => setArticleContent(c => ({ ...c, [next]: 'error' })));
    }

    if (!narratives[next]) {
      setNarratives(n => ({ ...n, [next]: 'loading' }));
      fetch(`/api/articles/${next}/narrative`, { method: 'POST' })
        .then(r => r.json())
        .then(d => setNarratives(n => ({ ...n, [next]: d.narrative || 'error' })))
        .catch(() => setNarratives(n => ({ ...n, [next]: 'error' })));
    }
  };

  const handleTextSelect = useCallback((e: React.MouseEvent, article: Article) => {
    setTimeout(() => {
      const selection = window.getSelection();
      const phrase = selection?.toString().trim() ?? '';
      if (phrase.length < 2) return;
      const sentence = selection?.anchorNode?.textContent?.trim() ?? '';
      const range = selection?.getRangeAt(0);
      const rect = range?.getBoundingClientRect();
      if (!rect || rect.width === 0) return;

      const x = Math.max(160, Math.min(rect.left + rect.width / 2, window.innerWidth - 160));
      const above = rect.top > 200;

      setTooltip({ phrase, sentence, x, y: above ? rect.top : rect.bottom, loading: true, definition: '', translation: '', articleId: article.id, source: article.source, saved: false });

      fetch('/api/lookup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phrase, sentence }),
      })
        .then(async r => { if (!r.ok) throw new Error(); return r.json(); })
        .then(d => setTooltip(t => t ? { ...t, loading: false, definition: d.definition || 'Sin definición.', translation: d.translation || '' } : null))
        .catch(() => setTooltip(t => t ? { ...t, loading: false, definition: 'No se pudo obtener la definición.', translation: '' } : null));
    }, 10);
  }, []);

  const handleSave = async () => {
    if (!tooltip) return;
    await fetch('/api/deck', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phrase: tooltip.phrase, sentence: tooltip.sentence, translation: tooltip.translation, definition: tooltip.definition, article_id: tooltip.articleId, source: tooltip.source }),
    });
    setTooltip(t => t ? { ...t, saved: true } : null);
    setTimeout(() => setTooltip(null), 800);
  };

  const handleDeletePhrase = async (id: string) => {
    await fetch(`/api/deck/${id}`, { method: 'DELETE' });
    setDeck(d => d.filter(p => p.id !== id));
  };

  // ── Derived ──

  const availableSources = [...new Set(articles.map(a => a.source))];
  const displayedArticles = articles.filter(a => !filterSource || a.source === filterSource).filter(isFootball);

  // ── Render ──

  return (
    <div className="min-h-screen bg-cream flex items-center justify-center p-4 md:p-8 lg:p-12">
      <div className="w-full flex overflow-hidden" style={{ maxWidth: '1280px', height: '90vh', background: 'oklch(0.992 0.004 72)', borderRadius: '28px', boxShadow: '0 48px 96px -24px oklch(0.16 0.010 58 / 0.17), 0 4px 12px oklch(0.16 0.010 58 / 0.08)', border: '1px solid oklch(0.89 0.018 68 / 0.7)' }}>
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} collapsed={collapsed} setCollapsed={setCollapsed} />

        <main className="flex-1 bg-surface flex flex-col overflow-hidden">

          {/* Header */}
          <header className="flex-shrink-0 flex items-center justify-between" style={{ padding: '54px 48px 42px' }}>
            <h2 className="font-sans text-ink" style={{ fontSize: '33px', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1 }}>
              {navItems.find(n => n.id === activeTab)?.label}
            </h2>

            {activeTab === 'articles' && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {/* Font size */}
                <div style={{ display: 'flex', alignItems: 'center', border: '1px solid oklch(0.89 0.018 68)', borderRadius: '10px', overflow: 'hidden' }}>
                  <button onClick={() => adjustFontSize(-1)} className="text-ink-faint hover:text-ink transition-colors duration-150" style={{ padding: '7px 11px', fontSize: '12px', fontWeight: 600, fontFamily: 'var(--font-serif)', background: 'transparent', cursor: 'pointer', lineHeight: 1 }} onMouseEnter={e => (e.currentTarget as HTMLButtonElement).style.background = 'oklch(0.93 0.008 68)'} onMouseLeave={e => (e.currentTarget as HTMLButtonElement).style.background = 'transparent'}>A−</button>
                  <div style={{ width: '1px', alignSelf: 'stretch', background: 'oklch(0.89 0.018 68)', flexShrink: 0 }} />
                  <button onClick={() => adjustFontSize(1)} className="text-ink-faint hover:text-ink transition-colors duration-150" style={{ padding: '7px 11px', fontSize: '15px', fontWeight: 600, fontFamily: 'var(--font-serif)', background: 'transparent', cursor: 'pointer', lineHeight: 1 }} onMouseEnter={e => (e.currentTarget as HTMLButtonElement).style.background = 'oklch(0.93 0.008 68)'} onMouseLeave={e => (e.currentTarget as HTMLButtonElement).style.background = 'transparent'}>A+</button>
                </div>

                {/* Source filter */}
                <div ref={filterRef} style={{ position: 'relative' }}>
                  <button onClick={() => setShowFilter(f => !f)} className="flex items-center gap-2 transition-colors duration-150" style={{ padding: '7px 12px', borderRadius: '10px', border: '1px solid oklch(0.89 0.018 68)', background: filterSource ? 'oklch(0.91 0.045 44)' : 'transparent', color: filterSource ? 'oklch(0.45 0.100 42)' : 'oklch(0.65 0.014 60)', cursor: 'pointer' }} onMouseEnter={e => { if (!filterSource) (e.currentTarget as HTMLButtonElement).style.background = 'oklch(0.93 0.008 68)'; }} onMouseLeave={e => { if (!filterSource) (e.currentTarget as HTMLButtonElement).style.background = 'transparent'; }}>
                    <SlidersHorizontal size={14} />
                  </button>
                  {showFilter && (
                    <div style={{ position: 'absolute', top: 'calc(100% + 8px)', right: 0, background: 'oklch(0.992 0.004 72)', border: '1px solid oklch(0.89 0.018 68)', borderRadius: '14px', padding: '6px', boxShadow: '0 8px 28px oklch(0.16 0.010 58 / 0.12)', zIndex: 20, minWidth: '168px' }}>
                      {([null, ...availableSources] as (string | null)[]).map(src => {
                        const isSelected = filterSource === src;
                        return (
                          <button key={src ?? '__all__'} onClick={() => { setFilterSource(src); setShowFilter(false); }} style={{ display: 'block', width: '100%', textAlign: 'left', padding: '9px 12px', borderRadius: '8px', fontSize: '14px', fontWeight: isSelected ? 600 : 500, color: isSelected ? 'oklch(0.45 0.100 42)' : 'oklch(0.16 0.010 58)', background: isSelected ? 'oklch(0.91 0.045 44)' : 'transparent', cursor: 'pointer', transition: 'background 0.15s ease' }} onMouseEnter={e => { if (!isSelected) (e.currentTarget as HTMLButtonElement).style.background = 'oklch(0.93 0.008 68)'; }} onMouseLeave={e => { if (!isSelected) (e.currentTarget as HTMLButtonElement).style.background = 'transparent'; }}>
                            {src === null ? 'Todas las fuentes' : (SOURCE_META[src]?.label ?? src)}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            )}
          </header>

          {/* ── Articles tab ── */}
          {activeTab === 'articles' && (
            <div className="flex-1 overflow-y-auto" style={{ padding: '0 48px 48px' }}>
              {loading ? (
                <p className="text-ink-faint" style={{ fontSize: '15px' }}>Cargando artículos…</p>
              ) : displayedArticles.length === 0 ? (
                <p className="text-ink-faint" style={{ fontSize: '15px' }}>{filterSource ? 'No hay artículos de esta fuente.' : 'No hay artículos. ¿Está corriendo el backend?'}</p>
              ) : (
                <div>
                  {displayedArticles.map((a, i) => {
                    const meta = SOURCE_META[a.source] ?? { label: a.source, color: 'oklch(0.40 0.010 58)', bg: 'oklch(0.93 0.008 68)' };
                    const dateStr = a.published_at ?? a.fetched_at;
                    const isExpanded = expandedId === a.id;
                    const contentIndent = a.image_url ? '88px' : '0';

                    return (
                      <article key={a.id} style={{ padding: '24px 0', borderTop: i > 0 ? '1px solid oklch(0.89 0.018 68)' : 'none' }}>

                        {/* Card header row */}
                        <button onClick={() => handleExpand(a.id)} style={{ width: '100%', textAlign: 'left', display: 'flex', gap: '16px', alignItems: 'flex-start', cursor: 'pointer', background: 'none', border: 'none', padding: 0 }}>
                          {a.image_url && <img src={a.image_url} alt="" style={{ width: '72px', height: '72px', objectFit: 'cover', borderRadius: '8px', flexShrink: 0, marginTop: '14px' }} />}
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <span style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '0.04em', padding: '3px 8px', borderRadius: '6px', color: meta.color, background: meta.bg }}>{meta.label}</span>
                                <span className="text-ink-faint" style={{ fontSize: '13px', fontWeight: 500 }}>{timeAgo(dateStr)}</span>
                              </div>
                              <ChevronDown size={16} className="text-ink-faint flex-shrink-0" style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.25s ease' }} />
                            </div>
                            <h3 className="font-sans text-ink" style={{ fontSize: '19px', fontWeight: 700, letterSpacing: '-0.02em', lineHeight: 1.25, marginBottom: a.summary ? '6px' : 0 }}>{a.title}</h3>
                            {a.summary && <p className="font-serif text-ink-faint" style={{ fontSize: '13px', lineHeight: 1.5, overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>{a.summary}</p>}
                          </div>
                        </button>

                        {/* Expanded content */}
                        {isExpanded && (
                          <div style={{ marginTop: '16px', paddingLeft: contentIndent }}>

                            {/* TPRS Narrative */}
                            {(() => {
                              const ns = narratives[a.id];
                              if (!ns || ns === 'error') return null;
                              return (
                                <div style={{ background: 'oklch(0.965 0.008 68)', borderRadius: '12px', padding: '20px 24px', marginBottom: '28px' }}>
                                  <span style={{ fontSize: '10px', fontWeight: 700, letterSpacing: '0.14em', textTransform: 'uppercase', color: 'oklch(0.58 0.135 42)', display: 'block', marginBottom: '12px' }}>
                                    Lectura fácil
                                  </span>
                                  {ns === 'loading' ? (
                                    <p className="text-ink-faint" style={{ fontSize: '15px' }}>Generando…</p>
                                  ) : (
                                    <p className="font-serif" style={{ fontSize: `${articleFontSize}px`, lineHeight: 1.75, color: 'oklch(0.26 0.010 58)' }}>{ns}</p>
                                  )}
                                </div>
                              );
                            })()}

                            {/* Full article text — selectable */}
                            <div onMouseUp={e => handleTextSelect(e, a)}>
                              {(() => {
                                const state = articleContent[a.id];
                                if (state === 'loading') return <p className="text-ink-faint" style={{ fontSize: '14px', marginBottom: '20px' }}>Cargando artículo…</p>;
                                if (state === 'error') return <p className="text-ink-faint" style={{ fontSize: '14px', marginBottom: '20px' }}>No se pudo cargar el contenido.</p>;
                                if (typeof state === 'string') {
                                  return state.split('\n\n').filter(p => p.trim()).map((para, pi) => (
                                    <p key={pi} className="font-serif text-ink-secondary" style={{ fontSize: `${articleFontSize}px`, lineHeight: 1.75, marginBottom: '16px' }}>{para}</p>
                                  ));
                                }
                                return null;
                              })()}
                            </div>

                            <a href={a.url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 hover:text-ink transition-colors duration-150" style={{ fontSize: '13px', fontWeight: 600, color: 'oklch(0.58 0.135 42)', marginTop: '6px', display: 'inline-flex' }}>
                              Leer en {meta.label}<ExternalLink size={12} />
                            </a>
                          </div>
                        )}
                      </article>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* ── Pau tab (deck) ── */}
          {activeTab === 'pau' && (
            <div className="flex-1 overflow-y-auto" style={{ padding: '0 48px 48px' }}>
              {deckLoading ? (
                <p className="text-ink-faint" style={{ fontSize: '15px' }}>Cargando mazo…</p>
              ) : deck.length === 0 ? (
                <div>
                  <p className="text-ink-faint font-serif" style={{ fontSize: '16px', lineHeight: 1.7, maxWidth: '480px' }}>
                    Tu mazo está vacío. Selecciona cualquier palabra o frase mientras lees un artículo y guárdala aquí.
                  </p>
                </div>
              ) : (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '28px' }}>
                    <a href="/api/deck/export" download="deck.csv" className="inline-flex items-center gap-2 text-ink-faint hover:text-ink transition-colors duration-150" style={{ fontSize: '13px', fontWeight: 600 }}>
                      <Download size={13} />Exportar para Anki
                    </a>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                    {deck.map((p, i) => (
                      <div key={p.id} style={{ padding: '20px 0', borderTop: i > 0 ? '1px solid oklch(0.89 0.018 68)' : 'none' }}>
                        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px' }}>
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                              <span className="font-sans text-ink" style={{ fontSize: '20px', fontWeight: 700, letterSpacing: '-0.02em' }}>{p.phrase}</span>
                              {p.source && <span style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '0.04em', padding: '3px 8px', borderRadius: '6px', color: SOURCE_META[p.source]?.color ?? 'oklch(0.40 0.010 58)', background: SOURCE_META[p.source]?.bg ?? 'oklch(0.93 0.008 68)' }}>{SOURCE_META[p.source]?.label ?? p.source}</span>}
                            </div>
                            {p.translation && <p style={{ fontSize: '15px', fontWeight: 600, color: 'oklch(0.58 0.135 42)', marginBottom: '4px' }}>{p.translation}</p>}
                            {p.definition && <p className="font-serif text-ink-secondary" style={{ fontSize: '14px', lineHeight: 1.6, marginBottom: '8px' }}>{p.definition}</p>}
                            <p className="font-serif text-ink-faint" style={{ fontSize: '13px', lineHeight: 1.5, fontStyle: 'italic' }}>"{p.sentence}"</p>
                          </div>
                          <button onClick={() => handleDeletePhrase(p.id)} className="text-ink-faint hover:text-ink transition-colors duration-150 flex-shrink-0" style={{ padding: '4px', marginTop: '4px', cursor: 'pointer', background: 'none', border: 'none' }}>
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

        </main>
      </div>

      {/* Lookup tooltip — fixed overlay */}
      {tooltip && (
        <div
          ref={tooltipRef}
          style={{
            position: 'fixed',
            left: tooltip.x,
            top: tooltip.y > 200 ? tooltip.y - 8 : tooltip.y + 8,
            transform: tooltip.y > 200 ? 'translate(-50%, -100%)' : 'translate(-50%, 0)',
            background: 'oklch(0.14 0.010 58)',
            color: 'oklch(0.96 0.004 72)',
            borderRadius: '14px',
            padding: '16px 18px',
            width: '300px',
            boxShadow: '0 12px 40px oklch(0.16 0.010 58 / 0.35)',
            zIndex: 50,
          }}
        >
          <p className="font-sans" style={{ fontWeight: 700, fontSize: '15px', marginBottom: '10px', color: 'oklch(0.96 0.004 72)' }}>{tooltip.phrase}</p>
          {tooltip.loading ? (
            <p style={{ fontSize: '13px', color: 'oklch(0.65 0.014 60)' }}>Buscando…</p>
          ) : (
            <>
              {tooltip.definition && <p className="font-serif" style={{ fontSize: '14px', lineHeight: 1.6, color: 'oklch(0.85 0.008 68)', marginBottom: '8px' }}>{tooltip.definition}</p>}
              {tooltip.translation && <p style={{ fontSize: '13px', color: 'oklch(0.58 0.135 42)', fontWeight: 600, marginBottom: '14px' }}>{tooltip.translation}</p>}
              <button
                onClick={handleSave}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '7px 14px',
                  borderRadius: '8px',
                  background: tooltip.saved ? 'oklch(0.45 0.12 145)' : 'oklch(0.58 0.135 42)',
                  color: 'white',
                  fontSize: '13px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: 'none',
                  transition: 'background 0.2s ease',
                }}
              >
                {tooltip.saved ? <><Check size={12} />Guardado</> : 'Guardar'}
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
