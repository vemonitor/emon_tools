import { DataTableColumnHeader } from "@/components/data-table/data-table-column-header"
import { ColumnDef } from "@tanstack/react-table"
import { CrudIconRowActions } from "@/components/data-table/crud-icons-row-actions"
 
// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type EmonHost = {
  id: number
  name: string
  host: string
  api_key: string
}
 
export const columns: ColumnDef<EmonHost>[] = [
  {
    accessorKey: "id",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Id" />
    ),
  },
  {
    id: "actions",
    cell: ({ row }) => <CrudIconRowActions row={row} base_path="/emon-host/" />,
  },
  {
    accessorKey: "name",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Name" />
    ),
  },
  {
    accessorKey: "host",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Host" />
    ),
  },
]