import clsx from 'clsx';
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts"
import Ut from '@/helpers/utils';
import { useDataViewer } from '@/stores/dataViewerStore';
import { ContentType } from 'recharts/types/component/Tooltip';
import { scaleTime } from 'd3-scale';
import { utcFormat } from 'd3-time-format';
import { utcHour, utcSecond, utcMinute, utcDay, utcMonth, utcYear, utcWeek } from 'd3-time';
import { GraphDataProps, SelectedFileItem } from '@/lib/graphTypes';
import ChartInfo from '@/components/fina_viewer/chartInfo';
export type GraphLocationProps = "left" | "right"

export type GraphFeedProps = {
  datapath_id: number,
  emonhost_id: number,
  file_id: number,
  feed_id: number,
  file_name: string,
  location: GraphLocationProps
}

export interface LineChartDataProps {
  data: GraphDataProps[],
  feeds: GraphFeedProps[]
}

type FeedLineChartProps = {
  data_points: LineChartDataProps;
  time_start: number;
  time_window: number;
  interval: number;
  selected_feeds: SelectedFileItem[];
  classBody?: string;
}

const getCurrentDomain = (data: GraphDataProps[], left: number, right: number) => {
  if (!data || !data.length ) {return [];}
  const is_domain = !(!Ut.isNumber(left) && !Ut.isNumber(right))
  return is_domain ? [
    new Date(left * 1000), new Date(right * 1000)
  ] : [
    new Date((data[0]?.date ?? 0) * 1000), new Date((data[data.length - 1]?.date ?? 0) * 1000)
  ];
}

const getTicks = (data: GraphDataProps[], left: number, right: number) => {
	if (!data || !data.length ) {return [];}
  const domain = getCurrentDomain(data, left, right);
  const scale = scaleTime().domain(domain).range([0, 1]);
  const ticks = scale.ticks(48)///timeMinute.every(60)); //scale.ticks(timeMinute.every(20));
  
  return ticks.map((entry: Date) => entry.getTime() / 1000);
};

const formatMillisecond = utcFormat(".%L"),
    formatSecond = utcFormat("%I:%M:%S"),
    formatMinute = utcFormat("%a %d %I:%M:%S"),
    formatHour = utcFormat("%a %d %H:%M"),
    formatDay = utcFormat("%b %a %d %H"),
    formatWeek = utcFormat("%b %d"),
    formatMonth = utcFormat("%B %d"),
    formatYear = utcFormat("%Y %b %d");
const dateFormat = (time: number, minTime?: number, maxTime?: number) => {
  const date = new Date(time * 1000)
  if (minTime !== undefined && maxTime !== undefined) {
    // Calculate overall range in milliseconds.
    const diffMs = (maxTime - minTime) * 1000;
    const onehour = 60 * 60 * 1000;
    const oneday = 24 * 60 * 60 * 1000;
    const oneWeek = 7 * 24 * 60 * 60 * 1000;
    const oneMonth = 30 * 24 * 60 * 60 * 1000;
    const oneYear = 365 * 24 * 60 * 60 * 1000;

    let formatter;
    if (diffMs <= onehour) {
      // For day or week ranges, show detailed day-level info.
      formatter = formatMinute;
    } else if (diffMs <= oneday) {
      // For day or week ranges, show detailed day-level info.
      formatter = formatHour;
    } else if (diffMs <= oneWeek) {
      // For day or week ranges, show detailed day-level info.
      formatter = formatDay;
    } else if (diffMs <= oneMonth) {
      // For month-range data, use a concise week-level format.
      formatter = formatWeek;
    } else if (diffMs <= oneYear) {
      // For year-range data, display the month.
      formatter = formatMonth;
    } else {
      // For ranges wider than a year, display the year.
      formatter = formatYear;
    }
    return formatter(date);
  }
	return (utcSecond(date) < date ? formatMillisecond
      : utcMinute(date) < date ? formatSecond
      : utcHour(date) < date ? formatMinute
      : utcDay(date) < date ? formatHour
      : utcMonth(date) < date ? (utcWeek(date) < date ? formatDay : formatWeek)
      : utcYear(date) < date ? formatMonth
      : formatYear)(date);
};

export function FeedLineChart({
  data_points,
  time_start,
  time_window,
  interval,
  selected_feeds,
  classBody
}: FeedLineChartProps) {
  const connect_nulls = useDataViewer((state) => state.connect_nulls)
  const can_zoom_view = useDataViewer((state) => state.can_zoom_view)
  const set_refAreaLeft = useDataViewer((state) => state.set_refAreaLeft)
  const set_refAreaRight = useDataViewer((state) => state.set_refAreaRight)
  const zoom_view = useDataViewer((state) => state.zoom_view)
  const zoom_graph = useDataViewer((state) => state.zoom_graph)
  
  const {
    topLeft, bottomLeft,
    topRight, bottomRight
  } = useDataViewer((state) => state.zoom)

  const {
    left, right,
    refAreaLeft, refAreaRight,
  } = useDataViewer((state) => state.selector)

  const empty_graph_data = (
    time_start: number,
    time_window: number,
    interval: number
  ) => {
    let result: LineChartDataProps = {data: [], feeds: []}
    if(Ut.isNumber(time_start) && Ut.isNumber(time_window) && Ut.isNumber(interval)
        && time_window > 0 && interval > 0){
      const nb_points = Math.ceil(time_window / interval)
      result = {
        data: [],
        feeds: []
      }
      result.feeds.push({
        datapath_id: 0,
        emonhost_id: 0,
        file_id: 0,
        feed_id: 0,
        file_name: "null",
        location: "left"
      })
      for (const x of Array(nb_points).keys()) {
        result.data.push({
          date: time_start + x * interval,
          "0": null
        })
      }
    }
    return result
  }

  const hasData = (data: LineChartDataProps | undefined): boolean => {
    return !!data && Ut.isArray(data.feeds)
      && data.feeds.length > 0
      && Ut.isArray(data.data)
      && data.data.length > 0
  }
  if(!hasData(data_points)){
    data_points = empty_graph_data(time_start, time_window, interval)
  }
  const min_date = data_points?.data[0]?.date ?? undefined;
  const max_date = data_points?.data[data_points?.data.length - 1]?.date ?? undefined;
  const CustomTooltip: ContentType<number, string> = ({
    active, payload, label
  }) => {
    if (active && payload && payload.length) {
      let valueIndex = 0
      let range_index = null
      if(payload.length == 2){
        valueIndex = 1
        range_index = 0
      }
      return (
        <div className="custom-tooltip">
          <p className="label">{`Feed: ${payload[valueIndex].name}`}</p>
          <p className="intro">{`Date: ${Ut.toLocaleDateFromTime(label)}`}</p>
          <p className="desc">{`Value : ${Ut.isNumber(payload[valueIndex].value) ? payload[valueIndex].value : 'null'}`}</p>
          {range_index !== null && payload[range_index] && payload[range_index].value && Array.isArray(payload[range_index].value) ? [
            <p key={`${payload[valueIndex].name}_min`} className="desc">{`Min : ${payload[range_index].value[0] ? payload[range_index].value[0] : ''}`}</p>,
            <p key={`${payload[valueIndex].name}_max`} className="desc">{`Max : ${payload[range_index].value[1]}`}</p>
          ] : null}
        </div>
      );
    }

    return null;
  };
  return (
    <>
      <div
        className={clsx(
          'w-full flex flex-col items-start justify-start gap-0 h-full',
          classBody)}
      >
        <div className='w-full h-full select-none'>
          <ResponsiveContainer
            width="100%"
            height={750}
            className='min-h-96 w-full'
          >
            <ComposedChart
              width={800}
              height={720}
              data={data_points?.data}
              onMouseDown={(e) => set_refAreaLeft(Number(e.activeLabel) || 0)}
              onMouseMove={(e) => refAreaLeft && set_refAreaRight(Number( e.activeLabel) || 0)}
              onMouseUp={()=>can_zoom_view ? zoom_view(data_points) : zoom_graph()}
              
            >
              <CartesianGrid strokeDasharray="3 2 1" opacity={0.2} />
              <XAxis
                dataKey="date"
                type="number"
                label="Date"
                domain={[left, right]}
                allowDataOverflow
                includeHidden
                height={220}
                angle={45}
                scale={'time'}
                ticks={getTicks(data_points?.data, left, right)}///data_points?.data, interval)}
                interval={5}
                textAnchor="start"
                tickFormatter={(value: number) => {
                  return dateFormat(value, min_date, max_date)
                }}
              />
              <YAxis
                yAxisId='left'
                type="number"
                orientation='left'
                scale={'linear'}
                domain={[bottomLeft, topLeft]}
              />
              <YAxis
                yAxisId='right'
                type="number"
                orientation='right'
                scale={'linear'}
                domain={[bottomRight, topRight]}
                allowDataOverflow
              />
              <Legend verticalAlign="top" height={36} />
              <Tooltip content={CustomTooltip}/>
              {data_points && Ut.isArray(data_points.feeds) && data_points.feeds && data_points.feeds.length > 0 ? (
                
                data_points.feeds.map((item, index) => [
                    <Area
                      key={`${index}_range`}
                      legendType='none'
                      type="linear"
                      dataKey={`${item.file_id}_range`}
                      yAxisId={item.location}
                      stroke="none"
                      fill="#ccc"
                      dot={false}
                      activeDot={false}
                      connectNulls={connect_nulls}
                      opacity={0.4}
                      animationDuration={300}
                    />,
                    <Line
                      key={`${index}_line`}
                      
                      connectNulls={connect_nulls}
                      dataKey={item.file_id}
                      yAxisId={item.location}
                      type="linear"
                      stroke="#8884d8"
                      strokeWidth={2}
                      dot={false}
                      animationDuration={300}
                    />

                  
                ])
              ) : (null) }
              {refAreaLeft && refAreaRight ? (
                <ReferenceArea yAxisId="left" x1={refAreaLeft} x2={refAreaRight} stroke="#8884d8" strokeOpacity={0.6} />
              ) : null}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        <div className='flex justify-between px-4'>
          <ChartInfo
            currentDomain={getCurrentDomain(data_points?.data, left, right)}
          />
        </div> 
      </div>
    </>
    
  )
}