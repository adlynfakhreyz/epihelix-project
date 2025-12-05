'use client'

import React, { useState, useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import { ComposableMap, Geographies, Geography, ZoomableGroup } from 'react-simple-maps'
import { scaleLinear } from 'd3-scale'
import { MapPin, Calendar, Activity, Info, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"

export default function HeatmapPage() {
  const [diseases, setDiseases] = useState([])
  const [selectedDisease, setSelectedDisease] = useState(null)
  const [heatmapData, setHeatmapData] = useState(null)
  const [selectedYear, setSelectedYear] = useState(null)
  const [selectedCountry, setSelectedCountry] = useState(null)
  const [loading, setLoading] = useState(false)

  // Fetch diseases on mount
  useEffect(() => {
    fetchDiseases()
  }, [])

  // Fetch heatmap data when disease or year changes
  useEffect(() => {
    if (selectedDisease) {
      fetchHeatmapData(selectedDisease.id, selectedYear)
    }
  }, [selectedDisease, selectedYear])

  async function fetchDiseases() {
    try {
      const response = await fetch('/api/entity/list?type=disease&limit=100')
      const data = await response.json()
      
      if (data.entities && data.entities.length > 0) {
        setDiseases(data.entities)
        // Set first disease with outbreak data as default
        const diseaseWithData = data.entities[0]
        setSelectedDisease(diseaseWithData)
      }
    } catch (error) {
      console.error('Error fetching diseases:', error)
    }
  }

  async function fetchHeatmapData(diseaseId, year) {
    setLoading(true)
    try {
      const params = new URLSearchParams({ diseaseId })
      if (year) params.append('year', year)
      
      const response = await fetch(`/api/heatmap?${params.toString()}`)
      const data = await response.json()
      
      console.log('=== HEATMAP DATA RECEIVED ===')
      console.log('Total countries:', data.countries?.length)
      console.log('First 5 countries:', data.countries?.slice(0, 5))
      console.log('Sample country codes:', data.countries?.slice(0, 5).map(c => c.countryCode))
      
      setHeatmapData(data)
      
      // Set selected year if not already set
      if (!selectedYear && data.availableYears && data.availableYears.length > 0) {
        setSelectedYear(data.selectedYear || data.availableYears[0])
      }
    } catch (error) {
      console.error('Error fetching heatmap data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Create color scale
  const colorScale = useMemo(() => {
    if (!heatmapData || !heatmapData.countries || heatmapData.countries.length === 0) {
      return scaleLinear().domain([0, 1]).range(['#e5e7eb', '#e5e7eb'])
    }
    
    const maxCases = Math.max(...heatmapData.countries.map(c => c.cases || 0))
    
    return scaleLinear()
      .domain([0, maxCases * 0.1, maxCases * 0.5, maxCases])
      .range(['#fee', '#fcc', '#f44', '#a00'])
      .clamp(true)
  }, [heatmapData])

  // Map country codes to case counts
  const countryDataMap = useMemo(() => {
    if (!heatmapData || !heatmapData.countries) return {}
    
    const map = {}
    
    console.log('=== BUILDING COUNTRY MAP ===')
    console.log('Total countries from API:', heatmapData.countries.length)
    
    heatmapData.countries.forEach((country, idx) => {
      if (country.countryCode) {
        const code = country.countryCode.trim().toUpperCase()
        
        // Store by the code from the database (ISO3)
        map[code] = country
        
        // Log first few for debugging
        if (idx < 5) {
          console.log(`Country ${idx}: ${country.countryName} -> ${code}`)
        }
      }
    })
    
    console.log('Map keys sample:', Object.keys(map).slice(0, 10))
    
    return map
  }, [heatmapData])

  function handleCountryClick(geo) {
    const iso3 = geo.properties.ISO_A3?.trim().toUpperCase()
    const iso2 = geo.properties.ISO_A2?.trim().toUpperCase()
    
    // Try ISO_A3 first (most reliable)
    const countryData = countryDataMap[iso3]
    
    if (countryData && countryData.cases > 0) {
      setSelectedCountry(countryData)
    }
  }

  return (
    <main className="flex-1 py-8 md:py-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        {/* Header */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight mb-2">
            <span className="bg-gradient-to-r from-red-400 via-orange-500 to-pink-500 bg-clip-text text-transparent">
              Disease Outbreak Heatmap
            </span>
          </h1>
          <p className="text-muted-foreground mt-2">
            Visualize disease outbreak intensity across countries over time
          </p>
        </motion.div>

        {/* Controls */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          {/* Disease Selector */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <Activity className="h-5 w-5 text-red-400" />
                Select Disease
              </CardTitle>
            </CardHeader>
            <CardContent>
              <select
                value={selectedDisease?.id || ''}
                onChange={(e) => {
                  const disease = diseases.find(d => d.id === e.target.value)
                  setSelectedDisease(disease)
                  setSelectedYear(null)
                }}
                disabled={loading || diseases.length === 0}
                className="w-full p-2 bg-card border border-border rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {diseases.length === 0 ? (
                  <option>Loading diseases...</option>
                ) : (
                  diseases.map(disease => (
                    <option key={disease.id} value={disease.id}>
                      {disease.label}
                    </option>
                  ))
                )}
              </select>
            </CardContent>
          </Card>

          {/* Year Selector */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <Calendar className="h-5 w-5 text-cyan-400" />
                Select Year
              </CardTitle>
            </CardHeader>
            <CardContent>
              {heatmapData && heatmapData.availableYears && heatmapData.availableYears.length > 0 ? (
                <div className="space-y-2">
                  <input
                    type="range"
                    min={Math.min(...heatmapData.availableYears)}
                    max={Math.max(...heatmapData.availableYears)}
                    value={selectedYear || heatmapData.selectedYear}
                    onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                    disabled={loading}
                    className="w-full accent-cyan-500 disabled:opacity-50"
                    style={{ cursor: loading ? 'not-allowed' : 'pointer' }}
                  />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>{Math.min(...heatmapData.availableYears)}</span>
                    <span className="text-lg font-bold text-foreground">
                      {selectedYear || heatmapData.selectedYear}
                    </span>
                    <span>{Math.max(...heatmapData.availableYears)}</span>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  {loading ? 'Loading years...' : 'No data available'}
                </p>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Map */}
        <motion.div
          className="bg-card/50 backdrop-blur-md border border-border/50 rounded-lg p-4 mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {loading ? (
            <div className="flex items-center justify-center h-96">
              <div className="text-muted-foreground">Loading map data...</div>
            </div>
          ) : (
            <ComposableMap
              projection="geoEqualEarth"
              projectionConfig={{
                scale: 147,
                center: [0, 0],
              }}
              className="w-full h-96"
            >
              <ZoomableGroup center={[0, 0]} zoom={1}>
                <Geographies geography={geoUrl}>
                  {({ geographies }) =>
                    geographies
                      .filter(geo => geo.properties.NAME !== "Antarctica") // Remove Antarctica
                      .map((geo, idx) => {
                        const iso3 = geo.properties.ISO_A3?.trim().toUpperCase()
                        const countryData = countryDataMap[iso3]
                        const cases = countryData?.cases || 0
                        
                        // Debug first few countries to see what's happening
                        if (idx < 5) {
                          console.log(`Map country ${idx}:`, geo.properties.NAME, 'ISO_A3:', iso3, 'Cases:', cases, 'Has data:', !!countryData)
                        }
                        
                        return (
                          <Geography
                            key={geo.rsmKey}
                            geography={geo}
                            fill={cases > 0 ? colorScale(cases) : '#374151'}
                            stroke="#1f2937"
                            strokeWidth={0.5}
                            style={{
                              default: { outline: 'none' },
                              hover: { 
                                fill: cases > 0 ? '#fbbf24' : '#4b5563',
                                outline: 'none',
                                cursor: 'pointer'
                              },
                              pressed: { outline: 'none' }
                            }}
                            onClick={() => handleCountryClick(geo)}
                          />
                        )
                      })
                  }
                </Geographies>
              </ZoomableGroup>
            </ComposableMap>
          )}
          
          {/* Legend */}
          <div className="mt-4 flex items-center justify-center gap-4">
            <span className="text-sm text-muted-foreground">Low</span>
            <div className="flex gap-1">
              {[0, 0.25, 0.5, 0.75, 1].map((val, idx) => (
                <div
                  key={idx}
                  className="w-12 h-6 border border-border"
                  style={{
                    backgroundColor: heatmapData && heatmapData.countries && heatmapData.countries.length > 0
                      ? colorScale(val * Math.max(...heatmapData.countries.map(c => c.cases || 0)))
                      : '#374151'
                  }}
                />
              ))}
            </div>
            <span className="text-sm text-muted-foreground">High</span>
          </div>
        </motion.div>

        {/* Country Info Panel */}
        {selectedCountry && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="fixed bottom-6 right-6 w-80 bg-card border border-border rounded-lg shadow-2xl"
          >
            <div className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <MapPin className="h-5 w-5 text-cyan-400" />
                  <h3 className="font-semibold text-lg">{selectedCountry.countryName}</h3>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedCountry(null)}
                  className="h-6 w-6 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Disease:</span>
                  <span className="font-medium">{heatmapData?.diseaseName}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Year:</span>
                  <span className="font-medium">{selectedYear || heatmapData?.selectedYear}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Cases:</span>
                  <span className="font-medium text-red-400">
                    {selectedCountry.cases?.toLocaleString() || 'N/A'}
                  </span>
                </div>
                {selectedCountry.deaths !== null && selectedCountry.deaths !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Deaths:</span>
                    <span className="font-medium text-orange-400">
                      {selectedCountry.deaths?.toLocaleString() || 'N/A'}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {/* Stats Summary */}
        {heatmapData && heatmapData.countries && (
          <motion.div
            className="grid grid-cols-1 sm:grid-cols-3 gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Countries Affected</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-cyan-400">
                  {heatmapData.countries.length}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Cases</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-red-400">
                  {heatmapData.countries.reduce((sum, c) => sum + (c.cases || 0), 0).toLocaleString()}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Most Affected</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-lg font-bold text-orange-400">
                  {heatmapData.countries[0]?.countryName || 'N/A'}
                </p>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </main>
  )
}
