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
  YAxis,
} from 'recharts';
import Ut from '@/helpers/utils';
import { useDataViewer } from '@/stores/dataViewerStore';
import { ContentType } from 'recharts/types/component/Tooltip';
import { scaleTime } from 'd3-scale';
import { utcFormat } from 'd3-time-format';
import { GraphDataProps, LineChartDataProps } from '@/lib/graphTypes';
import ChartInfo from '@/components/fina_viewer/chartInfo';
export type GraphLocationProps = 'left' | 'right';


type FeedLineChartProps = {
  data_points: LineChartDataProps;
  time_start: number;
  time_window: number;
  interval: number;
  classBody?: string;
};

const getCurrentDomain = (
  data: GraphDataProps[],
  left: string | number,
  right: string | number
) => {
  if (!data || !data.length) {
    return [];
  }
  const is_domain = !(!Ut.isNumber(left) && !Ut.isNumber(right));
  return is_domain
    ? [new Date(Number(left) * 1000), new Date(Number(right) * 1000)]
    : [
      new Date((data[0]?.date ?? 0) * 1000),
      new Date((data[data.length - 1]?.date ?? 0) * 1000),
    ];
};

const getTicks = (data: GraphDataProps[], left: string | number, right: string | number) => {
  if (!data || !data.length) {
    return [];
  }
  const domain = getCurrentDomain(data, left, right);
  const scale = scaleTime().domain(domain).range([0, 1]);
  const ticks = scale.ticks(48); ///timeMinute.every(60)); //scale.ticks(timeMinute.every(20));

  return ticks.map((entry: Date) => entry.getTime() / 1000);
};

const dateFormat = (time: number, minTime?: number, maxTime?: number): string[] => {
  const date = new Date(time > 9999999999 ? time : time * 1000);
  const diffMs = (maxTime! - minTime!) * 1000;

  const oneHour = 60 * 60 * 1000;
  const oneDay = 24 * 60 * 60 * 1000;
  const oneWeek = 7 * oneDay;
  const oneMonth = 30 * oneDay;
  const oneYear = 365 * oneDay;

  if (diffMs <= oneHour) {
    return [utcFormat('%H:%M:%S s')(date)];
  } else if (diffMs <= oneDay) {
    return [utcFormat('%a %H:%M:%S')(date)];
  } else if (diffMs <= oneWeek) {
    return [utcFormat('%a %d')(date), utcFormat('%H:%M')(date)];
  } else if (diffMs <= oneMonth) {
    return [utcFormat('%b %d')(date)];
  } else if (diffMs <= oneYear) {
    return [utcFormat('%Y')(date), utcFormat('%b %d')(date)];
  } else {
    return [utcFormat('%Y')(date), utcFormat('%b %d')(date)];
  }
};

const createMultiLineTick = (minDate: number, maxDate: number) => {
  return function MultiLineTick({
    x,
    y,
    payload
  }: { x: number; y: number; payload: { value: number } }) {
    const lines: string[] = dateFormat(payload.value, minDate, maxDate);
    return (
      <g transform={`translate(${x},${y})`}>
        <text textAnchor="middle" fill="#888" fontSize="12">
          {lines.map((line, index) => (
            <tspan x="0" dy={index === 0 ? 0 : 14} key={index}>
              {line}
            </tspan>
          ))}
        </text>
      </g>
    );
  };
};

export function FeedLineChart({
  data_points,
  time_start,
  time_window,
  interval,
  classBody,
}: FeedLineChartProps) {
  const connect_nulls = useDataViewer((state) => state.connect_nulls);
  const can_zoom_view = useDataViewer((state) => state.can_zoom_view);
  const set_refAreaLeft = useDataViewer((state) => state.set_refAreaLeft);
  const set_refAreaRight = useDataViewer((state) => state.set_refAreaRight);
  const zoom_view = useDataViewer((state) => state.zoom_view);
  const zoom_graph = useDataViewer((state) => state.zoom_graph);

  const { topLeft, bottomLeft, topRight, bottomRight } = useDataViewer(
    (state) => state.zoom
  );

  const { left, right, refAreaLeft, refAreaRight } = useDataViewer(
    (state) => state.selector
  );

  const empty_graph_data = (
    time_start: number,
    time_window: number,
    interval: number
  ) => {
    let result: LineChartDataProps = { data: [], feeds: [] };
    if (
      Ut.isNumber(time_start) &&
      Ut.isNumber(time_window) &&
      Ut.isNumber(interval) &&
      time_window > 0 &&
      interval > 0
    ) {
      const nb_points = Math.ceil(time_window / interval);
      result = {
        data: [],
        feeds: [],
      };
      result.feeds.push({
        id: 0,
        name: 'null',
        location: 'left',
        db_data: [{
          datapath_id: 0,
          emonhost_id: 0,
          feed_id: 0,
        }]
      });
      for (const x of Array(nb_points).keys()) {
        result.data.push({
          date: time_start + x * interval,
          '0': null,
        });
      }
    }
    return result;
  };

  const hasData = (data: LineChartDataProps | undefined): boolean => {
    return (
      !!data &&
      Ut.isArray(data.feeds) &&
      data.feeds.length > 0 &&
      Ut.isArray(data.data) &&
      data.data.length > 0
    );
  };
  if (!hasData(data_points)) {
    data_points = empty_graph_data(time_start, time_window, interval);
  }
  const min_date = data_points?.data[0]?.date ?? undefined;
  const max_date =
    data_points?.data[data_points?.data.length - 1]?.date ?? undefined;
  
  const getTootltipValue = (value: number | undefined, key: number) => {
    if (Ut.isArray(value)) {
      const nb_items = value.length
      return nb_items > key + 1 ? value[key] : '';
    }
    return '';
  }
  const CustomTooltip: ContentType<number, string> = ({
    active,
    payload,
    label,
  }) => {
    if (active && payload && payload.length) {
      let valueIndex = 0;
      let range_index = null;
      if (payload.length == 2) {
        valueIndex = 1;
        range_index = 0;
      }
      return (
        <div className="custom-tooltip bg-foreground text-background p-2 rounded-md opacity-90">
          <p className="label">{`Feed: ${payload[valueIndex].name}`}</p>
          <p className="intro">{`Date: ${Ut.toLocaleDateFromTime(label)}`}</p>
          <p className="desc">{`Value : ${Ut.isNumber(payload[valueIndex].value)
            ? payload[valueIndex].value
            : 'null'
            }`}</p>
          {range_index !== null &&
            payload[range_index] &&
            Array.isArray(payload[range_index].value)
            ? [
              <p
                key={`${payload[valueIndex].name}_min`}
                className="desc"
              >{`Min : ${getTootltipValue(payload[range_index].value, 0)}`}</p>,
              <p
                key={`${payload[valueIndex].name}_max`}
                className="desc"
              >{`Max : ${getTootltipValue(payload[range_index].value, 1)}`}</p>,
            ]
            : null}
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
          classBody
        )}
      >
        <div className="w-full h-full select-none">
          <ResponsiveContainer
            width="100%"
            height={750}
            className="min-h-96 w-full"
          >
            <ComposedChart
              width={800}
              height={720}
              data={data_points?.data}
              onMouseDown={(e) => set_refAreaLeft(Number(e.activeLabel) || 0)}
              onMouseMove={(e) =>
                refAreaLeft && set_refAreaRight(Number(e.activeLabel) || 0)
              }
              onMouseUp={() =>
                can_zoom_view ? zoom_view(data_points) : zoom_graph()
              }
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
                scale={'time'}
                ticks={getTicks(data_points?.data, left, right)} ///data_points?.data, interval)}
                interval={5}
                textAnchor="start"
                tick={createMultiLineTick(min_date, max_date)}
                tickMargin={12}
              />
              <YAxis
                yAxisId="left"
                type="number"
                orientation="left"
                scale={'linear'}
                domain={[bottomLeft, topLeft]}
              />
              <YAxis
                yAxisId="right"
                type="number"
                orientation="right"
                scale={'linear'}
                domain={[bottomRight, topRight]}
                allowDataOverflow
              />
              <Legend verticalAlign="top" height={36} />
              <Tooltip content={CustomTooltip} />
              {data_points &&
                Ut.isArray(data_points.feeds) &&
                data_points.feeds &&
                data_points.feeds.length > 0
                ? data_points.feeds.map((item, index) => [
                  <Area
                    key={`${index}_range`}
                    legendType="none"
                    type="linear"
                    dataKey={`${item.id}_range`}
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
                    dataKey={item.id}
                    yAxisId={item.location}
                    type="linear"
                    stroke="#8884d8"
                    strokeWidth={2}
                    dot={false}
                    animationDuration={300}
                  />,
                ])
                : null}
              {refAreaLeft && refAreaRight ? (
                <ReferenceArea
                  yAxisId="left"
                  x1={refAreaLeft}
                  x2={refAreaRight}
                  stroke="#8884d8"
                  strokeOpacity={0.6}
                />
              ) : null}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        <div className="flex justify-between px-4">
          <ChartInfo
            currentDomain={getCurrentDomain(data_points?.data, left, right)}
          />
        </div>
      </div>
    </>
  );
}
