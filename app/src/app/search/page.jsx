'use client'

import React, { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Search, Sparkles } from 'lucide-react'
import EntityCard from '../../components/EntityCard/EntityCard'
import InfoBox from '../../components/InfoBox/InfoBox'
import ResultSummary from '../../components/ResultSummary/ResultSummary'
import { useSearch } from '../../hooks/useSearch'
import { useEntity } from '../../hooks/useEntity'
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

function SearchPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [semantic, setSemantic] = useState(false)
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [page, setPage] = useState(1)
  const pageSize = 20
  
  // React Query hooks
  const { data: searchData, isLoading: loading, isFetching } = useSearch(debouncedQuery, { 
    page,
    page_size: pageSize,
    semantic, 
    enabled: debouncedQuery.length > 0 
  })
  
  // Extract results from paginated response
  const results = searchData?.results || []
  const topResult = results[0]
  const { data: knowledgePanelData } = useEntity(topResult?.id, { enabled: Boolean(topResult?.id) })
  
  const hasResults = results.length > 0

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
      setDebouncedQuery(q)
    }
  }, [searchParams])

  // Debounce query for search
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(query)
      setPage(1) // Reset to page 1 on new search
    }, 300)
    return () => clearTimeout(handler)
  }, [query])

  // Scroll to top when page changes
  useEffect(() => {
    if (page > 1) {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }, [page])

  function handleSearch(e) {
    e.preventDefault()
    if (query.trim()) {
      setDebouncedQuery(query.trim())
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
                {searchData?.total ? (
                  <>
                    Found {searchData.total} result{searchData.total !== 1 ? 's' : ''}
                    {searchData.total_pages > 1 && (
                      <span> (Page {searchData.page} of {searchData.total_pages})</span>
                    )}
                  </>
                ) : (
                  `Found ${results.length} result${results.length !== 1 ? 's' : ''}`
                )}
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
                        summary={searchData?.summary?.summary}
                        loading={loading || isFetching}
                      />
                    </div>
                  )}

                  {/* All Entity Cards */}
                  <div className="space-y-4 relative">
                    {/* Loading overlay for pagination */}
                    {isFetching && !loading && (
                      <div className="absolute inset-0 bg-background/50 backdrop-blur-sm z-10 flex items-center justify-center rounded-lg">
                        <div className="flex items-center gap-2 bg-card px-4 py-2 rounded-lg border border-border shadow-lg">
                          <div className="w-4 h-4 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
                          <span className="text-sm text-muted-foreground">Loading page {page}...</span>
                        </div>
                      </div>
                    )}
                    
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

                  {/* Pagination Controls */}
                  {searchData && searchData.total_pages > 1 && (
                    <motion.div
                      className="mt-8 flex items-center justify-center gap-2"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.8, duration: 0.6 }}
                    >
                      <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={!searchData.has_prev}
                        className="px-4 py-2 rounded-lg bg-card border border-border hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        Previous
                      </button>
                      
                      <div className="flex items-center gap-1">
                        {Array.from({ length: searchData.total_pages }, (_, i) => i + 1)
                          .filter(p => {
                            // Show first, last, current, and neighbors
                            return p === 1 || 
                                   p === searchData.total_pages || 
                                   Math.abs(p - searchData.page) <= 1
                          })
                          .map((p, idx, arr) => {
                            const showEllipsis = idx > 0 && p - arr[idx - 1] > 1
                            return (
                              <React.Fragment key={p}>
                                {showEllipsis && <span className="px-2 text-muted-foreground">...</span>}
                                <button
                                  onClick={() => setPage(p)}
                                  className={`w-10 h-10 rounded-lg transition-colors ${
                                    p === searchData.page
                                      ? 'bg-cyan-500/20 border-2 border-cyan-500 text-cyan-400 font-semibold'
                                      : 'bg-card border border-border hover:bg-accent'
                                  }`}
                                >
                                  {p}
                                </button>
                              </React.Fragment>
                            )
                          })}
                      </div>
                      
                      <button
                        onClick={() => setPage(p => Math.min(searchData.total_pages, p + 1))}
                        disabled={!searchData.has_next}
                        className="px-4 py-2 rounded-lg bg-card border border-border hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        Next
                      </button>
                    </motion.div>
                  )}
                </motion.div>

                {/* Right: InfoBox Panel (fixed width sidebar, sticky) */}
                <motion.aside
                  className="w-full lg:w-96 xl:w-[28rem] lg:flex-shrink-0 order-1 lg:order-2"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4, duration: 0.6 }}
                >
                  <div className="lg:sticky lg:top-6">
                    <InfoBox 
                      entity={knowledgePanelData} 
                      loading={!knowledgePanelData}
                      showRelations={false}
                    />
                  </div>
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

export default function SearchPage() {
  return (
    <Suspense fallback={
      <div className="flex-1 flex items-center justify-center">
        <div className="inline-block w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    }>
      <SearchPageContent />
    </Suspense>
  )
}
