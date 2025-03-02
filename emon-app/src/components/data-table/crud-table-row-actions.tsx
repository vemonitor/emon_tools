import { Row } from "@tanstack/react-table"
import {
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu"
import { DataTableRowActions } from "@/components/data-table/data-table-row-actions"
import { Link } from "react-router"


interface CrudTableRowActionsProps<TData extends { id: string | number }> {
  row: Row<TData>
}

export function CrudTableRowActions<TData extends { id: string | number }>({
  row
}: CrudTableRowActionsProps<TData>) {
  const row_id = row.original.id
  const base_path = `/emon-host/`
  return (
    <DataTableRowActions>
      <DropdownMenuItem asChild><Link to={`${base_path}view/${row_id}`}>View</Link></DropdownMenuItem>
      <DropdownMenuItem asChild><Link to={`${base_path}edit/${row_id}`}>Edit</Link></DropdownMenuItem>
      <DropdownMenuItem asChild><Link to={`${base_path}delete/${row_id}`}>Delete</Link></DropdownMenuItem>
    </DataTableRowActions>
  )
}