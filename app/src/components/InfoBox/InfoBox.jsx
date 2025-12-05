'use client'

import React from 'react'
import PropTypes from 'prop-types'
import { motion } from 'framer-motion'
import Image from 'next/image'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ExternalLink, ArrowRight, ImageIcon } from 'lucide-react'
import { fadeIn } from '../../lib/animations'
import { formatDate } from '../../lib/utils'
import TimeSeriesChart from '../Charts/TimeSeriesChart'

/**
 * InfoBox - displays detailed entity information
 * @param {Object} props
 * @param {Object} props.entity - Full entity data
 * @param {boolean} props.loading - Loading state
 * @param {boolean} props.showRelations - Whether to display relations section (default: true)
 */
export default function InfoBox({ entity, loading = false, showRelations = true }) {
  const [showAllRelations, setShowAllRelations] = React.useState(false)
  const INITIAL_RELATIONS_DISPLAY = 5

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
    
    // Handle DBpedia URIs - extract readable name
    if (typeof value === 'string' && value.startsWith('http://dbpedia.org/resource/')) {
      const name = value.replace('http://dbpedia.org/resource/', '')
      return name.replace(/_/g, ' ') // Replace underscores with spaces
    }
    
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
                          'wikidataId', 'dbpediaUri', 'wikipediaUrl', 'dataSource', 'embedding',
                          'thumbnailUrl', 'countryThumbnail', 'wikipediaAbstract', 'countryAbstract']

  // Get image URL based on entity type
  const getImageUrl = () => {
    if (!entity.properties) return null

    // For diseases: thumbnailUrl from DBpedia
    if (entity.type === 'Disease' && entity.properties.thumbnailUrl) {
      return entity.properties.thumbnailUrl
    }

    // For countries: countryThumbnail from DBpedia
    if (entity.type === 'Country' && entity.properties.countryThumbnail) {
      return entity.properties.countryThumbnail
    }

    return null
  }

  // Get abstract/description from enriched data
  const getDescription = () => {
    if (!entity.properties) return null

    // Priority order: specific abstracts, then general description
    if (entity.type === 'Disease' && entity.properties.wikipediaAbstract) {
      return entity.properties.wikipediaAbstract
    }

    if (entity.type === 'Country' && entity.properties.countryAbstract) {
      return entity.properties.countryAbstract
    }

    if (entity.properties.description) {
      return entity.properties.description
    }

    return null
  }

  const imageUrl = getImageUrl()
  const description = getDescription()
  const isEnriched = entity.properties?.enriched || entity.properties?.dbpediaEnriched

  return (
    <motion.div {...fadeIn} className="space-y-6">
      {/* Header with Image */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start gap-6">
            {/* Entity Image */}
            {imageUrl && (
              <div className="flex-shrink-0">
                <div className="relative w-48 h-48 rounded-lg overflow-hidden bg-muted border border-border/50">
                  <Image
                    src={imageUrl}
                    alt={entity.label}
                    fill
                    className="object-cover"
                    sizes="192px"
                    unoptimized
                  />
                </div>
              </div>
            )}

            {/* Header Info */}
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-foreground mb-3">{entity.label}</h1>
              <div className="flex items-center gap-2 flex-wrap mb-4">
                <Badge variant="default" className="text-sm">
                  {entity.type}
                </Badge>
                {isEnriched && (
                  <Badge variant="outline" className="text-sm border-cyan-500/30 text-cyan-400">
                    Enriched from External Sources
                  </Badge>
                )}
                {entity.id && (
                  <span className="text-sm text-muted-foreground font-mono">{entity.id}</span>
                )}
              </div>

              {/* Description from enriched data */}
              {description && (
                <div className="mt-4">
                  <p className="text-sm text-muted-foreground leading-relaxed line-clamp-6">
                    {description}
                  </p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Enriched Properties Section - Disease-specific */}
      {entity.type === 'Disease' && entity.properties && (
        <>
          {/* Symptoms */}
          {entity.properties.symptoms && entity.properties.symptoms.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Symptoms
                  <Badge variant="outline" className="text-xs">Wikidata</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {entity.properties.symptoms.map((symptom, idx) => (
                    <Badge key={idx} variant="secondary" className="text-sm">
                      {symptom}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Treatments */}
          {((entity.properties.drugs && entity.properties.drugs.length > 0) ||
            (entity.properties.possibleTreatments && entity.properties.possibleTreatments.length > 0)) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Treatments
                  <Badge variant="outline" className="text-xs">Wikidata</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {entity.properties.drugs && entity.properties.drugs.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">Drugs</h4>
                    <div className="flex flex-wrap gap-2">
                      {entity.properties.drugs.map((drug, idx) => (
                        <Badge key={idx} variant="default" className="text-sm">
                          {drug}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                {entity.properties.possibleTreatments && entity.properties.possibleTreatments.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">Possible Treatments</h4>
                    <div className="flex flex-wrap gap-2">
                      {entity.properties.possibleTreatments.map((treatment, idx) => (
                        <Badge key={idx} variant="outline" className="text-sm">
                          {treatment}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Transmission & Risk Factors */}
          {((entity.properties.transmissionMethods && entity.properties.transmissionMethods.length > 0) ||
            (entity.properties.riskFactors && entity.properties.riskFactors.length > 0)) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Transmission & Risk Factors
                  <Badge variant="outline" className="text-xs">Wikidata</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {entity.properties.transmissionMethods && entity.properties.transmissionMethods.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">Transmission Methods</h4>
                    <div className="flex flex-wrap gap-2">
                      {entity.properties.transmissionMethods.map((method, idx) => (
                        <Badge key={idx} variant="destructive" className="text-sm">
                          {method}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                {entity.properties.riskFactors && entity.properties.riskFactors.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">Risk Factors</h4>
                    <div className="flex flex-wrap gap-2">
                      {entity.properties.riskFactors.map((factor, idx) => (
                        <Badge key={idx} variant="outline" className="text-sm border-orange-500/30 text-orange-400">
                          {factor}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Medical Classifications */}
          {(entity.properties.icd10 || entity.properties.mesh) && (
            <Card>
              <CardHeader>
                <CardTitle>Medical Classifications</CardTitle>
              </CardHeader>
              <CardContent>
                <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {entity.properties.icd10 && (
                    <div className="flex flex-col space-y-1">
                      <dt className="text-sm text-muted-foreground font-medium">ICD-10 Code</dt>
                      <dd className="text-foreground font-mono">{entity.properties.icd10}</dd>
                    </div>
                  )}
                  {entity.properties.mesh && (
                    <div className="flex flex-col space-y-1">
                      <dt className="text-sm text-muted-foreground font-medium">MeSH ID</dt>
                      <dd className="text-foreground font-mono">{entity.properties.mesh}</dd>
                    </div>
                  )}
                  {entity.properties.incubationPeriod && (
                    <div className="flex flex-col space-y-1">
                      <dt className="text-sm text-muted-foreground font-medium">Incubation Period</dt>
                      <dd className="text-foreground">{entity.properties.incubationPeriod}</dd>
                    </div>
                  )}
                </dl>
              </CardContent>
            </Card>
          )}

          {/* Time-Series Data Visualization for Outbreaks */}
          <TimeSeriesChart
            entityId={entity.id}
            entityType={entity.type}
            dataType="outbreaks"
            title="Outbreak Cases Over Time"
            description="Visualize historical outbreak data with filters for time period and countries"
          />

          {/* Time-Series Data Visualization for Vaccinations */}
          {entity.properties?.vaccinePreventable && (
            <TimeSeriesChart
              entityId={entity.id}
              entityType={entity.type}
              dataType="vaccinations"
              title="Vaccination Coverage Over Time"
              description="Track vaccination rates across different countries and time periods"
            />
          )}
        </>
      )}

      {/* Enriched Properties Section - Country-specific */}
      {entity.type === 'Country' && entity.properties && (
        <>
          {/* Demographics & Geography */}
          {(entity.properties.population || entity.properties.capital || entity.properties.continent ||
            entity.properties.areaKm2 || entity.properties.areaTotal) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Demographics & Geography
                  <Badge variant="outline" className="text-xs">Wikidata + DBpedia</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {entity.properties.population && (
                    <div className="flex flex-col space-y-1">
                      <dt className="text-sm text-muted-foreground font-medium">Population</dt>
                      <dd className="text-foreground">
                        {entity.properties.population.toLocaleString()}
                      </dd>
                    </div>
                  )}
                  {entity.properties.capital && (
                    <div className="flex flex-col space-y-1">
                      <dt className="text-sm text-muted-foreground font-medium">Capital</dt>
                      <dd className="text-foreground">{formatValue(entity.properties.capital)}</dd>
                    </div>
                  )}
                  {entity.properties.continent && (
                    <div className="flex flex-col space-y-1">
                      <dt className="text-sm text-muted-foreground font-medium">Continent</dt>
                      <dd className="text-foreground">{entity.properties.continent}</dd>
                    </div>
                  )}
                  {(entity.properties.areaKm2 || entity.properties.areaTotal) && (
                    <div className="flex flex-col space-y-1">
                      <dt className="text-sm text-muted-foreground font-medium">Area</dt>
                      <dd className="text-foreground">
                        {(entity.properties.areaKm2 || entity.properties.areaTotal).toLocaleString()} km²
                      </dd>
                    </div>
                  )}
                  {entity.properties.populationDensity && (
                    <div className="flex flex-col space-y-1">
                      <dt className="text-sm text-muted-foreground font-medium">Population Density</dt>
                      <dd className="text-foreground">
                        {entity.properties.populationDensity.toFixed(1)} per km²
                      </dd>
                    </div>
                  )}
                  {entity.properties.officialLanguage && (
                    <div className="flex flex-col space-y-1">
                      <dt className="text-sm text-muted-foreground font-medium">Official Language</dt>
                      <dd className="text-foreground">{entity.properties.officialLanguage}</dd>
                    </div>
                  )}
                </dl>
              </CardContent>
            </Card>
          )}

          {/* Economic & Social Data */}
          {(entity.properties.gdp || entity.properties.lifeExpectancy || entity.properties.governmentType ||
            entity.properties.currency) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Economic & Social Data
                  <Badge variant="outline" className="text-xs">Wikidata + DBpedia</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {entity.properties.gdp && (
                    <div className="flex flex-col space-y-1">
                      <dt className="text-sm text-muted-foreground font-medium">GDP (Nominal)</dt>
                      <dd className="text-foreground">
                        ${(entity.properties.gdp / 1_000_000_000).toFixed(2)}B USD
                      </dd>
                    </div>
                  )}
                  {entity.properties.lifeExpectancy && (
                    <div className="flex flex-col space-y-1">
                      <dt className="text-sm text-muted-foreground font-medium">Life Expectancy</dt>
                      <dd className="text-foreground">{entity.properties.lifeExpectancy} years</dd>
                    </div>
                  )}
                  {entity.properties.governmentType && (
                    <div className="flex flex-col space-y-1">
                      <dt className="text-sm text-muted-foreground font-medium">Government Type</dt>
                      <dd className="text-foreground">{formatValue(entity.properties.governmentType)}</dd>
                    </div>
                  )}
                  {entity.properties.currency && (
                    <div className="flex flex-col space-y-1">
                      <dt className="text-sm text-muted-foreground font-medium">Currency</dt>
                      <dd className="text-foreground">{formatValue(entity.properties.currency)}</dd>
                    </div>
                  )}
                </dl>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* All Other Properties */}
      {entity.properties && Object.keys(entity.properties).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Additional Properties</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(entity.properties)
                .filter(([key]) => {
                  // Skip technical fields and already displayed enriched fields
                  const enrichedFields = [
                    ...skipProperties,
                    'symptoms', 'drugs', 'possibleTreatments', 'transmissionMethods', 'riskFactors',
                    'icd10', 'mesh', 'incubationPeriod', 'description',
                    'population', 'capital', 'continent', 'areaKm2', 'areaTotal', 'populationDensity',
                    'officialLanguage', 'gdp', 'lifeExpectancy', 'governmentType', 'currency'
                  ]
                  return !enrichedFields.includes(key)
                })
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
            <div className="flex items-center justify-between">
              <CardTitle>
                Relationships ({entity.relations.length})
              </CardTitle>
              <div className="flex items-center gap-2">
                {/* Show unique relationship types */}
                {Array.from(new Set(entity.relations.map(r => r.predicate))).slice(0, 3).map((predicate, idx) => (
                  <Badge key={idx} variant="outline" className="text-xs bg-blue-500/10 text-blue-400 border-blue-500/30">
                    {predicate.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                  </Badge>
                ))}
                {Array.from(new Set(entity.relations.map(r => r.predicate))).length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{Array.from(new Set(entity.relations.map(r => r.predicate))).length - 3} more
                  </Badge>
                )}
              </div>
            </div>
            {entity.relations.length > INITIAL_RELATIONS_DISPLAY && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAllRelations(!showAllRelations)}
                className="text-xs text-cyan-400 hover:text-cyan-300 mt-2"
              >
                {showAllRelations ? 'Show Less' : `Show All (${entity.relations.length})`}
              </Button>
            )}
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {(showAllRelations
                ? entity.relations
                : entity.relations.slice(0, INITIAL_RELATIONS_DISPLAY)
              ).map((rel, idx) => {
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

            {/* Show More Button (when collapsed and more items exist) */}
            {!showAllRelations && entity.relations.length > INITIAL_RELATIONS_DISPLAY && (
              <div className="mt-4 text-center">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowAllRelations(true)}
                  className="w-full text-cyan-400 hover:text-cyan-300 border-cyan-500/30 hover:border-cyan-500/50"
                >
                  Show {entity.relations.length - INITIAL_RELATIONS_DISPLAY} More Relationships
                </Button>
              </div>
            )}
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
