'use client'

import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { motion, AnimatePresence } from 'framer-motion'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Loader2 } from 'lucide-react'
import { debounce } from '../../lib/utils'
import { search } from '../../lib/api'
import { slideDown, listItem } from '../../lib/animations'

/**
 * SearchBar component with live suggestions
 * @param {Object} props
 * @param {string} props.value - Controlled value
 * @param {Function} props.onChange - Change handler
 * @param {Function} props.onSelect - Selection handler (receives entity ID)
 * @param {string} props.placeholder - Input placeholder
 * @param {boolean} props.semantic - Enable semantic search
 */
export default function SearchBar({
  value = '',
  onChange = () => {},
  onSelect = () => {},
  placeholder = 'Search diseases, locations, outbreaks...',
  semantic = false,
}) {
  const [query, setQuery] = useState(value)
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [loading, setLoading] = useState(false)

  // Debounced search
  useEffect(() => {
    const fetchSuggestions = debounce(async (q) => {
      if (!q.trim()) {
        setSuggestions([])
        return
      }

      setLoading(true)
      try {
        const results = await search(q, { limit: 5, semantic })
        setSuggestions(results)
        setShowSuggestions(true)
      } catch (error) {
        console.error('Search error:', error)
      } finally {
        setLoading(false)
      }
    }, 300)

    fetchSuggestions(query)
  }, [query, semantic])

  function handleChange(e) {
    const val = e.target.value
    setQuery(val)
    onChange(val)
  }

  function handleSelect(entity) {
    setQuery(entity.label)
    setShowSuggestions(false)
    onSelect(entity.id)
  }

  function handleKeyDown(e) {
    if (e.key === 'Escape') {
      setShowSuggestions(false)
    }
  }

  return (
    <div className="relative w-full max-w-2xl">
      <div className="relative">
        <Input
          type="text"
          value={query}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
          placeholder={placeholder}
          className="w-full h-12 text-base"
        />

        {/* Loading indicator */}
        {loading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
          </div>
        )}
      </div>

      {/* Suggestions dropdown */}
      <AnimatePresence>
        {showSuggestions && suggestions.length > 0 && (
          <motion.div
            {...slideDown}
            className="absolute z-50 w-full mt-2 bg-card border border-border rounded-lg shadow-xl overflow-hidden"
          >
            {suggestions.map((suggestion, idx) => (
              <motion.button
                key={suggestion.id}
                variants={listItem}
                onClick={() => handleSelect(suggestion)}
                className="w-full px-4 py-4 text-left hover:bg-accent transition-colors flex items-start justify-between gap-4 group border-b border-border last:border-0"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <span className="font-medium text-foreground group-hover:text-cyan-400 transition-colors">
                      {suggestion.label}
                    </span>
                    <Badge variant="outline" className="text-xs flex-shrink-0">
                      {suggestion.type}
                    </Badge>
                  </div>
                  {suggestion.snippet && (
                    <p className="text-sm text-muted-foreground line-clamp-2 pr-2">{suggestion.snippet}</p>
                  )}
                </div>
                {suggestion.score && (
                  <div className="flex-shrink-0 text-sm text-cyan-400 font-medium mt-1">
                    {(suggestion.score * 100).toFixed(0)}%
                  </div>
                )}
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Click outside to close */}
      {showSuggestions && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowSuggestions(false)}
        />
      )}
    </div>
  )
}

SearchBar.propTypes = {
  value: PropTypes.string,
  onChange: PropTypes.func,
  onSelect: PropTypes.func,
  placeholder: PropTypes.string,
  semantic: PropTypes.bool,
}
