import { create, StateCreator } from "zustand"
import { devtools } from "zustand/middleware"

type navigationStore = {
    current_page: string
    set_current_page: (page: string) => void,
}

const createPageSlice: StateCreator<
navigationStore,
[['zustand/devtools', never]],
[],
navigationStore
> = (set) => ({
      current_page: '',
      // store methods
      set_current_page: (page: string) => set( () => (
        { current_page: page }
      ), undefined, 'navigation/set_current_page'),
})

export const useNavigation = create<navigationStore>()(
  devtools((...args) => (
    {
      ...createPageSlice(...args),
  }
))
)