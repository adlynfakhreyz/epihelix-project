'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ExternalLink, MapPin, Calendar, Users, TrendingUp } from 'lucide-react'
import { motion } from 'framer-motion'
import PropTypes from 'prop-types'

/**
 * Google-style Knowledge Panel Component
 * Shows entity information, properties, and quick facts in a card format
 * 
 * @param {Object} props
 * @param {Object} props.entity - Entity data with properties and relations
 */
export default function KnowledgePanel({ entity }) {
  if (!entity) return null

  const {
    id,
    label,
    type,
    description,
    image,
    properties = {},
    relations = [],
    source,
  } = entity

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="sticky top-6">
        <CardHeader>
          {/* Entity Image */}
          {image && (
            <div className="mb-4 rounded-lg overflow-hidden bg-muted">
              <img
                src={image}
                alt={label}
                className="w-full h-48 object-cover"
              />
            </div>
          )}

          {/* Title and Type */}
          <div>
            <CardTitle className="text-xl mb-2">{label}</CardTitle>
            <Badge variant="outline" className="mb-3">
              {type}
            </Badge>
          </div>

          {/* Description */}
          {description && (
            <p className="text-sm text-muted-foreground leading-relaxed">
              {description}
            </p>
          )}
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Key Properties */}
          {Object.keys(properties).length > 0 && (
            <div>
              <h3 className="text-sm font-semibold mb-3 text-foreground">Key Information</h3>
              <div className="space-y-3">
                {properties.location && (
                  <div className="flex items-start gap-3">
                    <MapPin className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="text-xs text-muted-foreground">Location</div>
                      <div className="text-sm text-foreground">{properties.location}</div>
                    </div>
                  </div>
                )}

                {properties.date && (
                  <div className="flex items-start gap-3">
                    <Calendar className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="text-xs text-muted-foreground">Date</div>
                      <div className="text-sm text-foreground">{properties.date}</div>
                    </div>
                  </div>
                )}

                {properties.cases && (
                  <div className="flex items-start gap-3">
                    <Users className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="text-xs text-muted-foreground">Cases</div>
                      <div className="text-sm text-foreground">{properties.cases.toLocaleString()}</div>
                    </div>
                  </div>
                )}

                {properties.deaths && (
                  <div className="flex items-start gap-3">
                    <TrendingUp className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="text-xs text-muted-foreground">Deaths</div>
                      <div className="text-sm text-foreground">{properties.deaths.toLocaleString()}</div>
                    </div>
                  </div>
                )}

                {/* Additional properties */}
                {Object.entries(properties).map(([key, value]) => {
                  // Skip these properties
                  if (['location', 'date', 'cases', 'deaths', 'image', 'description', 'embedding', 'enriched', 'enrichedAt', 'dbpediaEnriched', 'wikidataId', 'dbpediaUri'].includes(key)) {
                    return null
                  }
                  return (
                    <div key={key} className="flex items-start gap-3">
                      <div className="h-4 w-4 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <div className="text-xs text-muted-foreground capitalize">
                          {key.replace(/_/g, ' ')}
                        </div>
                        <div className="text-sm text-foreground">
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Related Entities */}
          {relations && relations.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold mb-3 text-foreground">Related</h3>
              <div className="space-y-2">
                {relations.slice(0, 5).map((relation, index) => (
                  <div key={index} className="text-sm">
                    <span className="text-muted-foreground">{relation.pred}: </span>
                    <a
                      href={`/entity/${relation.obj?.id || relation.obj}`}
                      className="text-cyan-400 hover:text-cyan-300 hover:underline transition-colors"
                    >
                      {relation.obj?.label || relation.obj}
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Source Link */}
          {source && (
            <div className="pt-4 border-t border-border/50">
              <a
                href={source}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors group"
              >
                <ExternalLink className="h-4 w-4 group-hover:text-cyan-400 transition-colors" />
                <span>View source</span>
              </a>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

KnowledgePanel.propTypes = {
  entity: PropTypes.shape({
    id: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
    description: PropTypes.string,
    image: PropTypes.string,
    properties: PropTypes.object,
    relations: PropTypes.arrayOf(
      PropTypes.shape({
        pred: PropTypes.string,
        obj: PropTypes.oneOfType([
          PropTypes.string,
          PropTypes.shape({
            id: PropTypes.string,
            label: PropTypes.string,
          }),
        ]),
      })
    ),
    source: PropTypes.string,
  }),
}
