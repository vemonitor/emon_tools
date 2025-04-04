import { ComboBoxResponsive } from "@/components/layout/combo-select";
import { Loader } from "@/components/layout/loader";
import { useAuth } from "@/hooks/use-auth";
import {
    FeedDb,
    GraphLocationProps,
    PreSelectedToGraph,
    SelectedToGraph
} from "@/lib/graphTypes";
import { Status } from "@/lib/types";
import { useDataViewer } from "@/stores/dataViewerStore";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { EmonHost } from "../emon-host/table-header-columns";
import { ChangeEvent, useState } from "react";

import {
    SelectorCheck,
    SelectorDetail,
    SelectorItemConainer,
    SelectorItemHeader,
    SelectorsPane
} from "@/components/fina_viewer/graph-selector";
import DialogForm from "@/components/form/dialog-form";
import { Button } from "@/components/ui/button";
import { Settings2 } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

type HostSelectorProps = {
    setSelectedHost: (emonHost: EmonHost | null) => void
}

export function HostSelector({
    setSelectedHost
}: HostSelectorProps) {
    const { fetchWithAuth } = useAuth();
    const queryResult = useQuery(
        {
            queryKey: ['emon_host'],
            retry: false,
            refetchOnMount: 'always',
            queryFn: () =>
                fetchWithAuth(
                    `/api/v1/emon_host/`,
                    {
                        method: 'GET',
                    }
                ).then((response) => response.json()),
        }
    );

    const dataToStatus = (data: EmonHost[]) => {
        return data.map((item: EmonHost) => {
            return {
                value: `${item.id}`,
                label: item.name,
            }
        })
    }

    const handleChange = (status: Status) => {
        if (status) {
            const selectedHost = queryResult.data.data.find((item: EmonHost) => item.id === parseInt(status.value))
            setSelectedHost(selectedHost ? selectedHost : null);
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
                    defaultLabel="Host"
                    statuses={dataToStatus(queryResult.data.data)}
                    handleChange={handleChange}
                />
            )}
        </div>
    )
}

type FeedSettingsProps = {
    feed: FeedDb;
    successCallBack?: () => void
}

export function FeedSettings({
    feed,
    successCallBack
}: FeedSettingsProps) {
    return null
}

type FeedItemSelectorProps = {
    emonHost: EmonHost,
    feed: FeedDb;
    selectFeedToGraph: (selected_item: PreSelectedToGraph) => void
}

export function FeedItemSelector({
    feed,
    selectFeedToGraph
}: FeedItemSelectorProps) {
    const [dialogOpen, dialogSetOpen] = useState(false);
    const selected_feeds = useDataViewer((state) => state.selected_feeds)

    const is_selected = (side: GraphLocationProps, file: FeedDb) => {
        const selecteds = selected_feeds.filter(
            item => item.side === side && item.id === file.id)
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
        selectFeedToGraph(item)
    }

    const handleGraphRight = (e: ChangeEvent<HTMLInputElement>) => {
        const item = getSelectedFeed(e, 'right');
        selectFeedToGraph(item)
    }
    const handleSuccessForm = () => {
        dialogSetOpen(false)
    }

    const get_variant = (feed: FeedDb) => {
        if (feed) {
            return "success"
        }
        return "error"
    }

    const get_form = (feed: FeedDb) => {
        return (
            <DialogForm
                dialogOpen={dialogOpen}
                dialogSetOpen={dialogSetOpen}
                title="Feed Settings"
                trigger={(
                    <Button
                        variant='ghost'
                        className='m-auto'
                    >
                        <Settings2 />
                    </Button>
                )}
                form={(
                    <FeedSettings
                        feed={feed}
                        successCallBack={handleSuccessForm}
                    />
                )}
            />
        )
    }
    return (
        <SelectorItemConainer
            variant={get_variant(feed)}
        >
            <SelectorItemHeader>{feed.name}</SelectorItemHeader>
            <Separator className="my-1" />
            <SelectorCheck
                itemId={feed.id ?? 0}
                is_left={is_selected("left", feed)}
                handleSelectLeft={handleGraphLeft}
                is_right={is_selected("right", feed)}
                handleSelectRight={handleGraphRight}
            >
                {get_form(feed)}
            </SelectorCheck>
            <Separator className="my-1" />
            <SelectorDetail
                meta={feed.meta}
            />
        </SelectorItemConainer>
    )
}

type FeedListSelectorProps = {
    emonHost: EmonHost
}

export function FeedListSelector({
    emonHost
}: FeedListSelectorProps) {
    const { fetchWithAuth } = useAuth();
    const add_feed = useDataViewer((state) => state.add_feed)
    const remove_feed = useDataViewer((state) => state.remove_feed)
    const init_time_start = useDataViewer((state) => state.init_time_start)

    const queryClient = useQueryClient();
    const queryResult = useQuery(
        {
            queryKey: ['emoncms_feeds', emonHost.slug],
            retry: false,
            refetchOnMount: 'always',
            enabled: emonHost.slug ? true : false,
            queryFn: () =>
                fetchWithAuth(
                    `/api/v1/emoncms/feeds/${emonHost.slug}/`,
                    {
                        method: 'GET',
                    }
                ).then((response) => response.json()),
        }
    );
    const selectFeedToGraph = (
        pre_selected: PreSelectedToGraph
    ) => {
        const selected_item = queryResult.data.feeds.filter(
            (item: FeedDb) => item.id === pre_selected.id
        )
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
        queryClient.invalidateQueries({ queryKey: ['emoncms_datas'] })
    }

    return (
        <div className='w-full h-full flex-col gap-2'>
            {queryResult.isPending ? (
                <Loader />
            ) : queryResult.isError || !(queryResult.data && queryResult.data.success) ? (
                <div>No data available...</div>
            ) : (
                (
                    queryResult.data.feeds.map((feed: FeedDb, index: number) => [
                        <FeedItemSelector
                            key={index}
                            emonHost={emonHost}
                            feed={feed}
                            selectFeedToGraph={selectFeedToGraph}
                        />,
                        <Separator key={`sep_${index}`} className="my-2" />
                    ])
                )
            )}
        </div>
    )
}
type HostFeedViewerListProps = {
    selectedHost: EmonHost | null;
    setSelectedHost: (emonHost: EmonHost | null) => void
    host_slug?: string;
    classBody?: string;
}

export function HostFeedViewerList({
    selectedHost,
    setSelectedHost,
    host_slug,
    classBody
}: HostFeedViewerListProps) {
    const { fetchWithAuth } = useAuth();
    // Conditionaly fetch the host data
    useQuery(
        {
            queryKey: ['emon_host', host_slug],
            retry: false,
            refetchOnMount: 'always',
            enabled: host_slug ? true : false,
            queryFn: () =>
                fetchWithAuth(
                    `/api/v1/emon_host/by/${host_slug}/`,
                    {
                        method: 'GET',
                    }
                ).then((response) => (response.json())
                    .then((data) => {
                        if (data.success) {
                            setSelectedHost(data.data)
                        }
                        return data
                    })
                ),
        }
    );
    return (
        <SelectorsPane className={cn('w-full h-full flex-1 [&>[data-radix-scroll-area-viewport]]:max-h-[calc(100vh)]', classBody)}>
            <div className='flex flex-col gap-2'>
                {!host_slug ? (
                    <HostSelector
                        setSelectedHost={setSelectedHost}
                    />
                ) : null}
                {selectedHost && <FeedListSelector
                    emonHost={selectedHost}
                />}
            </div>
        </SelectorsPane>
    )
}
