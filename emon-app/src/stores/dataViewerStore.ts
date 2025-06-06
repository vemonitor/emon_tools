import { GraphHelper } from '@/helpers/graphHelper'
import Ut from '@/helpers/utils'
import { GraphSelector, GraphSource, GraphZoom, LineChartDataProps, NavigationMenu, SelectedToGraph } from '@/lib/graphTypes'
import { create, StateCreator } from 'zustand'
import { devtools } from 'zustand/middleware'


export const get_view_time_rage = () => {
  const time_start = useDataViewer.getState().time_start
  const time_window = useDataViewer.getState().time_window
  return {left: time_start, right: time_window}
}

export const initialNavGaph = {
  can_reload: true,
  can_go_back: true,
  can_go_after: true,
  can_zoom_in: true,
  can_zoom_out: true,
  can_go_start: true,
  can_go_end: true,
  zoom_level: 0.5,
  move_level: 0.25,
} as NavigationMenu

export const initialNavView = {
  can_reload: false,
  can_go_back: false,
  can_go_after: false,
  can_zoom_in: true,
  can_zoom_out: false,
  can_go_start: false,
  can_go_end: false,
  zoom_level: 0.5,
  move_level: 0.25,
} as NavigationMenu


export const initialSelector = {
  left: 'dataMin',
  right: 'dataMax',
  refAreaLeft: 0,
  refAreaRight: 0
} as GraphSelector

export const initialZoom = {
  topLeft: 'dataMax+0.5',
  bottomLeft: 'dataMin-0.5',
  topRight: 'dataMax+0.5',
  bottomRight: 'dataMin-0.5',
  animation: true,
} as GraphZoom

type DataViewerStore = {
    graph_source: GraphSource | null,
    selected_feeds: SelectedToGraph[],
    data_points: LineChartDataProps,
    time_start: number,
    time_window: number,
    interval: number,
    selector: GraphSelector,
    zoom: GraphZoom,
    nav_graph: NavigationMenu,
    can_zoom_view:  boolean,
    is_view_zoomed:  boolean,
    connect_nulls: boolean,
    setGraphSource: (graph_source: GraphSource) => void,
    add_feed: (selected_item: SelectedToGraph) => void,
    remove_feed: (selected_item: SelectedToGraph) => void,
    reset_feeds: () => void,
    set_data_points: (data_points: LineChartDataProps) => void,
    init_time_start: (time_start: number) => void,
    set_time_start: (time_start: number) => void,
    set_time_window: (time_window: number) => void,
    set_interval: (interval: number) => void,
    reset_refAreas: () => void,
    set_refAreaLeft: (value: number) => void,
    set_refAreaRight: (value: number) => void,
    zoom_view: (data: LineChartDataProps) => void,
    reload_view: () => void,
    toggle_can_zoom_view: () => void,
    reload: () => void,
    go_back: () => void,
    go_after: () => void,
    go_start: () => void,
    go_end: () => void,
    zoom_graph: () => void,
    reset_graph: () => void,
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
      graph_source: null,
      selected_feeds: [],
      data_points: {data: [], feeds: []},
      time_start: 0,
      time_window: 3600 * 24,
      interval: 120,
      selector: initialSelector,
      zoom: initialZoom,
      nav_graph: initialNavGaph,
      can_zoom_view:  false,
      is_view_zoomed:  false,
      connect_nulls: false,
      // store methods
      setGraphSource: (graph_source: GraphSource) => set( () => (
          { graph_source: graph_source }
      ), undefined, 'DataViewer/add_feed'),
      add_feed: (selected_item: SelectedToGraph) => set( (state) => (
          { selected_feeds: [...state.selected_feeds, selected_item] }
      ), undefined, 'DataViewer/add_feed'),
      remove_feed: (selected_item: SelectedToGraph) => set((state) => {
          const current_feeds = state.selected_feeds
            .filter((item) => item.id !== selected_item.id)
          if(current_feeds.length === 0){
            state.reset_store()
          }
          return{ selected_feeds: current_feeds }
      }, undefined, 'DataViewer/remove_feed'),
      reset_feeds: () => set(() => (
          { selected_feeds: [] }
      ), undefined, 'DataViewer/reset_feeds'),
      set_data_points: (data_points: LineChartDataProps) => set(() => {
          return {data_points: {
            data: data_points.data,
            feeds: data_points.feeds
          }}
      }, undefined, 'DataViewer/set_data_points'),
      init_time_start: (time_start: number) => set((state) => {
          if(state.time_start <= 0){
            return { time_start: time_start }
          }
          return {}
      }, undefined, 'DataViewer/init_time_start'),
      set_time_start: (time_start: number) => set(() => (
          { time_start: time_start }
      ), undefined, 'DataViewer/set_time_start'),
      set_time_window: (time_window: number) => set(() => {
        const zoom = GraphHelper.get_interval_by_window(time_window)
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
      set_refAreaLeft: (value: number) => set((state) => (
          { selector: { ...state.selector, refAreaLeft: value } }
      ), undefined, 'DataViewer/set_refAreaLeft'),
      set_refAreaRight: (value: number) => set((state) => (
          { selector: { ...state.selector, refAreaRight: value } }
      ), undefined, 'DataViewer/set_refAreaRight'),
      reset_refAreas: () => set((state) => (
          { selector: { ...state.selector, refAreaLeft: 0, refAreaRight: 0 } }
      ), undefined, 'DataViewer/reset_refAreas'),
      zoom_graph: () => set((state) => {
        let { refAreaLeft, refAreaRight } = state.selector;
        if (refAreaLeft === refAreaRight || refAreaRight === 0) {
          state.reset_refAreas();
          return {}
        }

        if (refAreaLeft > refAreaRight) {
          [refAreaLeft, refAreaRight] = [refAreaRight, refAreaLeft];
        }
        const time_window = refAreaRight - refAreaLeft
        const zoom = GraphHelper.zoom_in(time_window)
        return {
          selector:{
            refAreaLeft: 0,
            refAreaRight: 0,
            left: refAreaLeft,
            right: refAreaRight,
          },
          nav_graph: {
            ...state.nav_graph,
            can_zoom_in: GraphHelper.zoom_in(zoom.time_window).time_window != zoom.time_window,
            can_zoom_out: true
          },
          time_start: refAreaLeft,
          time_window: time_window,
          interval: zoom.interval
        }
      }, undefined, 'DataViewer/zoom_graph'),
      reset_graph: () => set((state) => {
          const currentSerach = GraphHelper.init_default_search(
            state.selected_feeds,
            true,
            86400
          )
          return {
            ...currentSerach,
            selector: initialSelector,
            nav_graph: initialNavGaph
          }
      }, undefined, 'DataViewer/reset_graph'),
      zoom_view: (data: LineChartDataProps) => set((state) => {
        let { refAreaLeft, refAreaRight } = state.selector;
        if (refAreaLeft === refAreaRight || refAreaRight === 0) {
          state.reset_refAreas();
          return {}
        }

        if (refAreaLeft > refAreaRight) {
          [refAreaLeft, refAreaRight] = [refAreaRight, refAreaLeft];
        }
        const verticalRange = GraphHelper.getAxisYRange(
          data,
          refAreaLeft,
          refAreaRight
        )
        return {
          is_view_zoomed: true,
          nav_graph: {
            can_reload: true,
            can_go_back: true,
            can_go_after: true,
            can_zoom_in: true,
            can_zoom_out: true,
            can_go_start: true,
            can_go_end: true,
            zoom_level: state.nav_graph.zoom_level,
            move_level: state.nav_graph.move_level,
          },
          selector: {
            refAreaLeft: 0,
            refAreaRight: 0,
            left: refAreaLeft,
            right: refAreaRight,
          },
          zoom: {
            ...state.zoom,
            topLeft: verticalRange.topLeft,
            bottomLeft: verticalRange.bottomLeft,
            topRight: verticalRange.topRight,
            bottomRight: verticalRange.bottomRight,
          }
        }
      }, undefined, 'DataViewer/zoom_view'),
      reload_view: () => set(() => {
        return{
          is_view_zoomed: false,
          zoom: initialZoom,
          selector: initialSelector,
          nav_graph: initialNavView
        }
      }, undefined, 'DataViewer/reload_view'),
      toggle_can_zoom_view: () => set((state) => {
        const currentState = state.can_zoom_view === true
        if(currentState === false){
          state.reload_view()
          return {can_zoom_view: true}
        }
        return {
          nav_graph: initialNavGaph,
          can_zoom_view: currentState ? false : true
        }
      }, undefined, 'DataViewer/toggle_can_zoom_view'),
      reload: () => set((state) => {
        if(state.can_zoom_view === true){
          state.reload_view()
          return {}
        }
        state.reset_graph()
        return {}
      }, undefined, 'DataViewer/reload'),
      go_back: () => set((state) => {
        if(state.can_zoom_view === true){
          if(Ut.isNumber(state.selector.left)){
            const move = Math.ceil(Number(state.selector.left) * state.nav_graph.move_level)
            return {selector: {
              ...initialSelector,
              left: Number(state.selector.left) - move,
              right: Number(state.selector.right) - move
            }}
          }
          return {}
        }
        return{ time_start: state.time_start - Math.ceil(( state.time_window) * state.nav_graph.move_level) }
      }, undefined, 'DataViewer/go_back'),
      go_after: () => set((state) => {
        if(state.can_zoom_view === true){
          if(Ut.isNumber(state.selector.right)){
            const move = Math.ceil(Number(state.selector.right) * state.nav_graph.move_level)
            return {selector: {
              ...initialSelector,
              left: Number(state.selector.left) - move,
              right: Number(state.selector.right) - move
            }}
          }
          return {}
        }
        return{ time_start: state.time_start + Math.ceil(( state.time_window) * state.nav_graph.move_level) }
      }, undefined, 'DataViewer/go_after'),
      go_start: () => set((state) => {
        if(state.selected_feeds.length > 0){
          const currents = state.selected_feeds.filter(item => item.meta.start_time === state.time_start)
          if(currents.length > 0){
            const nexts = state.selected_feeds.filter(item => item.meta.start_time !== state.time_start)
            if(nexts.length > 0){
              return {
                time_start: nexts[0].meta.start_time,
                selector: initialSelector,
              }
            }
            return {}
          }
          return {
            time_start: state.selected_feeds[0].meta.start_time,
            selector: initialSelector,
          }
        }
        return {}
      }, undefined, 'DataViewer/go_start'),
      go_end: () => set((state) => {
        if(state.selected_feeds.length > 0){
          const currents = state.selected_feeds.filter(item => item.meta.end_time === state.time_start + state.time_window)
          if(currents.length > 0){
            const nexts = state.selected_feeds.filter(item => item.meta.end_time !== state.time_start + state.time_window)
            if(nexts.length > 0){
              return {
                time_start: nexts[0].meta.end_time - state.time_window,
                selector: initialSelector,
              }
            }
            return {}
          }
          return {
            time_start: state.selected_feeds[0].meta.end_time - state.time_window,
            selector: initialSelector,
          }
        }
        return {}
      }, undefined, 'DataViewer/go_end'),
      zoom_in: () => set((state) => {
        const move = Math.ceil(state.time_window * state.nav_graph.zoom_level)
        const zoom = GraphHelper.zoom_in(state.time_window - move)
        return ({
          nav_graph: {
            ...state.nav_graph,
            can_zoom_in: GraphHelper.zoom_in(zoom.time_window).time_window != zoom.time_window,
            can_zoom_out: true
          },
          selector: initialSelector,
          time_window: zoom.time_window,
          interval: zoom.interval,
          
        })
      }, undefined, 'DataViewer/zoom_in'),
      zoom_out: () => set((state) => {
        const move = Math.ceil(state.time_window * state.nav_graph.zoom_level)
        const zoom = GraphHelper.zoom_out(state.time_window + move)
        return ({
          nav_graph: {
            ...state.nav_graph,
            can_zoom_out: GraphHelper.zoom_out(zoom.time_window).time_window != zoom.time_window,
            can_zoom_in: true
          },
          selector: initialSelector,
          time_window: zoom.time_window,
          interval: zoom.interval
        })
      }, undefined, 'DataViewer/zoom_out'),
      toggle_connect_nulls: () => set((state) => {
          return {
            connect_nulls: state.connect_nulls === true ? false : true
          }
      }, undefined, 'DataViewer/toggle_connect_nulls'),
      reset_store: () => set(() => ({
          selected_feeds: [],
          time_start: 0,
          //time_window: 0,
          //interval: 0,
          nav_graph: initialNavGaph
          
      }), undefined, 'DataViewer/reset_store')
})

export const useDataViewer = create<DataViewerStore>()(
  devtools((...args) => (
    {
      ...createDataViewerSlice(...args),
  }
))
)