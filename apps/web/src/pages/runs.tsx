import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import EmptyState from '@/components/state/empty-state'
import ErrorState from '@/components/state/error-state'
import { SkeletonList } from '@/components/state/skeleton'
import { useRuns } from '@/features/runs/use-runs'
import { runStatusBadgeVariant, runStatusLabel } from '@/lib/status'
import { useDebounce } from '@/lib/debounce'
import { Search, ChevronLeft, ChevronRight, Copy, Check, Download, Eye, EyeOff, List, Minimize2, Save, Bookmark, Star, ArrowDownUp } from 'lucide-react'

const PAGE_SIZE = 10

type StatusFilter = 'all' | 'passed' | 'failed' | 'running' | 'queued'

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="ghost" size="icon-sm" onClick={handleCopy}>
            {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          {copied ? 'Copied!' : 'Copy ID'}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

function ToggleButton({ label, enabled, onToggle }: { label: string; enabled: boolean; onToggle: () => void }) {
  return (
    <Button variant={enabled ? 'default' : 'outline'} size="sm" onClick={onToggle}>
      {enabled ? <Eye className="h-4 w-4 mr-1" /> : <EyeOff className="h-4 w-4 mr-1" />}
      {label}
    </Button>
  )
}

export default function RunsPage() {
  const runs = useRuns()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [page, setPage] = useState(1)
  const [showSummary, setShowSummary] = useState(true)
  const [showDate, setShowDate] = useState(true)
  const [selectedRuns, setSelectedRuns] = useState<Set<string>>(new Set())
  const [viewMode, setViewMode] = useState<'list' | 'compact'>('list')
  const [savedFilters, setSavedFilters] = useState<{name: string; filter: StatusFilter}[]>(() => {
    const saved = localStorage.getItem('glyphser-filter-presets')
    return saved ? JSON.parse(saved) : []
  })
  const [favorites, setFavorites] = useState<Set<string>>(() => {
    const saved = localStorage.getItem('glyphser-favorite-runs')
    return saved ? new Set(JSON.parse(saved)) : new Set()
  })
  const debouncedSearch = useDebounce(search, 300)

  const toggleFavorite = (id: string) => {
    const newFavorites = new Set(favorites)
    if (newFavorites.has(id)) {
      newFavorites.delete(id)
    } else {
      newFavorites.add(id)
    }
    setFavorites(newFavorites)
    localStorage.setItem('glyphser-favorite-runs', JSON.stringify([...newFavorites]))
  }

  const saveCurrentFilter = () => {
    const name = prompt('Enter a name for this filter:')
    if (name) {
      const newFilters = [...savedFilters, { name, filter: statusFilter }]
      setSavedFilters(newFilters)
      localStorage.setItem('glyphser-filter-presets', JSON.stringify(newFilters))
    }
  }

  const loadFilter = (filter: StatusFilter) => {
    setStatusFilter(filter)
    setPage(1)
  }

  const [sortFavoritesFirst, setSortFavoritesFirst] = useState(true)
  const [compareRuns, setCompareRuns] = useState<string[]>([])
  const [recentSearches, setRecentSearches] = useState<string[]>(() => {
    const saved = localStorage.getItem('glyphser-recent-searches')
    return saved ? JSON.parse(saved) : []
  })
  const [showRecent, setShowRecent] = useState(false)
  const debouncedSearch = useDebounce(search, 300)

  const handleSearchChange = (value: string) => {
    setSearch(value)
    if (value.length > 2) {
      const newSearches = [value, ...recentSearches.filter(s => s !== value)].slice(0, 5)
      setRecentSearches(newSearches)
      localStorage.setItem('glyphser-recent-searches', JSON.stringify(newSearches))
    }
  }

  const toggleCompare = (id: string) => {
    if (compareRuns.includes(id)) {
      setCompareRuns(compareRuns.filter(r => r !== id))
    } else if (compareRuns.length < 2) {
      setCompareRuns([...compareRuns, id])
    }
  }

  const filteredRuns = useMemo(() => {
    return runs.data?.filter((run) => {
      const matchesSearch =
        !debouncedSearch ||
        run.id.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        run.summary?.toLowerCase().includes(debouncedSearch.toLowerCase())
      const matchesStatus = statusFilter === 'all' || run.status === statusFilter
      return matchesSearch && matchesStatus
    }) ?? []
  }, [runs.data, debouncedSearch, statusFilter])

  const sortedRuns = useMemo(() => {
    if (!sortFavoritesFirst) return filteredRuns
    return [...filteredRuns].sort((a, b) => {
      const aFav = favorites.has(a.id) ? 0 : 1
      const bFav = favorites.has(b.id) ? 0 : 1
      return aFav - bFav
    })
  }, [filteredRuns, sortFavoritesFirst, favorites])

  const totalPages = Math.ceil(sortedRuns.length / PAGE_SIZE)
  const paginatedRuns = sortedRuns.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const handleFilterChange = () => {
    setPage(1)
  }

  const toggleSelectAll = () => {
    if (selectedRuns.size === filteredRuns.length) {
      setSelectedRuns(new Set())
    } else {
      setSelectedRuns(new Set(filteredRuns.map(r => r.id)))
    }
  }

  const toggleSelect = (id: string) => {
    const newSet = new Set(selectedRuns)
    if (newSet.has(id)) {
      newSet.delete(id)
    } else {
      newSet.add(id)
    }
    setSelectedRuns(newSet)
  }

  const statusOptions: StatusFilter[] = ['all', 'passed', 'failed', 'running', 'queued']

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by ID or summary..."
            value={search}
            onChange={(e) => { handleSearchChange(e.target.value); setPage(1); }}
            onFocus={() => setShowRecent(true)}
            onBlur={() => setTimeout(() => setShowRecent(false), 200)}
            className="pl-9"
          />
          {showRecent && recentSearches.length > 0 && (
            <div className="absolute top-full left-0 right-0 bg-background border rounded-md mt-1 p-2 z-20 shadow-lg">
              <div className="text-xs text-muted-foreground mb-1">Recent searches</div>
              {recentSearches.map(s => (
                <button key={s} className="block w-full text-left text-sm py-1 hover:bg-muted px-2 rounded" onClick={() => { setSearch(s); setShowRecent(false); }}>
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
        <div className="flex gap-1 flex-wrap">
          {statusOptions.map((status) => (
            <Button
              key={status}
              variant={statusFilter === status ? 'default' : 'outline'}
              size="sm"
              onClick={() => { setStatusFilter(status); handleFilterChange(); }}
            >
              {status === 'all' ? 'All' : runStatusLabel(status as 'passed' | 'failed' | 'running' | 'queued')}
            </Button>
          ))}
          {filteredRuns.length > 0 && (
            <Button variant="outline" size="sm" onClick={() => {
              const blob = new Blob([JSON.stringify(filteredRuns, null, 2)], { type: 'application/json' })
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = `runs-${new Date().toISOString().split('T')[0]}.json`
              a.click()
              URL.revokeObjectURL(url)
            }}>
              <Download className="h-4 w-4 mr-1" />
              Export
            </Button>
          )}
          <ToggleButton label="Summary" enabled={showSummary} onToggle={() => setShowSummary(!showSummary)} />
          <ToggleButton label="Date" enabled={showDate} onToggle={() => setShowDate(!showDate)} />
          {filteredRuns.length > 0 && (
            <Button variant="outline" size="sm" onClick={toggleSelectAll}>
              {selectedRuns.size === filteredRuns.length ? '✓ Deselect All' : 'Select All'}
            </Button>
          )}
          <Button variant={viewMode === 'list' ? 'default' : 'outline'} size="sm" onClick={() => setViewMode('list')}>
            <List className="h-4 w-4" />
          </Button>
          <Button variant={viewMode === 'compact' ? 'default' : 'outline'} size="sm" onClick={() => setViewMode('compact')}>
            <Minimize2 className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={saveCurrentFilter}>
            <Save className="h-4 w-4 mr-1" />
            Save
          </Button>
          <Button variant={sortFavoritesFirst ? 'default' : 'outline'} size="sm" onClick={() => setSortFavoritesFirst(!sortFavoritesFirst)}>
            <ArrowDownUp className="h-4 w-4 mr-1" />
            Favorites First
          </Button>
        </div>
      </div>

      {runs.isError ? (
        <ErrorState message={runs.error.message} onRetry={() => runs.refetch()} />
      ) : null}

      {filteredRuns.length === 0 && !runs.isLoading ? (
        <EmptyState
          title="No runs found"
          message={search || statusFilter !== 'all' ? "Try adjusting your search or filter." : "When you run a verification, it will appear here."}
        />
      ) : null}

      {paginatedRuns.length > 0 ? (
        <Card>
          <CardHeader className="sticky top-0 bg-background z-10">
            <CardTitle>Recent runs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {paginatedRuns.map((run) => (
              <div
                key={run.id}
                className={`flex items-center gap-2 rounded-md border p-3 transition-colors hover:bg-accent/40 ${viewMode === 'compact' ? 'py-1 px-2' : ''}`}
              >
                <input
                  type="checkbox"
                  checked={selectedRuns.has(run.id)}
                  onChange={() => toggleSelect(run.id)}
                  className="h-4 w-4"
                />
                <Link to={`/runs/${encodeURIComponent(run.id)}`} className="flex-1 min-w-0">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="truncate font-mono text-sm">{run.id}</span>
                        <Badge variant={runStatusBadgeVariant(run.status)}>
                          {runStatusLabel(run.status)}
                        </Badge>
                      </div>
                      {showSummary && run.summary ? (
                        <p className="mt-1 text-sm text-muted-foreground">
                          {run.summary}
                        </p>
                      ) : null}
                    </div>
                    {showDate && (
                      <div className="text-sm text-muted-foreground">
                        <span className="font-medium">Started:</span>{' '}
                        {new Date(run.started_at).toLocaleString()}
                      </div>
                    )}
                  </div>
                </Link>
                <button onClick={(e) => { e.preventDefault(); toggleFavorite(run.id); }} className="p-1 hover:text-yellow-500">
                  <Star className={`h-4 w-4 ${favorites.has(run.id) ? 'fill-yellow-500 text-yellow-500' : ''}`} />
                </button>
                <CopyButton text={run.id} />
              </div>
            ))}
          </CardContent>
        </Card>
      ) : null}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => p - 1)}
            disabled={page === 1}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => p + 1)}
            disabled={page === totalPages}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}

      {runs.isLoading ? <SkeletonList items={5} /> : null}
    </div>
  )
}
