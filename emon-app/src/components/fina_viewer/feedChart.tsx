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
import Ut from '@/utils/utils';
import { SelectedFileItem, setZoom, useDataViewer } from '@/stores/dataViewerStore';

export type GraphLocationProps = "left" | "right"

export type GraphDataProps = {[key: string]: number | null}

export type GraphFeedProps = { feed_id: number, location: GraphLocationProps }

export interface LineChartDataProps {
  data: GraphDataProps[],
  feeds: GraphFeedProps[]
}

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
  const set_refAreaLeft = useDataViewer((state) => state.set_refAreaLeft)
  const set_refAreaRight = useDataViewer((state) => state.set_refAreaRight)
  const zoom_view = useDataViewer((state) => state.zoom_view)
  const {
    left, right,
    topLeft, bottomLeft,
    topRight, bottomRight,
    refAreaLeft, refAreaRight,
  } = useDataViewer((state) => state.zoom)

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
          <ComposedChart
            width={800}
            height={800}
            data={data_points?.data}
            onMouseDown={(e) => set_refAreaLeft(Number(e.activeLabel) || 0)}
            onMouseMove={(e) => refAreaLeft && set_refAreaRight(Number( e.activeLabel) || 0)}
            onMouseUp={()=>zoom_view(data_points)}
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
              domain={[bottomLeft, topLeft]}
            />
            <YAxis
              yAxisId='right'
              type="number"
              orientation='right'
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
                    dataKey={`${item.feed_id}_range`}
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
                    dataKey={item.feed_id}
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
    </>
    
  )
}