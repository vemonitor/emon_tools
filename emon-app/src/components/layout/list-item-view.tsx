import { ColumnDef } from "@tanstack/react-table"
import { DataTable } from '@/components/data-table/data-table'
import { Pane, PaneProps } from '@/components/layout/pane'
import { UseQueryResult } from "@tanstack/react-query"
import { useToast } from "@/hooks/use-toast"
import { useEffect } from "react"
import { Loader } from "@/components/layout/loader"

type ListViewProps<TData, TValue> = {
    paneProps: PaneProps
    columns: ColumnDef<TData, TValue>[]
    queryResult: UseQueryResult<{ data: TData[] }, Error>
}

export default function ListView<TData, TValue>({
    paneProps,
    columns,
    queryResult
}: ListViewProps<TData, TValue>) {
    const { toast } = useToast()
    useEffect(() => {
          if (!queryResult.isPending && queryResult.isError) {
            toast({
                title: "List Reaquest Error",
                description: queryResult.error ? queryResult.error.message : '',
            })
          }
    }, [queryResult, toast]);
    
    return (
        <Pane
            {...paneProps}
        >
            {queryResult.isPending ? (
                <Loader />
            ) : queryResult.isError || !(queryResult.data && queryResult.data.data) ? (
                <div>No data available...</div>
            ) : (
                <DataTable columns={columns} data={queryResult.data.data as TData[]} />
            )}
        </Pane>
    )
}
