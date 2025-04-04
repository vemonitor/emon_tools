import Ut from '@/helpers/utils';
import { getWithFetch } from '@/helpers/fetcher';
import { UseQueryResult } from '@tanstack/react-query';
import {
  FeedDataIn,
  FinaDataIn,
  GraphDataIn,
  GraphDataProps,
  GraphFeedProps,
  GraphLocationProps,
  LineChartDataProps,
  SelectedFileItem,
  timeSerie
} from '@/lib/graphTypes';
import { getApiUrl } from '@/lib/utils';

export interface ExecQueriesParams {
  file_name: string;
}



export type FinaDataFetchItem = {
  success: boolean,
  id: number,
  name: string,
  location: GraphLocationProps,
  data: number[][],
}



export type FeedDataFetchItem = {
  success: boolean,
  id: number,
  name: string,
  location: GraphLocationProps,
  data: timeSerie[],
}

export type QueryResultIn = UseQueryResult<
  FinaDataFetchItem[] | undefined,
  Error
>[]

export type combineResultsOut = {
  data: FinaDataFetchItem[] | undefined;
  isLoading: boolean;
  isError: boolean;
  error: any[];
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

const get_time_series = (data: timeSerie[], itemId: number): GraphDataProps[] | null => {
  if(Ut.isArray(data, {notEmpty: true})){
    return data
      .map((value: timeSerie) => {
        const nb_items: number = value.length
        if(nb_items === 2){
          return {
            date: value[0],
            [itemId]: value[1]
          } as GraphDataProps
        }
        else if(nb_items >= 4){
          return {
            date: value[0],
            [`${itemId}`]: value[2],
            [`${itemId}_range`]: nb_items >= 4 ? [value[1], value[3]] : [],
            
          } as GraphDataProps
        }
        return undefined
      })
      .filter((item): item is GraphDataProps => item !== undefined);
  }
  return null
}

export type GraphDataType = {
  feeds: GraphFeedProps[],
  data: GraphDataProps[]
}

export const format_graph_data = (
  name: string,
  itemId: number,
  data: timeSerie[],
  location: GraphLocationProps,
  current : GraphDataType
): GraphDataType => {
  if(Ut.isArray(data)){
    const feed_data: GraphDataProps[] | null = get_time_series(data, itemId)
    current.data = feed_data ? current.data.concat(feed_data) : current.data
    current.feeds.push({
      id: itemId,
      name: name,
      location: location
    })
  }
  return current
}

export const format_feed_data = (
    dataFetch: FeedDataIn[],
    location: GraphLocationProps
  ): LineChartDataProps => {
    if(Ut.isArray(dataFetch) && dataFetch.length > 0){
      return dataFetch.reduce((obj, item: FeedDataIn) => {
        const name = item.name
        const itemId = item.id
        const data = item.data
        return format_graph_data(
          name,
          itemId,
          data,
          location,
          obj
        )
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

export const format_file_data = (
  dataFetch: FinaDataIn[],
  location: GraphLocationProps
): LineChartDataProps => {
  if(Ut.isArray(dataFetch) && dataFetch.length > 0){
    return dataFetch.reduce((obj, item) => {
      const name = item.name
      const itemId = item.file_id
      const data = item.data
      return format_graph_data(
        name,
        itemId,
        data,
        location,
        obj
      )
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
    leftFetch: GraphDataIn[],
    rightFetch: GraphDataIn[],
    graph_source: "files" | "feeds"
  ): LineChartDataProps => {
    let leftData: GraphDataType | null = null
    let rightData: GraphDataType | null = null
    if(graph_source === "files"){
      leftData = format_file_data(leftFetch as FinaDataIn[], 'left')
      rightData = format_file_data(rightFetch as FinaDataIn[], 'right')
    }
    else if(graph_source === "feeds"){
      leftData = format_feed_data(leftFetch as FeedDataIn[], 'left')
      rightData = format_feed_data(rightFetch as FeedDataIn[], 'right')
    }

    return {
      data: leftData && rightData ? leftData.data.concat(rightData.data).flat() : [],
      feeds: leftData && rightData ? leftData.feeds.concat(rightData.feeds).flat() : []
    }
}

export const getFeedIdFromFileName = (file_name: string) => {
  if(Ut.isStr(file_name)){
    const tmp = file_name.split('.');
    return parseInt(tmp[0])
  }
  return 0
}

export const getSearchParams = (
  time_start: number,
  window: number,
  interval: number
) => {
  const searchParams = new URLSearchParams({
    start: time_start.toString(),
    window: window.toString(),
    interval: interval.toString(),
  });
  return searchParams.toString()
}

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
