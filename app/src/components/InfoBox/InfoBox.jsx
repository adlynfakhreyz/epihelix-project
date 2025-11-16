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
 */
export default function InfoBox({ entity, loading = false }) {
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
              {Object.entries(entity.properties).map(([key, value]) => (
                <div key={key} className="flex flex-col">
                  <dt className="text-sm text-muted-foreground capitalize mb-1">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </dt>
                  <dd className="text-foreground font-medium">
                    {typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}/)
                      ? formatDate(value)
                      : String(value)}
                  </dd>
                </div>
              ))}
            </dl>
          </CardContent>
        </Card>
      )}

      {/* Relations */}
      {entity.relations && entity.relations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Relations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {entity.relations.map((rel, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 p-3 bg-accent/50 rounded-lg border border-border"
                >
                  <span className="text-sm text-muted-foreground font-mono">{rel.pred}</span>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  <a
                    href={`/entity/${rel.obj.id}`}
                    className="text-cyan-400 hover:text-cyan-300 transition-colors font-medium"
                  >
                    {rel.obj.label}
                  </a>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Provenance */}
      {entity.provenance && entity.provenance.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Data Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {entity.provenance.map((prov, idx) => (
                <div key={idx} className="flex items-start gap-2 text-sm">
                  <span className="font-medium text-foreground">{prov.source}</span>
                  {prov.uri && (
                    <a
                      href={prov.uri}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-cyan-400 hover:underline inline-flex items-center gap-1"
                    >
                      View source
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                  {prov.query && <span className="text-muted-foreground">({prov.query})</span>}
                </div>
              ))}
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
        pred: PropTypes.string,
        obj: PropTypes.shape({
          id: PropTypes.string,
          label: PropTypes.string,
        }),
      })
    ),
    provenance: PropTypes.arrayOf(
      PropTypes.shape({
        source: PropTypes.string,
        uri: PropTypes.string,
        query: PropTypes.string,
      })
    ),
  }),
  loading: PropTypes.bool,
}
