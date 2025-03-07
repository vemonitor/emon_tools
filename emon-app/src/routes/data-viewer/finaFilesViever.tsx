import { FilesListPane } from "@/components/fina_viewer/feedList";
import { getFinaFiles } from "@/emon-tools-api/dataViewerApi";
import { useAuth } from "@/hooks/use-auth";
import { DataViewerProps, SelectedFileItem } from "@/lib/graphTypes";
import { useDataViewer } from "@/stores/dataViewerStore";
import { useQuery, useQueryClient } from "@tanstack/react-query";


export function DataViewerList({path_id}: DataViewerProps){
    const { fetchWithAuth } = useAuth();
    const add_feed = useDataViewer((state) => state.add_feed)
    const remove_feed = useDataViewer((state) => state.remove_feed)
    const init_time_start = useDataViewer((state) => state.init_time_start)
    
    const queryClient = useQueryClient();
    const queryResult = useQuery(
      {
        queryKey: ['emon_fina_files', path_id],
        retry: false,
        refetchOnMount: 'always',
        queryFn: () =>
          fetchWithAuth(
            `http://127.0.0.1:8000/api/v1/fina_data/files/${path_id}/`,
            {
              method: 'GET',
            }
          ).then((response) => response.json()),
      }
    );
    
    const selectFileToGraph = (selected_item: SelectedFileItem) => {
        if(selected_item.is_checked){
            add_feed(selected_item)
            init_time_start(selected_item.meta.start_time)
        } else {
            remove_feed(selected_item)
        }
        queryClient.invalidateQueries({ queryKey: ['emon_fina_datas'] })
    }
  
    return (
      <div className='w-full h-full'>
        {queryResult.isPending ? (
            <div>Loading...</div>
        ) : queryResult.isError || !(queryResult.data && queryResult.data.data) ? (
            <div>No data available...</div>
        ) : (
            <FilesListPane
              data={queryResult.data.data}
              handleSelectItem={selectFileToGraph}
              classBody='h-full'
            />
        )}
      </div>
    )
  }
  