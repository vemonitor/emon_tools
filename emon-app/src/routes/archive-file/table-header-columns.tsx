import { DataTableColumnHeader } from "@/components/data-table/data-table-column-header"
import { ColumnDef } from "@tanstack/react-table"
import { CrudIconRowActions } from "@/components/data-table/crud-icons-row-actions"
import { ArchiveFileList } from "@/lib/types"
 

export const columns: ColumnDef<ArchiveFileList>[] = [
  {
    accessorKey: "id",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Id" />
    ),
  },
  {
    id: "actions",
    cell: ({ row }) => <CrudIconRowActions row={row} base_path="/archive-file/" />,
  },
  {
    accessorKey: "name",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Name" />
    ),
  },
  {
    accessorKey: "file_name",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="File Name" />
    ),
  },
  {
    accessorKey: "emonhost.name",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Emoncms Host" />
    ),
    cell: ({ row }) => <div>{row.original.emonhost?.name ?? ''}</div>,
  },
  {
    accessorKey: "category.name",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Category" />
    ),
    cell: ({ row }) => <div>{row.original.category?.name ?? ''}</div>
  },
  {
    accessorKey: "start_time",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Start time" />
    ),
  },
  {
    accessorKey: "end_time",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="End time" />
    ),
  },
  {
    accessorKey: "interval",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Interval" />
    ),
  },
  {
    accessorKey: "size",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Size" />
    ),
  },
  
]