import * as React from "react"
import { addDays, subDays, format, isSameDay } from "date-fns"
import { Calendar as CalendarIcon, ChevronDown, X } from "lucide-react"
import { DateRange } from "react-day-picker"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { useState, useEffect } from "react"
import { Label } from "./label"
import { Switch } from "./switch"

type QuickRange = 'today' | 'yesterday' | 'last7' | 'last30' | 'last90' | 'thisMonth' | 'lastMonth' | 'custom'

interface DateRangePickerProps {
  className?: string
  date: DateRange | undefined
  onDateChange: (date: DateRange | undefined) => void
  compareEnabled?: boolean
  onCompareChange?: (enabled: boolean) => void
  compareDate?: DateRange | undefined
  onCompareDateChange?: (date: DateRange | undefined) => void
  showQuickSelect?: boolean
}

export function DatePickerWithRange({
  className,
  date,
  onDateChange,
  compareEnabled = false,
  onCompareChange,
  compareDate,
  onCompareDateChange,
  showQuickSelect = true,
}: DateRangePickerProps) {
  const [quickRange, setQuickRange] = useState<QuickRange>('last30')
  const [isOpen, setIsOpen] = useState(false)
  const [isCompareOpen, setIsCompareOpen] = useState(false)

  // Set initial date range based on quick range
  useEffect(() => {
    if (quickRange === 'custom' || !showQuickSelect) return
    
    const today = new Date()
    let newDate: DateRange = { from: today, to: today }
    
    switch (quickRange) {
      case 'yesterday':
        newDate = { from: subDays(today, 1), to: subDays(today, 1) }
        break
      case 'last7':
        newDate = { from: subDays(today, 6), to: today }
        break
      case 'last30':
        newDate = { from: subDays(today, 29), to: today }
        break
      case 'last90':
        newDate = { from: subDays(today, 89), to: today }
        break
      case 'thisMonth':
        newDate = {
          from: new Date(today.getFullYear(), today.getMonth(), 1),
          to: today
        }
        break
      case 'lastMonth':
        const firstDayLastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1)
        const lastDayLastMonth = new Date(today.getFullYear(), today.getMonth(), 0)
        newDate = {
          from: firstDayLastMonth,
          to: lastDayLastMonth
        }
        break
      default:
        return
    }
    
    onDateChange(newDate)
    
    // If comparison is enabled, set the comparison range to the same duration before the selected range
    if (compareEnabled && onCompareDateChange) {
      const duration = newDate.to && newDate.from ? 
        Math.ceil((newDate.to.getTime() - newDate.from.getTime()) / (1000 * 60 * 60 * 24)) : 30
        
      onCompareDateChange({
        from: subDays(newDate.from || today, duration + 1),
        to: subDays(newDate.from || today, 1)
      })
    }
  }, [quickRange, compareEnabled])

  const handleDateSelect = (newDate: DateRange | undefined) => {
    onDateChange(newDate)
    setQuickRange('custom')
    
    // If comparison is enabled and we have a date range, update the comparison range
    if (compareEnabled && newDate?.from && newDate?.to && onCompareDateChange) {
      const duration = Math.ceil((newDate.to.getTime() - newDate.from.getTime()) / (1000 * 60 * 60 * 24))
      onCompareDateChange({
        from: subDays(newDate.from, duration + 1),
        to: subDays(newDate.from, 1)
      })
    }
  }

  const handleCompareToggle = (checked: boolean) => {
    if (onCompareChange) {
      onCompareChange(checked)
      
      // If enabling comparison and we have a date range, set the comparison range
      if (checked && date?.from && date?.to && onCompareDateChange) {
        const duration = Math.ceil((date.to.getTime() - date.from.getTime()) / (1000 * 60 * 60 * 24))
        onCompareDateChange({
          from: subDays(date.from, duration + 1),
          to: subDays(date.from, 1)
        })
      }
    }
  }

  const formatDateRange = (range: DateRange | undefined) => {
    if (!range?.from) return ''
    if (!range.to) return format(range.from, 'MMM d, yyyy')
    return `${format(range.from, 'MMM d')} - ${format(range.to, 'MMM d, yyyy')}`
  }

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center justify-between">
        <Label>Date Range</Label>
        {onCompareChange && (
          <div className="flex items-center space-x-2">
            <Label htmlFor="compare-toggle" className="text-sm font-normal">Compare to previous period</Label>
            <Switch 
              id="compare-toggle" 
              checked={compareEnabled} 
              onCheckedChange={handleCompareToggle} 
            />
          </div>
        )}
      </div>
      
      <div className="flex flex-col space-y-2">
        <div className="flex items-center space-x-2">
          <Popover open={isOpen} onOpenChange={setIsOpen}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "w-full justify-between text-left font-normal",
                  !date && "text-muted-foreground"
                )}
              >
                <div className="flex items-center">
                  <CalendarIcon className="mr-2 h-4 w-4 flex-shrink-0" />
                  {date?.from ? (
                    date.to ? (
                      <span>{formatDateRange(date)}</span>
                    ) : (
                      <span>{format(date.from, 'MMM d, yyyy')}</span>
                    )
                  ) : (
                    <span>Select date range</span>
                  )}
                </div>
                <ChevronDown className={`ml-2 h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <div className="p-2">
                {showQuickSelect && (
                  <div className="grid grid-cols-2 gap-2 mb-4">
                    <Button 
                      variant={quickRange === 'today' ? 'default' : 'outline'} 
                      size="sm"
                      onClick={() => setQuickRange('today')}
                    >
                      Today
                    </Button>
                    <Button 
                      variant={quickRange === 'yesterday' ? 'default' : 'outline'} 
                      size="sm"
                      onClick={() => setQuickRange('yesterday')}
                    >
                      Yesterday
                    </Button>
                    <Button 
                      variant={quickRange === 'last7' ? 'default' : 'outline'} 
                      size="sm"
                      onClick={() => setQuickRange('last7')}
                    >
                      Last 7 days
                    </Button>
                    <Button 
                      variant={quickRange === 'last30' ? 'default' : 'outline'} 
                      size="sm"
                      onClick={() => setQuickRange('last30')}
                    >
                      Last 30 days
                    </Button>
                    <Button 
                      variant={quickRange === 'last90' ? 'default' : 'outline'} 
                      size="sm"
                      onClick={() => setQuickRange('last90')}
                    >
                      Last 90 days
                    </Button>
                    <Button 
                      variant={quickRange === 'thisMonth' ? 'default' : 'outline'} 
                      size="sm"
                      onClick={() => setQuickRange('thisMonth')}
                    >
                      This month
                    </Button>
                    <Button 
                      variant={quickRange === 'lastMonth' ? 'default' : 'outline'} 
                      size="sm"
                      onClick={() => setQuickRange('lastMonth')}
                    >
                      Last month
                    </Button>
                    <Button 
                      variant={quickRange === 'custom' ? 'default' : 'outline'} 
                      size="sm"
                      onClick={() => setQuickRange('custom')}
                      className="col-span-2"
                    >
                      Custom range
                    </Button>
                  </div>
                )}
                <Calendar
                  initialFocus
                  mode="range"
                  defaultMonth={date?.from}
                  selected={date}
                  onSelect={handleDateSelect}
                  numberOfMonths={2}
                />
              </div>
            </PopoverContent>
          </Popover>
        </div>

        {compareEnabled && onCompareDateChange && (
          <div className="flex items-center space-x-2">
            <Popover open={isCompareOpen} onOpenChange={setIsCompareOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    "w-full justify-between text-left font-normal text-muted-foreground",
                    compareDate && "text-foreground"
                  )}
                >
                  <div className="flex items-center">
                    <CalendarIcon className="mr-2 h-4 w-4 flex-shrink-0" />
                    {compareDate?.from ? (
                      compareDate.to ? (
                        <span>vs {formatDateRange(compareDate)}</span>
                      ) : (
                        <span>vs {format(compareDate.from, 'MMM d, yyyy')}</span>
                      )
                    ) : (
                      <span>Compare to previous period</span>
                    )}
                  </div>
                  <ChevronDown className={`ml-2 h-4 w-4 transition-transform ${isCompareOpen ? 'rotate-180' : ''}`} />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <div className="p-2">
                  <Calendar
                    initialFocus
                    mode="range"
                    defaultMonth={compareDate?.from}
                    selected={compareDate}
                    onSelect={onCompareDateChange}
                    numberOfMonths={2}
                  />
                </div>
              </PopoverContent>
            </Popover>
          </div>
        )}
      </div>
    </div>
  )
}