import { useQueries } from '@tanstack/react-query';
import {
  format_datas
} from '@/emon-tools-api/dataViewerApi';
import { useDataViewer } from '@/stores/dataViewerStore';
import clsx from 'clsx';
import { Skeleton } from '@/components/ui/skeleton';
import { Suspense } from 'react';
import { SelectedToGraph } from '@/lib/graphTypes';
import { useAuth } from '@/hooks/use-auth';
import { validateSlug } from '@/lib/utils';
import { FeedLineChart } from '@/components/fina_viewer/managed-chart';
import { ChartTopMenu } from '@/components/fina_viewer/chartTopMenu';

const GraphLoader = () => {
  return (
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

const execHostDataQueries = (
  item: SelectedToGraph,
  host_slug: string,
  time_start: number,
  window: number,
  interval: number,
  fetchWithAuth: (input: RequestInfo, init?: RequestInit) => Promise<Response>
) => {
  const feed_id = item.id;
  const searchParams = new URLSearchParams({
    start: time_start.toString(),
    window: window.toString(),
    interval: interval.toString(),
  });
  const url = `/api/v1/emoncms/data/${host_slug}/${feed_id}/?${searchParams.toString()}`;
  return {
    queryKey: ['emoncms_datas', feed_id, time_start, window, interval],
    retry: false,
    enabled: host_slug && feed_id ? true : false,
    queryFn: async () => {
      const response = await fetchWithAuth(url, { method: 'GET' });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const json = await response.json();
      return json || {};
    },
  };
};

type FeedChartViewerProps = {
  host_slug: string;
  selected_feeds: SelectedToGraph[]
  classBody?: string;
}

export function FeedChartViewer({
  host_slug,
  selected_feeds
}: FeedChartViewerProps) {
  const { fetchWithAuth } = useAuth();

  const time_start = useDataViewer((state) => state.time_start)
  const time_window = useDataViewer((state) => state.time_window)
  const interval = useDataViewer((state) => state.interval)

  // Ensure selected_feeds is always an array.
  const feeds = Array.isArray(selected_feeds) ? selected_feeds : [];
  const leftFeeds = feeds.filter((feed) => feed.side === 'left');
  const rightFeeds = feeds.filter((feed) => feed.side === 'right');

  // Always call useQueries, even if the feed arrays are empty.
  const leftQueries = useQueries({
    queries: leftFeeds.map((feed) =>
      execHostDataQueries(feed, host_slug, time_start, time_window, interval, fetchWithAuth)
    ),
  });
  const rightQueries = useQueries({
    queries: rightFeeds.map((feed) =>
      execHostDataQueries(feed, host_slug, time_start, time_window, interval, fetchWithAuth)
    ),
  });

  // Combine query results.
  const leftData = leftQueries.flatMap((query) => query.data || []);
  const rightData = rightQueries.flatMap((query) => query.data || []);
  const data_points = format_datas(leftData, rightData, "feeds");

  return (
    <>
      <div className='w-full h-full'>
        <FeedLineChart
          data_points={data_points}
          time_start={time_start}
          time_window={time_window}
          interval={interval}
        />
      </div>
      <div className="w-full h-20">

      </div>

    </>
  )
}

type ChartPaneProps = {
  host_slug?: string
  classBody?: string;
}

export function ChartFeedPane({
  host_slug,
  classBody
}: ChartPaneProps) {
  const selected_feeds = useDataViewer((state) => state.selected_feeds)
  const slug = validateSlug(host_slug);
  if (!slug) {
    return (
      <div className='flex items-center justify-center h-full'>
        <h1 className='text-2xl font-bold'>Please chose Emoncms Instance.</h1>
      </div>
    )
  }
  return (
    <div
      className={clsx('w-full flex flex-col items-center gap-2 h-full', classBody)}
    >
      <div className="w-full">
        <ChartTopMenu />
      </div>
      <Suspense fallback={<GraphLoader />}>
        <FeedChartViewer
          host_slug={slug}
          selected_feeds={selected_feeds}
        />
      </Suspense>

    </div>

  )
}