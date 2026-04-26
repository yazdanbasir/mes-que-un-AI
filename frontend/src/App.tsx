import { BookOpen, MessageSquare, Bot } from 'lucide-react';
import { useState } from 'react';

const navItems = [
  {
    id: 'articles',
    label: 'Artículos',
    sublabel: 'Articles',
    icon: BookOpen,
    quote: {
      es: 'El periodismo deportivo español no tiene igual. Leer es aprender.',
      en: 'Select an article from the feed to begin reading.',
    },
  },
  {
    id: 'tweets',
    label: 'Tweets',
    sublabel: 'Social',
    icon: MessageSquare,
    quote: {
      es: 'Twitter fue donde aprendí más español sin darme cuenta.',
      en: 'Your curated Spanish football timeline.',
    },
  },
  {
    id: 'pau',
    label: 'Pau',
    sublabel: 'Tutor IA',
    icon: Bot,
    quote: {
      es: 'La mejor manera de aprender un idioma es hablarlo.',
      en: 'Start a conversation. Ask anything in Spanish.',
    },
  },
];

const Sidebar = ({
  activeTab,
  setActiveTab,
}: {
  activeTab: string;
  setActiveTab: (id: string) => void;
}) => {
  return (
    <aside
      className="w-[272px] flex-shrink-0 bg-sidebar flex flex-col"
      style={{ borderRight: '1px solid oklch(0.89 0.018 68)' }}
    >
      {/* Wordmark */}
      <div
        className="animate-fade-in px-8 pt-10 pb-9"
        style={{ animationDelay: '0ms' }}
      >
        <div
          className="w-5 h-5 rounded-[4px] bg-accent mb-5"
          style={{ transform: 'rotate(12deg)' }}
        />
        <h1
          className="font-sans leading-[1.05] tracking-[-0.04em] text-ink"
          style={{ fontSize: '26px', fontWeight: 800 }}
        >
          Més que
          <br />
          <span style={{ color: 'oklch(0.58 0.135 42)' }}>un AI.</span>
        </h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 pb-4">
        <p
          className="text-ink-faint px-4 mb-3 uppercase"
          style={{
            fontSize: '9px',
            fontWeight: 700,
            letterSpacing: '0.18em',
            animationDelay: '80ms',
          }}
        >
          Modos
        </p>
        <ul className="space-y-0.5">
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
                  className="w-full text-left rounded-xl transition-all duration-200"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '10px 16px',
                    background: isActive
                      ? 'oklch(0.93 0.030 44)'
                      : 'transparent',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive)
                      (e.currentTarget as HTMLButtonElement).style.background =
                        'oklch(0.92 0.014 72 / 0.7)';
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive)
                      (e.currentTarget as HTMLButtonElement).style.background =
                        'transparent';
                  }}
                >
                  <Icon
                    size={15}
                    style={{
                      flexShrink: 0,
                      color: isActive
                        ? 'oklch(0.58 0.135 42)'
                        : 'oklch(0.65 0.014 60)',
                      transition: 'color 0.15s',
                    }}
                  />
                  <div>
                    <span
                      className="block leading-tight"
                      style={{
                        fontSize: '13px',
                        fontWeight: isActive ? 700 : 500,
                        color: isActive
                          ? 'oklch(0.58 0.135 42)'
                          : 'oklch(0.16 0.010 58)',
                        transition: 'all 0.15s',
                        letterSpacing: '-0.01em',
                      }}
                    >
                      {item.label}
                    </span>
                    <span
                      className="block leading-tight mt-0.5"
                      style={{
                        fontSize: '10px',
                        fontWeight: 500,
                        color: isActive
                          ? 'oklch(0.72 0.080 44)'
                          : 'oklch(0.65 0.014 60)',
                        transition: 'color 0.15s',
                        letterSpacing: '0.01em',
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
        className="animate-fade-in px-8 py-6"
        style={{
          borderTop: '1px solid oklch(0.89 0.018 68)',
          animationDelay: '400ms',
        }}
      >
        <p
          className="text-ink-faint uppercase leading-snug"
          style={{
            fontSize: '9px',
            fontWeight: 600,
            letterSpacing: '0.14em',
          }}
        >
          Comprensión
          <br />
          auditiva &amp; lectora
        </p>
      </div>
    </aside>
  );
};

const WelcomePane = ({ activeTab }: { activeTab: string }) => {
  const item = navItems.find((n) => n.id === activeTab)!;

  return (
    <div
      key={activeTab}
      className="flex-1 flex flex-col items-center justify-center px-16 py-20 animate-fade-in"
      style={{ animationDelay: '0ms' }}
    >
      <div style={{ maxWidth: '480px', textAlign: 'center' }}>
        {/* Decorative bar */}
        <div
          className="mx-auto mb-8"
          style={{
            width: '32px',
            height: '3px',
            background: 'oklch(0.58 0.135 42)',
            borderRadius: '2px',
          }}
        />

        {/* Spanish quote */}
        <p
          className="font-serif text-ink"
          style={{
            fontSize: '22px',
            fontWeight: 400,
            fontStyle: 'italic',
            lineHeight: 1.45,
            letterSpacing: '-0.01em',
            marginBottom: '20px',
          }}
        >
          &ldquo;{item.quote.es}&rdquo;
        </p>

        {/* English subtitle */}
        <p
          className="text-ink-secondary"
          style={{
            fontSize: '13px',
            fontWeight: 400,
            letterSpacing: '0.01em',
            lineHeight: 1.6,
          }}
        >
          {item.quote.en}
        </p>
      </div>
    </div>
  );
};

export default function App() {
  const [activeTab, setActiveTab] = useState('articles');

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
            '0 48px 96px -24px oklch(0.16 0.010 58 / 0.13), 0 4px 12px oklch(0.16 0.010 58 / 0.06)',
          border: '1px solid oklch(0.89 0.018 68 / 0.7)',
        }}
      >
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        <main className="flex-1 bg-surface">
          <WelcomePane activeTab={activeTab} />
        </main>
      </div>
    </div>
  );
}
