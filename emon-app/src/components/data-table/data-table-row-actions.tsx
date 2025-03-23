import { MoreHorizontal } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

import { PropsWithChildren } from "react"
import clsx from "clsx"

type DataTableRowActionsProps = PropsWithChildren<{
  classBody?: string
}>

export function DataTableRowActions({
  classBody,
  children
}: DataTableRowActionsProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="flex h-8 w-8 p-0 data-[state=open]:bg-muted"
        >
          <MoreHorizontal />
          <span className="sr-only">Open menu</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className={clsx("w-[160px]", classBody)}>
        {children}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}