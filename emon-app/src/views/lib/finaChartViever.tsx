import { useQueries } from '@tanstack/react-query';
import {
  combineResults,
  execFinaDataQueries,
  format_datas
} from '@/emon-tools-api/dataViewerApi';
import { useDataViewer } from '@/stores/dataViewerStore';
import clsx from 'clsx';
import { FeedLineChart } from '@/components/fina_viewer/feedChart';
import { ChartTopMenu } from './chartTopMenu';
import Ut from '@/helpers/utils';
import { Skeleton } from '@/components/ui/skeleton';
import { useShallow } from 'zustand/react/shallow'
import { Suspense } from 'react';
import { FinaSourceProps, SelectedFileItem } from '@/lib/graphTypes';

type FinaChartViewerProps = {
  source: FinaSourceProps,
  selected_feeds: SelectedFileItem[]
  classBody?: string;
}

const GraphLoader = () => {
  return(
    <>
      <div className='w-full min-h-[400px] p-4'>
        <Skeleton className="h-full w-full rounded-xl" />
      </div>
      <div className="w-full h-20 p-4">
        <Skeleton className="h-full w-full rounded-xl" />
      </div>
    </>
  )
}



export function FinaChartViewer({
  source,
  selected_feeds
}: FinaChartViewerProps){
    /*const { 
      time_start,
      time_end,
      time_window,
      interval
    } = useDataViewer()*/
    const time_start = useDataViewer((state) => state.time_start)
    const time_window = useDataViewer((state) => state.time_window)
    const interval = useDataViewer((state) => state.interval)
    
    const is_selected_feeds = Ut.isArray(selected_feeds)
    
    const has_selected_feeds = is_selected_feeds
      && selected_feeds.length > 0

    const leftGraph = useQueries({
      queries: selected_feeds
        .filter((item) => item.side === 'left')
        .map((item) => execFinaDataQueries(
          item,
          source,
          time_start,
          time_window,
          interval
        )),
      combine: (results) => {
        return combineResults(results)
      },
    });
  
    const rightGraph = useQueries({
      queries: selected_feeds
        .filter((item) => item.side === 'right')
        .map((item) => execFinaDataQueries(
          item,
          source,
          time_start,
          time_window,
          interval
        )),
      combine: (results) => {
        return combineResults(results)
      }
    });

    if(!has_selected_feeds || leftGraph.pending || rightGraph.pending){
      return (
        <GraphLoader />
      )
    }
    const data_points = format_datas(leftGraph.data ?? [], rightGraph.data ?? [])
    //set_data_points(data_points)
    return (
      <>
        <div className='w-full h-full'>
          {leftGraph.pending || rightGraph.pending ? (
              <div>Loading...</div>
            ) : (leftGraph.data && rightGraph.data ? (
              <FeedLineChart 
                data_points={format_datas(leftGraph.data, rightGraph.data)}
                time_start={time_start}
                time_window={time_window}
                interval={interval}
                selected_feeds={selected_feeds}
              />
                          
            ) : (
              <div>No data available</div>
            )
          )}
        </div>
        <div className="w-full h-20">
      
        </div>
        
      </>
    )
}

type ChartPaneProps = {
  source: FinaSourceProps
  classBody?: string;
}

export function ChartPane({
  source,
  classBody
}: ChartPaneProps) {
  const selected_feeds = useDataViewer((state) => state.selected_feeds)

  return (
  <div
    className={clsx('w-full flex flex-col items-center gap-2 h-full', classBody)}
  >
    <div className="w-full">
      <ChartTopMenu />
    </div>
    <FinaChartViewer
      source={source}
      selected_feeds={selected_feeds}
    />
  </div>

  )
}