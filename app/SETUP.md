# EpiHelix Frontend - Setup Complete ✅

**Note:** This is the frontend application setup guide. For the complete project structure, see [../README.md](../README.md).

## What's Been Created

### Core Structure
```
/app/                        # Frontend application (in monorepo)
├── src/
│   ├── app/
│   │   ├── layout.js            # Root layout with Header & Footer
│   │   ├── page.js              # Enhanced home page with hero & features
│   ├── search/page.jsx      # Search page with live suggestions
│   ├── entity/[id]/page.jsx # Dynamic entity detail pages
│   ├── query/page.jsx       # Query console (Cypher/SPARQL)
│   ├── chat/page.jsx        # AI chat interface
│   └── globals.css          # Dark theme with shadcn/ui tokens
├── components/
│   ├── ui/                  # shadcn/ui primitives
│   │   ├── button.jsx
│   │   ├── card.jsx         # Enhanced translucency (70% opacity)
│   │   ├── badge.jsx
│   │   └── input.jsx
│   ├── Shared/              # Layout components
│   │   ├── Header.jsx       # Header with search modal & keyboard shortcuts
│   │   ├── Footer.jsx       # Compact footer with inline links
│   │   ├── GlobalSearch.jsx # Floating search modal (Cmd+K)
│   │   └── AnimatedGraphBackground.jsx  # Pulsing particle network with infinite space
│   ├── SearchBar/SearchBar.jsx    # Enhanced autocomplete search
│   ├── EntityCard/EntityCard.jsx  # Enhanced result cards
│   └── InfoBox/InfoBox.jsx        # Enhanced entity detail view
├── hooks/
│   ├── useSearch.js         # Search hook with loading states
│   └── useEntity.js         # Entity fetching hook
└── lib/
    ├── api.js               # Mock API client (ready for FastAPI)
    ├── utils.js             # Enhanced utility functions (cn, debounce, etc.)
    └── animations.js        # Framer Motion presets
```

### Features Implemented

✅ **Professional Layout** - Header with responsive nav, compact Footer (hidden on chat page)  
✅ **Enhanced Home Page** - Gradient hero, typewriter search, feature cards, data source slider, statistics  
✅ **shadcn/ui Integration** - Button, Card, Badge, Input components  
✅ **Enhanced Search** - Google-style search with semantic/keyword toggle  
✅ **Search Results Page** - Google-style layout (Summary + EntityCards left, Knowledge Panel sticky right)  
✅ **Enhanced Entity Pages** - Card-based layout with improved styling  
✅ **Query Console** - Cypher/SPARQL editor with optimized animations (45% faster)  
✅ **AI Chat** - Full-page ChatGPT-style interface with suggested prompts  
✅ **Data Source Slider** - Infinite scrolling showcase (Wikidata, DBpedia, Kaggle, WHO, CDC, PubMed, NCBI)  
✅ **Statistics Card** - Gradient card showing KG metrics (10K+ entities, 50+ sources, 100K+ relationships)  
✅ **Dark Theme** - shadcn/ui design tokens (HSL color system)  
✅ **Uniform Animations** - Consistent fade+slide animations (0.6s pages, 0.4s query console)  
✅ **Responsive Design** - Mobile-first with tablet and desktop breakpoints  
✅ **Lucide Icons** - Consistent iconography throughout  
✅ **Mock API** - Complete client with JSDoc, ready to swap for real calls  
✅ **Tailwind CSS v3** - Properly configured with shadcn/ui compatibility  
✅ **Global Search Modal** - Inline semantic toggle with keyboard navigation (Cmd+K / Ctrl+K)  
✅ **Animated Background** - Moving particle network with pulsing effect  
✅ **Glass Morphism** - Translucent cards with backdrop blur effects  
✅ **Hover Effects** - Consistent card interactions (cyan borders, scale animations)

### Installation & Run

```bash
# Navigate to app directory
cd /path/to/epihelix-project/app

# Install dependencies (if not already done)
npm install

# Dependencies already installed:
# - next@16.0.3, react@19.2.0, react-dom@19.2.0
# - tailwindcss@3.4.18 (downgraded from v4 for shadcn/ui compatibility)
# - tailwindcss-animate, postcss, autoprefixer
# - class-variance-authority
# - clsx, tailwind-merge
# - lucide-react
# - framer-motion@12.23.24
# - @tanstack/react-query@5.90.9
# - prop-types

# Start dev server
npm run dev
```

Visit: http://localhost:3000

### Configuration Files

✅ **`tailwind.config.js`** - Tailwind CSS v3 configuration with shadcn/ui presets
✅ **`postcss.config.mjs`** - PostCSS with `tailwindcss` and `autoprefixer` plugins
✅ **`components.json`** - shadcn/ui configuration pointing to correct paths
✅ **`src/app/globals.css`** - Tailwind directives + HSL color tokens

**Important**: This project uses **Tailwind CSS v3.4.18** (not v4) for full shadcn/ui compatibility.

### UI Components (shadcn/ui)

The project now uses shadcn/ui design system with these components:

- **Button** - Multiple variants (default, outline, ghost, etc.)
- **Card** - Container with header, content, footer sections
- **Badge** - Labels with different variants
- **Input** - Form inputs with consistent styling
- **Header** - Navigation with mobile menu
- **Footer** - Links and social icons

All components use HSL color tokens for consistent theming.

### Advanced UI Features

#### 🔍 Global Search Modal
- **Trigger**: Click search icon in header or press `Cmd+K` (Mac) / `Ctrl+K` (Windows/Linux)
- **Features**:
  - Floating modal with backdrop blur
  - Live search suggestions with debouncing
  - **Inline semantic/keyword toggle** (right side of input bar)
  - Keyboard navigation (↑↓ arrows, Enter to select, Esc to close)
  - Redirects to `/search` page with query results
  - Beautiful spring-physics animations
  - Entity type badges and match scores
- **File**: `src/components/Shared/GlobalSearch.jsx`

#### 🏠 Homepage Features
- **Typewriter Search**: 5 rotating placeholders (`placeholders` array moved outside component)
  - Thick blinking cursor (`|`) embedded in placeholder text
  - **Hydration-safe**: Uses `suppressHydrationWarning` for SSR compatibility
  - No `isMounted` state needed with suppressHydrationWarning approach
- **Semantic/Keyword Toggle**: Rounded pill button with Sparkles icon
- **Quick Access Buttons**: Search Database, Query Console, AI Assistant
- **Feature Cards**: 5 cards showcasing app capabilities (3+2 grid layout)
- **Data Source Slider**: Infinite horizontal scroll with 7 trusted sources
  - Logos: Wikidata, DBpedia, Kaggle, WHO, CDC, PubMed, NCBI
  - Real brand colors with hover effects (scale + opacity)
  - 45-second loop, fully transparent background
- **Statistics Card**: Gradient card with 3 metrics
  - 10K+ Entities, 50+ Sources, 100K+ Relationships
  - Hover scale animation on each stat
- **Gradient Headings**: "Start Exploring" and "Powerful Features" with sharp underlines

#### 🔎 Search Page Layout
- **Google-style structure**:
  - Left column: Summary text + EntityCard list (flex-1)
  - Right sidebar: Knowledge Panel (w-80 xl:w-96, sticky)
  - Mobile: Knowledge Panel on top, results below
- **Semantic toggle**: Matches homepage style (rounded pill)
- **Typewriter animation**: In search input with thick cursor
  - **Hydration-safe**: Uses `suppressHydrationWarning` to prevent SSR warnings
  - `placeholders` array moved outside component for performance

#### 💬 Chat Page
- **Full-page layout**: Escapes parent padding with negative margins
- **Height**: `calc(100vh - 8rem)` accounting for spacing
- **Suggested prompts**: 4 examples with hover effects (no blinking)
- **Footer**: Hidden on chat page for full-screen experience

#### � Query Console
- **Optimized animations**: Total animation time reduced from 1.1s → 0.6s (45% faster)
  - Header: 0s delay, 0.4s duration
  - Query type selector: 0.1s delay, 0.4s duration  
  - Editor: 0.2s delay, 0.4s duration
  - Actions: 0.3s delay, 0.4s duration
  - Examples: 0.4s delay, 0.5s & 0.6s staggered
- **Query types**: Cypher and SPARQL toggles with icons
- **Example queries**: Cards with hover effects (no blinking)

#### �🌌 Animated Graph Background
- **Canvas-based particle system** with 150-200 particles (scales with screen size)
- **Dynamic connections** form between nearby particles (200-300px range)
- **Pulsing nodes** - Each particle breathes with sine wave animation
- **Infinite space effect** - Particles wrap around edges (no bouncing)
- **Smart resize handling** - Particles scale proportionally when window resizes
- **Performance optimized** - 60fps with requestAnimationFrame
- **Colors**: Cyan particles (#22c1c3) + Purple connections (#7c5cff)
- **Non-intrusive** - pointer-events disabled, z-index 0
- **File**: `src/components/Shared/AnimatedGraphBackground.jsx`

#### ✨ Glass Morphism Effects
All cards and components now have translucent backgrounds with backdrop blur:
- Cards use `bg-card/70` with `backdrop-blur-xl` (70% opacity)
- Main content container: Route-based layouts
  - Home: `bg-card/30` with rounded corners and padding
  - Other pages: `bg-card/30` full-screen with internal padding
- Borders: `border-border/50` for softer appearance
- Custom utility classes in `globals.css`:
  - `.glass-card` - Semi-transparent with blur
  - `.glass-card-strong` - More opaque variant
  - `.gradient-border` - Animated gradient borders
  - `.custom-scrollbar` - Styled scrollbars

#### 🎨 Animation System
- **Uniform timing**: Consistent across all pages
  - Standard pages: 0.6s duration, 0.2s delay increments
  - Query console: 0.4s duration, 0.1s delay increments (optimized)
- **Fade + slide pattern**: `initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}`
- **Hover effects**: `whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}`
- **Typewriter**: 100ms typing, 50ms deleting, 2s pause between words
  - **SSR-safe**: `suppressHydrationWarning` on inputs prevents hydration mismatches
  - Placeholders arrays moved outside components for stable references
- **No blinking**: Removed `transition-all` from cards, only text uses `transition-colors duration-200`

#### 🎯 Hover Effects (Standardized)
All interactive cards use consistent hover styling:
- Border: `hover:border-cyan-500/50`
- Shadow: `hover:shadow-lg hover:shadow-cyan-500/10`
- Text: `group-hover:text-cyan-400`
- Scale: `whileHover={{ scale: 1.02 }}`
Applied to: feature cards, entity cards, chat prompts, query examples

### Keyboard Shortcuts

- **`Cmd+K` / `Ctrl+K`** - Open global search modal
- **`Esc`** - Close search modal
- **`↑` / `↓`** - Navigate search suggestions
- **`Enter`** - Select search result

### Next Steps

1. **Test the Enhanced UI**:
   - Visit home page → See typewriter search, data source slider, statistics
   - Press `Cmd+K` → Open global search modal with inline semantic toggle
   - Type to search → See live suggestions with animations
   - Visit `/search` → See Google-style layout with Knowledge Panel
   - Visit `/query` → Experience optimized animations (45% faster)
   - Visit `/chat` → Full-page ChatGPT-style interface
   - Test all hover effects → Consistent cyan highlights and scale animations
   - Check responsive design (mobile, tablet, desktop)
   - Notice glass morphism effect on all cards

2. **Connect to Backend** (when ready):
   - Backend services are in `../services/` directory
   - Start FastAPI: `cd ../services/api && uvicorn main:app --reload`
   - Create `.env.local` in app directory:
     ```
     NEXT_PUBLIC_API_URL=http://localhost:8000/api
     ```
   - Uncomment real fetch calls in `src/lib/api.js`

3. **Add Interactive Graph Visualization** (future):
   ```bash
   npm install react-force-graph
   # or
   npm install cytoscape react-cytoscapejs
   ```
   Create `/components/GraphView/GraphView.jsx` for entity relationship exploration

### API Mock → Real Backend Migration

Current: `src/lib/api.js` returns mock data
Future: Uncomment the fetch calls and point to FastAPI

Example:
```js
// Mock (current)
export async function search(q) {
  return Promise.resolve([...mockData])
}

// Real (when backend ready)
export async function search(q) {
  const response = await fetch(`${API_BASE_URL}/search?q=${q}`)
  return response.json()
}
```

### Design System

**Colors (HSL tokens)**:
- Background: `222.2 84% 4.9%`
- Foreground: `210 40% 98%`
- Primary: `210 40% 98%`
- Accent: `217.2 32.6% 17.5%`
- Custom accents: Cyan (#22c1c3), Purple (#7c5cff)

**Typography**: Inter, Geist Sans, system fallbacks

**Components**: shadcn/ui with class-variance-authority for variants

### Files You Can Customize

- `src/app/globals.css` - Global styles and theme tokens
- `components.json` - shadcn/ui configuration
- `src/lib/animations.js` - Motion presets
- `src/lib/api.js` - API client
- `src/components/ui/*` - shadcn/ui components
- `src/components/Shared/*` - Layout components

## Summary

The frontend is **professionally styled** with **shadcn/ui** components, **animated backgrounds**, and **glass morphism effects**. Recent updates include:

- **Data source slider** with infinite scroll showcasing 7 trusted sources
- **Statistics card** with gradient styling and hover animations
- **Optimized query console** animations (45% faster, 1.1s → 0.6s)
- **Uniform animation system** across all pages for consistency
- **Standardized hover effects** with cyan accents and scale animations
- **Google-style search layout** with sticky Knowledge Panel
- **Inline semantic toggles** in all search interfaces
- **Full-page chat interface** with suggested prompts
- **Route-based layouts** (rounded container on home, full-screen on others)
- **Fixed hydration errors** by moving placeholders array outside component
- **No card blinking** - removed conflicting CSS transitions

**Current state**: Production-ready demo UI with premium visual effects and optimized performance  
**Ready for**: Backend integration, interactive graph visualization, and real data

Refer to `.github/instructions/epihelix-instructions.instructions.md` for full architecture and API contracts.
