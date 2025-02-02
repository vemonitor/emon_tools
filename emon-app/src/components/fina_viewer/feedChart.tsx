import clsx from 'clsx';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts"
import {
    ChartConfig,
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
  } from "@/components/ui/chart"
import Ut from '@/utils/utils';
import { SelectedFileItem, setZoom, useDataViewer } from '@/stores/dataViewerStore';
import { SetStateAction, useState } from 'react';

export type GraphLocationProps = "left" | "right"

export type GraphDataProps = {[key: string]: number | null}

export type GraphFeedProps = { feed_id: number, location: GraphLocationProps }

export interface LineChartDataProps {
  data: GraphDataProps[],
  feeds: GraphFeedProps[]
}


const roundFloat = (value: number) => {
  return Math.round((value + Number.EPSILON) * 1000) / 1000
}

type StateProps = {
  data: LineChartDataProps
  left: string | number,
  right: string | number,
  refAreaLeft: number,
  refAreaRight: number,
  top: string | number,
  bottom: string | number,
  top2: string | number,
  bottom2: string | number,
  animation: boolean,
  time_start: number,
  time_window: number,
  interval: number,
}
const initialState = {
  data: {data: [], feeds: []},
  left: 'dataMin',
  right: 'dataMax',
  refAreaLeft: 0,
  refAreaRight: 0,
  top: 'dataMax+0.5',
  bottom: 'dataMin-0.5',
  top2: 'dataMax+0.5',
  bottom2: 'dataMin-0.5',
  animation: true,
  time_start: 0,
  time_window: 0,
  interval: 0,
} as StateProps;

const getAxisYDomain = (
  data: GraphDataProps[],
  from: number,
  to: number,
  ref: string
) => {
  const refData = data.filter((item) => {
    return item.date !== null && item.date >= from &&  item.date <= to
  });
  let [bottom, top] = [refData[0][ref], refData[0][ref]];
  refData.forEach((d) => {
    if (d[ref] !== null && ((top !== null && d[ref] > top) || top === null)) top = d[ref];
    if (d[ref] !== null && ((bottom !== null && d[ref] < bottom) || bottom === null)) bottom = d[ref];
  });
  return [bottom, top];
};

type FeedLineChartProps = {
  data_points?: LineChartDataProps;
  time_start: number;
  time_window: number;
  interval: number;
  selected_feeds: SelectedFileItem[];
  classBody?: string;
}

export function FeedLineChart({
  data_points,
  time_start,
  time_window,
  interval,
  selected_feeds,
  classBody
}: FeedLineChartProps) {
  const connect_nulls = useDataViewer((state) => state.connect_nulls)
  
  const [state, setState] = useState<StateProps>({
    data: data_points || { data: [], feeds: [] },
    left: 'dataMin',
    right: 'dataMax',
    refAreaLeft: 0,
    refAreaRight: 0,
    top: 'dataMax+0.5',
    bottom: 'dataMin-0.5',
    top2: 'dataMax+0.5',
    bottom2: 'dataMin-0.5',
    animation: true,
    time_start: time_start,
    time_window: time_window,
    interval: interval,
  });
  
  const zoom = () => {
    let { refAreaLeft, refAreaRight, data } = state;
    if (refAreaLeft === refAreaRight || refAreaRight === 0) {
      setState((prev) => ({ ...prev, refAreaLeft: 0, refAreaRight: 0 }));
      return;
    }
    if (refAreaLeft > refAreaRight) [refAreaLeft, refAreaRight] = [refAreaRight, refAreaLeft];

    const verticalZ = data.feeds
      .reduce((result, item)=>{
        const [bottom, top] = getAxisYDomain(
          data?.data, refAreaLeft, refAreaRight, `${item.feed_id}`);
        if(item.location === 'left'){
          if(top !== null) {result.left_top.push(top)}
          if(bottom !== null) {result.left_bottom.push(bottom)}
        }
        else{
          if(top !== null) {result.right_top.push(top)}
          if(bottom !== null) {result.right_bottom.push(bottom)}
        }
          
        return result
      }, {left_top: [], left_bottom: [], right_top: [], right_bottom: [], })
    let top = initialState.top
    let bottom = initialState.bottom
    let top2 = initialState.top2
    let bottom2 = initialState.bottom2
    
    const offset_right = (top - bottom) * 5 / 100
    if(verticalZ.left_top.length > 0 && verticalZ.left_bottom.length > 0){
      top = Math.max(verticalZ.left_top)
      bottom = Math.min(verticalZ.left_bottom)
      const offset_left = (top - bottom) * 5 / 100
      top = roundFloat(top + offset_left)
      bottom = roundFloat(bottom - offset_left)
    }
    if(verticalZ.right_top.length > 0 && verticalZ.right_bottom.length > 0){
      top2 = Math.max(verticalZ.right_top)
      bottom2 = Math.min(verticalZ.right_bottom)
      const offset_right = Ut.toFixedFloat((top2 - bottom2) * 5 / 100, 3)
      top2 += offset_right
      bottom2 += offset_right
    }
    setState((prev) => ({
      ...prev,
      refAreaLeft: 0,
      refAreaRight: 0,
      data: data,
      left: refAreaLeft,
      right: refAreaRight,
      bottom,
      top,
      bottom2,
      top2,
    }));
  };

  const zoomOut = () => {
    setState({
      data: data_points,
      refAreaLeft: 0,
      refAreaRight: 0,
      left: 'dataMin',
      right: 'dataMax',
      top: 'dataMax+1',
      bottom: 'dataMin',
      top2: 'dataMax+50',
      bottom2: 'dataMin+50',
      time_start: time_start,
      time_window: time_window,
      interval: interval,
    });
  };

  const empty_graph_data = (
    time_start: number,
    time_window: number,
    interval: number
  ) => {
    let result: LineChartDataProps |undefined = undefined
    if(Ut.isNumber(time_start) && Ut.isNumber(time_window) && Ut.isNumber(interval)
        && time_window > 0 && interval > 0){
      const nb_points = Math.ceil(time_window / interval)
      result = {
        data: [],
        feeds: []
      }
      result.feeds.push({
        feed_id: 0,
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
  const { data, left, right, bottom, top, bottom2, top2, refAreaLeft, refAreaRight } = state;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="label">{`Feed: ${payload[0].name}`}</p>
          <p className="intro">{`Date: ${Ut.toLocaleDateFromTime(label)}`}</p>
          <p className="desc">{`Value : ${payload[0].value}`}</p>
        </div>
      );
    }

    return null;
  };
  return (
    <>
      <div
        className={clsx('w-full flex items-start justify-start gap-2 h-full', classBody)}
      >
       <ResponsiveContainer
          width="100%"
          height={800}
          className='min-h-96 w-full'
        >
          <LineChart
            width={800}
            height={800}
            data={data?.data}
            onMouseDown={(e) => setState((prev) => ({ ...prev, refAreaLeft: Number(e.activeLabel) || 0 }))}
            onMouseMove={(e) => state.refAreaLeft && setState((prev) => ({ ...prev, refAreaRight: Number( e.activeLabel) || 0 }))}
            onMouseUp={zoom}
          >
            <CartesianGrid strokeDasharray="3 2 1" opacity={0.2} />
            <XAxis
              dataKey="date"
              type="number"
              label="Date"
              domain={[left, right]}
              allowDataOverflow
              height={200}
              angle={45}
              scale={'time'}
              textAnchor="start"
              tickFormatter={(value: number) => {
                return setZoom.get_value_date_by_window(value, time_window)
              }}
            />
            <YAxis
              yAxisId='left'
              type="number"
              orientation='left'
              domain={[bottom, top]}
            />
            <YAxis
              yAxisId='right'
              type="number"
              orientation='right'
              domain={[bottom2, top2]}
              allowDataOverflow
            />
            <Legend verticalAlign="top" height={36} />
            <Tooltip content={CustomTooltip}/>
            {data && Ut.isArray(data.feeds) && data.feeds && data.feeds.length > 0 ? (
              data.feeds.map((item, index) => (
                <Line
                  key={index}
                  connectNulls={connect_nulls}
                  dataKey={item.feed_id}
                  yAxisId={item.location}
                  type="linear"
                  stroke="#8884d8"
                  strokeWidth={2}
                  dot={false}
                  animationDuration={300}
                />
              ))
            ) : (null) }
            {refAreaLeft && refAreaRight ? (
              <ReferenceArea yAxisId="left" x1={refAreaLeft} x2={refAreaRight} stroke="#8884d8" strokeOpacity={0.6} />
            ) : null}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </>
    
  )
}