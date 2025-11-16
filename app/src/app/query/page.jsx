'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, Trash2, Code, Database } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export default function QueryPage() {
  const [queryType, setQueryType] = useState('cypher')
  const [query, setQuery] = useState(
    queryType === 'cypher'
      ? 'MATCH (n) RETURN n LIMIT 10'
      : 'SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10'
  )
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)

  async function executeQuery() {
    setLoading(true)
    // Mock execution for now
    setTimeout(() => {
      setResults({
        columns: ['id', 'label', 'type'],
        rows: [
          ['disease:influenza_A', 'Influenza A', 'Disease'],
          ['disease:covid19', 'COVID-19', 'Disease'],
        ],
      })
      setLoading(false)
    }, 1000)
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
            Execute custom SPARQL or Cypher queries against the knowledge graph
          </p>
        </motion.div>

        {/* Query Type Selector */}
        <motion.div
          className="flex gap-2 mb-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.4 }}
        >
          <button
            onClick={() => setQueryType('cypher')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              queryType === 'cypher'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                : 'bg-card/50 text-muted-foreground border border-border/50 hover:border-border'
            }`}
          >
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              Cypher (Neo4j)
            </div>
          </button>
          <button
            onClick={() => setQueryType('sparql')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              queryType === 'sparql'
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                : 'bg-card/50 text-muted-foreground border border-border/50 hover:border-border'
            }`}
          >
            <div className="flex items-center gap-2">
              <Code className="h-4 w-4" />
              SPARQL (RDF)
            </div>
          </button>
        </motion.div>

        {/* Query Editor */}
        <motion.div
          className="mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full h-48 p-4 bg-card/60 backdrop-blur-md border border-border/50 rounded-lg text-foreground font-mono text-sm 
                     focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all
                     placeholder:text-muted-foreground"
            placeholder="Enter your query..."
          />
        </motion.div>

        {/* Actions */}
        <motion.div
          className="flex gap-4 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          <Button
            onClick={executeQuery}
            disabled={loading}
            size="lg"
            className="bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700"
          >
            <Play className="h-4 w-4 mr-2" />
            {loading ? 'Executing...' : 'Run Query'}
          </Button>
          <Button
            onClick={() => setQuery('')}
            variant="outline"
            size="lg"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Clear
          </Button>
        </motion.div>

        {/* Results */}
        <AnimatePresence mode="wait">
          {results && (
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
                <p className="text-sm text-muted-foreground">{results.rows.length} rows</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted/20">
                    <tr>
                      {results.columns.map((col) => (
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
                    {results.rows.map((row, idx) => (
                      <motion.tr
                        key={idx}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.05, duration: 0.3 }}
                        className="border-t border-border/30 hover:bg-muted/20 transition-colors"
                      >
                        {row.map((cell, cellIdx) => (
                          <td
                            key={cellIdx}
                            className="px-4 py-3 text-sm text-muted-foreground font-mono"
                          >
                            {cell}
                          </td>
                        ))}
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Example Queries */}
        <motion.div
          className="mt-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.4 }}
        >
          <h3 className="text-xl font-semibold text-foreground mb-4">Example Queries</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <motion.div
              className="p-4 bg-card/30 backdrop-blur-md border border-border/50 rounded-lg 
                       hover:border-cyan-500/50 hover:shadow-lg hover:shadow-cyan-500/10 
                       cursor-pointer group"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.4 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setQuery('MATCH (d:Disease) RETURN d LIMIT 20')}
            >
              <h4 className="font-medium text-foreground mb-2 group-hover:text-cyan-400 transition-colors duration-200">
                Find all diseases
              </h4>
              <code className="text-xs text-muted-foreground font-mono">
                MATCH (d:Disease) RETURN d LIMIT 20
              </code>
            </motion.div>
            <motion.div
              className="p-4 bg-card/30 backdrop-blur-md border border-border/50 rounded-lg 
                       hover:border-cyan-500/50 hover:shadow-lg hover:shadow-cyan-500/10 
                       cursor-pointer group"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.4 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setQuery('MATCH (d:Disease)-[r]-(n) RETURN d, type(r), n LIMIT 50')}
            >
              <h4 className="font-medium text-foreground mb-2 group-hover:text-cyan-400 transition-colors duration-200">
                Disease relationships
              </h4>
              <code className="text-xs text-muted-foreground font-mono">
                MATCH (d:Disease)-[r]-(n) RETURN d, type(r), n LIMIT 50
              </code>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </main>
  )
}
