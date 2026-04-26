import { BookOpen, MessageSquare, Bot, PanelLeftClose, PanelLeftOpen, ExternalLink } from 'lucide-react';
import { useState, useEffect } from 'react';

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
}

const SOURCE_META: Record<string, { label: string; color: string; bg: string }> = {
  marca:          { label: 'Marca',         color: 'oklch(0.40 0.010 58)', bg: 'oklch(0.93 0.008 68)' },
  as:             { label: 'AS',            color: 'oklch(0.40 0.010 58)', bg: 'oklch(0.93 0.008 68)' },
  sport:          { label: 'Sport',         color: 'oklch(0.45 0.100 42)', bg: 'oklch(0.91 0.045 44)' },
  mundodeportivo: { label: 'Mundo Dep.',    color: 'oklch(0.45 0.100 42)', bg: 'oklch(0.91 0.045 44)' },
  lavanguardia:   { label: 'La Vanguardia', color: 'oklch(0.40 0.010 58)', bg: 'oklch(0.93 0.008 68)' },
  elpais:         { label: 'El País',       color: 'oklch(0.40 0.010 58)', bg: 'oklch(0.93 0.008 68)' },
};

function timeAgo(dateStr: string): string {
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
  if (diff < 3600) return `hace ${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)}h`;
  return `hace ${Math.floor(diff / 86400)}d`;
}

const EASE = 'cubic-bezier(0.16, 1, 0.3, 1)';
const WIDTH_DURATION = '0.3s';

const Sidebar = ({
  activeTab,
  setActiveTab,
  collapsed,
  setCollapsed,
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
      style={{
        width: collapsed ? '76px' : '375px',
        borderRight: '1px solid oklch(0.89 0.018 68)',
        transition: `width ${WIDTH_DURATION} ${EASE}`,
      }}
    >
      {/* Wordmark */}
      <div
        className="animate-fade-in flex-shrink-0"
        style={{
          padding: collapsed ? '54px 0 48px' : '54px 44px 48px',
          transition: `padding ${WIDTH_DURATION} ${EASE}`,
          animationDelay: '0ms',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div
            className="bg-accent flex-shrink-0"
            style={{
              width: '27px',
              height: '27px',
              borderRadius: '6px',
              transform: 'rotate(12deg)',
            }}
          />
          <h1
            className="font-sans text-ink"
            style={{
              fontSize: '33px',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              lineHeight: 1,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              opacity: collapsed ? 0 : 1,
              maxWidth: collapsed ? 0 : '260px',
              marginLeft: collapsed ? 0 : '16px',
              transition: textTransition,
            }}
          >
            Mes Que Un AI
          </h1>
        </div>
      </div>

      {/* Navigation */}
      <nav
        className="flex-1"
        style={{
          padding: collapsed ? '0 6px 22px' : '0 22px 22px',
          transition: `padding ${WIDTH_DURATION} ${EASE}`,
        }}
      >
        <p
          className="text-ink-faint uppercase"
          style={{
            fontSize: '12px',
            fontWeight: 700,
            letterSpacing: '0.18em',
            padding: collapsed ? '0 0 18px' : '0 22px 18px',
            opacity: collapsed ? 0 : 1,
            maxWidth: collapsed ? 0 : '260px',
            overflow: 'hidden',
            whiteSpace: 'nowrap',
            transition: `${textTransition}, padding ${WIDTH_DURATION} ${EASE}`,
          }}
        >
          Modos
        </p>
        <ul style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item, i) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <li
                key={item.id}
                className="animate-fade-in-up"
                style={{ animationDelay: `${120 + i * 55}ms` }}
              >
                <button
                  onClick={() => setActiveTab(item.id)}
                  className="w-full text-left rounded-xl"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'flex-start',
                    padding: collapsed ? '15px 23px' : '15px 22px',
                    background: isActive ? 'oklch(0.91 0.045 44)' : 'transparent',
                    transition: `background 0.2s ease`,
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive)
                      (e.currentTarget as HTMLButtonElement).style.background =
                        'oklch(0.92 0.014 72 / 0.7)';
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive)
                      (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
                  }}
                >
                  <Icon
                    size={20}
                    style={{
                      flexShrink: 0,
                      color: 'oklch(0.16 0.010 58)',
                    }}
                  />
                  <div
                    style={{
                      overflow: 'hidden',
                      opacity: collapsed ? 0 : 1,
                      maxWidth: collapsed ? 0 : '220px',
                      marginLeft: collapsed ? 0 : '14px',
                      whiteSpace: 'nowrap',
                      transition: textTransition,
                    }}
                  >
                    <span
                      className="block leading-tight"
                      style={{
                        fontSize: '16px',
                        fontWeight: isActive ? 700 : 500,
                        color: 'oklch(0.16 0.010 58)',
                        letterSpacing: '-0.01em',
                      }}
                    >
                      {item.label}
                    </span>
                    <span
                      className="block leading-tight"
                      style={{
                        fontSize: '13px',
                        fontWeight: 500,
                        color: isActive ? 'oklch(0.42 0.020 55)' : 'oklch(0.65 0.014 60)',
                        letterSpacing: '0.01em',
                        marginTop: '4px',
                      }}
                    >
                      {item.sublabel}
                    </span>
                  </div>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div
        className="animate-fade-in flex-shrink-0 flex items-center"
        style={{
          borderTop: '1px solid oklch(0.89 0.018 68)',
          padding: collapsed ? '36px 0' : '36px 20px',
          justifyContent: collapsed ? 'center' : 'space-between',
          transition: `padding ${WIDTH_DURATION} ${EASE}`,
          animationDelay: '400ms',
        }}
      >
        {/* Flag */}
        <span
          style={{
            flexShrink: 0,
            opacity: collapsed ? 0 : 1,
            maxWidth: collapsed ? 0 : '16px',
            overflow: 'hidden',
            display: 'flex',
            transition: textTransition,
          }}
        >
          <SpanishFlag />
        </span>

        {/* Label */}
        <p
          className="text-ink-faint uppercase"
          style={{
            fontSize: '10.5px',
            fontWeight: 600,
            letterSpacing: '0.14em',
            textAlign: 'center',
            flex: collapsed ? '0 0 0px' : 1,
            opacity: collapsed ? 0 : 1,
            overflow: 'hidden',
            whiteSpace: 'nowrap',
            transition: textTransition,
          }}
        >
          A language learning app
        </p>

        {/* Collapse button */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-ink-faint hover:text-ink transition-colors duration-150 flex-shrink-0"
          style={{
            padding: '28px',
            margin: '-28px',
          }}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed
            ? <PanelLeftOpen size={16} />
            : <PanelLeftClose size={16} />
          }
        </button>
      </div>
    </aside>
  );
};

export default function App() {
  const [activeTab, setActiveTab] = useState('articles');
  const [collapsed, setCollapsed] = useState(false);
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTab !== 'articles') return;
    setLoading(true);
    fetch('/api/articles')
      .then(r => r.json())
      .then((data: Article[]) => setArticles(data))
      .catch(() => setArticles([]))
      .finally(() => setLoading(false));
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-cream flex items-center justify-center p-4 md:p-8 lg:p-12">
      <div
        className="w-full flex overflow-hidden"
        style={{
          maxWidth: '1280px',
          height: '90vh',
          background: 'oklch(0.992 0.004 72)',
          borderRadius: '28px',
          boxShadow:
            '0 48px 96px -24px oklch(0.16 0.010 58 / 0.17), 0 4px 12px oklch(0.16 0.010 58 / 0.08)',
          border: '1px solid oklch(0.89 0.018 68 / 0.7)',
        }}
      >
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          collapsed={collapsed}
          setCollapsed={setCollapsed}
        />
        <main className="flex-1 bg-surface flex flex-col">
          <header
            className="flex-shrink-0"
            style={{
              padding: '54px 48px 48px',
            }}
          >
            <h2
              className="font-sans text-ink"
              style={{ fontSize: '33px', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1 }}
            >
              {navItems.find(n => n.id === activeTab)?.label}
            </h2>
          </header>
          <div className="flex-1 overflow-y-auto" style={{ padding: '0 48px 48px' }}>
            {activeTab === 'articles' && (
              loading ? (
                <p className="text-ink-faint" style={{ fontSize: '15px' }}>Cargando artículos…</p>
              ) : articles.length === 0 ? (
                <p className="text-ink-faint" style={{ fontSize: '15px' }}>
                  No hay artículos. ¿Está corriendo el backend?
                </p>
              ) : (
                <div>
                  {articles.map((a, i) => {
                    const meta = SOURCE_META[a.source] ?? { label: a.source, color: 'oklch(0.40 0.010 58)', bg: 'oklch(0.93 0.008 68)' };
                    const dateStr = a.published_at ?? a.fetched_at;
                    return (
                      <article
                        key={a.id}
                        style={{
                          padding: '28px 0',
                          borderTop: i > 0 ? '1px solid oklch(0.89 0.018 68)' : 'none',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <span
                              style={{
                                fontSize: '11px',
                                fontWeight: 600,
                                letterSpacing: '0.04em',
                                padding: '3px 8px',
                                borderRadius: '6px',
                                color: meta.color,
                                background: meta.bg,
                              }}
                            >
                              {meta.label}
                            </span>
                            <span className="text-ink-faint" style={{ fontSize: '13px', fontWeight: 500 }}>
                              {timeAgo(dateStr)}
                            </span>
                          </div>
                          <a
                            href={a.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-ink-faint hover:text-ink transition-colors duration-150"
                          >
                            <ExternalLink size={15} />
                          </a>
                        </div>
                        <h3
                          className="font-sans text-ink"
                          style={{
                            fontSize: '20px',
                            fontWeight: 700,
                            letterSpacing: '-0.02em',
                            lineHeight: 1.25,
                            marginBottom: a.summary ? '10px' : 0,
                          }}
                        >
                          {a.title}
                        </h3>
                        {a.summary && (
                          <p
                            className="font-serif text-ink-secondary"
                            style={{
                              fontSize: '15px',
                              lineHeight: 1.65,
                              display: '-webkit-box',
                              WebkitLineClamp: 3,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden',
                            }}
                          >
                            {a.summary}
                          </p>
                        )}
                      </article>
                    );
                  })}
                </div>
              )
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
