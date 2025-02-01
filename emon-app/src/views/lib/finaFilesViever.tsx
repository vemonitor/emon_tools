import { FilesListPane } from "@/components/fina_viewer/feedList";
import { DataViewerProps, getFinaFiles } from "@/emon-tools-api/dataViewerApi";
import { SelectedFileItem, useDataViewer } from "@/stores/dataViewerStore";
import { useQuery, useQueryClient } from "@tanstack/react-query";


export function DataViewerList({source}: DataViewerProps){
    const add_feed = useDataViewer((state) => state.add_feed)
    const remove_feed = useDataViewer((state) => state.remove_feed)
    const init_time_start = useDataViewer((state) => state.init_time_start)
    
    const queryClient = useQueryClient();
    const { data, error, isError, isPending: loading } = useQuery(
      getFinaFiles(source)
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
        {loading ? (
          <div>Loading...</div>
        ) : (
          isError ? (
            <div>No data available: {error.message}</div>
          ) : (
            <FilesListPane
                  data={data}
                  handleSelectItem={selectFileToGraph}
                  classBody='h-full'
                />
          )
        )}
      </div>
    )
  }
  