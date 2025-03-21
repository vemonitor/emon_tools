import { Pane } from "@/components/layout/pane";
import { useParams } from "react-router";
import { DataViewerList } from "../data-viewer/finaFilesViever";
import { ChartPane } from "../data-viewer/finaChartViever";
import { validateStringId } from "@/lib/utils";

function ViewDataPath() {
  const { path_id } = useParams();
  const item_id = validateStringId(path_id) 
  return (
    <Pane
      title='Fina Reader'
      classBody={'h-full'}
    >

      <div className='grid grid-cols-8 h-full'>
        <div className='col-span-2 h-full'>
          <DataViewerList
            path_id={(item_id)}
          />
        </div>
        <div className='col-span-6 h-full'>
          <ChartPane
            source={item_id}
            classBody='h-full'
          />
        </div>
      </div>
    </Pane>
  )
}

export default ViewDataPath