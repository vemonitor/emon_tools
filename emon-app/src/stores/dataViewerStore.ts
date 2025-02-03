import { GraphDataProps, LineChartDataProps } from '@/components/fina_viewer/feedChart'
import { FeedMetaOut } from '@/emon-tools-api/dataViewerApi'
import Ut from '@/utils/utils'
import { create, StateCreator } from 'zustand'
import { devtools } from 'zustand/middleware'

export type FinaSourceProps = "emoncms" | "archive"

export type GraphLocationProps = "left" | "right"

export type SelectedFeedsProps = {file_name: string, position: GraphLocationProps}

export type SelectedFileItem = {
  is_checked: boolean;
  item_id: string;
  side: GraphLocationProps;
  name: string;
  meta: FeedMetaOut;
}

export type VerticalRange = {
  left_top: number[], left_bottom: number[], right_top: number[], right_bottom: number[]
}

export class setZoom {
  static is_time_ref(time_start: number, time_end: number){
    return time_start >= 0 && time_end >= 0
  }

  static is_end_time(time_start: number, time_end: number){
    return time_end >= 0
      || (time_start >= 0 && time_start < time_end)
  }

  static get_static_zooms(){
    return [
      {label: "5 sec", time_window: 5, interval: 0, moveBy: 1},
      {label: "10 sec", time_window: 10, interval: 0, moveBy: 1},
      {label: "30 sec", time_window: 30, interval: 0, moveBy: 10},
      {label: "1 min", time_window: 60, interval: 0, moveBy: 30},
      {label: "2 min", time_window: 120, interval: 0, moveBy: 60},
      {label: "3 min", time_window: 180, interval: 0, moveBy: 60},
      {label: "5 min", time_window: 300, interval: 0, moveBy: 60},
      {label: "15 min", time_window: 900 , interval: 0, moveBy: 300},
      {label: "30 min", time_window: 1800 , interval: 0, moveBy: 900},
      {label: "1 hour", time_window: 3600 , interval: 10, moveBy: 1800},
      {label: "6 hours", time_window: 21600 , interval: 30, moveBy: 3600},
      {label: "12 hours", time_window: 43200 , interval: 60, moveBy: 3600},
      {label: "1 day", time_window: 86400 , interval: 120, moveBy: 3600},
      {label: "1 week", time_window: 604800 , interval: 900, moveBy: 86400},
      {label: "2 week", time_window: 1209600 , interval: 1800, moveBy: 172800},
      {label: "1 month", time_window: 2592000 , interval: 3600, moveBy: 604800},
      {label: "1 year", time_window: 31449600 , interval: 43200, moveBy: 2592000},
      {label: "2 year", time_window: 62899200 , interval: 86400, moveBy: 31449600},
      {label: "3 year", time_window: 94348800 , interval: 86400, moveBy: 31449600},
      {label: "5 year", time_window: 157248000 , interval: 604800, moveBy: 31449600}
    ]
  }

  static getMonths() {
    return ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  }
  
  static add_leading_zeros(value: number){
    if(Ut.isNumber(value) && value <= 9){
      return `0${value}`
    }
    return `${value}`
  }

  static get_value_date_by_window(
    value: number,
    time_window: number
  ){
    const dt = new Date(value * 1000)
    const zoom = setZoom.get_zoom_by_window(time_window)
    if(zoom.time_window <= 21600){
      return `${setZoom.add_leading_zeros(dt.getDate())} ${dt.toLocaleTimeString()}`
    }
    else if(zoom.time_window <= 86400){
      return `${setZoom.add_leading_zeros(dt.getDate())} ${dt.toLocaleTimeString()}`
    }
    else if(zoom.time_window <= 2592000){
      return `${setZoom.getMonths()[dt.getMonth()]} ${setZoom.add_leading_zeros(dt.getDate())}`
    }
    else if(zoom.time_window > 2592000){
      return `${setZoom.getMonths()[dt.getMonth()]} ${dt.getFullYear()}`
    }
    return dt.toLocaleDateString() + ' ' + dt.toLocaleTimeString()
  }

  static get_zoom_by_window(
    time_window: number,
    default_time_window: number = 86400
  ){
    const zooms = setZoom.get_static_zooms();
    if(time_window == 0){
      return zooms.filter(item => item.time_window === default_time_window)[0]
    }
    return zooms
      .reduce(function(prev, curr) {
        return (
          Math.abs(curr.time_window - time_window) < Math.abs(prev.time_window - time_window) ? curr : prev);
      });
  }

  static get_interval_by_window(time_window: number){
    const zooms = setZoom.get_static_zooms();
    let zoom = zooms
      .filter(zoom => zoom.time_window == time_window)
    if(zoom.length > 0){
      return zoom[0]
    }
    zoom = zooms
    .reduce(function(prev, curr) {
      return (Math.abs(curr.time_window - time_window) < Math.abs(prev.time_window - time_window) ? curr : prev);
    });
    if(zoom.length > 0){
      return zoom[0]
    }
    return zooms[12]
  }

  static zoom_out(time_window: number){
    const zooms = setZoom.get_static_zooms();
    const zoom = zooms
      .filter(zoom => zoom.time_window > time_window)
    if(zoom.length > 0){
      return zoom[0]
    }
    return zooms[zooms.length - 1]
  }

  static zoom_in(time_window: number){
    const zooms = setZoom.get_static_zooms();
    const zoom = zooms
      .filter(zoom => zoom.time_window < time_window)
    const nb_zoom = zoom.length
    if(nb_zoom > 0){
      return zoom[nb_zoom - 1]
    }
    return zooms[0]
  }

  static set_end_time(
    time_start: number,
    time_end: number,
    time_window: number
  ){
    if(setZoom.is_end_time(time_start, time_end)){
      return {

      }
    }
  }

  static getAxisYDomain(
    data: GraphDataProps[],
    from: number,
    to: number,
    ref: string
  ){
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

  static roundFloat(value: number){
    return Math.round((value + Number.EPSILON) * 1000) / 1000
  }

  static getAxisYRange(
    data: LineChartDataProps,
    refAreaLeft: number,
    refAreaRight: number
  ){
    const result = {
      topLeft: initialZoom.topLeft,
      bottomLeft: initialZoom.bottomLeft,
      topRight: initialZoom.topRight,
      bottomRight: initialZoom.bottomRight,
    }
    const verticalRange = data.feeds
      .reduce((result: VerticalRange, item) =>{
        const [bottom, top] = setZoom.getAxisYDomain(
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
      }, {
        left_top: [], left_bottom: [], right_top: [], right_bottom: []
      })
    
    if(verticalRange.left_top.length > 0 && verticalRange.left_bottom.length > 0){
      result.topLeft = Math.max(...verticalRange.left_top)
      result.bottomLeft = Math.min(...verticalRange.left_bottom)
      const offset_left = (result.topLeft - result.bottomLeft) * 5 / 100
      result.topLeft = setZoom.roundFloat(result.topLeft + offset_left)
      result.bottomLeft = setZoom.roundFloat(result.bottomLeft - offset_left)
    }
    if(verticalRange.right_top.length > 0 && verticalRange.right_bottom.length > 0){
      result.topRight = Math.max(...verticalRange.right_top)
      result.bottomRight = Math.min(...verticalRange.right_bottom)
      const offset_right = (result.topRight - result.bottomRight) * 5 / 100
      result.topRight = setZoom.roundFloat(result.topRight + offset_right)
      result.bottomRight = setZoom.roundFloat(result.bottomRight - offset_right)
    }
    return result
  }
}

export const get_view_time_rage = () => {
  const time_start = useDataViewer.getState().time_start
  const time_window = useDataViewer.getState().time_window
  return {left: time_start, right: time_window}
}

export type NavigationMenu = {
  can_go_start: boolean;
  can_go_back: boolean;
  can_go_after: boolean;
  can_go_end: boolean;
  can_zoom_in: boolean;
  can_zoom_out: boolean;
  zoom_level: number;
  move_level: number;
}

export const initialNavGaph = {
  can_go_back: true,
  can_go_after: true,
  can_zoom_in: true,
  can_zoom_out: true,
  can_go_start: true,
  can_go_end: true,
  zoom_level: 0.25,
  move_level: 0.25,
} as NavigationMenu

export const initialNavView = {
  can_go_back: true,
  can_go_after: true,
  can_zoom_in: true,
  can_zoom_out: true,
  can_go_start: true,
  can_go_end: true,
  zoom_level: 0.25,
  move_level: 0.25,
} as NavigationMenu

export type GraphZoom = {
  left: string | number,
  right: string | number,
  refAreaLeft: number,
  refAreaRight: number,
  topLeft: string | number,
  bottomLeft: string | number,
  topRight: string | number,
  bottomRight: string | number,
  animation: boolean
}

export const initialZoom = {
  left: 'dataMin',
  right: 'dataMax',
  refAreaLeft: 0,
  refAreaRight: 0,
  topLeft: 'dataMax+0.5',
  bottomLeft: 'dataMin-0.5',
  topRight: 'dataMax+0.5',
  bottomRight: 'dataMin-0.5',
  animation: true,
} as GraphZoom

type DataViewerStore = {
    selected_feeds: SelectedFileItem[],
    source: FinaSourceProps,
    time_start: number,
    time_window: number,
    interval: number,
    zoom: GraphZoom,
    nav_graph: NavigationMenu,
    nav_view: NavigationMenu,
    can_zoom_view:  boolean,
    is_view_zoomed:  boolean,
    connect_nulls: boolean,
    add_feed: (selected_item: SelectedFileItem) => void,
    remove_feed: (selected_item: SelectedFileItem) => void,
    reset_feeds: (file_name: string) => void,
    init_time_start: (time_start: number) => void,
    set_time_start: (time_start: number) => void,
    set_time_window: (time_window: number) => void,
    set_interval: (interval: number) => void,
    set_source: (source: FinaSourceProps) => void,
    reset_refAreas: () => void,
    set_refAreaLeft: (value: number) => void,
    set_refAreaRight: (value: number) => void,
    zoom_view: (data: LineChartDataProps) => void,
    zoom_out_view: () => void,
    toggle_can_zoom_view: () => void,
    go_back: () => void,
    go_after: () => void,
    go_start: () => void,
    go_end: () => void,
    zoom_in: () => void,
    zoom_out: () => void,
    reset_store: () => void,
    toggle_connect_nulls: () => void,
}

const createDataViewerSlice: StateCreator<
DataViewerStore,
[['zustand/devtools', never]],
[],
DataViewerStore
> = (set) => ({
      selected_feeds: [],
      source: 'archive',
      time_start: 0,
      time_window: 3600 * 24,
      interval: 120,
      zoom: initialZoom,
      nav_graph: initialNavGaph,
      nav_view: initialNavView,
      can_zoom_view:  false,
      is_view_zoomed:  false,
      connect_nulls: false,
      // store methods
      add_feed: (selected_item: SelectedFileItem) => set( (state) => (
          { selected_feeds: [...state.selected_feeds, selected_item] }
      ), undefined, 'DataViewer/add_feed'),
      remove_feed: (selected_item: SelectedFileItem) => set((state) => {
          const current_feeds = state.selected_feeds
            .filter((item) => (
              item.item_id !== selected_item.item_id && item.side !== selected_item.side
            ) || (item.item_id !== selected_item.item_id && item.side === selected_item.side))
          if(current_feeds.length === 0){
            state.reset_store()
          }
          return{ selected_feeds: current_feeds }
      }, undefined, 'DataViewer/remove_left_graph'),
      reset_feeds: () => set(() => (
          { selected_feeds: [] }
      ), undefined, 'DataViewer/reset_selected_feeds'),
      init_time_start: (time_start: number) => set((state) => {
          if(state.time_start <= 0){
            return { time_start: time_start }
          }
          return {}
      }, undefined, 'DataViewer/set_time_start'),
      set_time_start: (time_start: number) => set(() => (
          { time_start: time_start }
      ), undefined, 'DataViewer/set_time_start'),
      set_time_window: (time_window: number) => set(() => {
        const zoom = setZoom.get_interval_by_window(time_window)
        if(zoom.time_window == time_window){
          return{
            time_window: time_window,
            interval: zoom.interval
          }
        }
        return{
          time_window: zoom.time_window,
          interval: zoom.interval
        }

    }, undefined, 'DataViewer/set_time_window'),
      set_interval: (interval: number) => set(() => (
          { interval: interval }
      ), undefined, 'DataViewer/set_interval'),
      set_source: (source: FinaSourceProps) => set(() => (
          { source: source }
      ), undefined, 'DataViewer/set_source'),
      set_refAreaLeft: (value: number) => set((state) => (
          { zoom: { ...state.zoom, refAreaLeft: value } }
      ), undefined, 'DataViewer/set_refAreaLeft'),
      set_refAreaRight: (value: number) => set((state) => (
          { zoom: { ...state.zoom, refAreaRight: value } }
      ), undefined, 'DataViewer/refAreaRight'),
      reset_refAreas: () => set((state) => (
          { zoom: { ...state.zoom, refAreaLeft: 0, refAreaRight: 0 } }
      ), undefined, 'DataViewer/reset_refAreas'),
      zoom_view: (data: LineChartDataProps) => set((state) => {
        let { refAreaLeft, refAreaRight } = state.zoom;
        if (refAreaLeft === refAreaRight || refAreaRight === 0) {
          state.reset_refAreas();
          return {}
        }

        if (refAreaLeft > refAreaRight) {
          [refAreaLeft, refAreaRight] = [refAreaRight, refAreaLeft];
        }
        const verticalRange = setZoom.getAxisYRange(
          data,
          refAreaLeft,
          refAreaRight
        )
        return {
          is_view_zoomed: true,
          zoom: {
            ...state.zoom,
            refAreaLeft: 0,
            refAreaRight: 0,
            left: refAreaLeft,
            right: refAreaRight,
            topLeft: verticalRange.topLeft,
            bottomLeft: verticalRange.bottomLeft,
            topRight: verticalRange.topRight,
            bottomRight: verticalRange.bottomRight,
          }
        }
      }, undefined, 'DataViewer/zoom_view'),
      zoom_out_view: () => set(() => {
        return{ is_view_zoomed: false, zoom: initialZoom }
      }, undefined, 'DataViewer/zoom_out_view'),
      toggle_can_zoom_view: () => set((state) => {
          return {
            can_zoom_view: state.can_zoom_view === true ? false : true
          }
      }, undefined, 'DataViewer/reset_store'),
      go_back: () => set((state) => {
        state.zoom_out_view()
        const zoom = setZoom.get_interval_by_window(state.time_window)
        return{ time_start: state.time_start - zoom.moveBy }
      }, undefined, 'DataViewer/go_back'),
      go_after: () => set((state) => {
        state.zoom_out_view()
        const zoom = setZoom.get_interval_by_window(state.time_window)
        return{ time_start: state.time_start + zoom.moveBy }
      }, undefined, 'DataViewer/go_after'),
      go_start: () => set((state) => {
        state.zoom_out_view()
        const zoom = setZoom.get_interval_by_window(state.time_window)
        return{ time_start: state.time_start }
      }, undefined, 'DataViewer/go_start'),
      go_end: () => set((state) => {
        state.zoom_out_view()
        const zoom = setZoom.get_interval_by_window(state.time_window)
        return{ time_start: state.time_start + state.time_start }
      }, undefined, 'DataViewer/go_end'),
      zoom_in: () => set((state) => {
        state.zoom_out_view()
        const zoom = setZoom.zoom_in(state.time_window)
        return ({
          nav_graph: {
            ...state.nav_graph,
            can_zoom_in: setZoom.zoom_in(zoom.time_window).time_window != zoom.time_window,
            can_zoom_out: true
          },
          time_window: zoom.time_window,
          interval: zoom.interval,
          
        })
      }, undefined, 'DataViewer/zoom_in'),
      zoom_out: () => set((state) => {
        state.zoom_out_view()
        const zoom = setZoom.zoom_out(state.time_window)
        return ({
          nav_graph: {
            ...state.nav_graph,
            can_zoom_out: setZoom.zoom_out(zoom.time_window).time_window != zoom.time_window,
            can_zoom_in: true
          },
          time_window: zoom.time_window,
          interval: zoom.interval
        })
      }, undefined, 'DataViewer/zoom_out'),
      toggle_connect_nulls: () => set((state) => {
          return {
            connect_nulls: state.connect_nulls === true ? false : true
          }
      }, undefined, 'DataViewer/reset_store'),
      reset_store: () => set(() => ({
          selected_feeds: [],
          time_start: 0,
          //time_window: 0,
          //interval: 0,
          can_go_back: true,
          can_go_after: true,
          can_zoom_in: true,
          can_zoom_out: true,
      }), undefined, 'DataViewer/reset_store')
})

export const useDataViewer = create<DataViewerStore>()(
  devtools((...args) => (
    {
      ...createDataViewerSlice(...args),
  }
))
)