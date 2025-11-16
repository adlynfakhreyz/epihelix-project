'use client'

import React, { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Search, Sparkles } from 'lucide-react'
import EntityCard from '../../components/EntityCard/EntityCard'
import KnowledgePanel from '../../components/KnowledgePanel/KnowledgePanel'
import ResultSummary from '../../components/ResultSummary/ResultSummary'
import useSearch from '../../hooks/useSearch'
import { generateSummary, getKnowledgePanel } from '../../lib/api'
import { motion, AnimatePresence } from 'framer-motion'
import { staggerChildren, listItem } from '../../lib/animations'

// Placeholders array outside component to prevent recreation on each render
const placeholders = [
  '1918 Spanish Flu',
  'COVID-19 symptoms',
  'pandemic timeline',
  'Influenza A virus',
  'vaccine development',
]

export default function SearchPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { results, loading, executeSearch } = useSearch()
  const [semantic, setSemantic] = useState(false)
  const [query, setQuery] = useState('')
  const [hasResults, setHasResults] = useState(false)
  
  // Top result data
  const [topSummary, setTopSummary] = useState(null)
  const [topKnowledgePanel, setTopKnowledgePanel] = useState(null)
  const [loadingSummary, setLoadingSummary] = useState(false)

  // Typewriter animation
  const [placeholderIndex, setPlaceholderIndex] = useState(0)
  const [displayedText, setDisplayedText] = useState('')
  const [isDeleting, setIsDeleting] = useState(false)

  // Typewriter effect
  useEffect(() => {
    const currentPlaceholder = placeholders[placeholderIndex]
    const typingSpeed = isDeleting ? 50 : 100
    const pauseTime = isDeleting ? 500 : 2000

    if (!isDeleting && displayedText === currentPlaceholder) {
      setTimeout(() => setIsDeleting(true), pauseTime)
      return
    }

    if (isDeleting && displayedText === '') {
      setIsDeleting(false)
      setPlaceholderIndex((prev) => (prev + 1) % placeholders.length)
      return
    }

    const timeout = setTimeout(() => {
      setDisplayedText(
        isDeleting
          ? currentPlaceholder.substring(0, displayedText.length - 1)
          : currentPlaceholder.substring(0, displayedText.length + 1)
      )
    }, typingSpeed)

    return () => clearTimeout(timeout)
  }, [displayedText, isDeleting, placeholderIndex])

  // Load query from URL on mount
  useEffect(() => {
    const q = searchParams.get('q')
    if (q) {
      setQuery(q)
      executeSearch(q, { semantic })
    }
  }, [searchParams])

  // Update hasResults when results change
  useEffect(() => {
    setHasResults(results.length > 0)
  }, [results])

  // Load summary and knowledge panel for top result
  useEffect(() => {
    if (results.length > 0 && query) {
      const topResult = results[0]
      
      // Load summary
      setLoadingSummary(true)
      generateSummary(topResult.id, query, topResult.type)
        .then((data) => {
          setTopSummary(data.summary)
          setLoadingSummary(false)
        })
        .catch(() => {
          setLoadingSummary(false)
        })

      // Load knowledge panel
      getKnowledgePanel(topResult.id)
        .then((data) => {
          setTopKnowledgePanel(data)
        })
    } else {
      setTopSummary(null)
      setTopKnowledgePanel(null)
    }
  }, [results, query])

  function handleSearch(e) {
    e.preventDefault()
    if (query.trim()) {
      executeSearch(query, { semantic })
      // Update URL with query
      router.push(`/search?q=${encodeURIComponent(query.trim())}`, { scroll: false })
    }
  }

  function handleSelect(entityId) {
    router.push(`/entity/${entityId}`)
  }

  // Dynamic layout: centered when no results, top when has results
  const searchContainerClass = hasResults || loading
    ? 'pt-6 pb-4' // Compact at top when results shown
    : 'min-h-[50vh] flex items-center justify-center' // Centered when empty

  return (
    <main className="flex-1 py-8">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        {/* Search Bar - Dynamic positioning */}
        <motion.div
          className={searchContainerClass}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className={hasResults || loading ? 'w-full max-w-4xl mx-auto' : 'w-full max-w-2xl text-center'}>
            {/* "Browse Now" heading - only show when no results */}
            {!hasResults && !loading && (
              <motion.div
                className="relative inline-block mb-8"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.6 }}
              >
                <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight relative">
                  <span className="relative inline-block">
                    <span className="bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
                      Browse Now
                    </span>
                    <div className="absolute -bottom-2 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-cyan-500 to-transparent"></div>
                  </span>
                </h2>
              </motion.div>
            )}

            <form onSubmit={handleSearch}>
              <div className="relative group mb-4">
                <Search className="absolute left-6 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-cyan-400 transition-colors" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={`${displayedText}|`}
                  suppressHydrationWarning
                  autoFocus
                  className="w-full pl-14 pr-16 py-4 rounded-full bg-card/80 backdrop-blur-xl border-2 border-border/50 
                           text-foreground placeholder:text-muted-foreground
                           focus:outline-none focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/20
                           hover:border-border hover:shadow-lg hover:shadow-cyan-500/5
                           transition-all duration-200 text-base"
                />
              </div>
            </form>

            {/* Semantic toggle */}
            <motion.div
              className="flex items-center justify-center gap-3"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.6 }}
            >
              <button
                type="button"
                onClick={() => setSemantic(!semantic)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full border transition-all ${
                  semantic
                    ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400'
                    : 'bg-card/50 border-border/50 text-muted-foreground hover:border-border'
                }`}
              >
                <Sparkles className="h-4 w-4" />
                <span className="text-sm font-medium">
                  {semantic ? 'Vector Search' : 'Keyword Search'}
                </span>
              </button>
            </motion.div>
          </div>
        </motion.div>

        {/* Results Section */}
        <AnimatePresence mode="wait">
          {loading && (
            <motion.div
              key="loading"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.6 }}
              className="text-center py-12"
            >
              <div className="inline-block w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-muted-foreground mt-4">Searching...</p>
            </motion.div>
          )}

          {!loading && hasResults && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.6 }}
              className="pb-12"
            >
              <motion.div
                className="text-sm text-muted-foreground mb-6"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.6 }}
              >
                Found {results.length} result{results.length !== 1 ? 's' : ''}
              </motion.div>

              {/* Google-style Layout: Left (Summary + EntityCards) | Right (Knowledge Panel) */}
              <div className="flex flex-col lg:flex-row gap-6 lg:gap-8 items-start">
                {/* Left: Summary + All Results (main content area) */}
                <motion.div
                  className="flex-1 min-w-0 order-2 lg:order-1"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4, duration: 0.6 }}
                >
                  {/* Top Result Summary */}
                  {results[0] && (
                    <div className="mb-6">
                      <ResultSummary
                        result={results[0]}
                        query={query}
                        summary={topSummary}
                        loading={loadingSummary}
                      />
                    </div>
                  )}

                  {/* All Entity Cards */}
                  <div className="space-y-4">
                    {results.map((entity, index) => (
                      <motion.div
                        key={entity.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 + (index * 0.1), duration: 0.6 }}
                      >
                        <EntityCard entity={entity} />
                      </motion.div>
                    ))}
                  </div>
                </motion.div>

                {/* Right: Knowledge Panel (fixed width sidebar, sticky) */}
                <motion.aside
                  className="w-full lg:w-80 xl:w-96 lg:flex-shrink-0 order-1 lg:order-2"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4, duration: 0.6 }}
                >
                  {topKnowledgePanel && (
                    <div className="lg:sticky lg:top-6">
                      <KnowledgePanel entity={topKnowledgePanel} />
                    </div>
                  )}
                </motion.aside>
              </div>
            </motion.div>
          )}

          {!loading && !hasResults && query && (
            <motion.div
              key="no-results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.6 }}
              className="text-center py-12"
            >
              <div className="text-4xl mb-4">🔍</div>
              <p className="text-muted-foreground">
                No results found for "{query}"
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                Try different keywords or enable semantic search
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  )
}
