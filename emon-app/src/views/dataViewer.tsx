import { FinaSourceProps } from '@/lib/graphTypes';
import Pane from '../components/layout/pane'
import { useDataViewer } from '../stores/dataViewerStore';
import { ChartPane } from './lib/finaChartViever';
import { DataViewerList } from './lib/finaFilesViever';



export function DataViewer({
  source_ref
}: {
  source_ref: FinaSourceProps
}) {
  //const source = useDataViewer((state) => state.source)
 
  return (
    <Pane
      title='Fina Reader'>
      
      <div className='grid grid-cols-8 h-full'>
        <div className='col-span-2 h-full'>
          <DataViewerList 
            source={source_ref}
          />
        </div>
        <div className='col-span-6 h-full'>
          <ChartPane
            source={source_ref}
            classBody='h-full'
          />
        </div>
      </div>
    </Pane>
  )
}

