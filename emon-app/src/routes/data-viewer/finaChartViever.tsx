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
import { SelectedFileItem } from '@/lib/graphTypes';
import { useAuth } from '@/hooks/use-auth';

type FinaChartViewerProps = {
  path_id: number,
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
  path_id,
  selected_feeds
}: FinaChartViewerProps){
    const { fetchWithAuth } = useAuth();
  
    const time_start = useDataViewer((state) => state.time_start)
    const time_window = useDataViewer((state) => state.time_window)
    const interval = useDataViewer((state) => state.interval)
    const set_data_points = useDataViewer(useShallow((state) => state.set_data_points))

    // Ensure selected_feeds is always an array.
    const feeds = Array.isArray(selected_feeds) ? selected_feeds : [];
    const leftFeeds = feeds.filter((feed) => feed.side === 'left');
    const rightFeeds = feeds.filter((feed) => feed.side === 'right');

    // Always call useQueries, even if the feed arrays are empty.
    const leftQueries = useQueries({
      queries: leftFeeds.map((feed) =>
        execFinaDataQueries(feed, time_start, time_window, interval, fetchWithAuth)
      ),
    });
    const rightQueries = useQueries({
      queries: rightFeeds.map((feed) =>
        execFinaDataQueries(feed, time_start, time_window, interval, fetchWithAuth)
      ),
    });

    // Determine loading state based on queries.
    const isLoading =
      leftQueries.some((query) => query.isLoading) ||
      rightQueries.some((query) => query.isLoading);

    // Combine query results.
    const leftData = leftQueries.flatMap((query) => query.data || []);
    const rightData = rightQueries.flatMap((query) => query.data || []);
    const data_points = format_datas(leftData, rightData);

    // Always call useEffect, but conditionally perform an action inside it.
    /*useEffect(() => {
      if (!isLoading) {
        set_data_points(data_points);
      }
    }, [isLoading, data_points, set_data_points]);*/
    return (
      <>
        <div className='w-full h-full'>
          <FeedLineChart 
            data_points={data_points}
            time_start={time_start}
            time_window={time_window}
            interval={interval}
            selected_feeds={selected_feeds}
          />
        </div>
        <div className="w-full h-20">
      
        </div>
        
      </>
    )
}

type ChartPaneProps = {
  path_id: number
  classBody?: string;
}

export function ChartPane({
  path_id,
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
    <Suspense fallback={<GraphLoader />}>
      <FinaChartViewer
        path_id={path_id}
        selected_feeds={selected_feeds}
      />
    </Suspense>
    
  </div>

  )
}