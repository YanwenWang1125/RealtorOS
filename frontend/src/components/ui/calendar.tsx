"use client"

import * as React from "react"
import { Calendar as AriaCalendar, CalendarGrid, CalendarGridHeader, CalendarHeaderCell, CalendarGridBody, CalendarCell, Button } from "react-aria-components"
import { CalendarDate, parseDate, today, getLocalTimeZone, fromDate } from "@internationalized/date"
import { cn } from "@/lib/utils/index"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { buttonVariants } from "@/components/ui/Button"

// 兼容 react-day-picker 的 API
interface CalendarProps {
  mode?: "single" | "range" | "multiple"
  selected?: Date | undefined
  onSelect?: (date: Date | undefined) => void
  disabled?: (date: Date) => boolean
  className?: string
  classNames?: Record<string, string>
  showOutsideDays?: boolean
  [key: string]: any
}

function Calendar({
  mode = "single",
  selected,
  onSelect,
  disabled,
  className,
  showOutsideDays = true,
  ...props
}: CalendarProps) {
  // 转换 Date 到 CalendarDate
  const [value, setValue] = React.useState<CalendarDate | null>(() => {
    if (!selected) return null
    try {
      const zonedDate = fromDate(selected, getLocalTimeZone())
      return new CalendarDate(zonedDate.year, zonedDate.month, zonedDate.day)
    } catch {
      return null
    }
  })

  // 跟踪当前显示的月份
  const [focusedDate, setFocusedDate] = React.useState<CalendarDate>(() => {
    if (selected) {
      try {
        const zonedDate = fromDate(selected, getLocalTimeZone())
        return new CalendarDate(zonedDate.year, zonedDate.month, zonedDate.day)
      } catch {
        return today(getLocalTimeZone())
      }
    }
    return today(getLocalTimeZone())
  })

  // 当 selected prop 变化时更新内部值
  React.useEffect(() => {
    if (selected) {
      try {
        const zonedDate = fromDate(selected, getLocalTimeZone())
        const newValue = new CalendarDate(zonedDate.year, zonedDate.month, zonedDate.day)
        setValue(newValue)
        setFocusedDate(newValue)
      } catch {
        setValue(null)
      }
    } else {
      setValue(null)
    }
  }, [selected])

  // 处理日期选择
  const handleChange = (date: CalendarDate) => {
    setValue(date)
    if (onSelect) {
      // 转换 CalendarDate 回 Date
      const jsDate = date.toDate(getLocalTimeZone())
      onSelect(jsDate)
    }
  }

  // 检查日期是否禁用
  const isDateDisabled = (date: CalendarDate) => {
    if (!disabled) return false
    const jsDate = date.toDate(getLocalTimeZone())
    return disabled(jsDate)
  }

  return (
    <div className={cn("border rounded-md p-3 w-full", className)} style={{ fontVariantNumeric: "tabular-nums" }}>
      <AriaCalendar
        value={value || undefined}
        onChange={handleChange}
        // @ts-expect-error - react-aria-components CalendarProps may use isDisabled instead of isDateDisabled
        isDateDisabled={isDateDisabled}
        {...props}
      >
        {(state) => {
          // 使用 visibleRange 或 focusedDate，如果不存在则使用内部状态
          // @ts-expect-error - react-aria-components CalendarRenderProps type may not include all properties
          const currentMonth: CalendarDate = state.visibleRange?.start || state.focusedDate || focusedDate
          
          // 格式化月份和年份：转换为 Date 后格式化
          const jsDate = currentMonth.toDate(getLocalTimeZone())
          const monthLabel = jsDate.toLocaleDateString("en-US", {
            month: "long",
            year: "numeric"
          })
          
          return (
            <>
              <div className="flex items-center justify-between mb-4">
                <Button
                  slot="previous"
                  onPress={() => {
                    const newDate = focusedDate.subtract({ months: 1 })
                    setFocusedDate(newDate)
                  }}
                  className={cn(
                    buttonVariants({ variant: "outline" }),
                    "h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100"
                  )}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <h2 className="text-sm font-medium">
                  {monthLabel}
                </h2>
                <Button
                  slot="next"
                  onPress={() => {
                    const newDate = focusedDate.add({ months: 1 })
                    setFocusedDate(newDate)
                  }}
                  className={cn(
                    buttonVariants({ variant: "outline" }),
                    "h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100"
                  )}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>

              <CalendarGrid className="w-full">
                <CalendarGridHeader>
                  {(day) => (
                    <CalendarHeaderCell className="text-muted-foreground text-xs font-normal text-center py-2">
                      {day}
                    </CalendarHeaderCell>
                  )}
                </CalendarGridHeader>
                <CalendarGridBody>
                  {(date) => {
                    const isSelected = value && date.compare(value) === 0
                    const isToday = date.compare(today(getLocalTimeZone())) === 0
                    const isDisabled = isDateDisabled(date)
                    const isOutsideMonth = date.month !== currentMonth.month

                    // 如果不需要显示外部日期，返回一个不可见的元素而不是null
                    if (!showOutsideDays && isOutsideMonth) {
                      return (
                        <CalendarCell
                          date={date}
                          className="hidden"
                          aria-hidden="true"
                        />
                      )
                    }

                    return (
                      <CalendarCell
                        date={date}
                        className={cn(
                          "h-9 w-full flex items-center justify-center text-sm rounded-md",
                          "hover:bg-secondary/10 focus:bg-secondary/10 focus:outline-none",
                          // 选中状态：确保文字颜色清晰可见
                          isSelected && "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground !text-primary-foreground",
                          // 今天但未选中
                          isToday && !isSelected && "bg-secondary/10 text-secondary",
                          // 禁用状态
                          isDisabled && "text-muted-foreground opacity-50 cursor-not-allowed",
                          // 其他月份
                          isOutsideMonth && "text-muted-foreground opacity-50",
                          // 默认文字颜色（确保未选中时有清晰的颜色）
                          !isSelected && !isToday && !isDisabled && !isOutsideMonth && "text-foreground"
                        )}
                        style={
                          isSelected
                            ? {
                                backgroundColor: "hsl(var(--primary))",
                                color: "hsl(var(--primary-foreground))",
                                // 强制覆盖任何其他样式
                              }
                            : undefined
                        }
                      />
                    )
                  }}
                </CalendarGridBody>
              </CalendarGrid>
            </>
          )
        }}
      </AriaCalendar>
    </div>
  )
}

Calendar.displayName = "Calendar"

export { Calendar }
