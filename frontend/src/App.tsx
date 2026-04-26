import { BookOpen, MessageSquare, Bot, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { id: 'articles', label: 'Artículos', sublabel: 'Articles', icon: BookOpen },
  { id: 'tweets',   label: 'Tweets',    sublabel: 'Social',   icon: MessageSquare },
  { id: 'pau',      label: 'Pau',       sublabel: 'Tutor IA', icon: Bot },
];

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
          padding: collapsed ? '36px 0' : '36px 44px',
          justifyContent: collapsed ? 'center' : 'space-between',
          transition: `padding ${WIDTH_DURATION} ${EASE}`,
          animationDelay: '400ms',
        }}
      >
        <p
          className="text-ink-faint uppercase leading-snug"
          style={{
            fontSize: '12px',
            fontWeight: 600,
            letterSpacing: '0.14em',
            opacity: collapsed ? 0 : 1,
            maxWidth: collapsed ? 0 : '220px',
            overflow: 'hidden',
            whiteSpace: 'nowrap',
            transition: textTransition,
          }}
        >
          A language learning app
        </p>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-ink-faint hover:text-ink transition-colors duration-150 flex-shrink-0"
          style={{
            marginLeft: collapsed ? 0 : '12px',
            padding: '8px',
            margin: collapsed ? '-8px' : '-8px -8px -8px 4px',
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
        <main className="flex-1 bg-surface" />
      </div>
    </div>
  );
}
