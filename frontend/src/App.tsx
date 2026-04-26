import { FileText, MessageSquare, User } from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { id: 'articles', label: 'Articles', icon: FileText },
  { id: 'tweets', label: 'Tweets', icon: MessageSquare },
  { id: 'pau', label: 'Pau', icon: User },
];

const Sidebar = () => {
  const [activeTab, setActiveTab] = useState('articles');

  return (
    <aside className="w-72 bg-natural-sidebar border-r border-anthropic-warm-gray flex flex-col p-8">
      <div className="mb-12 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-anthropic-tan" />
        <h1 className="text-xl font-bold tracking-tight text-anthropic-black leading-tight font-serif">
          Mes Que Un AI
        </h1>
      </div>

      <nav className="flex-1">
        <p className="text-[10px] tracking-[0.2em] font-bold text-anthropic-black/30 mb-6 uppercase">
          Learning Paths
        </p>
        <ul className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <li key={item.id}>
                <button
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 w-full text-left ${
                    isActive
                      ? 'bg-anthropic-white shadow-sm border border-anthropic-tan/20'
                      : 'hover:bg-anthropic-tan/10'
                  }`}
                >
                  <Icon
                    size={18}
                    className={`${isActive ? 'text-anthropic-tan' : 'text-stone-400'} transition-colors`}
                  />
                  <span className={`text-xs tracking-wider font-semibold ${isActive ? 'text-anthropic-black' : 'text-stone-500'}`}>
                    {item.label}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="mt-auto pt-8 border-t border-anthropic-warm-gray">
        <p className="text-[10px] tracking-widest text-stone-400 font-bold uppercase">
          A language learning app
        </p>
      </div>
    </aside>
  );
};

export default function App() {
  return (
    <div className="min-h-screen bg-anthropic-warm-gray flex items-center justify-center p-4 md:p-8 lg:p-12">
      <div className="w-full max-w-6xl h-[85vh] bg-anthropic-white rounded-[32px] overflow-hidden flex shadow-[0_32px_64px_-16px_rgba(0,0,0,0.1)] border border-anthropic-tan/20">
        <Sidebar />
        <main className="flex-1" />
      </div>
    </div>
  );
}
