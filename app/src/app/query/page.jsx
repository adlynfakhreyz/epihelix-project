'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, Trash2, Database, AlertCircle, History, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useQueryConsole } from '@/hooks/useQuery'

export default function QueryPage() {
  const [query, setQuery] = useState('MATCH (d:Disease) RETURN d.id, d.name, d.eradicated LIMIT 10')
  const [showHistory, setShowHistory] = useState(false)
  
  const {
    execute,
    clearHistory,
    history,
    isLoading,
    error,
    data
  } = useQueryConsole()

  function handleExecute() {
    if (query.trim()) {
      execute(query, 'cypher')
    }
  }

  function handleClear() {
    setQuery('')
  }

  function loadFromHistory(queryText) {
    setQuery(queryText)
    setShowHistory(false)
  }

  function formatTimestamp(timestamp) {
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: 'numeric', 
      minute: '2-digit' 
    })
  }

  return (
    <main className="flex-1 py-8 md:py-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl">
        {/* Header */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight mb-2">
            <span className="relative inline-block">
              <span className="bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
                Query Console
              </span>
              <div className="absolute -bottom-2 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-cyan-500 to-transparent"></div>
            </span>
          </h1>
          <p className="text-muted-foreground mt-4">
            Execute custom Cypher queries against the Neo4j knowledge graph
          </p>
          <div className="flex items-center gap-2 mt-2">
            <Database className="h-4 w-4 text-cyan-400" />
            <span className="text-sm text-cyan-400 font-medium">Cypher (Neo4j)</span>
          </div>
        </motion.div>

        {/* Query Editor */}
        <motion.div
          className="mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.4 }}
        >
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                handleExecute()
              }
            }}
            className="w-full h-48 p-4 bg-card/60 backdrop-blur-md border border-border/50 rounded-lg text-foreground font-mono text-sm 
                     focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all
                     placeholder:text-muted-foreground"
            placeholder="Enter your Cypher query... (Ctrl/Cmd + Enter to execute)"
          />
        </motion.div>

        {/* Actions */}
        <motion.div
          className="flex gap-4 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <Button
            onClick={handleExecute}
            disabled={isLoading || !query.trim()}
            size="lg"
            className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700"
          >
            <Play className="h-4 w-4 mr-2" />
            {isLoading ? 'Executing...' : 'Run Query'}
          </Button>
          <Button
            onClick={handleClear}
            variant="outline"
            size="lg"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Clear
          </Button>
          {history.length > 0 && (
            <>
              <Button
                onClick={() => setShowHistory(!showHistory)}
                variant="outline"
                size="lg"
                className="border-cyan-500/50 hover:bg-cyan-500/10"
              >
                <History className="h-4 w-4 mr-2" />
                History ({history.length})
              </Button>
              <Button
                onClick={clearHistory}
                variant="ghost"
                size="lg"
                className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Clear History
              </Button>
            </>
          )}
        </motion.div>

        {/* Query History Panel */}
        <AnimatePresence>
          {showHistory && history.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0, marginBottom: 0 }}
              animate={{ opacity: 1, height: 'auto', marginBottom: 24 }}
              exit={{ opacity: 0, height: 0, marginBottom: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="bg-card/50 backdrop-blur-md border border-border/50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                  <History className="h-5 w-5 text-cyan-400" />
                  Query History
                </h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {[...history].reverse().map((item, idx) => (
                    <motion.div
                      key={history.length - idx - 1}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="p-3 bg-muted/20 hover:bg-muted/40 rounded-lg border border-border/30 
                               hover:border-cyan-500/50 cursor-pointer transition-all group"
                      onClick={() => loadFromHistory(item.query)}
                    >
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {formatTimestamp(item.timestamp)}
                        </div>
                        <div className="text-xs text-cyan-400 font-medium">
                          {item.result?.count || item.result?.rows?.length || 0} rows
                        </div>
                      </div>
                      <code className="text-sm text-foreground font-mono block overflow-hidden text-ellipsis whitespace-nowrap group-hover:text-cyan-300 transition-colors">
                        {item.query.split('\n')[0]}
                      </code>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg"
          >
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-400 mt-0.5" />
              <div>
                <h4 className="font-medium text-red-400 mb-1">Query Error</h4>
                <p className="text-sm text-red-300">
                  {error.message || 'Failed to execute query'}
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Results */}
        <AnimatePresence mode="wait">
          {data && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.6 }}
              className="bg-card/50 backdrop-blur-md border border-border/50 rounded-lg overflow-hidden"
            >
              <div className="p-4 border-b border-border/50">
                <h3 className="text-lg font-semibold text-foreground">Results</h3>
                <p className="text-sm text-muted-foreground">{data.count || data.rows?.length || 0} rows</p>
              </div>
              <div className="overflow-x-auto">
                {data.rows && data.rows.length > 0 ? (
                  <table className="w-full">
                    <thead className="bg-muted/20">
                      <tr>
                        {data.columns.map((col) => (
                          <th
                            key={col}
                            className="px-4 py-3 text-left text-sm font-medium text-foreground"
                          >
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {data.rows.map((row, idx) => (
                        <motion.tr
                          key={idx}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.02, duration: 0.3 }}
                          className="border-t border-border/30 hover:bg-muted/20 transition-colors"
                        >
                          {row.map((cell, cellIdx) => (
                            <td
                              key={cellIdx}
                              className="px-4 py-3 text-sm text-muted-foreground font-mono"
                            >
                              {typeof cell === 'object' ? JSON.stringify(cell, null, 2) : String(cell)}
                            </td>
                          ))}
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="p-8 text-center text-muted-foreground">
                    No results returned
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Example Queries */}
        <motion.div
          className="mt-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          <h3 className="text-xl font-semibold text-foreground mb-4">Example Queries</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              {
                title: 'All Diseases',
                query: 'MATCH (d:Disease) RETURN d.id, d.name, d.eradicated ORDER BY d.name LIMIT 20'
              },
              {
                title: 'COVID-19 Deaths by Country',
                query: `MATCH (o:Outbreak)-[:OCCURRED_IN]->(c:Country)
MATCH (o)-[:CAUSED_BY]->(d:Disease {id: 'covid19'})
WHERE o.excessDeaths IS NOT NULL
RETURN c.name, SUM(o.excessDeaths) as totalDeaths
ORDER BY totalDeaths DESC LIMIT 10`
              },
              {
                title: 'Malaria Cases Over Time',
                query: `MATCH (o:Outbreak)-[:CAUSED_BY]->(d:Disease {id: 'malaria'})
WHERE o.year >= 2015 AND o.cases IS NOT NULL
RETURN o.year, SUM(o.cases) as totalCases
ORDER BY o.year`
              },
              {
                title: 'Countries with Most Outbreaks',
                query: `MATCH (c:Country)<-[:OCCURRED_IN]-(o:Outbreak)
RETURN c.name, c.code, COUNT(o) as outbreakCount
ORDER BY outbreakCount DESC LIMIT 15`
              }
            ].map((example, idx) => (
              <motion.div
                key={idx}
                className="p-4 bg-card/30 backdrop-blur-md border border-border/50 rounded-lg 
                         hover:border-cyan-500/50 hover:shadow-lg hover:shadow-cyan-500/10 
                         cursor-pointer group transition-all"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + idx * 0.1, duration: 0.4 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setQuery(example.query)}
              >
                <h4 className="font-medium text-foreground mb-2 group-hover:text-cyan-400 transition-colors duration-200">
                  {example.title}
                </h4>
                <code className="text-xs text-muted-foreground font-mono block overflow-hidden text-ellipsis whitespace-nowrap">
                  {example.query.split('\n')[0]}...
                </code>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </main>
  )
}
