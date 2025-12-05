'use client'

import React, { useState, useEffect, useMemo } from 'react'
import PropTypes from 'prop-types'
import { motion } from 'framer-motion'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Calendar, TrendingUp, Filter, Download, Check, ChevronsUpDown, X } from 'lucide-react'
import { fadeIn } from '@/lib/animations'
import { cn } from '@/lib/utils'

/**
 * TimeSeriesChart - Interactive time-series visualization for Outbreak and VaccinationRecord data
 *
 * @param {Object} props
 * @param {string} props.entityId - The disease or entity ID
 * @param {string} props.entityType - Type of entity (Disease, Country, etc.)
 * @param {string} props.dataType - Type of data to display ('outbreaks' or 'vaccinations')
 * @param {string} props.title - Chart title
 * @param {string} props.description - Chart description
 */
export default function TimeSeriesChart({
  entityId,
  entityType,
  dataType = 'outbreaks',
  title,
  description
}) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [countriesLoading, setCountriesLoading] = useState(true)
  const [countries, setCountries] = useState([])
  const [selectedCountries, setSelectedCountries] = useState([])
  const [yearRange, setYearRange] = useState({ start: '', end: '' })
  const [chartType, setChartType] = useState('line') // line, bar, area
  const [aggregation, setAggregation] = useState('country') // country, total
  const [comboboxOpen, setComboboxOpen] = useState(false)

  // Fetch available countries
  useEffect(() => {
    const fetchCountries = async () => {
      setCountriesLoading(true)
      try {
        const response = await fetch(`/api/entity/${entityId}/countries?dataType=${dataType}`)
        const result = await response.json()
        const countryList = result.countries || []
        setCountries(countryList)
        
        // Set initial selection to first country
        if (countryList.length > 0) {
          setSelectedCountries([countryList[0].code])
        }
      } catch (error) {
        console.error('Failed to fetch countries:', error)
      } finally {
        setCountriesLoading(false)
      }
    }

    if (entityId) {
      fetchCountries()
    }
  }, [entityId, dataType])

  // Fetch time-series data
  useEffect(() => {
    const fetchData = async () => {
      // Don't fetch if no countries are selected
      if (!entityId || selectedCountries.length === 0) {
        setLoading(false)
        return
      }

      setLoading(true)
      try {
        const params = new URLSearchParams({
          dataType,
          countries: selectedCountries.join(','),
          yearStart: yearRange.start || '',
          yearEnd: yearRange.end || '',
          aggregation,
        })

        const response = await fetch(`/api/entity/${entityId}/timeseries?${params}`)
        const result = await response.json()
        setData(result.data || [])
      } catch (error) {
        console.error('Failed to fetch time-series data:', error)
        setData([])
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [entityId, dataType, selectedCountries, yearRange, aggregation])

  // Auto-detect year range from data
  useEffect(() => {
    if (data.length > 0 && !yearRange.start && !yearRange.end) {
      const years = data.map(d => d.year).filter(Boolean)
      if (years.length > 0) {
        const minYear = Math.min(...years)
        const maxYear = Math.max(...years)
        setYearRange({ start: minYear.toString(), end: maxYear.toString() })
      }
    }
  }, [data, yearRange])

  // Handle country selection
  const handleCountryToggle = (countryCode) => {
    setSelectedCountries(prev => {
      // If "ALL" is selected
      if (countryCode === 'ALL') {
        return ['ALL']
      }

      // Remove "ALL" if specific country is selected
      const filtered = prev.filter(c => c !== 'ALL')

      // Toggle the country
      if (filtered.includes(countryCode)) {
        const updated = filtered.filter(c => c !== countryCode)
        return updated.length === 0 ? ['ALL'] : updated
      } else {
        return [...filtered, countryCode]
      }
    })
  }

  // Format data for charts
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return []

    // Group by time period
    const grouped = {}

    data.forEach(item => {
      const key = item.year || item.date || item.period
      if (!grouped[key]) {
        grouped[key] = { period: key }
      }

      if (aggregation === 'total') {
        // Sum all countries
        const value = item.cases || item.deaths || item.coveragePercent || 0
        grouped[key].value = (grouped[key].value || 0) + value
      } else {
        // Separate by country
        const country = item.countryCode || item.country
        grouped[key][country] = item.cases || item.deaths || item.coveragePercent || 0
      }
    })

    return Object.values(grouped).sort((a, b) => {
      const periodA = a.period.toString()
      const periodB = b.period.toString()
      return periodA.localeCompare(periodB)
    })
  }, [data, aggregation])

  // Get data keys for multi-line charts
  const dataKeys = useMemo(() => {
    if (aggregation === 'total') {
      return ['value']
    }

    const keys = new Set()
    chartData.forEach(item => {
      Object.keys(item).forEach(key => {
        if (key !== 'period') {
          keys.add(key)
        }
      })
    })
    return Array.from(keys)
  }, [chartData, aggregation])

  // Color palette for multiple countries
  const colors = [
    '#06b6d4', // cyan
    '#3b82f6', // blue
    '#8b5cf6', // purple
    '#ec4899', // pink
    '#f59e0b', // amber
    '#10b981', // emerald
    '#f43f5e', // rose
    '#6366f1', // indigo
  ]

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload || payload.length === 0) return null

    return (
      <div className="bg-card/95 backdrop-blur-sm border border-border rounded-lg p-3 shadow-lg">
        <p className="text-sm font-medium text-foreground mb-2">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-muted-foreground">{entry.name}:</span>
            <span className="font-medium text-foreground">
              {entry.value?.toLocaleString() || 0}
              {dataType === 'vaccinations' && '%'}
            </span>
          </div>
        ))}
      </div>
    )
  }

  // Export data as CSV
  const handleExport = () => {
    const csvContent = [
      // Header
      ['Period', ...dataKeys].join(','),
      // Data rows
      ...chartData.map(row =>
        [row.period, ...dataKeys.map(key => row[key] || 0)].join(',')
      )
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${entityId}_${dataType}_${Date.now()}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  // Render chart based on type
  const renderChart = () => {
    const commonProps = {
      data: chartData,
      margin: { top: 5, right: 30, left: 20, bottom: 5 },
    }

    const Chart = chartType === 'bar' ? BarChart : chartType === 'area' ? AreaChart : LineChart
    const DataComponent = chartType === 'bar' ? Bar : chartType === 'area' ? Area : Line

    return (
      <ResponsiveContainer width="100%" height={400}>
        <Chart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
          <XAxis
            dataKey="period"
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
            iconType="line"
          />
          {dataKeys.map((key, index) => (
            <DataComponent
              key={key}
              type="monotone"
              dataKey={key}
              name={key === 'value' ? (dataType === 'outbreaks' ? 'Cases' : 'Coverage %') : key}
              stroke={colors[index % colors.length]}
              fill={chartType === 'area' || chartType === 'bar' ? colors[index % colors.length] : undefined}
              fillOpacity={chartType === 'area' ? 0.3 : 1}
              strokeWidth={2}
              dot={chartType === 'line' ? { r: 3 } : false}
              activeDot={chartType === 'line' ? { r: 5 } : false}
            />
          ))}
        </Chart>
      </ResponsiveContainer>
    )
  }

  // Don't render if entityId is not provided
  if (!entityId) {
    return null
  }

  // Don't render if no countries have data for this data type (after loading completes)
  if (!countriesLoading && countries.length === 0) {
    return null
  }

  return (
    <motion.div {...fadeIn}>
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-cyan-400" />
                {title || `${dataType === 'outbreaks' ? 'Outbreak Cases' : 'Vaccination Coverage'} Over Time`}
              </CardTitle>
              {description && (
                <CardDescription className="mt-2">{description}</CardDescription>
              )}
            </div>
            <Badge variant="outline" className="text-cyan-400 border-cyan-500/30">
              Interactive
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Filters */}
          <div className="bg-muted/30 rounded-lg p-4 space-y-4">
            <div className="flex items-center gap-2 text-sm font-medium text-foreground mb-3">
              <Filter className="h-4 w-4 text-cyan-400" />
              Filters
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Year Range */}
              <div className="space-y-2">
                <Label htmlFor="yearStart" className="text-sm">Start Year</Label>
                <Input
                  id="yearStart"
                  type="number"
                  placeholder="e.g., 2000"
                  value={yearRange.start}
                  onChange={(e) => setYearRange(prev => ({ ...prev, start: e.target.value }))}
                  className="bg-card"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="yearEnd" className="text-sm">End Year</Label>
                <Input
                  id="yearEnd"
                  type="number"
                  placeholder="e.g., 2023"
                  value={yearRange.end}
                  onChange={(e) => setYearRange(prev => ({ ...prev, end: e.target.value }))}
                  className="bg-card"
                />
              </div>

              {/* Chart Type */}
              <div className="space-y-2">
                <Label htmlFor="chartType" className="text-sm">Chart Type</Label>
                <Select value={chartType} onValueChange={setChartType}>
                  <SelectTrigger id="chartType" className="bg-card">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="line">Line Chart</SelectItem>
                    <SelectItem value="bar">Bar Chart</SelectItem>
                    <SelectItem value="area">Area Chart</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Aggregation */}
              <div className="space-y-2">
                <Label htmlFor="aggregation" className="text-sm">View</Label>
                <Select value={aggregation} onValueChange={setAggregation}>
                  <SelectTrigger id="aggregation" className="bg-card">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="country">By Country</SelectItem>
                    <SelectItem value="total">Total (All Countries)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Country Selection - Searchable Multi-Select */}
            {aggregation === 'country' && countries.length > 0 && (
              <div className="space-y-2">
                <Label className="text-sm">Countries</Label>
                <Popover open={comboboxOpen} onOpenChange={setComboboxOpen}>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      role="combobox"
                      aria-expanded={comboboxOpen}
                      className="w-full justify-between bg-card"
                    >
                      <span className="truncate">
                        {selectedCountries.includes('ALL')
                          ? 'All Countries'
                          : selectedCountries.length === 0
                          ? 'Select countries...'
                          : `${selectedCountries.length} selected`}
                      </span>
                      <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-full p-0" align="start">
                    <Command>
                      <CommandInput placeholder="Search countries..." />
                      <CommandList>
                        <CommandEmpty>No country found.</CommandEmpty>
                        <CommandGroup>
                          <CommandItem
                            onSelect={() => {
                              handleCountryToggle('ALL')
                            }}
                            className="cursor-pointer"
                          >
                            <Check
                              className={cn(
                                'mr-2 h-4 w-4',
                                selectedCountries.includes('ALL') ? 'opacity-100' : 'opacity-0'
                              )}
                            />
                            All Countries
                          </CommandItem>
                          <CommandSeparator />
                          {countries.map((country) => (
                            <CommandItem
                              key={country.code}
                              value={`${country.name} ${country.code}`}
                              onSelect={() => {
                                handleCountryToggle(country.code)
                              }}
                              className="cursor-pointer"
                            >
                              <Check
                                className={cn(
                                  'mr-2 h-4 w-4',
                                  selectedCountries.includes(country.code)
                                    ? 'opacity-100'
                                    : 'opacity-0'
                                )}
                              />
                              {country.name}
                            </CommandItem>
                          ))}
                        </CommandGroup>
                      </CommandList>
                    </Command>
                  </PopoverContent>
                </Popover>

                {/* Selected Countries Display */}
                {!selectedCountries.includes('ALL') && selectedCountries.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {selectedCountries.map((countryCode) => {
                      const country = countries.find((c) => c.code === countryCode)
                      return (
                        <Badge
                          key={countryCode}
                          variant="secondary"
                          className="gap-1 pr-1"
                        >
                          {country?.name || countryCode}
                          <button
                            onClick={() => handleCountryToggle(countryCode)}
                            className="ml-1 rounded-full hover:bg-muted p-0.5"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </Badge>
                      )
                    })}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Chart */}
          <div className="mt-6">
            {loading ? (
              <div className="h-[400px] flex items-center justify-center bg-muted/20 rounded-lg">
                <div className="text-center space-y-2">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400 mx-auto" />
                  <p className="text-sm text-muted-foreground">Loading data...</p>
                </div>
              </div>
            ) : chartData.length === 0 ? (
              <div className="h-[400px] flex items-center justify-center bg-muted/20 rounded-lg">
                <div className="text-center space-y-2">
                  <Calendar className="h-12 w-12 text-muted-foreground mx-auto" />
                  <p className="text-sm text-muted-foreground">No data available for the selected filters</p>
                </div>
              </div>
            ) : (
              renderChart()
            )}
          </div>

          {/* Stats & Export */}
          {chartData.length > 0 && (
            <div className="flex items-center justify-between pt-4 border-t border-border/50">
              <div className="flex gap-4 text-sm text-muted-foreground">
                <span>
                  <span className="font-medium text-foreground">{chartData.length}</span> data points
                </span>
                <span>
                  <span className="font-medium text-foreground">{dataKeys.length}</span> series
                </span>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={handleExport}
                className="gap-2"
              >
                <Download className="h-4 w-4" />
                Export CSV
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

TimeSeriesChart.propTypes = {
  entityId: PropTypes.string.isRequired,
  entityType: PropTypes.string,
  dataType: PropTypes.oneOf(['outbreaks', 'vaccinations']).isRequired,
  title: PropTypes.string,
  description: PropTypes.string,
}
