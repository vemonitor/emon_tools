import { Loader } from "@/components/layout/loader";
import { useAuth } from "@/hooks/use-auth";
import {
  FinaFileDb,
  GraphLocationProps,
  PreSelectedToGraph,
  SelectedFileItem,
  SelectedToGraph
} from "@/lib/graphTypes";
import { useDataViewer } from "@/stores/dataViewerStore";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { DataPath } from "@/routes/data-path/table-header-columns";
import { Status } from "@/lib/types";
import { ComboBoxResponsive } from "@/components/layout/combo-select";
import { ChangeEvent, useState } from "react";
import {
  SelectorCheck,
  SelectorDetail,
  SelectorItemConainer,
  SelectorItemHeader,
  SelectorsPane
} from "@/components/fina_viewer/graph-selector";
import { Separator } from "@/components/ui/separator";
import DialogForm from "@/components/form/dialog-form";
import { Button } from "@/components/ui/button";
import { BadgePlus, Pencil } from "lucide-react";
import { cn } from "@/lib/utils";
import Ut from "@/helpers/utils";
import EditArchiveFile from "@/routes/archive-file/edit";
import AddArchiveFile from "@/routes/archive-file/add";

type DataPathSelectorProps = {
  setSelectedPath: (dataPath: DataPath | null) => void
}

export function DataPathSelector({
  setSelectedPath
}: DataPathSelectorProps) {
  const { fetchWithAuth } = useAuth();
  const queryResult = useQuery(
    {
      queryKey: ['data_path'],
      retry: false,
      refetchOnMount: 'always',
      queryFn: () =>
        fetchWithAuth(
          `/api/v1/data_path/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json()),
    }
  );

  const dataToStatus = (data: DataPath[]) => {
    return data.map((item: DataPath) => {
      return {
        value: `${item.id}`,
        label: item.name,
      }
    })
  }

  const handleChange = (status: Status) => {
    if (status) {
      const selectedPath = queryResult.data.data.find((item: DataPath) => item.id === parseInt(status.value))
      setSelectedPath(selectedPath ? selectedPath : null);
    }

  }

  return (
    <div className='w-full h-full flex items-center justify-center'>
      {queryResult.isPending ? (
        <Loader />
      ) : queryResult.isError || !(queryResult.data && queryResult.data.count) ? (
        <div>No data available...</div>
      ) : (
        <ComboBoxResponsive
          defaultLabel="Path"
          statuses={dataToStatus(queryResult.data.data)}
          handleChange={handleChange}
        />
      )}
    </div>
  )
}

type FinaItemSelectorProps = {
  dataPath: DataPath,
  file: FinaFileDb;
  selectFileToGraph: (selected_item: PreSelectedToGraph) => void
}

export function FinaItemSelector({
  file,
  selectFileToGraph
}: FinaItemSelectorProps) {
  const [dialogOpen, dialogSetOpen] = useState(false);
  const selected_feeds = useDataViewer((state) => state.selected_feeds)

  const is_selected = (side: GraphLocationProps, file: FinaFileDb) => {
    const selecteds = selected_feeds.filter(
      item => item.side === side && item.id === file.file_db.file_id)
    return selecteds.length > 0
  }
  const getSelectedFeed = (
    e: ChangeEvent<HTMLInputElement>,
    side: GraphLocationProps
  ): PreSelectedToGraph => {
    const target = e.target;
    const is_checked = target.type === 'checkbox' && target.checked;
    const file_id = Number(target.value)
    return {
      is_checked: is_checked,
      id: file_id,
      side: side,
    }
  }
  const handleGraphLeft = (e: ChangeEvent<HTMLInputElement>) => {
    const item = getSelectedFeed(e, 'left');
    selectFileToGraph(item)
  }

  const handleGraphRight = (e: ChangeEvent<HTMLInputElement>) => {
    const item = getSelectedFeed(e, 'right');
    selectFileToGraph(item)
  }
  const handleSuccessForm = () => {
    dialogSetOpen(false)
  }

  const get_variant = (file: FinaFileDb) => {
    if (Ut.isObject(file.file_db)
      && Ut.isNumber(file.file_db.file_id, { positive: true })) {
      return "success"
    }
    return "error"
  }

  const get_form = (file: FinaFileDb) => {
    if (Ut.isObject(file.file_db) && Ut.isNumber(
      file.file_db.file_id, { positive: true })) {
      return (
        <DialogForm
          dialogOpen={dialogOpen}
          dialogSetOpen={dialogSetOpen}
          title="Edit Fina File"
          trigger={(
            <Button
              variant='ghost'
              className='m-auto'
            >
              Edit <Pencil />
            </Button>
          )}
          form={(
            <EditArchiveFile
              row_id={file.file_db?.file_id ?? undefined}
              is_dialog={true}
              successCallBack={handleSuccessForm}
            />
          )}
        />)
    }
    return (
      <DialogForm
        dialogOpen={dialogOpen}
        dialogSetOpen={dialogSetOpen}
        title="Add Fina File"
        trigger={(
          <Button
            variant='ghost'
            className='m-auto'
          >
            Add <BadgePlus />
          </Button>
        )}
        form={(
          <AddArchiveFile
            is_dialog={true}
            successCallBack={handleSuccessForm}
            data={{
              file_name: file.file_name,
              name: file.name
            }}
          />
        )}
      />)
  }
  return (
    <SelectorItemConainer
      variant={get_variant(file)}
    >
      <SelectorItemHeader>{file.name}</SelectorItemHeader>
      <Separator className="my-1" />
      <SelectorCheck
        itemId={file.file_db?.file_id ?? 0}
        is_left={is_selected("left", file)}
        handleSelectLeft={handleGraphLeft}
        is_right={is_selected("right", file)}
        handleSelectRight={handleGraphRight}
      >
        {get_form(file)}
      </SelectorCheck>
      <Separator className="my-1" />
      <SelectorDetail
        meta={file.meta}
      />
    </SelectorItemConainer>
  )
}

type FinaListSelectorProps = {
  dataPath: DataPath
}

export function FinaListSelector({
  dataPath
}: FinaListSelectorProps) {
  const { fetchWithAuth } = useAuth();
  const add_feed = useDataViewer((state) => state.add_feed)
  const remove_feed = useDataViewer((state) => state.remove_feed)
  const init_time_start = useDataViewer((state) => state.init_time_start)

  const queryClient = useQueryClient();
  const queryResult = useQuery(
    {
      queryKey: ['emon_fina_files', dataPath.slug],
      retry: false,
      refetchOnMount: 'always',
      enabled: dataPath.slug ? true : false,
      queryFn: () =>
        fetchWithAuth(
          `/api/v1/fina_data/files/by/${dataPath.slug}/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json()),
    }
  );
  
  const selectFileToGraph = (
    pre_selected: PreSelectedToGraph
  ) => {
    const selected_item = queryResult.data.files.filter(
      (item: SelectedFileItem) => item.file_db?.file_id === pre_selected.id
    ) as FinaFileDb[]
    const selected = {
      ...pre_selected,
      name: selected_item[0]?.name,
      meta: selected_item[0]?.meta,
      files_db: selected_item[0]?.file_db
    } as SelectedToGraph
    if (selected.is_checked) {
      add_feed(selected)
      init_time_start(selected.meta.start_time)
    } else {
      remove_feed(selected)
    }
    queryClient.invalidateQueries({ queryKey: ['emon_fina_datas'] })
  }

  return (
    <div className='w-full h-full flex-col gap-2'>
      {queryResult.isPending ? (
        <Loader />
      ) : queryResult.isError || !(queryResult.data && queryResult.data.success) ? (
        <div>No data available...</div>
      ) : (
        (
          queryResult.data.files.map((file: FinaFileDb, index: number) => [
            <FinaItemSelector
              key={index}
              dataPath={dataPath}
              file={file}
              selectFileToGraph={selectFileToGraph}
            />,
            <Separator key={`sep_${index}`} className="my-2" />
          ])
        )
      )}
    </div>
  )
}

type FinaViewerListProps = {
  selectedPath: DataPath | null;
  setSelectedPath: (dataPath: DataPath | null) => void
  path_slug?: string;
  classBody?: string;
}

export function FinaViewerList({
  selectedPath,
  setSelectedPath,
  path_slug,
  classBody
}: FinaViewerListProps) {
  const { fetchWithAuth } = useAuth();
  useQuery(
    {
      queryKey: ['data_path', path_slug],
      retry: false,
      refetchOnMount: 'always',
      enabled: path_slug ? true : false,
      queryFn: () =>
        fetchWithAuth(
          `/api/v1/data_path/by/${path_slug}/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json())
          .then((data) => {
            if (data.success) {
              setSelectedPath(data.data)
            }
            return data
          })
    }
  );

  return (
    <SelectorsPane className={cn('w-full h-full flex-1 [&>[data-radix-scroll-area-viewport]]:max-h-[calc(100vh)]', classBody)}>
      <div className='flex flex-col gap-2'>
        {!path_slug ? (
          <DataPathSelector
            setSelectedPath={setSelectedPath}
          />
        ) : null}
        {selectedPath && <FinaListSelector
          dataPath={selectedPath}
        />}
      </div>
    </SelectorsPane>
  )
}
