import { create } from 'zustand';

interface FilterState {
  clientStageFilter: string | null;
  taskStatusFilter: string | null;
  emailStatusFilter: string | null;
  searchQuery: string;
  setClientStageFilter: (stage: string | null) => void;
  setTaskStatusFilter: (status: string | null) => void;
  setEmailStatusFilter: (status: string | null) => void;
  setSearchQuery: (query: string) => void;
  clearFilters: () => void;
}

export const useFilterStore = create<FilterState>((set) => ({
  clientStageFilter: null,
  taskStatusFilter: null,
  emailStatusFilter: null,
  searchQuery: '',
  setClientStageFilter: (stage) => set({ clientStageFilter: stage }),
  setTaskStatusFilter: (status) => set({ taskStatusFilter: status }),
  setEmailStatusFilter: (status) => set({ emailStatusFilter: status }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  clearFilters: () =>
    set({
      clientStageFilter: null,
      taskStatusFilter: null,
      emailStatusFilter: null,
      searchQuery: '',
    }),
}));
