# EpiHelix — Pandemic Insights Explorer (Frontend)

Professional Next.js (JavaScript/JSX) application with shadcn/ui for exploring pandemic knowledge graphs.

**Note:** This is the frontend application. For the complete project structure including backend services and KG construction, see the [project root README](../README.md).

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or pnpm

### Installation

```bash
# Navigate to app directory
cd /path/to/epihelix-project/app

# Install dependencies
npm install

# All required packages are already installed:
# Core: next@16.0.3, react@19.2.0, react-dom@19.2.0
# Styling: tailwindcss@3.4.18 (v3 for shadcn/ui compatibility)
# - tailwindcss-animate, postcss, autoprefixer
# - class-variance-authority, clsx, tailwind-merge
# Icons & Animation: lucide-react, framer-motion@12.23.24
# State Management: @tanstack/react-query@5.90.9
# Other: prop-types

# Run development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
/app                        # Frontend application root
  /src
    /app                    # Next.js App Router pages
      layout.js             # Root layout with Header & Footer
      page.js               # Enhanced home page
      globals.css           # Tailwind directives + HSL color tokens
      /entity/[id]/         # Entity detail page
      /search/              # Search page
      /query/               # Query console
      /chat/                # AI chat interface
    /components
      /ui/                  # shadcn/ui primitives
        button.jsx
        card.jsx
        badge.jsx
        input.jsx
      /Shared/              # Layout components
        Header.jsx          # Professional header with nav
        Footer.jsx          # Footer with links
      /SearchBar/           # Enhanced search with autocomplete
      /EntityCard/          # Enhanced entity cards
      /InfoBox/             # Enhanced entity details
    /hooks                  # Custom React hooks
      useSearch.js
      useEntity.js
    /lib                    # Utilities and API client
      api.js                # Mock API (replace with real FastAPI calls)
      utils.js              # Enhanced utilities (cn, debounce, etc.)
      animations.js         # Framer Motion presets
  components.json           # shadcn/ui configuration
  tailwind.config.js        # Tailwind CSS v3 config
  postcss.config.mjs        # PostCSS configuration
```

## 🎨 Features

✅ **Professional UI**: shadcn/ui components with responsive design  
✅ **Header & Footer**: Consistent navigation across all pages (compact footer, hidden on chat page)  
✅ **Global Search Modal**: Keyboard shortcuts (Cmd+K / Ctrl+K) with inline semantic/keyword toggle  
✅ **Animated Background**: Pulsing particle network with infinite space wrap-around effect  
✅ **Glass Morphism**: Highly translucent cards (70% opacity) with backdrop blur effects  
✅ **Translucent Layout**: Route-based containers (rounded on home, full-screen on others)  
✅ **Enhanced Search**: Google-style search with typewriter animation and semantic toggle  
✅ **Entity Pages**: Card-based layouts with properties, relations, provenance  
✅ **Query Console**: Execute custom Cypher/SPARQL queries (optimized animations, 45% faster)  
✅ **AI Chat**: Full-page ChatGPT-style interface with suggested prompts  
✅ **Data Source Slider**: Infinite scrolling showcase of trusted data sources (7 logos)  
✅ **Statistics Card**: Gradient card showing knowledge graph metrics  
✅ **Dark Theme**: HSL-based design tokens for consistent theming  
✅ **Animations**: Smooth uniform animations across all pages (0.6s pages, 0.4s query console)  
✅ **Icons**: Lucide React for consistent iconography  
✅ **Hover Effects**: Consistent interactions across all cards (cyan borders, scale animations)  
✅ **Hydration Safe**: TypeWriter placeholders with suppressHydrationWarning for SSR compatibility

## 🛠 Tech Stack

- **Framework**: Next.js 16.0.3 (App Router) + React 19.2.0
- **Language**: JavaScript (JSX)
- **UI Library**: shadcn/ui (with Tailwind CSS v3)
- **Styling**: Tailwind CSS 3.4.18 + PostCSS + Autoprefixer
- **Animation**: Framer Motion 12.23.24
- **State**: React Hooks + React Query 5.90.9
- **Icons**: Lucide React
- **Type Safety**: PropTypes + JSDoc
- **Utilities**: clsx, tailwind-merge, class-variance-authority

## 🔗 API Integration

The app currently uses mock data in `src/lib/api.js`. To connect to the FastAPI backend:

1. Start the backend service:
   ```bash
   cd ../services/api
   uvicorn main:app --reload
   ```

2. Set environment variable in `app/.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

3. Uncomment the real fetch calls in `src/lib/api.js`

## 📖 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## 🎨 Design System

**Colors (HSL tokens)**:
- Background: `222.2 84% 4.9%`
- Foreground: `210 40% 98%`
- Primary: `210 40% 98%`
- Accent: `217.2 32.6% 17.5%`
- Custom accents: Cyan (#22c1c3), Purple (#7c5cff)

**Typography**: Inter, Geist Sans, system fonts

**Components**: shadcn/ui with class-variance-authority for variants

## 📋 Next Steps

1. ✅ Professional frontend UI with shadcn/ui
2. ✅ Header/Footer navigation with responsive design
3. ✅ Enhanced components with consistent styling and animations
4. ✅ Data source slider and statistics showcase
5. ✅ Query console with optimized performance
6. ⏳ Connect to FastAPI backend
7. ⏳ Add interactive graph visualizations (react-force-graph or cytoscape)
8. ⏳ Implement semantic search backend with embeddings
9. ⏳ Add RAG chatbot with real LLM integration

## 📚 Documentation

- **Project Root**: [../README.md](../README.md) - Complete monorepo structure
- **Setup Guide**: [SETUP.md](./SETUP.md) - Detailed feature documentation
- **Instructions**: [../.github/instructions/epihelix-instructions.instructions.md](../../.github/instructions/epihelix-instructions.instructions.md) - Architecture & API specs
- **Backend Services**: [../services/](../services/) - FastAPI and connectors
- **KG Construction**: [../kg-construction/](../kg-construction/) - Knowledge graph pipeline

