'use client'

import React, { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, X, Loader2, TrendingUp, Sparkles } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { debounce } from '@/lib/utils'
import { search } from '@/lib/api'

/**
 * Global search modal component with floating UI
 */
export function GlobalSearch({ isOpen, onClose }) {
  const [query, setQuery] = useState('')
  const [semantic, setSemantic] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef(null)
  const router = useRouter()

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100)
      setQuery('')
      setSuggestions([])
    }
  }, [isOpen])

  // Debounced search
  useEffect(() => {
    const fetchSuggestions = debounce(async (q) => {
      if (!q.trim()) {
        setSuggestions([])
        return
      }

      setLoading(true)
      try {
        const results = await search(q, { limit: 8 })
        setSuggestions(results)
        setSelectedIndex(0)
      } catch (error) {
        console.error('Search error:', error)
      } finally {
        setLoading(false)
      }
    }, 300)

    fetchSuggestions(query)
  }, [query])

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return

      if (e.key === 'Escape') {
        onClose()
      } else if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex((prev) => Math.min(prev + 1, suggestions.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex((prev) => Math.max(prev - 1, 0))
      } else if (e.key === 'Enter' && suggestions.length > 0) {
        e.preventDefault()
        handleSelect(suggestions[selectedIndex])
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, suggestions, selectedIndex, onClose])

  function handleSelect(entity) {
    // Navigate to search page with query
    router.push(`/search?q=${encodeURIComponent(entity.label)}&semantic=${semantic}`)
    onClose()
  }

  function handleSearchSubmit(e) {
    e.preventDefault()
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query)}&semantic=${semantic}`)
      onClose()
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]"
            onClick={onClose}
          />

          {/* Search Modal */}
          <div className="fixed inset-0 z-[101] flex items-start justify-center pt-[15vh] px-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -20 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="w-full max-w-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Search Box */}
              <div className="bg-card/95 backdrop-blur-xl border border-border/50 rounded-2xl shadow-2xl overflow-hidden">
                {/* Input Section with Toggle */}
                <form onSubmit={handleSearchSubmit} className="relative">
                  <div className="flex items-center gap-3 px-6 py-5 border-b border-border/50">
                    <Search className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                    <Input
                      ref={inputRef}
                      type="text"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="Search diseases, locations, outbreaks..."
                      className="flex-1 border-0 bg-transparent text-lg focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-muted-foreground/60"
                    />
                    {loading && (
                      <Loader2 className="w-5 h-5 animate-spin text-cyan-400 flex-shrink-0" />
                    )}
                    
                    {/* Semantic Search Toggle - Inline */}
                    <button
                      type="button"
                      onClick={() => setSemantic(!semantic)}
                      className={`flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all flex-shrink-0 ${
                        semantic
                          ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400'
                          : 'bg-card/50 border-border/50 text-muted-foreground hover:border-border'
                      }`}
                      title={semantic ? 'Vector Search' : 'Keyword Search'}
                    >
                      <Sparkles className="h-3.5 w-3.5" />
                      <span className="text-xs font-medium hidden sm:inline">
                        {semantic ? 'Vector' : 'Keyword'}
                      </span>
                    </button>
                    
                    <button
                      type="button"
                      onClick={onClose}
                      className="p-1.5 hover:bg-accent rounded-lg transition-colors flex-shrink-0"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                </form>

                {/* Results Section */}
                {suggestions.length > 0 ? (
                  <div className="max-h-[60vh] overflow-y-auto">
                    {suggestions.map((suggestion, idx) => (
                      <motion.button
                        key={suggestion.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        onClick={() => handleSelect(suggestion)}
                        className={`w-full px-6 py-4 text-left transition-all flex items-start justify-between gap-4 group border-b border-border/30 last:border-0 ${
                          idx === selectedIndex
                            ? 'bg-accent/80'
                            : 'hover:bg-accent/50'
                        }`}
                      >
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2 flex-wrap">
                            <span className="font-medium text-foreground group-hover:text-cyan-400 transition-colors">
                              {suggestion.label}
                            </span>
                            <Badge
                              variant={
                                suggestion.type === 'Disease'
                                  ? 'destructive'
                                  : suggestion.type === 'Location'
                                  ? 'default'
                                  : 'secondary'
                              }
                              className="text-xs flex-shrink-0"
                            >
                              {suggestion.type}
                            </Badge>
                          </div>
                          {suggestion.snippet && (
                            <p className="text-sm text-muted-foreground line-clamp-2">
                              {suggestion.snippet}
                            </p>
                          )}
                        </div>
                        {suggestion.score && (
                          <div className="flex-shrink-0 text-sm font-medium mt-1">
                            <div className="flex items-center gap-1 text-cyan-400">
                              <TrendingUp className="w-3 h-3" />
                              {(suggestion.score * 100).toFixed(0)}%
                            </div>
                          </div>
                        )}
                      </motion.button>
                    ))}
                  </div>
                ) : query.trim() && !loading ? (
                  <div className="px-6 py-12 text-center">
                    <p className="text-muted-foreground">
                      No results found for &quot;{query}&quot;
                    </p>
                    <p className="text-sm text-muted-foreground/60 mt-2">
                      Try searching for diseases, locations, or outbreaks
                    </p>
                  </div>
                ) : (
                  <div className="px-6 py-12 text-center">
                    <Search className="w-12 h-12 mx-auto mb-3 text-muted-foreground/40" />
                    <p className="text-muted-foreground">
                      Start typing to search
                    </p>
                    <p className="text-sm text-muted-foreground/60 mt-2">
                      Search across diseases, locations, and outbreaks
                    </p>
                  </div>
                )}

                {/* Footer Hints */}
                <div className="px-6 py-3 bg-muted/30 border-t border-border/50 flex items-center justify-between text-xs text-muted-foreground">
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                      <kbd className="px-2 py-0.5 bg-background/80 border border-border/50 rounded text-xs">↑↓</kbd>
                      Navigate
                    </span>
                    <span className="flex items-center gap-1">
                      <kbd className="px-2 py-0.5 bg-background/80 border border-border/50 rounded text-xs">↵</kbd>
                      Select
                    </span>
                  </div>
                  <span className="flex items-center gap-1">
                    <kbd className="px-2 py-0.5 bg-background/80 border border-border/50 rounded text-xs">Esc</kbd>
                    Close
                  </span>
                </div>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}
