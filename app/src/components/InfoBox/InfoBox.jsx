'use client'

import React from 'react'
import PropTypes from 'prop-types'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ExternalLink, ArrowRight } from 'lucide-react'
import { fadeIn } from '../../lib/animations'
import { formatDate } from '../../lib/utils'

/**
 * InfoBox - displays detailed entity information
 * @param {Object} props
 * @param {Object} props.entity - Full entity data
 * @param {boolean} props.loading - Loading state
 * @param {boolean} props.showRelations - Whether to display relations section (default: true)
 */
export default function InfoBox({ entity, loading = false, showRelations = true }) {
  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/3" />
            <div className="h-4 bg-muted rounded w-1/2" />
            <div className="space-y-2">
              <div className="h-4 bg-muted rounded" />
              <div className="h-4 bg-muted rounded w-5/6" />
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!entity) {
    return (
      <Card>
        <CardContent className="p-6 text-center text-muted-foreground">
          Entity not found
        </CardContent>
      </Card>
    )
  }

  // Helper to format property keys
  const formatKey = (key) => {
    return key
      .replace(/([A-Z])/g, ' $1')
      .replace(/_/g, ' ')
      .trim()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  // Helper to format property values
  const formatValue = (value) => {
    if (value === null || value === undefined) return 'N/A'
    if (typeof value === 'boolean') return value ? 'Yes' : 'No'
    if (typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}/)) {
      return formatDate(value)
    }
    if (Array.isArray(value)) {
      return value.join(', ')
    }
    if (typeof value === 'number') {
      return value.toLocaleString()
    }
    return String(value)
  }

  // Skip these properties from display (meta/technical fields)
  const skipProperties = ['enriched', 'enrichedAt', 'dbpediaEnriched', 'externalSource', 
                          'wikidataId', 'dbpediaUri', 'wikipediaUrl', 'dataSource', 'embedding']

  return (
    <motion.div {...fadeIn} className="space-y-6">
      {/* Header */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-foreground mb-3">{entity.label}</h1>
              <div className="flex items-center gap-2 flex-wrap">
                <Badge variant="default" className="text-sm">
                  {entity.type}
                </Badge>
                {entity.id && (
                  <span className="text-sm text-muted-foreground font-mono">{entity.id}</span>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Properties */}
      {entity.properties && Object.keys(entity.properties).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Properties</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(entity.properties)
                .filter(([key]) => !skipProperties.includes(key))
                .map(([key, value]) => (
                  <div key={key} className="flex flex-col space-y-1">
                    <dt className="text-sm text-muted-foreground font-medium">
                      {formatKey(key)}
                    </dt>
                    <dd className="text-foreground">
                      {formatValue(value)}
                    </dd>
                  </div>
                ))}
            </dl>
          </CardContent>
        </Card>
      )}

      {/* Relations */}
      {showRelations && entity.relations && entity.relations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>
              Relationships ({entity.relations.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {entity.relations.map((rel, idx) => {
                const isOutgoing = rel.direction === 'outgoing'
                const relationLabel = rel.predicate
                  .replace(/_/g, ' ')
                  .toLowerCase()
                  .replace(/\b\w/g, l => l.toUpperCase())
                
                return (
                  <div
                    key={idx}
                    className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg border border-border/50 
                             hover:border-cyan-500/30 hover:bg-muted/50 transition-all group"
                  >
                    {!isOutgoing && (
                      <span className="text-xs px-2 py-1 bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded">
                        ← incoming
                      </span>
                    )}
                    <span className="text-sm text-muted-foreground font-medium">
                      {relationLabel}
                    </span>
                    <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-cyan-400 transition-colors" />
                    <a
                      href={`/entity/${rel.object.id}`}
                      className="text-cyan-400 hover:text-cyan-300 transition-colors font-medium flex items-center gap-2"
                    >
                      {rel.object.label}
                      <Badge variant="outline" className="text-xs">
                        {rel.object.type}
                      </Badge>
                    </a>
                    {isOutgoing && (
                      <span className="text-xs px-2 py-1 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 rounded ml-auto">
                        outgoing →
                      </span>
                    )}
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Data Source Info */}
      {entity.properties && (entity.properties.wikidataId || entity.properties.dbpediaUri || entity.properties.dataSource) && (
        <Card>
          <CardHeader>
            <CardTitle>Data Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {entity.properties.dataSource && (
                <div className="flex items-start gap-2 text-sm">
                  <span className="font-medium text-foreground">Internal Dataset:</span>
                  <span className="text-muted-foreground">{entity.properties.dataSource}</span>
                </div>
              )}
              {entity.properties.wikidataId && (
                <div className="flex items-start gap-2 text-sm">
                  <span className="font-medium text-foreground">Wikidata:</span>
                  <a
                    href={`https://www.wikidata.org/wiki/${entity.properties.wikidataId}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-cyan-400 hover:underline inline-flex items-center gap-1"
                  >
                    {entity.properties.wikidataId}
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              )}
              {entity.properties.dbpediaUri && (
                <div className="flex items-start gap-2 text-sm">
                  <span className="font-medium text-foreground">DBpedia:</span>
                  <a
                    href={entity.properties.dbpediaUri}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-cyan-400 hover:underline inline-flex items-center gap-1"
                  >
                    View on DBpedia
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              )}
              {entity.properties.wikipediaUrl && (
                <div className="flex items-start gap-2 text-sm">
                  <span className="font-medium text-foreground">Wikipedia:</span>
                  <a
                    href={entity.properties.wikipediaUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-cyan-400 hover:underline inline-flex items-center gap-1"
                  >
                    View article
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </motion.div>
  )
}

InfoBox.propTypes = {
  entity: PropTypes.shape({
    id: PropTypes.string,
    label: PropTypes.string,
    type: PropTypes.string,
    properties: PropTypes.object,
    relations: PropTypes.arrayOf(
      PropTypes.shape({
        predicate: PropTypes.string,
        direction: PropTypes.string,
        object: PropTypes.shape({
          id: PropTypes.string,
          label: PropTypes.string,
          type: PropTypes.string,
        }),
      })
    ),
  }),
  loading: PropTypes.bool,
}
