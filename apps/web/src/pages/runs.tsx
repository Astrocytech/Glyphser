import { useState, useMemo, useRef, useEffect } from 'react'
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
import { Search, ChevronLeft, ChevronRight, Copy, Check, CheckSquare, Square, Download, Star, ChevronDown, X, Circle } from 'lucide-react'

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

function DropdownMenu({ trigger, children }: { trigger: React.ReactNode; children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="relative" ref={ref}>
      <div onClick={() => setOpen(!open)} className="cursor-pointer">{trigger}</div>
      {open && (
        <div className="absolute right-0 top-full mt-1.5 bg-background border border-border rounded-lg shadow-xl z-50 py-1 min-w-[180px] animate-in fade-in zoom-in-95 duration-100">
          {children}
        </div>
      )}
    </div>
  )
}

export default function RunsPage() {
  const runs = useRuns()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<StatusFilter[]>(['all'])
  const [page, setPage] = useState(1)
  const [showSummary, setShowSummary] = useState(true)
  const [showDate, setShowDate] = useState(true)
  const [favorites, setFavorites] = useState<Set<string>>(() => {
    const saved = localStorage.getItem('glyphser-favorite-runs')
    return saved ? new Set(JSON.parse(saved)) : new Set()
  })
  const [recentSearches, setRecentSearches] = useState<string[]>(() => {
    const saved = localStorage.getItem('glyphser-recent-searches')
    return saved ? JSON.parse(saved) : []
  })
  const [showRecent, setShowRecent] = useState(false)
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

  const handleSearchChange = (value: string) => {
    setSearch(value)
    if (value.length > 2) {
      const newSearches = [value, ...recentSearches.filter(s => s !== value)].slice(0, 5)
      setRecentSearches(newSearches)
      localStorage.setItem('glyphser-recent-searches', JSON.stringify(newSearches))
    }
  }

  const filteredRuns = useMemo(() => {
    return runs.data?.filter((run) => {
      const matchesSearch =
        !debouncedSearch ||
        run.id.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        run.summary?.toLowerCase().includes(debouncedSearch.toLowerCase())
      const matchesStatus = statusFilter.includes('all') || statusFilter.includes(run.status)
      return matchesSearch && matchesStatus
    }) ?? []
  }, [runs.data, debouncedSearch, statusFilter])

  const sortedRuns = useMemo(() => {
    return [...filteredRuns].sort((a, b) => {
      const aFav = favorites.has(a.id) ? 0 : 1
      const bFav = favorites.has(b.id) ? 0 : 1
      return aFav - bFav
    })
  }, [filteredRuns, favorites])

  const totalPages = Math.ceil(sortedRuns.length / PAGE_SIZE)
  const paginatedRuns = sortedRuns.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const statusOptions: StatusFilter[] = ['all', 'passed', 'failed', 'running', 'queued', 'partial', 'unknown']

  const exportRuns = () => {
    const blob = new Blob([JSON.stringify(filteredRuns, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `runs-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="mx-auto max-w-5xl space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search runs..."
            value={search}
            onChange={(e) => { handleSearchChange(e.target.value); setPage(1); }}
            onFocus={() => setShowRecent(true)}
            onBlur={() => setTimeout(() => setShowRecent(false), 200)}
            className="pl-9 pr-8"
          />
          {search && (
            <button
              onClick={() => { setSearch(''); setPage(1); }}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1 hover:bg-accent rounded"
            >
              <X className="h-3.5 w-3.5 text-muted-foreground" />
            </button>
          )}
          {showRecent && recentSearches.length > 0 && (
            <div className="absolute top-full left-0 right-0 bg-background border rounded-lg mt-1 p-1 z-20 shadow-lg">
              <div className="text-xs text-muted-foreground px-2 py-1">Recent</div>
              {recentSearches.map(s => (
                <button key={s} className="block w-full text-left text-sm py-1.5 hover:bg-accent px-2 rounded" onClick={() => { setSearch(s); setShowRecent(false); setPage(1); }}>
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
        <div className="flex gap-2 items-center">
          <DropdownMenu
            trigger={
              <Button variant="outline" size="sm" className="gap-1.5 w-[90px] justify-start">
                <span className={statusFilter.length > 0 && !statusFilter.includes('all') ? 'font-medium' : ''}>{statusFilter.length > 0 && !statusFilter.includes('all') ? `${statusFilter.length} Status` : 'Status'}</span>
                <ChevronDown className="h-3.5 w-3.5 text-muted-foreground ml-auto" />
              </Button>
            }
          >
            {statusOptions.map((status) => {
              const isSelected = statusFilter.includes(status)
              return (
                <button
                  key={status}
                  className={`w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent rounded-sm mx-1 ${isSelected ? 'bg-accent font-medium' : ''}`}
                  onClick={() => {
                    if (status === 'all') {
                      setStatusFilter(['all'])
                    } else {
                      const newFilter = statusFilter.filter(s => s !== 'all')
                      if (newFilter.includes(status)) {
                        const updated = newFilter.filter(s => s !== status)
                        setStatusFilter(updated.length === 0 ? ['all'] : updated)
                      } else {
                        setStatusFilter([...newFilter, status])
                      }
                    }
                    setPage(1)
                  }}
                >
                  <span className="w-4">{isSelected ? <CheckSquare className="h-4 w-4 text-primary" /> : <Square className="h-4 w-4" />}</span>
                  <Circle className={`h-2.5 w-2.5 fill-current ${status === 'passed' ? 'text-green-500' : status === 'failed' ? 'text-red-500' : status === 'running' ? 'text-blue-500' : status === 'queued' ? 'text-yellow-500' : 'text-muted-foreground'}`} />
                  <span>{status === 'all' ? 'All' : runStatusLabel(status)}</span>
                </button>
              )
            })}
          </DropdownMenu>
          <DropdownMenu
            trigger={
              <Button variant="outline" size="sm" className="gap-1.5 w-[95px] justify-start">
                Columns <ChevronDown className="h-3.5 w-3.5 text-muted-foreground ml-auto" />
              </Button>
            }
          >
            <button
              className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent rounded-sm mx-1"
              onClick={() => setShowSummary(!showSummary)}
            >
              <span className="w-4">{showSummary ? <CheckSquare className="h-4 w-4 text-primary" /> : <Square className="h-4 w-4" />}</span>
              Summary
            </button>
            <button
              className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent rounded-sm mx-1"
              onClick={() => setShowDate(!showDate)}
            >
              <span className="w-4">{showDate ? <CheckSquare className="h-4 w-4 text-primary" /> : <Square className="h-4 w-4" />}</span>
              Date
            </button>
          </DropdownMenu>
          <DropdownMenu
            trigger={
              <Button variant="outline" size="sm" className="gap-1.5 w-[90px] justify-start">
                Actions <ChevronDown className="h-3.5 w-3.5 text-muted-foreground ml-auto" />
              </Button>
            }
          >
            <button
              className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent rounded-sm mx-1"
              onClick={() => { setFavorites(new Set()); localStorage.setItem('glyphser-favorite-runs', '[]'); }}
            >
              <Star className="h-4 w-4 text-muted-foreground" />
              Clear Favorites
            </button>
            {filteredRuns.length > 0 && (
              <button
                className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent rounded-sm mx-1"
                onClick={exportRuns}
              >
                <Download className="h-4 w-4 text-muted-foreground" />
                Export to JSON
              </button>
            )}
          </DropdownMenu>
          {(search || (statusFilter.length > 0 && !statusFilter.includes('all'))) && (
            <Button variant="ghost" size="sm" onClick={() => { setSearch(''); setStatusFilter(['all']); setPage(1); }} className="text-muted-foreground hover:text-foreground">
              <X className="h-4 w-4 mr-1" />
              Clear
            </Button>
          )}
        </div>
      </div>

      {runs.isError ? (
        <ErrorState message={runs.error.message} onRetry={() => runs.refetch()} />
      ) : null}

      {filteredRuns.length === 0 && !runs.isLoading ? (
        <EmptyState
          title="No runs found"
          message={search || (statusFilter.length > 0 && !statusFilter.includes('all')) ? "Try adjusting your search or filter." : "When you run a verification, it will appear here."}
        />
      ) : null}

      {paginatedRuns.length > 0 ? (
        <Card>
          <CardHeader className="sticky top-0 bg-background z-10 py-3 border-b">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Runs</CardTitle>
              <span className="text-sm text-muted-foreground">{filteredRuns.length} results</span>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y">
              {paginatedRuns.map((run) => (
                <div
                  key={run.id}
                  className="flex items-center gap-3 px-4 py-2.5 hover:bg-accent/50"
                >
                  <Link to={`/runs/${encodeURIComponent(run.id)}`} className="flex-1 min-w-0 flex items-center gap-3">
                    <span className="truncate font-mono text-sm text-foreground">{run.id}</span>
                    <Badge variant={runStatusBadgeVariant(run.status)} className="shrink-0 font-normal">
                      {runStatusLabel(run.status)}
                    </Badge>
                    {showSummary && run.summary && (
                      <span className="hidden md:block text-sm text-muted-foreground truncate">{run.summary}</span>
                    )}
                    {showDate && (
                      <span className="text-xs text-muted-foreground shrink-0 ml-auto">{new Date(run.started_at).toLocaleDateString()}</span>
                    )}
                  </Link>
                  <button onClick={(e) => { e.preventDefault(); toggleFavorite(run.id); }} className="p-1.5 rounded hover:bg-accent opacity-40 hover:opacity-100 hover:text-yellow-500 transition-opacity">
                    <Star className={`h-4 w-4 ${favorites.has(run.id) ? 'fill-yellow-500 text-yellow-500 opacity-100' : ''}`} />
                  </button>
                  <CopyButton text={run.id} />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}

      {totalPages > 1 && (
        <div className="flex items-center justify-between py-2">
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <div className="flex items-center gap-1">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => p - 1)}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => p + 1)}
              disabled={page === totalPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {runs.isLoading ? <SkeletonList items={5} /> : null}
    </div>
  )
}
