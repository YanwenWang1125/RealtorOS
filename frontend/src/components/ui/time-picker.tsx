"use client"

import * as React from "react"
import { Clock } from "lucide-react"
import { cn } from "@/lib/utils"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Button } from "@/components/ui/Button"

interface TimePickerProps {
  value?: string // Format: "HH:MM"
  onChange: (value: string) => void
  disabled?: boolean
  className?: string
  placeholder?: string
}

const hours = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, "0"))
const minutes = ["00", "15", "30", "45"]

export function TimePicker({
  value,
  onChange,
  disabled = false,
  className,
  placeholder = "Select time",
}: TimePickerProps) {
  const [open, setOpen] = React.useState(false)
  
  // Parse current hour and minute from value
  const [hour, setHour] = React.useState<string>(() => {
    return value?.split(":")[0] || "09"
  })
  const [minute, setMinute] = React.useState<string>(() => {
    return value?.split(":")[1] || "00"
  })

  // Refs for scroll containers and buttons
  const hourContainerRef = React.useRef<HTMLDivElement>(null)
  const minuteContainerRef = React.useRef<HTMLDivElement>(null)
  const hourButtonRefs = React.useRef<Record<string, HTMLButtonElement | null>>({})
  const minuteButtonRefs = React.useRef<Record<string, HTMLButtonElement | null>>({})

  // Update internal state when external value changes
  React.useEffect(() => {
    if (value) {
      const [h, m] = value.split(":")
      if (h) setHour(h)
      if (m) setMinute(m)
    }
  }, [value])

  // Scroll to selected hour
  React.useEffect(() => {
    if (open && hour && hourContainerRef.current && hourButtonRefs.current[hour]) {
      const button = hourButtonRefs.current[hour]
      const container = hourContainerRef.current
      if (button) {
        const buttonTop = button.offsetTop
        const containerHeight = container.clientHeight
        const scrollPosition = buttonTop - containerHeight / 2 + button.clientHeight / 2
        container.scrollTo({
          top: scrollPosition,
          behavior: 'smooth'
        })
      }
    }
  }, [hour, open])

  // Scroll to selected minute
  React.useEffect(() => {
    if (open && minute && minuteContainerRef.current && minuteButtonRefs.current[minute]) {
      const button = minuteButtonRefs.current[minute]
      const container = minuteContainerRef.current
      if (button) {
        const buttonTop = button.offsetTop
        const containerHeight = container.clientHeight
        const scrollPosition = buttonTop - containerHeight / 2 + button.clientHeight / 2
        container.scrollTo({
          top: scrollPosition,
          behavior: 'smooth'
        })
      }
    }
  }, [minute, open])

  const handleWheel = (e: React.WheelEvent<HTMLDivElement>, type: "hour" | "minute") => {
    e.preventDefault()
    const arr = type === "hour" ? hours : minutes
    const current = type === "hour" ? hour : minute
    const index = arr.indexOf(current)
    let next = index + (e.deltaY > 0 ? 1 : -1)
    if (next < 0) next = arr.length - 1
    if (next >= arr.length) next = 0
    const nextValue = arr[next]
    
    if (type === "hour") {
      setHour(nextValue)
      onChange(`${nextValue}:${minute}`)
    } else {
      setMinute(nextValue)
      onChange(`${hour}:${nextValue}`)
    }
  }

  const displayValue = value || (hour && minute ? `${hour}:${minute}` : placeholder)
  const isValue = Boolean(value)

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            "w-full justify-start text-left font-normal h-10",
            !isValue && "text-muted-foreground",
            className
          )}
          disabled={disabled}
        >
          <Clock className="mr-2 h-4 w-4 shrink-0" />
          <span>{displayValue}</span>
        </Button>
      </PopoverTrigger>

      <PopoverContent
        align="start"
        side="bottom"
        className="z-50 mt-2 w-[260px] max-h-[60vh] rounded-xl border bg-popover p-3 shadow-lg outline-none animate-in fade-in-0 slide-in-from-top-2 duration-150"
      >
        <div className="flex items-start gap-4">
          {/* Hour Column */}
          <div
            ref={hourContainerRef}
            onWheel={(e) => handleWheel(e, "hour")}
            className="flex-1 max-h-48 overflow-y-auto text-center scroll-smooth scrollbar-thin scrollbar-thumb-muted scrollbar-thumb-rounded-full"
          >
            <div className="text-xs text-muted-foreground mb-1 font-medium tracking-wide">Hour</div>
            <div className="flex flex-col items-center gap-1">
              {hours.map((h) => (
                <button
                  key={h}
                  ref={(el) => {
                    hourButtonRefs.current[h] = el
                  }}
                  onClick={() => {
                    setHour(h)
                    onChange(`${h}:${minute}`)
                  }}
                  className={cn(
                    "w-10 py-1 rounded-md text-sm transition-colors duration-150",
                    h === hour
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  {h}
                </button>
              ))}
            </div>
          </div>

          {/* Divider */}
          <div className="w-px h-44 bg-border" />

          {/* Minute Column */}
          <div
            ref={minuteContainerRef}
            onWheel={(e) => handleWheel(e, "minute")}
            className="flex-1 max-h-48 overflow-y-auto text-center scroll-smooth scrollbar-thin scrollbar-thumb-muted scrollbar-thumb-rounded-full"
          >
            <div className="text-xs text-muted-foreground mb-1 font-medium tracking-wide">Minute</div>
            <div className="flex flex-col items-center gap-1">
              {minutes.map((m) => (
                <button
                  key={m}
                  ref={(el) => {
                    minuteButtonRefs.current[m] = el
                  }}
                  onClick={() => {
                    setMinute(m)
                    onChange(`${hour}:${m}`)
                  }}
                  className={cn(
                    "w-10 py-1 rounded-md text-sm transition-colors duration-150",
                    m === minute
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  )
}
