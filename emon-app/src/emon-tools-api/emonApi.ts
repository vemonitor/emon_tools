import Ut from '@/helpers/utils';
import { getWithFetch } from '@/helpers/fetcher';
import { urlSearchParamsType } from '@/lib/types';

export interface FeedDataArgs {
    feed_id: number,
    start?: number,
    end?: number,
    window?: number,
    interval?: number,
    average?: boolean,
    time_format?: string,
    skip_missing?: boolean,
    limit_interval?: boolean,
    delta?: boolean,
}

export interface FeedMetaArgs {
  id: number,
  interval: number,
  start_time: number,
  npoints: number,
  end_time: number
}

export class EmonFeedApi {
  base_url?: string = undefined;
  api_key?: string = undefined;

  constructor(base_url: string, api_key: string){
    this.base_url = base_url;
    this.api_key = api_key;
  }

  async getFeedMeta(feed_id: number){
    if(Ut.isNumber(feed_id)){
      const response = await fetch(
        this.base_url + '/feed/getmeta.json?id=' + feed_id + '&apikey=' + this.api_key,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json'
          }
        }
      );
      if (!response.ok) {
        throw new Error(`HTTP error: Status ${response.status}`);
      }
      return response.json();
    }
  }

  static isValidFeedDataArgs(args: FeedDataArgs, meta: FeedMetaArgs){
    if(Ut.isObject(args) && Ut.isObject(meta)){
      if(args.start && Ut.isNumber(args.start)
          && args.end && Ut.isNumber(args.end)){
        if(args.start < meta.start_time && args.end > meta.start_time){
          return true
        }
      }
    }
    return false
  }

  async fetchFeedData(args: FeedDataArgs){
    if(Ut.isObject(args) && Ut.isNumber(args.feed_id)){
      const meta = await this.getFeedMeta(args.feed_id);
      if(EmonFeedApi.isValidFeedDataArgs(args, meta)){
        const searchParams = new URLSearchParams(args as urlSearchParamsType);
        searchParams.append('apikey', this.api_key? this.api_key : '');

        const url = this.base_url + '/feed/data.json?' + searchParams.toString();
        const response = await fetch(
          url,
          {
            method: 'GET',
            headers: {
              'Accept': 'application/json'
            }
          }
        );
        if (!response.ok) {
          throw new Error(`HTTP error: Status ${response.status}`);
        }
        const feed = response.json();
        if(Ut.isArray(feed)){
          return feed
        }
      }
    }
    return undefined
  }

}

type getFeedDataProps = {
    args: FeedDataArgs
}

export const getFeedData = ({
    args
}: getFeedDataProps) => {
    const get_ids_req = (feed_ids: [number]) => {
        let result = ""
        if(Ut.isArray(feed_ids)){
            feed_ids.map((id, index)=>{
                result += (index === 0 ) ? '' : '&'
                result += 'feed_ids=' + id
            })
        }
        return result;
    }

    const get_req_args = (args: FeedDataArgs) => {
        let result = ""
        if(Ut.isObject(args)){
            result += get_ids_req(args.feed_ids as [number])
            if(Ut.isNumber(args.start)){
                result += (result === "") ? '' : '&';
                result += 'start=' + args.start
            }

            if(Ut.isNumber(args.end)){
                result += (result === "") ? '' : '&';
                result += 'end=' + args.end
            }

            if(Ut.isNumber(args.window)){
                result += (result === "") ? '' : '&';
                result += 'window=' + args.window
            }

            if(Ut.isNumber(args.interval)){
                result += (result === "") ? '' : '&';
                result += 'interval=' + args.interval
            }
        }
        return result;
    }

    return {
        queryKey: ['emon_feeds_data'],
        queryFn: () =>
          getWithFetch({
            url:'http://127.0.0.1:5000/v1/emoncms/data?' + get_req_args(args)
          }),
      }
}