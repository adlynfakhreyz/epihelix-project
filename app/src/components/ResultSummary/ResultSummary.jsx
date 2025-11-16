'use client'

import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Sparkles, Info } from 'lucide-react'
import { motion } from 'framer-motion'
import PropTypes from 'prop-types'

/**
 * Result Summary Component
 * Shows LLM-generated summary for search results (entities, relations/facts, subgraphs)
 * 
 * @param {Object} props
 * @param {Object} props.result - Search result data
 * @param {string} props.query - Original search query
 * @param {string} props.summary - LLM-generated summary text
 * @param {boolean} props.loading - Loading state for summary generation
 */
export default function ResultSummary({ result, query, summary, loading = false }) {
  if (!result) return null

  const { type, label } = result

  // Render different layouts based on result type
  const renderContent = () => {
    if (type === 'fact' || type === 'relation') {
      // For facts/relations: subject - predicate - object
      const { subject, predicate, object } = result
      return (
        <div className="mb-4">
          <div className="flex items-center gap-2 flex-wrap mb-3">
            <Badge variant="outline" className="text-cyan-400 border-cyan-500/50">
              {subject?.label || subject}
            </Badge>
            <span className="text-muted-foreground text-sm">→</span>
            <Badge variant="outline" className="text-purple-400 border-purple-500/50">
              {predicate}
            </Badge>
            <span className="text-muted-foreground text-sm">→</span>
            <Badge variant="outline" className="text-pink-400 border-pink-500/50">
              {object?.label || object}
            </Badge>
          </div>
        </div>
      )
    }

    // For entities and subgraphs
    return (
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-foreground mb-2">{label}</h2>
        <Badge variant="outline" className="mb-3">
          {type}
        </Badge>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="mb-6"
    >
      <Card className="border-cyan-500/30 bg-gradient-to-br from-cyan-500/5 via-transparent to-purple-500/5">
        <CardContent className="p-6">
          {/* Result Type Indicator */}
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="h-4 w-4 text-cyan-400" />
            <span className="text-sm font-medium text-cyan-400">
              {type === 'fact' || type === 'relation' ? 'Fact Summary' : 'AI Summary'}
            </span>
          </div>

          {/* Content based on type */}
          {renderContent()}

          {/* LLM-Generated Summary */}
          <div className="prose prose-sm prose-invert max-w-none">
            {loading ? (
              <div className="flex items-center gap-3 text-muted-foreground">
                <div className="w-4 h-4 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
                <span>Generating summary...</span>
              </div>
            ) : summary ? (
              <p className="text-foreground leading-relaxed">{summary}</p>
            ) : (
              <div className="flex items-start gap-3 text-muted-foreground">
                <Info className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <p className="text-sm">
                  Summary will be generated using LLM based on the retrieved context (entity properties, relations, and immediate neighborhood).
                </p>
              </div>
            )}
          </div>

          {/* Query Context */}
          {query && (
            <div className="mt-4 pt-4 border-t border-border/50">
              <p className="text-xs text-muted-foreground">
                Based on your search: <span className="text-foreground font-medium">"{query}"</span>
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

ResultSummary.propTypes = {
  result: PropTypes.shape({
    type: PropTypes.string.isRequired,
    label: PropTypes.string,
    subject: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.shape({
        id: PropTypes.string,
        label: PropTypes.string,
      }),
    ]),
    predicate: PropTypes.string,
    object: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.shape({
        id: PropTypes.string,
        label: PropTypes.string,
      }),
    ]),
  }),
  query: PropTypes.string,
  summary: PropTypes.string,
  loading: PropTypes.bool,
}
