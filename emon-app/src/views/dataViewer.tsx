import Pane from '../components/layout/pane'
import { useDataViewer } from '../stores/dataViewerStore';
import { ChartPane } from './lib/finaChartViever';
import { DataViewerList } from './lib/finaFilesViever';



export function DataViewer() {
  const source = useDataViewer((state) => state.source)
 
  return (
    <Pane
      title='Fina Reader'>
      
      <div className='grid grid-cols-8 h-full'>
        <div className='col-span-2 h-full'>
          <DataViewerList 
            source={source}
          />
        </div>
        <div className='col-span-6 h-full'>
          <ChartPane
            source={source}
            classBody='h-full'
          />
        </div>
      </div>
    </Pane>
  )
}

