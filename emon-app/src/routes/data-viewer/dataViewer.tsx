import { Pane } from '../../components/layout/pane'
import { ChartPane } from './finaChartViever';
import { DataViewerList } from './finaFilesViever';
import { useParams } from "react-router";
import clsx from 'clsx';


export function DataViewer({
  className
}: {
  className?: string
}) {
  const { path_id } = useParams();
  return (
    <Pane
      title='Fina Reader'
      classBody={clsx('h-full', className)}
    >
      
      <div className='grid grid-cols-8 h-full'>
        <div className='col-span-2 h-full'>
          <DataViewerList 
            path_id={path_id ?? 'archive'}
          />
        </div>
        <div className='col-span-6 h-full'>
          <ChartPane
            source={path_id ?? 'archive'}
            classBody='h-full'
          />
        </div>
      </div>
    </Pane>
  )
}

