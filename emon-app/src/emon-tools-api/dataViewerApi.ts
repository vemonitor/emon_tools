import Ut from '@/helpers/utils';
import { getWithFetch } from '@/helpers/fetcher';
import { UseQueryResult } from '@tanstack/react-query';
import {
  GraphDataProps,
  GraphFeedProps,
  GraphLocationProps,
  LineChartDataProps
} from '@/components/fina_viewer/feedChart';
import { SelectedFileItem } from '@/lib/graphTypes';
import { getApiUrl } from '@/lib/utils';

export interface ExecQueriesParams {
  file_name: string;
}

export type FinaDataFetchItem = {
  success: boolean,
  datapath_id: number,
  emonhost_id: number,
  file_id: number,
  feed_id: number,
  file_name: string,
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




export const getFinaFiles = (path_id: number) => {
  const url = getApiUrl(`/api/v1/fina_data/files/${path_id}/`);
  return {
      queryKey: ['emon_fina_files', path_id],
      queryFn: () =>
        getWithFetch({
          url: url
        }),
    }
}

export const format_data = (
    dataFetch: FinaDataFetchItem[],
    location: GraphLocationProps
  ): LineChartDataProps => {
    if(Ut.isArray(dataFetch) && dataFetch.length > 0){
      return dataFetch.reduce((obj, item) => {
        const datapath_id = item.datapath_id
        const emonhost_id = item.emonhost_id
        const file_name = item.file_name
        const file_id = item.file_id
        const feed_id = item.feed_id
        const data = item.data
        if(Ut.isArray(data)){
          const feed_data: GraphDataProps[] = data.map((value) => {
            if(value.length === 2){
              return {
                date: value[0],
                [file_id]: value[1],
                [`${file_id}_range`]: []
              }
            }
            else if(value.length >= 4){
              return {
                date: value[0],
                [`${file_id}_range`]: [value[1], value[3]],
                [`${file_id}`]: value[2],
              }
            }
          })
          obj.data = obj.data.concat(feed_data)
          obj.feeds.push({
            file_id: file_id,
            feed_id: feed_id,
            datapath_id: datapath_id,
            emonhost_id: emonhost_id,
            file_name: file_name,
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
  path_id: number
) => {
  const feed_id = getFeedIdFromFileName(item.file_name);
  const url = getApiUrl(`/api/v1/fina_data/meta/${path_id}/${feed_id}`);
  return {
    queryKey: ['emon_fina_metas', path_id, feed_id],
    queryFn: () => getWithFetch({ url: url }),
    retry: false
  };
};

export const execFinaDataQueries = (
  item: SelectedFileItem,
  time_start: number,
  window: number,
  interval: number,
  fetchWithAuth: (input: RequestInfo, init?: RequestInit) => Promise<Response>
) => {
  const file_id = item.file_db?.file_id ?? 0;
  const searchParams = new URLSearchParams({
    start: time_start.toString(),
    window: window.toString(),
    interval: interval.toString(),
  });
  const url = `/api/v1/fina_data/data/${file_id}/?${searchParams.toString()}`;
  return {
    queryKey: ['emon_fina_datas', file_id, time_start, window, interval],
    retry: false,
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

export const combineResults = (
  results: QueryResultIn
): combineResultsOut => {
  const data = results.flatMap((result) => result.data || []);
  const isLoading = results.some((result) => result.isLoading);
  const isError = results.some((result) => result.isError);
  const errors = results.map((result) => result.error).filter(Boolean);
  return { data, isLoading, isError, errors };
}
