import Ut from '@/utils/utils';
import { getWithFetch } from '../utils/fetcherWithFetch';
import { UseQueryResult } from '@tanstack/react-query';
import { GraphDataProps, GraphFeedProps, GraphLocationProps, LineChartDataProps } from '@/components/fina_viewer/feedChart';
import { FinaSourceProps, SelectedFileItem } from '@/stores/dataViewerStore';



export type DataViewerProps = {
  source: FinaSourceProps
}

export interface ExecQueriesParams {
  file_name: string;
}

export type FinaDataFetchItem = {
  success: boolean,
  feed_id: number,
  location: GraphLocationProps,
  data: number[][],
}

export type QueryResultIn = UseQueryResult<
  FinaDataFetchItem[] | undefined,
  Error
>[]

export type combineResultsOut = {
  data: FinaDataFetchItem[] | undefined;
  pending: boolean,
  error: any[]
}

export type FeedMetaResponse = {
  success: boolean,
  feed_id: number,
  data: FeedMetaOut[]
}

export type FeedMetaOut = {
  start_time: number,
  end_time: number,
  npoints: number,
  interval: number
}

export const getFinaFiles = (source: FinaSourceProps) => {
    return {
        queryKey: ['emon_fina_files', source],
        queryFn: () =>
          getWithFetch({
            url:`http://127.0.0.1:8000/api/v1/emon_fina/files/${source}`
          }),
      }
}

export const format_data = (
    dataFetch: FinaDataFetchItem[],
    location: GraphLocationProps
  ): LineChartDataProps => {
    if(Ut.isArray(dataFetch) && dataFetch.length > 0){
      return dataFetch.reduce((obj, item) => {
        const feed_id = item.feed_id
        const data = item.data
        if(Ut.isArray(data)){
          const feed_data: GraphDataProps[] = data.map((value) => {
            if(value.length === 2){
              return {
                date: value[0],
                [feed_id]: value[1],
                [`${feed_id}_range`]: []
              }
            }
            else if(value.length >= 4){
              return {
                date: value[0],
                [`${feed_id}_range`]: [value[1], value[3]],
                [`${feed_id}`]: value[2],
              }
            }
          })
          obj.data = obj.data.concat(feed_data)
          obj.feeds.push({
            feed_id: feed_id,
            location: location
          })
        }
        return obj
      }, {
        feeds: [] as GraphFeedProps[],
        data: [] as GraphDataProps[]
      })
    }
    return {
      feeds: [],
      data: []
    }
}

export const format_datas = (
    leftFetch: FinaDataFetchItem[],
    rightFetch: FinaDataFetchItem[]
  ): LineChartDataProps => {
    const leftData = format_data(leftFetch, 'left')
    const rightData = format_data(rightFetch, 'right')

    return {
      data: leftData.data.concat(rightData.data).flat(),
      feeds: leftData.feeds.concat(rightData.feeds).flat()
    }
}

export const getFeedIdFromFileName = (file_name: string) => {
  if(Ut.isStr(file_name)){
    const tmp = file_name.split('.');
    return parseInt(tmp[0])
  }
  return 0
}

export const execFinaMetaQueries = (
  item: ExecQueriesParams,
  source: FinaSourceProps
) => {
  const feed_id = getFeedIdFromFileName(item.file_name);
  const url = 'http://127.0.0.1:8000/api/v1/emon_fina/meta/' + source + '/' + feed_id;
  return {
    queryKey: ['emon_fina_metas', source, feed_id],
    queryFn: () => getWithFetch({ url: url }),
    retry: false
  };
};

export const execFinaDataQueries = (
  item: SelectedFileItem,
  source: FinaSourceProps,
  time_start: number,
  window: number,
  interval: number
) => {
  const feed_id = item.item_id;
  const searchParams = new URLSearchParams({
    start: time_start.toString(),
    window: window.toString(),
    interval: interval.toString(),
  });
  const url = 'http://127.0.0.1:8000/api/v1/emon_fina/data/' + source + '/' + feed_id + '?' + searchParams.toString();
  return {
    queryKey: ['emon_fina_datas', source, feed_id, time_start, window, interval],
    queryFn: () => getWithFetch({ url: url }),
    retry: false
  };
};

export const combineResults = (
  results: QueryResultIn
): combineResultsOut => {
  return {
    data: results.flatMap((result) => result.data || []),
    pending: results.some((result) => result.isPending),
    error: results.flatMap((result) => result.error || []),
  }
}
